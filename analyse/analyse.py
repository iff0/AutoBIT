import onnx
import sys

def param_cnt(model, weight_name):
    weights = model.graph.initializer
    for w in weights:
        if w.name == weight_name:
            return len(w.raw_data)

def analyze(model):
    conv_cnt = 0
    fc_cnt = 0
    conv_param_cnt = 0
    fc_param_cnt = 0
    layers = []
    for node in model.graph.node:
        temp_param_cnt = 0
        temp_name = ''
        if node.op_type == 'Conv':
            weight_name = node.input[1]
            temp_name = str(weight_name).split('.')[0]
            w_cnt = param_cnt(model, weight_name)
            conv_param_cnt += w_cnt
            temp_param_cnt += w_cnt
            if len(node.input) == 3:
                bias_name = node.input[2]
                b_cnt = param_cnt(model, bias_name)
                conv_param_cnt += b_cnt
                temp_param_cnt += b_cnt
            conv_cnt += 1
            layers.append((temp_name, temp_param_cnt))

        elif node.op_type == 'Gemm':
            weight_name = node.input[1]
            temp_name = str(weight_name).split('.')[0]
            w_cnt = param_cnt(model, weight_name)
            fc_param_cnt += w_cnt
            temp_param_cnt += w_cnt
            if len(node.input) == 3:
                bias_name = node.input[2]
                b_cnt = param_cnt(model, bias_name)
                fc_param_cnt += b_cnt
                temp_param_cnt += b_cnt
            fc_cnt += 1
            layers.append((temp_name, temp_param_cnt))
    analyze_dict = {
        'conv_cnt': conv_cnt,
        'fc_cnt': fc_cnt,
        'conv_param_cnt': conv_param_cnt,
        'fc_param_cnt': fc_param_cnt,
        'layers': layers
    }
    return analyze_dict

def main():
    model_name = sys.argv[1]
    model_path = "../upload/tem/" + model_name
    model = onnx.load(model_path)
    analyze_dict = analyze(model)
    print(analyze_dict['conv_cnt'])
    print(analyze_dict['fc_cnt'])
    print(analyze_dict['conv_param_cnt'])
    print(analyze_dict['fc_param_cnt'])
    print(analyze_dict['layers'])

if __name__ == '__main__':
    main()