
import json
import re
import textwrap

from .cas_kernel import CasKernel, CasConfig

###########################################################################

class Macaulay2Config(CasConfig):

    prompt_char = "\u2192"
    prompt_cmd = "<< utf8 {} << flush;".format(ord(prompt_char))
    cmd = \
        [ "M2"
         , "--silent"
         , "--no-prompts"
         , "--no-debug"
         , "-e", "clearEcho stdio"
         , "-e", "Thing#{Standard,Print} = x -> ( << x << endl )"
         # "-e", "Thing#{Standard,AfterPrint} = x -> ( << endl << class x << endl )"
         , "-e", prompt_cmd
         ]
    use_intermediate_file = False
    initial_input = None

    @classmethod
    def input_cmd(cls, input_num, code, intermediate_file):
        if len(code)>0 and code[-1] == ";":
            return "value {};\n{}\n".format(json.dumps(code), cls.prompt_cmd)
        else:
            return "value {}\n{}\n".format(json.dumps(code), cls.prompt_cmd)

    @classmethod
    def output_filter(cls, input_num, output, intermediate_file):
        out_lines = output.splitlines()
        if len(out_lines) > 2 and out_lines[-2] == "":
            out_lines[-1] = re.sub("^\s*o\d*\s*:\s*","",out_lines[-1])
        while out_lines and out_lines[0] == "" or out_lines[0].isspace():
            out_lines.pop(0)
        output = "\n".join(out_lines)
        return output


class Macaulay2Kernel(CasKernel):

    implementation = 'Macaulay2'
    implementation_version = '1.0'
    language = 'Macaulay2'
    language_version = '1.6'
    language_info = dict(
        mimetype = 'text/plain',
        file_extension = 'm2',
        codemirror_mode = 'plain',
        name = 'macaulay2'
    )
    banner = textwrap.dedent(
    """\
    ┌────────────────────────────────────────────────────────────────────┐
    │ Macaulay2                                                          │
    │ A software system for research in algebraic geometry               │
    │ by: Daniel Grayson, Michael Stillman                               │
    └────────────────────────────────────────────────────────────────────┘\
    """)
    help_links = [{
        'text': 'Macaulay2 Documentation', 
        'url': 'http://www.math.uiuc.edu/Macaulay2/doc/Macaulay2-1.8.1/share/doc/Macaulay2/Macaulay2Doc/html/'
    }]

    cas_config = Macaulay2Config

###########################################################################

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=Macaulay2Kernel)
