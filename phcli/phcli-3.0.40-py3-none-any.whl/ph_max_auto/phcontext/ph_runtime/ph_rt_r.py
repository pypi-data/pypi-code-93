import os
import subprocess

from phcli.ph_errs.ph_err import *
from .ph_rt_base import PhRTBase
from phcli.define_value import CLI_CLIENT_VERSION
from phcli.ph_max_auto import define_value as dv
from phcli.ph_max_auto.ph_config.phconfig.phconfig import PhYAMLConfig


class PhRTR(PhRTBase):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def c9_create_phmain(self, path=None):
        if not path:
            path = self.job_path

        config = PhYAMLConfig(path)
        config.load_yaml()
        f_lines = self.phs3.open_object_by_lines(dv.TEMPLATE_BUCKET, dv.CLI_VERSION + dv.TEMPLATE_PHMAIN_FILE_R)
        with open(path + "/phmain.R", "w") as file:
            options_args = []
            for arg in config.spec.containers.args:
                options_args.append('c("key"="{key}", "desc"="参数{key}")'.format(key=arg.key))
            for output in config.spec.containers.outputs:
                options_args.append('c("key"="{key}", "desc"="参数{key}")'.format(key=output.key))

            for line in f_lines:
                line = line + "\n"
                if "$options_args" in line:
                    line = line.replace("$options_args", ',\n\t'.join(options_args))
                file.write(line)

    def jupyter_to_c9(self, dag_full_path, **kwargs):
        im = kwargs['im']
        om = kwargs['om']
        ipynb_dict = kwargs['ipynb_dict']

        self.phs3.download(dv.TEMPLATE_BUCKET, dv.CLI_VERSION + dv.TEMPLATE_PHJOB_FILE_R, dag_full_path + "/phjob.R")
        config = PhYAMLConfig(dag_full_path)
        config.load_yaml()

        with open(dag_full_path + "/phjob.R", "a") as file:
            file.write("execute <- function(")
            file.write(", ".join(im.keys()))
            file.write(", ")
            file.write(", ".join(om.keys()))
            file.write("){\n")

            # copy 逻辑代码
            for cell in ipynb_dict['cells'][2:]:
                for row in cell['source']:
                    file.write('    '+row)
                file.write('\r\n')
                file.write('\r\n')

            file.write('}')

    def jupyter_create(self, **kwargs):
        path = self.job_path + ".ipynb"
        dir_path = "/".join(path.split('/')[:-1])
        subprocess.call(['mkdir', '-p', dir_path])

        f_lines = self.phs3.open_object_by_lines(dv.TEMPLATE_BUCKET, dv.CLI_VERSION + dv.TEMPLATE_JUPYTER_R_FILE)
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
        if self.ide == 'jupyter':
            self.jupyter_create(**kwargs)
        else:
            raise exception_function_not_implement

    def submit_run(self, **kwargs):
        submit_conf = {}
        submit_file = {
            "files": self.submit_prefix + "phjob.R",
        }
        submit_main = self.submit_prefix + "phmain.R"

        super().submit_run(submit_conf=submit_conf,
                           submit_file=submit_file,
                           submit_main=submit_main)

    def script_run(self, **kwargs):
        self.phs3.download(dv.TEMPLATE_BUCKET, dv.CLI_VERSION + self.s3_job_path + "/phmain.R", 'phmain.R')
        self.phs3.download(dv.TEMPLATE_BUCKET, dv.CLI_VERSION + self.s3_job_path + "/phjob.R", 'phjob.R')
        entrypoint = ['Rscript', './phmain.R']
        super().script_run(entrypoint=entrypoint)
