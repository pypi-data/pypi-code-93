"""
author : kerwin
function : personal settings
note : 用于修改所有文件的默认配置信息

警示： 以后再配置默认路径的时候，不要带上尾巴上的‘/’.  实际应用中看着不舒服。。。
        ("D:/自如/" 由于历史原因，不想改了。。。) //k200207:已经修改回来了
"""


"""
mac 和 linux 的路径除了开头的/Users 替换成 /home 外，其他是一样的。
"""



# 自动判断该系统是 ’windows' 还是 ‘mac’
import platform
import sys, os


# 配置信息
user_name   = "kerwin" # [重点提醒]: 使用kw618这个库之前必须做好 '用户名修改' !!!


    # win
if platform.system() == "Windows":
    PYTHON = "python"
    HOST = "127.0.0.1"
    REMOTE_HOST = "120.55.63.193" # 阿里云的ip
    REMOTE_HOST = "kw618.xyz" # 阿里云的ip
    FILE_PATH_FOR_DESKTOP = "C:/Users/Administrator/Desktop"
    FILE_PATH_FOR_MYCODE = f"D:/{user_name}/MyCode"
    FILE_PATH_FOR_LIBS = f"D:/{user_name}/MyCode/Libs"
    FILE_PATH_FOR_ZIRU_CODE = f"D:/{user_name}/MyCode/BusinessProj/Ziru"
    FILE_PATH_FOR_ZIRU = "D:/自如"

    # mac
elif platform.system() == "Darwin":
    PYTHON = "python3"
    HOST = "127.0.0.1" # 本地ip  (mac上的代码默认用本地ip，若个别脚本有特别需要，可以设置成REMOTE_HOST)
    REMOTE_HOST = "120.55.63.193" # 阿里云的ip
    REMOTE_HOST = "kw618.xyz" # 阿里云的ip
    FILE_PATH_FOR_HOME = f"/Users/{user_name}" # 家目录
    FILE_PATH_FOR_DESKTOP = f"/Users/{user_name}/Desktop"
    FILE_PATH_FOR_MYBOX = f"/Users/{user_name}/MyBox"
    # FILE_PATH_FOR_KW618 = f"/Users/{user_name}/MyBox/kw618/kw618"  # 尽量减少使用这个文件路径 (因为它是pypi包, 不应该有固定路径!!!)
    FILE_PATH_FOR_MYCODE = f"/Users/{user_name}/MyBox/MyCode" # 最顶层代码目录
    FILE_PATH_FOR_LIBS = f"/Users/{user_name}/MyBox/MyCode/Libs" # 指: 顶层目录中用于存储 "资源" 的目录
    FILE_PATH_FOR_ZIRU_CODE = f"/Users/{user_name}/MyBox/MyCode/BusinessProj/Ziru" # 指:"自如项目代码"的路径
    FILE_PATH_FOR_ZIRU = f"/Users/{user_name}/MyBox/工作相关/自如" # 指:"自如excel, ppt等文件的目录"的路径
    FILE_PATH_FOR_VUE = f"/Users/{user_name}/MyBox/VueProj"

    proxy_host = "127.0.0.1"
    proxy_port = "7890"
    http_proxy_host = proxy_host
    http_proxy_port = proxy_port

    # linux
elif platform.system() == "Linux":
    PYTHON = "python3"
    HOST = "127.0.0.1"
    REMOTE_HOST = "120.55.63.193" # 阿里云的ip
    # REMOTE_HOST = "kw618.xyz" # 阿里云的ip
    FILE_PATH_FOR_HOME = f"/home/{user_name}" # 家目录
    FILE_PATH_FOR_DESKTOP = f"/home/{user_name}/Desktop"
    FILE_PATH_FOR_MYBOX = f"/home/{user_name}/MyBox"
    # FILE_PATH_FOR_KW618 = f"/home/{user_name}/MyBox/kw618/kw618" # 尽量减少使用这个文件路径 (因为它是pypi包, 不应该有固定路径!!!)
    FILE_PATH_FOR_MYCODE = f"/home/{user_name}/MyBox/MyCode"
    FILE_PATH_FOR_LIBS = f"/home/{user_name}/MyBox/MyCode/Libs"
    FILE_PATH_FOR_ZIRU_CODE = f"/home/{user_name}/MyBox/MyCode/BusinessProj/Ziru"
    FILE_PATH_FOR_ZIRU = f"/home/{user_name}/MyBox/工作相关/自如"
    FILE_PATH_FOR_VUE = f"/home/{user_name}/MyBox/VueProj"

    proxy_host = ""
    proxy_port = ""
    http_proxy_host = proxy_host
    http_proxy_port = proxy_port


# # 自动搜索kw618库包的位置 (暂时不用pypi的包, 所以可以定死"FILE_PATH_FOR_KW618"的路径) (上面已经定死, 这里后期优化)
site_pkgs_path = [path for path in sys.path if "packages" in path]
FILE_PATH_FOR_KW618 = ""
    # 1. 先看本地目录路径中是否有 'kw618'
if os.path.exists(f"{FILE_PATH_FOR_MYBOX}/kw618/kw618"):
    FILE_PATH_FOR_KW618 = f"{FILE_PATH_FOR_MYBOX}/kw618/kw618"
    kw618_pkg = "Local"
else:
    # 2. 再看第三方库中是否有 'kw618'
    for path in site_pkgs_path:
        if os.path.exists(f"{path}/kw618"):
            FILE_PATH_FOR_KW618 = f"{path}/kw618"
            kw618_pkg = "Third-party Libs"
            break
    # 3. 都没有, 则报警告
if not FILE_PATH_FOR_KW618:
        kw618_pkg = "There isn't kw618 pkg."
        print(
            "\n\n[kk警告]:  在本地 site-packages 路径中找不到kw618库, 尝试使用 pip3 install -i https://pypi.org/simple kw618  重新下载kw618库\n"
            "(使用pypi原地址而不是镜像, 才可以下载到最新上传的库包)\n\n"
        )


# 检查是否存在核心文件路径; (没有则抛出'警告'[不能是'报错', 否则体验更差])
error_path = []
for path in [FILE_PATH_FOR_DESKTOP, FILE_PATH_FOR_MYCODE]:
    if not os.path.exists(path):
        error_path.append(path)
if error_path:
    print(
        "[kk警告]:\n不存在以下文件路径:",
        "\n".join(error_path),
        "\n建议:"
        "\n  1. 修改user_name"
        "\n  2. 创建对应目录后, 重试"
        f"\n    (或在'{FILE_PATH_FOR_KW618}'目录下, 直接删除上面源代码)\n"
    )



if __name__ == "__main__":
    print("start!")
    print(FILE_PATH_FOR_DESKTOP)
    # print(FILE_PATH_FOR_KW618)
    print("end!")
