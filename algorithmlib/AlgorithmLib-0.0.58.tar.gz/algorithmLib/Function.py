
import  os

def project_root_path(project_name=None):

    """

    获取当前项目根路径

    :param project_name:

    :return: 根路径

    """

    PROJECT_NAME = 'audiotestalgorithm' if project_name is None else project_name

    project_path = os.path.abspath(os.path.dirname(__file__))

    root_path = project_path[:project_path.find("{}\\".format(PROJECT_NAME)) + len("{}\\".format(PROJECT_NAME))]

    #print('当前项目名称：{}\r\n当前项目根路径：{}'.format(PROJECT_NAME, root_path))

    return root_path

if __name__ == '__main__':
    print(project_root_path())