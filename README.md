## web_browser_side


### python库:

`netron`, `django`, `tvm`

### 现有目标
+ 重构`html`
+ ~~加入`django`~~

### 可视化方案
+ ~~`matplotlib` + `jquery`~~
+ `echarts` + `jquery` + `json`

### 仓库视图
+ `newdj/`
    > 设置及路径映射
    + `settings.py`
      
        > 全局设置
    + `urls.py`
      
        > 路径映射
+ `static/`
    > 静态文件目录
    + `js/`
    + `css/`
    + `..`
+ `templates/`
    > 模板文件目录
    + `index.html`
      
        > 主页
    + `deploy.html`
    + `analyse.html`
+ `upload/`
    > 文件上传目录
    + `tem/`
      
        > 缓存目录
+ 应用功能
    + `guide/`
    + `deploy/`
    + `analyse/`

### url分配
+ `^guide/.*`
    + `^guide/upload/.*`
      
        > 文件上传
    + `^guide/structure_view/.*`
      
        > 结构可视化
+ `^deploy/.*`

+ `^analyse/.*`
    + `^analyse/params/.*`
      
        > 静态各层参数量分析
        
        > 卷积层与全连接层层数占比
        
        > 卷积层与全连接层参数量占比

    + `^analyse/run_time/.*`
        
        > 各层运行时间对比

### 服务器的启动
`cd .`<br>
`python manager.py runserver --port 8000`<br>
`Starting development server at http://127.0.0.1:8000/`<br>

### 更新日志
#### v0.4.2
+ 对接了django部分交互事件
+ 首页文件上传、下载正常
+ 分析页实现单页tag切换
+ 内嵌echarts脚本， 正常接收服务器预设数据并绘图

#### v0.4.3

+ deploy/：增加文件下载与平台选择
+ 对接了analyse/的静态分析代码

#### v0.4.4

+ deploy/: 把ace-editor改装成实时输出代码的UI
+ deploy/: 左上角的模型基本信息是真实的了
+ 修复侧边栏显示bug

#### v0.4.5
+ 对接后端模型部署与日志输出
+ 增加上传进度条与参数选项
