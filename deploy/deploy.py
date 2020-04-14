import os
import sys
from time import sleep

import onnx
import tarfile
import numpy as np

import tvm
import tvm.relay as relay
from tvm import autotvm
from tvm.autotvm.tuner import XGBTuner, GATuner, RandomTuner, GridSearchTuner
from tvm.contrib import util, graph_runtime

batch_size = 1
calibration_samples = 99
log_file = 'log_file.log'
quantize_flag = False
autotvm_flag = False
tuning_option = {
    'log_filename': log_file,
    'tuner': 'xgb',
    'n_trial': 2000,
    'early_stopping': 600,
    'measure_option': autotvm.measure_option(
        builder=autotvm.LocalBuilder(timeout=10),
        runner=autotvm.LocalRunner(number=20, repeat=3, timeout=4, min_repeat_ms=150),
    ),
}


def save_tempdir(graph, lib, params):
    tempdir = util.tempdir()
    lib.export_library(tempdir.relpath('deploy_lib.tar'))
    with open(tempdir.relpath('deploy_graph.json'), 'w') as fo:
        fo.write(graph)
    with open(tempdir.relpath('deploy_param.params'), 'wb') as fo:
        fo.write(relay.save_param_dict(params))

    return tempdir


def save(tempdir, save_path, module_name='deploy'):
    tar_path = save_path + module_name + '.tar.gz'
    if os.path.isfile(tar_path):
        os.remove(tar_path)

    tar = tarfile.open(name=tar_path, mode='w:gz')
    tar.add(tempdir.relpath('deploy_lib.tar'), arcname='deploy_lib.tar')
    tar.add(tempdir.relpath('deploy_graph.json'), arcname='deploy_graph.json')
    tar.add(tempdir.relpath('deploy_param.params'), arcname='deploy_param.params')
    tar.close()


def convert(module, target, quantize_flag=False, autotvm_flag=False):
    print("Convert start...")
    module_graph = module.graph
    input_blob = module_graph.input[0]
    input_shape = tuple(map(lambda x: getattr(x, 'dim_value'), input_blob.type.tensor_type.shape.dim))
    input_name = input_blob.name
    shape_dict = {input_name: input_shape}
    mod, params = relay.frontend.from_onnx(module, shape_dict)
    if quantize_flag:
        mod = quantize(mod, params)
    if autotvm_flag:
        graph, lib, params = tune(tuning_option, mod, params, target)
        return save_tempdir(graph, lib, params)
    # relay.frontend.from_pytorch 也可,后续可以根据模型类型进行不同转换
    else:
        with relay.build_config(opt_level=3):
            graph, lib, params = relay.build(mod, target=target, params=params)
        return save_tempdir(graph, lib, params)


def get_val_data():
    root = 'dataset/imagenet-val-100/val/'
    meta = 'dataset/meta/val.txt'
    from torchvision.transforms import transforms
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    from PIL import Image
    with open(meta, 'r') as f:
        content = f.readlines()
        for i in range(0, len(content), batch_size):
            batch = content[i:i + batch_size]
            imgs = []
            categories = []
            for item in batch:
                img_name, category = item.strip().split()
                category = int(category)

                with Image.open(root + img_name) as img:
                    img = img.convert('RGB')
                    img = preprocess(img)
                imgs.append(img.detach().numpy())
                categories.append(category)
                yield {'data': np.stack(imgs), 'label': categories}


def calibrate_dataset():
    generator = get_val_data()
    for i, batch in enumerate(generator):
        if i * batch_size >= calibration_samples:
            break
        yield {'data': batch['data']}


def quantize(mod, params):
    print("Quantizing...")
    with relay.quantize.qconfig(calibrate_mode='kl_divergence', weight_scale='max'):
        mod = relay.quantize.quantize(mod, params, dataset=calibrate_dataset())
    return mod


def tune_tasks(tasks, measure_option,tuner='xgb',n_trial=1000,early_stopping=None,
               log_filename='tuning.log', use_transfer_learning=True):
    tmp_log_file = log_filename + ".tmp"
    if os.path.exists(tmp_log_file):
        os.remove(tmp_log_file)

    for i, tsk in enumerate(reversed(tasks)):
        prefix = "[Task %2d/%2d] " % (i + 1, len(tasks))

        # create tuner
        if tuner == 'xgb' or tuner == 'xgb-rank':
            tuner_obj = XGBTuner(tsk, loss_type='rank', num_threads=12)
        elif tuner == 'ga':
            tuner_obj = GATuner(tsk, pop_size=100)
        elif tuner == 'random':
            tuner_obj = RandomTuner(tsk)
        elif tuner == 'gridsearch':
            tuner_obj = GridSearchTuner(tsk)
        else:
            raise ValueError("Invalid tuner: " + tuner)

        if use_transfer_learning:
            if os.path.isfile(tmp_log_file):
                tuner_obj.load_history(autotvm.record.load_from_file(tmp_log_file))

        # do tuning
        tsk_trial = min(n_trial, len(tsk.config_space))
        tuner_obj.tune(n_trial=tsk_trial,
                       early_stopping=early_stopping,
                       measure_option=measure_option,
                       callbacks=[
                           autotvm.callback.progress_bar(tsk_trial, prefix=prefix),
                           autotvm.callback.log_to_file(tmp_log_file)
                       ])

    # pick best records to a cache file
    autotvm.record.pick_best(tmp_log_file, log_filename)
    os.remove(tmp_log_file)


def tune(tuning_opt, mod, params, target):
    print("Extract tasks...")
    tasks = autotvm.task.extract_from_program(mod["main"], target=tvm.target.cuda(),
                                              params=params,
                                              ops=(relay.op.get("nn.conv2d"),))
    # run tuning tasks
    print("Tuning...")
    tune_tasks(tasks, **tuning_opt)
    # compile kernels with history best records
    with autotvm.apply_history_best(log_file):
        print("Compile...")
        with relay.build_config(opt_level=3):
            graph, lib, params = relay.build_module.build(
                mod, target=target, params=params)
            return graph, lib, params


def inference(tempdir, target):
    context = tvm.context(str(target), 0)

    graph = open(tempdir.relpath('deploy_graph.json')).read()
    lib = tvm.runtime.load_module(tempdir.relpath('deploy_lib.tar'))
    params = bytearray(open(tempdir.relpath('deploy_param.params'), 'rb').read())

    module = graph_runtime.create(graph, lib, context)
    module.load_params(params)
    #evaluate time cost
    print("Evaluate inference time cost...")
    ftimer = module.module.time_evaluator("run", context, number=1, repeat=600)
    prof_res = np.array(ftimer().results) * 1000
    print("Mean inference time (std dev): %.2f ms (%.2f ms)" %
          (np.mean(prof_res), np.std(prof_res)))


def run_deploy(model_path, target, quantize_flag=False, autotvm_flag=False, inference_flag=False):
    if os.path.isfile(model_path):
        model = onnx.load(model_path)
    print("model in " + model_path)
    print("target " + target)
    tempdir = convert(model, target, quantize_flag, autotvm_flag)
    if inference_flag:
        inference(tempdir, target)
    save_path = "download/tem/"
    save(tempdir, save_path)


def main():
    module_path = sys.argv[1]
    module = onnx.load(module_path)
    target = sys.argv[2]
    quantize_flag = True if sys.argv[3] == 'quantize' else False
    autotvm_flag = True if sys.argv[4] == 'tune' else False
    print("module in " + module_path)
    print("target: " + target)
    print('quantize: ' + str(quantize_flag))
    print('autotune: ' + str(autotvm_flag))
    tempdir = convert(module, target, quantize_flag, autotvm_flag)
    inference(tempdir, target)
    save_path = "download/tem/"
    save(tempdir, save_path)
    print("module saved in " + save_path)
    print("$EOF$")

if __name__ == '__main__':
    main()
