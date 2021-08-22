
import textwrap

from .cas_kernel import CasKernel, CasConfig

###########################################################################

class MathematicaConfig(CasConfig):

    prompt_char = "\u2192"
    output_separator = "\u0001"
    prompt_cmd = ""
    cmd = \
        [ "mathematica"
        #, "-noprompt"
        ]
    initial_input = r"""
        SetOptions[ $Output[[1]],
            PageWidth -> Infinity,
            PageHeight -> Infinity
        ];
        yyyJUPYTERyyy[ x0_ ] := Module[ {x=x0},
            x = ExportString[x, "PNG"];
            x = ExportString[x, "Base64"];
            x = StringReplace[x, "\n" -> ""];
            x = "{\"text/plain\": \"-Graphics-\", \"image/png\": \"" <> x <> "\"}";
            x = "\:0001" <> x;
            x
        ];
        While[True,
            Print["\:2192"];
            xxxJUPYTERxxx = InputString[""];
            xxxJUPYTERxxx = Get[xxxJUPYTERxxx];
            If[ xxxJUPYTERxxx =!= Null,
                If[ Head[xxxJUPYTERxxx] === Graphics,
                    xxxJUPYTERxxx = yyyJUPYTERyyy[xxxJUPYTERxxx];
                ]
                If[ Head[xxxJUPYTERxxx] === Graphics3D,
                    xxxJUPYTERxxx = yyyJUPYTERyyy[xxxJUPYTERxxx];
                ]
                Print[xxxJUPYTERxxx]
            ]
        ]
    """.strip() + "\n"
    use_intermediate_file = True

    @classmethod
    def input_cmd(cls, inputnum, code, intermediate_file):
        return intermediate_file.name + "\n"


class MathematicaKernel(CasKernel):

    implementation = 'mathematica'
    implementation_version = '1.0'
    language = 'mathematica'
    language_version = '10'
    language_info = dict(
        mimetype = 'text/x-mathematica',
        file_extension = 'm',
        codemirror_mode = 'mathematica',
        name = 'mathematica'
    )
    banner = "Mathematica"

    cas_config = MathematicaConfig

###########################################################################

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=MathematicaKernel)
