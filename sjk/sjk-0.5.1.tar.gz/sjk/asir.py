
import textwrap

from .cas_kernel import CasKernel, CasConfig
from .syntax import asir as asir_syntax

###########################################################################

class AsirConfig(CasConfig):

    prompt_char = "\u2192"
    prompt_cmd = "print(\"{}\",2)$".format(prompt_char)
    cmd = \
        [ "asir"
         , "-quiet"
         ]
    initial_input = prompt_cmd + "\n"
    use_intermediate_file = True

    @classmethod
    def syntaxchecker(cls, code):
        return asir_syntax.check(code)

    @classmethod
    def input_cmd(cls, inputnum, code, intermediate_file):
        return "load(\"{}\")$\n{}\n".format(
            intermediate_file.name, cls.prompt_cmd)


class AsirKernel(CasKernel):

    implementation = 'asir'
    implementation_version = '1.0'
    language = 'asir'
    language_version = '20110616'
    language_info = dict(
        mimetype = 'text/x-csrc',
        file_extension = 'asir',
        codemirror_mode = 'clike',
        name = 'asir'
    )
    banner = "This is Risa/Asir"
    help_links = [{
        'text': 'Risa/Asir Home Page', 
        'url': 'http://www.math.kobe-u.ac.jp/Asir/'
    }]

    cas_config = AsirConfig

###########################################################################

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=AsirKernel)
