import os
import sys
import inspect
import suanpan
from suanpan.app.arguments import String, Json, ListOfString, Bool, Int
from suanpan.app import app
from suanpan.storage import storage
from suanpan.log import logger
from suanpan import g
from suanpan.node import node
from suanpan_custom_code.packages.common.auto_sync_inputs import AutoSyncInputs
from suanpan_custom_code.packages.common.type_convert import cast


g.mod = None
g.mod1 = None
g.autoSyncObj = None


def check_all_class(module_name, class_name):
    """检查输入类名是否在指定python模块

    Args:
        module_name (string): 模块名
        class_name (string): 类名

    Returns:
        bool: True/False
    """
    classes = []
    cls_members = inspect.getmembers(module_name, inspect.isclass)
    for (name, value) in cls_members:
        classes.append(name)
    if class_name in classes:
        return True
    else:
        return False


def installPip(name, version):
    """安装pip包

    Args:
        name (string): 包名
        version (string): 版本号

    Returns:
        None: 安装pip包
    """
    package_name = name
    package_version = version
    if package_version != "":
        os.system(f"pip install {package_name}=={package_version}")
    else:
        os.system(f"pip install {package_name}")


def send(x):
    """组件回调函数，
    开发者需要用app.send将x发送输出。

    Args:
        x (any): 需要输出的数据。
    """
    t1 = tuple([x])
    print(f"x: {x}, call app.send(x)")
    app.send(t1, args=node.outargs)


@app.param(String(key="param1", alias="pythonFilePath"))
@app.param(ListOfString(key="param2", alias="resourceFilePath"))
@app.param(Json(key="param3", alias="requirements"))
@app.param(Json(key="param4", alias="pythonClassParameters"))
@app.param(String(key="param5", alias="className", default="CustomCode"))
@app.param(Bool(key="param6", alias="autoSyncInputs", default=False))
@app.param(Int(key="param7", alias="queueLength", default=100))
def upload(context):
    args = context.args
    # logger.info(f"my params is {args}")
    # 加载输入数据
    try:
        inargs = app.load(node.inargs)
    except Exception as e:
        logger.info(f"输入具体类型异常, {e}")
        return
    # 从组件输入端按顺序接收run函数的参数
    run_param_list = [
        value for key, value in inargs.items() if "inputData" in key
    ]
    # 判断是否异步转同步
    if args.autoSyncInputs:
        run_param_list = g.autoSyncObj.stage(*run_param_list)
        if not run_param_list:
            return
    # 增加hints格式自动转换
    g.mod1.run = cast(g.mod1.run)
    result = g.mod1.run(*run_param_list)
    # 如果run函数有return,再构造结果send
    if result:
        d1 = {}
        try:
            for i in range(len(result)):
                d1[f"out{i+1}"] = result[i]
        except Exception:
            d1["out1"] = result
        finally:
            # logger.info(f"d1 is {d1}")
            app.send(d1, args=node.outargs)


@app.afterInit
def onInitialSetup(context):
    args = context.args
    print(args)
    inargs = node.inargs  # 加载输入类型
    outargs = node.outargs  # “加载”输出类型
    # 　打印每个输入端子类型
    for i, inarg in enumerate(inargs):
        print(f"in{i+1} is a {inarg.__class__.__name__}")
    # 打印每个输出端子输出类型
    for i, outarg in enumerate(outargs):
        print(f"out{i+1} is a {outarg.__class__.__name__}")
    # 部署后进行类的实例化和下载文件(这些都是在配置参数就能获取)
    # 第一个配置参数: python文件路径
    pythonFilePath = args.pythonFilePath
    pythonFileName = os.path.basename(pythonFilePath)  # 带后缀
    storage.download(pythonFilePath, pythonFileName)
    pythonFilePath = os.path.join(os.getcwd(), pythonFileName)  # 下载到本地的路径
    logger.info(f"python文件路径：{pythonFilePath}")
    assert os.path.isfile(pythonFilePath)
    # param2: 资源文件路径列表, storage下载到本地, python文件和资源文件就在同一目录
    # param2可以为空, 这个添加系统路径是为了上传的python文件初始导包
    resourceFilePath = args.resourceFilePath
    if resourceFilePath:
        for fname in args.resourceFilePath:
            sys.path.append(os.path.dirname(fname))
            storage.download(fname, os.path.basename(fname))
    # param3: 依赖库信息,pip安装，在运行python文件前安装
    if args.requirements:
        for name, version in args.requirements.items():
            # print(name, version)
            installPip(name, version)
    # param5: 类名,有默认值,需检测用户输入类名是否在python模块中
    moduleName = os.path.splitext(pythonFileName)[0]
    className = args.className
    import importlib.util

    spec = importlib.util.spec_from_file_location(moduleName, pythonFilePath)
    g.mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g.mod)
    if check_all_class(g.mod, className):
        # param4: 类实例化的参数
        ini_params = args.pythonClassParameters
        # logger.info(f"ini_params is {ini_params}")
        try:
            if ini_params is not None:
                g.mod1 = getattr(g.mod, args.className)(**ini_params)  # 实例化
            else:
                g.mod1 = getattr(g.mod, args.className)()
        except Exception as e:
            logger.info(f"实例化错误,{e}")
            return
        else:
            g.mod1.send = send  # 添加send函数

    else:
        logger.info("输入类名不在python模块中")
        return
    # param6和param7创建队列
    if args.autoSyncInputs:
        max_length = args.queueLength
        g.autoSyncObj = AutoSyncInputs(max_length, len(inargs))


if __name__ == "__main__":
    suanpan.run(app)
