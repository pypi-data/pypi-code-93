import os
import re
import json
import subprocess

from phcli.ph_errs.ph_err import *
from .ph_rt_base import PhRTBase
from phcli.define_value import CLI_CLIENT_VERSION
from phcli.ph_max_auto import define_value as dv
from phcli.ph_max_auto.ph_config.phconfig.phconfig import PhYAMLConfig


class PhRTPython3(PhRTBase):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def c9_create_init(self, path=None):
        if not path:
            path = self.job_path + "/__init__.py"
        subprocess.call(["touch", path])

    def c9_create_phmain(self, path=None):
        if not path:
            path = self.job_path

        config = PhYAMLConfig(path)
        config.load_yaml()
        f_lines = self.phs3.open_object_by_lines(dv.TEMPLATE_BUCKET, dv.CLI_VERSION + dv.TEMPLATE_PHMAIN_FILE_PY)
        with open(path + "/phmain.py", "w") as file:
            s = []
            for arg in config.spec.containers.args:
                s.append(arg.key)

            for line in f_lines:
                line = line + "\n"
                if line == "$alfred_debug_execute\n":
                    file.write("@click.command()\n")
                    for must in dv.PRESET_MUST_ARGS.split(","):
                        file.write("@click.option('--{}')\n".format(must.strip()))
                    for arg in config.spec.containers.args:
                        file.write("@click.option('--" + arg.key + "')\n")
                    for output in config.spec.containers.outputs:
                        file.write("@click.option('--" + output.key + "')\n")
                    file.write("""def debug_execute(**kwargs):
    try:
        args = {"name": "$alfred_name"}
        outputs = [$alfred_outputs]

        args.update(kwargs)
        result = exec_before(**args)

        args.update(result if isinstance(result, dict) else {})
        result = execute(**args)

        args.update(result if isinstance(result, dict) else {})
        result = exec_after(outputs=outputs, **args)

        return result
    except Exception as e:
        logger = phs3logger(kwargs["job_id"])
        logger.error(traceback.format_exc())
        print(traceback.format_exc())
        raise e
        
@click.command()
@click.option('--owner')
@click.option('--dag_name')
@click.option('--run_id')
@click.option('--job_full_name')
@click.option('--job_id')
@click.option('--job_args_name')
def online_debug_execute(**kwargs):
    try:
        args = {"name": "$alfred_name"}
        outputs = [$alfred_outputs]
        
        args.update(kwargs)
        result = exec_before(**args)

        args.update(result if isinstance(result, dict) else {})
        result = execute(**args)

        args.update(result if isinstance(result, dict) else {})
        result = exec_after(outputs=outputs, **args)

        return result
    except Exception as e:
        logger = phs3logger(kwargs["job_id"])
        logger.error(traceback.format_exc())
        print(traceback.format_exc())
        raise e
"""
                               .replace('$alfred_outputs', ', '.join(['"'+output.key+'"' for output in config.spec.containers.outputs])) \
                               .replace('$alfred_name', config.metadata.name)
                               )
                else:
                    file.write(line)

    def c9_create(self, **kwargs):
        # 1. /__init__.py file
        self.c9_create_init()

        # 2. /phjob.py file
        self.phs3.download(dv.TEMPLATE_BUCKET, dv.CLI_VERSION + dv.TEMPLATE_PHJOB_FILE_PY, self.job_path + "/phjob.py")
        with open(self.job_path + "/phjob.py", "a") as file:
            file.write("""def execute(**kwargs):\n""")

            file.write("""    logger = phs3logger(kwargs["job_id"], LOG_DEBUG_LEVEL)\n""")

            if self.command == 'submit':
                file.write('    spark = kwargs["spark"]()')

            file.write("""
    result_path_prefix = kwargs["result_path_prefix"]
    depends_path = kwargs["depends_path"]
    
    logger.info(kwargs["a"])
    logger.info(kwargs["b"])
    logger.info(kwargs["c"])
    logger.info(kwargs["d"])
    return {}
""")

        # 3. /phmain.py file
        self.c9_create_phmain()

    def jupyter_create(self, **kwargs):
        path = self.job_path + ".ipynb"
        dir_path = "/".join(path.split('/')[:-1])
        subprocess.call(['mkdir', '-p', dir_path])

        f_lines = self.phs3.open_object_by_lines(dv.TEMPLATE_BUCKET, dv.CLI_VERSION + dv.TEMPLATE_JUPYTER_PYTHON_FILE)
        with open(path, "w") as file:
            for line in f_lines:
                line = line.replace('$name', self.name) \
                            .replace('$runtime', self.runtime) \
                            .replace('$command', self.command) \
                            .replace('$timeout', str(self.timeout)) \
                            .replace('$user', os.getenv('USER', 'unknown')) \
                            .replace('$group', self.group) \
                            .replace('$ide', self.ide) \
                            .replace('$access_key', os.getenv('AWS_ACCESS_KEY_ID', "NULL")) \
                            .replace('$secret_key', os.getenv('AWS_SECRET_ACCESS_KEY', "NULL"))
                file.write(line)

    def create(self, **kwargs):
        if self.ide == 'c9':
            self.c9_create(**kwargs)
        elif self.ide == 'jupyter':
            self.jupyter_create(**kwargs)
        else:
            raise exception_function_not_implement

    def c9_to_jupyter(self, source_path, target_path, exts):
        # 创建json文件
        subprocess.run(["touch", target_path])

        with open(target_path, "w") as file:
            indentation = 4
            first_cell_index = 0
            second_cell_index = 1
            redundantCell_begin_index = 2
            redundantCell_end_index = 5

            # 从S3中获取jupyter模板
            template_str = self.phs3.open_object(dv.TEMPLATE_BUCKET, dv.CLI_VERSION + dv.TEMPLATE_JUPYTER_PYTHON_FILE)
            # 字符串转换成字典
            data = json.loads(template_str)
            # phconf.yaml中获取数据
            config = PhYAMLConfig(source_path)
            config.load_yaml()
            job_name = config.metadata.name
            job_runtime = config.spec.containers.runtime
            job_command = config.spec.containers.command
            job_timeout = str(config.spec.containers.timeout)

            ##### 处理第一个输入框 #####
            first_cell_source = data['cells'][first_cell_index]['source']
            # 写入基本信息
            for index, old_str in enumerate(first_cell_source):
                first_cell_source[index] = old_str.replace('$name', job_name) \
                    .replace('$runtime', job_runtime) \
                    .replace('$command', job_command) \
                    .replace('$timeout', job_timeout)

            # 写入input_args数据
            input_index = first_cell_source.index("a = 123\n")
            first_cell_input_before_row = first_cell_source[:input_index]
            first_cell_input_after_row = first_cell_source[input_index+2:]
            new_input_row = []
            for arg in config.spec.containers.args:
                arg_key = arg.key
                arg_value = arg.value
                if str.isdigit(str(arg_value)):
                    new_input_row.insert(input_index, arg_key + " = " + str(arg_value) + "\n")
                else:
                    new_input_row.insert(input_index, arg_key + " = '" + str(arg_value) + "'\n")
            first_cell_source = first_cell_input_before_row + new_input_row + first_cell_input_after_row

            # 写入output_args数据
            output_index = first_cell_source.index("c = 'abc'\n")
            first_cell_output_before_row = first_cell_source[:output_index]
            first_cell_output_after_row = first_cell_source[output_index+2:]
            new_output_row = []
            for output in config.spec.containers.outputs:
                output_key = output.key
                output_value = output.value
                if str.isdigit(str(output_value)):
                    new_output_row.insert(output_index, output_key + " = " + str(output_value) + "\n")
                else:
                    new_output_row.insert(output_index, output_key + " = '" + str(output_value) + "'\n")
            first_cell_source = first_cell_output_before_row + new_output_row + first_cell_output_after_row
            data['cells'][first_cell_index]['source'] = first_cell_source
            ##### 处理第一个输入框 #####


            ##### 处理第二个输入框 #####
            second_cell_source = data['cells'][second_cell_index]['source']
            for index, old_str in enumerate(second_cell_source):
                second_cell_source[index] = old_str.replace('$name', job_name) \
                                                   .replace('$runtime', job_runtime) \
                                                   .replace('$command', job_command) \
                                                   .replace('$timeout', job_timeout) \
                                                   .replace('$user', os.getenv('USER', 'unknown')) \
                                                   .replace('$group', exts['group']) \
                                                   .replace('$ide', exts['ide']) \
                                                   .replace('$access_key', os.getenv('AWS_ACCESS_KEY_ID', "NULL")) \
                                                   .replace('$secret_key', os.getenv('AWS_SECRET_ACCESS_KEY', "NULL"))
            data['cells'][second_cell_index]['source'] = second_cell_source
            ##### 处理第二个输入框 #####


            ##### 删除data中多余的cell #####
            del data['cells'][redundantCell_begin_index:redundantCell_end_index]
            ##### 删除data中多余的cell #####


            ##### phjob 的内容 copy 到 .ipynb 下的其余 source 中 #####
            with open(source_path + "/phjob.py", "r") as phjob_flie:
                line = phjob_flie.readline()
                while line:
                    while line.startswith('def') or line.startswith('@') or line.startswith('    # %%'):
                        demo = {
                            "cell_type": "code",
                            "execution_count": None,
                            "metadata": {},
                            "outputs": [],
                            "source": []
                        }
                        if line.startswith('@'):
                            demo['source'].append(line)
                            line = phjob_flie.readline()
                        demo['source'].append(line)
                        line = phjob_flie.readline()
                        while not line.startswith('def') and not line.startswith('@') and not line.startswith('    # %%') and not line == "":
                            demo['source'].append(line)
                            line = phjob_flie.readline()
                        data['cells'].append(demo)
                    line = phjob_flie.readline()

                execute_indexes = []
                for cell in data['cells']:
                    for source in cell['source']:
                        if source.startswith('def execute') or source.startswith('    # %%'):
                            execute_index = data['cells'].index(cell)
                            execute_indexes.append(execute_index)

                for execute_index in execute_indexes:
                    empty_source = []
                    for execute_source_str in data['cells'][execute_index]['source']:
                        if len(execute_source_str) - len(execute_source_str.lstrip()) >= indentation:
                            if execute_source_str.lstrip().startswith('logger = '):
                                continue
                            elif execute_source_str.lstrip().startswith('spark = '):
                                continue
                            if execute_source_str.lstrip().startswith('result_path_prefix = '):
                                continue
                            if execute_source_str.lstrip().startswith('depends_path = '):
                                continue
                            if execute_source_str.lstrip().startswith('### input args ###'):
                                continue
                            if execute_source_str.lstrip().startswith('### output args ###'):
                                continue

                            # logger 替换为 print
                            execute_source_str = re.sub(r'\t*logger\.\w*\(([\'|\"]?.*?[\'|\"]?)\)$', r"print(\1)", execute_source_str)
                            # 对简单 kwargs 删除，如 a = kwargs['a']
                            kv_check = re.sub(r'\s*(.*)\s*=\s*kwargs\[[\'|\"](\w*?)[\'|\"]\]', r"\1,\2", execute_source_str)
                            kv_check = kv_check.split(",")
                            if len(kv_check) == 2 and kv_check[0].strip() == kv_check[1].strip():
                                continue

                            # 对复杂 kwargs 替换，如 a = kwargs['b'] + c ==> a = b + c
                            execute_source_str = re.sub(r'^(.*)kwargs\[[\'|\"](\w*)[\'|\"]\](.*)', r"\1\2\3", execute_source_str)
                            empty_source.append(execute_source_str[indentation:])
                        elif execute_source_str.lstrip().startswith('#'):
                            empty_source.append(execute_source_str)
                    data['cells'][execute_index]['source'] = empty_source
            ##### phjob 的内容 copy 到 .ipynb 下的其余 source 中 #####

            # 把 data 从字典转换成 json 格式, indent=1 进行换行，ensure_ascii防止汉字转成Unicode码
            json_str = json.dumps(data, indent=1, ensure_ascii=False)
            file.write(json_str)

    def jupyter_to_c9(self, source_path, target_path, exts):
        def get_ipynb_map_by_key(source, key):
            """
            获取 ipynb 中定义的配置
            :param source: ipynb 中的文本行
            :param key: 需要获得的字典，可以是 config、input args、output args
            :return:
            """
            range = []
            for i, row in enumerate(source):
                if "== {} ==".format(key) in row:
                    range.append(i)
            source = source[range[0]+1: range[1]]

            result = {}
            for row in source:
                if row and '=' in row:
                    r = row.split('=', 1)
                    result[r[0].strip()] = eval(r[-1].strip())
            return result

        # 1. 检查是否存在
        if not os.path.exists(source_path):
            raise exception_file_not_exist

        # 2. 创建目标文件夹
        subprocess.call(["mkdir", "-p", target_path])

        # 3. 读取源文件的配置和输入输出参数
        with open(source_path, 'r') as rf:
            ipynb_dict = json.load(rf)
            source = ipynb_dict['cells'][0]['source']
            cm = get_ipynb_map_by_key(source, 'config')
            im = get_ipynb_map_by_key(source, 'input args')
            om = get_ipynb_map_by_key(source, 'output args')

        # 4. 将读取的配置和参数写到 phconf.yaml 中
        input_str = ["- key: {}\n        value: '{}'".format(k, v) for k, v in im.items()]
        input_str = '\n      '.join(input_str)
        output_str = ["- key: {}\n        value: '{}'".format(k, v) for k, v in om.items()]
        output_str = '\n      '.join(output_str)
        self.create_phconf_file(path=target_path, input_str=input_str, output_str=output_str,
                                name=cm['job_name'], runtime=cm['job_runtime'],
                                command=cm['job_command'], timeout=cm['job_timeout'])

        # python 需要 __init__.py 文件
        if cm['job_runtime'] == 'python3':
            # 5. 创建 /__init__.py file
            self.c9_create_init(target_path + "/__init__.py")

        # 6. 生成 /phmain.* file
        self.c9_create_phmain(target_path)

        # 8. phconf 转为 args.properties
        self.yaml2args(target_path)

        self.phs3.download(dv.TEMPLATE_BUCKET, dv.CLI_VERSION + dv.TEMPLATE_PHJOB_FILE_PY, target_path + "/phjob.py")
        with open(target_path + "/phjob.py", "a") as file:
            file.write("""def execute(**kwargs):
    logger = phs3logger(kwargs["job_id"], LOG_DEBUG_LEVEL)
    spark = kwargs['spark']()
    result_path_prefix = kwargs["result_path_prefix"]
    depends_path = kwargs["depends_path"]
    
    ### input args ###
""")
            # 取入参
            for input in im:
                file.write("    {key} = kwargs['{key}']\n".format(key=input))
            file.write("    ### input args ###\n")
            file.write("    \n")

            # 取出参
            file.write("    ### output args ###\n")
            for output in om:
                file.write("    {key} = kwargs['{key}']\n".format(key=output))
            file.write("    ### output args ###\n")
            file.write("\n")

            # copy 逻辑代码
            for row in ipynb_dict['cells'][2]['source']:
                row = re.sub(r'(^\s*)print(\(.*)', r"\1logger.debug\2", row)
                row = re.sub(r'(^.*)kwargs\[[\\"|\'](.*)[\\"|\']\](.*)', r"\1\2\3", row)
                file.write('    ' + row)
            for cell in ipynb_dict['cells'][3:]:
                if cell['source'][0].startswith('# %%'):
                    for row in cell['source']:
                        row = re.sub(r'(^\s*)print(\(.*)', r"\1logger.debug\2", row)
                        row = re.sub(r'(^.*)kwargs\[[\\"|\'](.*)[\\"|\']\](.*)', r"\1\2\3", row)
                        file.write('    ' + row)
                else:
                    for row in cell['source']:
                        row = re.sub(r'(^\s*)print(\(.*)', r"\1logger.debug\2", row)
                        row = re.sub(r'(^.*)kwargs\[[\\"|\'](.*)[\\"|\']\](.*)', r"\1\2\3", row)
                        file.write(row)
                file.write('\n')

    def submit_run(self, **kwargs):
        submit_conf = {
            "jars": "s3a://ph-platform/2020-11-11/jobs/python/phcli/common/aws-java-sdk-bundle-1.11.828.jar,"
                    "s3a://ph-platform/2020-11-11/jobs/python/phcli/common/hadoop-aws-3.2.1.jar",
        }
        submit_file = {
            "py-files": "s3a://" + dv.TEMPLATE_BUCKET + "/" + dv.CLI_VERSION + dv.DAGS_S3_PHJOBS_PATH + "common/phcli-{}-py3.8.egg,".format(CLI_CLIENT_VERSION) +
                        self.submit_prefix + "phjob.py",
        }
        submit_main = self.submit_prefix + "phmain.py"

        super().submit_run(submit_conf=submit_conf,
                           submit_file=submit_file,
                           submit_main=submit_main)

    def script_run(self, **kwargs):
        self.phs3.download(dv.TEMPLATE_BUCKET, dv.CLI_VERSION + self.s3_job_path + "/phmain.py", 'phmain.py')
        self.phs3.download(dv.TEMPLATE_BUCKET, dv.CLI_VERSION + self.s3_job_path + "/phjob.py", 'phjob.py')
        entrypoint = ['python3', './phmain.py']
        super().script_run(entrypoint=entrypoint)


