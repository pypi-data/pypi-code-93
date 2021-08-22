from colorama import init, Fore, Back, Style

init(autoreset=True)


class Colored(object):
    '''
    from termcolor import colored
    https://blog.csdn.net/qianghaohao/article/details/52117082
    RED = '\033[31m'       # 红色
    GREEN = '\033[32m'     # 绿色
    YELLOW = '\033[33m'    # 黄色
    BLUE = '\033[34m'      # 蓝色
    FUCHSIA = '\033[35m'   # 紫红色
    CYAN = '\033[36m'      # 青蓝色
    WHITE = '\033[37m'     # 白色
    RESET = '\033[0m'      # 终端默认颜色

    colored('[%(name)s]', 'magenta', attrs=['bold'])  紫色
    colored('[%(asctime)s]', 'blue' 蓝色
    colored('%(levelname)s:', 'green') 绿色
    colored('%(message)s', 'white') 灰色

    # -----------------colorama模块的一些常量---------------------------
    # Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
    # Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
    # Style: DIM, NORMAL, BRIGHT, RESET_ALL
    #

    print(Colored.red('I am red!'))
    print(Colored.green('I am gree!'))
    print(Colored.yellow('I am yellow!'))
    print(Colored.blue('I am blue!'))
    print(Colored.magenta('I am magenta!'))
    print(Colored.cyan('I am cyan!'))
    print(Colored.white('I am white!'))
    print(Colored.white_green('I am white green!'))
    '''

    #  前景色:红色  背景色:默认
    @staticmethod
    def red(s):
        return Fore.RED + s + Fore.RESET

    #  前景色:绿色  背景色:默认
    @staticmethod
    def green(s):
        return Fore.GREEN + s + Fore.RESET

    #  前景色:黄色  背景色:默认
    @staticmethod
    def yellow(s):
        return Fore.YELLOW + s + Fore.RESET

    #  前景色:蓝色  背景色:默认
    @staticmethod
    def blue(s):
        return Fore.BLUE + s + Fore.RESET

    #  前景色:洋红色  背景色:默认
    @staticmethod
    def magenta(s):
        return Fore.MAGENTA + s + Fore.RESET

    #  前景色:青色  背景色:默认
    @staticmethod
    def cyan(s):
        return Fore.CYAN + s + Fore.RESET

    #  前景色:白色  背景色:默认
    @staticmethod
    def white(s):
        return Fore.WHITE + s + Fore.RESET

    #  前景色:黑色  背景色:默认
    @staticmethod
    def black(s):
        return Fore.BLACK

    #  前景色:白色  背景色:绿色
    @staticmethod
    def white_green(s):
        return Fore.WHITE + Back.GREEN + s + Fore.RESET + Back.RESET