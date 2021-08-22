
import textwrap

from .cas_kernel import CasKernel, CasConfig
from .syntax import singular as singular_syntax

###########################################################################

class SingularConfig(CasConfig):

    prompt_char = "\u2192"
    prompt_cmd = "print(\"{}\");".format(prompt_char)
    cmd = \
        [ "Singular"
        , "--quiet"
        , "--no-tty"
        , "-c", "option(noprompt);" + prompt_cmd
        ]
    initial_input = None
    use_intermediate_file = True

    @classmethod
    def syntaxchecker(cls, code):
        return singular_syntax.check(code)

    @classmethod
    def input_cmd(cls, inputnum, code, intermediate_file):
        return "< \"{}\";\n{}\n".format(
            intermediate_file.name, cls.prompt_cmd)


class SingularKernel(CasKernel):

    implementation = 'singular'
    implementation_version = '1.0'
    language = 'singular'
    language_version = '4.0.1' # not really, no
    language_info = dict(
        name = 'singular',
        mimetype = 'text/x-singular',
        file_extension = 'sing',
        codemirror_mode = 'clike',
        pygments_lexer = 'singular'
    )
    banner = textwrap.dedent(
    """\
    ┌────────────────────────────────────────────────────────────────────┐
    │                      SINGULAR                                 /    │
    │  A Computer Algebra System for Polynomial Computations       /     │
    │                                                            0<      │
    │  by: W. Decker, G.-M. Greuel, G. Pfister, H. Schoenemann     \\     │
    │ FB Mathematik der Universitaet, D-67653 Kaiserslautern        \\    │
    └────────────────────────────────────────────────────────────────────┘\
    """)
    help_links = [{
        'text': 'Singular Manual', 
        'url': 'http://www.singular.uni-kl.de/Manual/latest/index.htm'
    }]

    cas_config = SingularConfig

###########################################################################

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=SingularKernel)
