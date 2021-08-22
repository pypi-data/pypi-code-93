
import atexit
import json
import multiprocessing
import subprocess
import tempfile

from ipykernel.kernelbase import Kernel

###########################################################################

class CasConfig(object):

    prompt_char = "\u2192"
    output_separator = None
    prompt_cmd = "\"{}\"\n".format(prompt_char)
    cmd = [ "bc" , "--quiet" ]
    initial_input = prompt_cmd
    use_intermediate_file = False

    input_num = None
    intermediate_file = None

    @classmethod
    def syntaxchecker(cls, code):
        return ("complete", code.strip(), None)

    @classmethod
    def input_cmd(cls, input_num, code, intermediate_file):
        return "{}\n{}\n".format(code, cls.prompt_cmd)

    @classmethod
    def output_filter(cls, input_num, output, intermediate_file):
        if input_num is not None and intermediate_file is not None:
            cell = "cell {}".format(input_num)
            output = output.replace(intermediate_file.name, cell)
        return output

###########################################################################

class CasKernel(Kernel):

    implementation = 'bc'
    implementation_version = '1.0'
    language = 'bc'
    language_version = '0.1'
    language_info = dict(
        name = 'bc',
        mimetype = 'text/plain',
        file_extesnion = 'txt',
        codemirror_mode = 'plain',
        pygments_lexer = 'bc'
    )
    banner = "bc - An arbitrary precision calculator language"

    cas_config = CasConfig

    def __init__(self, *args, **kwargs):
        super(CasKernel, self).__init__(*args, **kwargs)
        self.repl = REPL(self.cas_config, start=True)

    def _debug_(self, msg):
        return
        msg = "[debug] {}\n".format(repr(msg))
        stream_content = {'name': 'stdout', 'text': msg}
        self.send_response(self.iopub_socket, 'stream', stream_content)

    def do_is_complete(self, code):
        status, clean_code, err = self.cas_config.syntaxchecker(code)
        return { 'status': status }

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
        ex_count = self.execution_count
        self._debug_((ex_count, code, self.repl.status.value))
        self.repl.inqueue.put((ex_count, code))
        self._debug_((ex_count, code, self.repl.status.value))
        while True:
            num, ok, outputs = self.repl.outqueue.get()
            self._debug_((num, ex_count, ok, outputs))
            if num != ex_count:
                continue
            elif not ok:
                self._debug_(("ERROR", outputs))
                msg = {'status': 'error', 'execution_count': ex_count,
                        'ename': 'cas-error', 'evalue': 'cas-error', 
                        'traceback': [outputs]}
                self.send_response(self.iopub_socket, "error", msg)
                return {'status': 'error', 'execution_count': ex_count,
                        'ename': 'cas-error', 'evalue': 'cas-error', 
                        'traceback': [outputs]}
            else:
                #self._debug_(self.process_outputs(outputs))
                for msg_type, msg in self.process_outputs(outputs):
                    self.send_response(self.iopub_socket, msg_type, msg)
                return {'status': 'ok', 'execution_count': ex_count,
                        'payload': [], 'user_expressions': {}}

    def process_outputs(self, outputs):
        proc_outs = []
        last = len(outputs) - 1
        for n, output in enumerate(outputs):
            if output == "":
                continue
            if n == 0:
                if output[-1] == "\n":
                    output = output[:-1]
                data = {'text/plain': str(output)}
            else:
                try:
                    data = json.loads(output)
                except:
                    data = {'text/plain': str(output)}
            mess = dict(data=data, metadata={})
            if n == last:
                mess['execution_count'] = self.execution_count
                proc_outs.append(('execute_result', mess))
            else:
                proc_outs.append(('display_data', mess))
        return proc_outs

 
###########################################################################

class REPL(object):

    def __init__(self, config, start=False):
        self.config = config
        if start:
            self.start()

    def start(self):
        # start child
        self.child = subprocess.Popen(self.config.cmd, 
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT,
                                      encoding="utf8",
                                      errors="replace")
        atexit.register(self.child.kill)

        # start main loop
        self.inqueue = multiprocessing.Queue()
        self.outqueue = multiprocessing.Queue()
        self.status = multiprocessing.Array('c', 100)
        self.proc = multiprocessing.Process(
            target = self.repl,
            args = (self.config,
                    self.child,
                    self.inqueue, 
                    self.outqueue, 
                    self.status))
        self.proc.daemon = True
        self.proc.start()

    @staticmethod
    def repl(config, child, inqueue, outqueue, status):
        # initialize child
        status.value = b"initializing"
        if config.initial_input is not None:
            child.stdin.write(config.initial_input)
            child.stdin.flush()

        # main loop
        while True:
            if not REPL.read_output(config, child, outqueue):
                status.value = b"exited"
                break
            status.value = b"awaiting input"
            REPL.feed_child(config, child, inqueue, outqueue)
            status.value = b"reading output"

    @staticmethod
    def read_output(config, child, outqueue):
        output = [""]
        idx = 0
        while True:
            c = child.stdout.read(1)
            if not c:
                return False
            output[idx] += c
            if output[idx][-1] == config.prompt_char:
                output[idx] = output[idx][:-1]
                break
            elif output[idx][-1] == config.output_separator:
                output[idx] = output[idx][:-1]
                output.append("")
                idx += 1
        if len(output[0])>0 and output[0][0]=="\n":
            output[0] = output[0][1:]
        if config.input_num != None:
            output[0] = config.output_filter(config.input_num, 
                                             output[0],
                                             config.intermediate_file)
            outqueue.put((config.input_num, True, output))
        if config.use_intermediate_file:
            try:
                config.intermediate_file.close()
            except:
                pass
        return True

    @staticmethod
    def feed_child(config, child, inqueue, outqueue):
        while True:
            config.input_num, raw_code = inqueue.get()
            status, code, err = config.syntaxchecker(raw_code)
            if status == "complete":
                break
            else:
                outqueue.put((config.input_num, False, err))
        if config.use_intermediate_file:
            config.intermediate_file = tempfile.NamedTemporaryFile('w+')
            config.intermediate_file.write( code )
            config.intermediate_file.flush()
        child.stdin.write(config.input_cmd(
            config.input_num, code, config.intermediate_file))
        child.stdin.flush()


###########################################################################

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=CasKernel)
