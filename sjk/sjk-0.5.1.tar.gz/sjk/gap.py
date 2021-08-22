
import textwrap

from .cas_kernel import CasKernel, CasConfig
from .syntax import gap as gap_syntax

###########################################################################

class GapConfig(CasConfig):

    prompt_char = "\u2192"
    prompt_cmd = "Print(\"{}\");".format(prompt_char)
    cmd = \
        [ "gap"
         , "-q"
         , "-n"
         , "-T"
         ]
    initial_input = prompt_cmd + "\n"
    use_intermediate_file = False # terrible, I know

    @classmethod
    def syntaxchecker(cls, code):
        return gap_syntax.check(code)

    @classmethod
    def input_cmd(cls, input_num, cmd_list, intermediate_file):
        if not cmd_list:
            return cls.prompt_cmd + "\n"
        ret = ""
        for cmd, cmd_end in cmd_list:
            ret += cmd
        return "{}{}\n".format(ret, cls.prompt_cmd) # fingers crossed!!
        # return "load(\"{}\")$\n{}\n".format(
        #     intermediate_file.name, cls.prompt_cmd)


class GapKernel(CasKernel):

    implementation = 'gap'
    implementation_version = '1.0'
    language = 'gap'
    language_version = '1'
    language_info = dict(
        mimetype = 'text/plain',
        file_extension = 'gap',
        codemirror_mode = 'plain',
        name = 'gap'
    )
    banner = "GAP"
    help_links = [{
        'text': 'GAP Documentation', 
        'url': 'http://www.gap-system.org/Doc/doc.html'
    }]

    cas_config = GapConfig

###########################################################################

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=GapKernel)
