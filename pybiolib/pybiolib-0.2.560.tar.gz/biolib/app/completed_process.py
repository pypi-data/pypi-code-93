import re
import nest_asyncio  # type: ignore # necessary import fix required for async to work in notebooks

from biolib import cli_utils

nest_asyncio.apply()


class CompletedProcess:
    def __init__(self, stdout, stderr, exitcode):
        self.stdout = stdout
        self.stderr = stderr
        self.exitcode = exitcode

    def __str__(self):
        return cli_utils.get_pretty_print_module_output_string(self.stdout, self.stderr, self.exitcode)

    def ipython_markdown(self):
        import IPython.display  # type:ignore # pylint: disable=import-error, import-outside-toplevel
        markdown_str = self.stdout.decode('utf-8')
        # prepend ./biolib_results/ to all paths
        # ie [SeqLogo](./SeqLogo2.png) test ![SeqLogo](./SeqLogo.png)
        # ![SeqLogo](SeqLogo.png)  ![SeqLogo](/SeqLogo.png)
        # is transformed to ![SeqLogo](./biolib_results/SeqLogo2.png) test ![SeqLogo](./biolib_results/SeqLogo.png)
        # ![SeqLogo](./biolib_results/SeqLogo.png)  ![SeqLogo](./biolib_results/SeqLogo.png)
        markdown_str_modified = re.sub(
            r'\!\[([^\]]*)\]\((\.\/|\/|)([^\)]*)\)',
            r'![\1](./biolib_results/\3)',
            markdown_str,
        )
        IPython.display.display(IPython.display.Markdown(markdown_str_modified))
