import argparse
import magic

def configure_parser_onnx2trt(sub_parsers):
    p = sub_parsers.add_parser("onnx2trt", help="convert onnx to tensorrt")
    p.add_argument("--onnx", default='', help="onnx path")
    p.add_argument('--batch', default=1, type=int, help="max batch，default=1")
    p.add_argument("--fp16", default=0, type=int, help="default=0")

def execute_onnx2trt(args):
    from magic.tensorrt.onnx2trt import onnx_convert
    assert args.onnx.endswith(".onnx"), "need .onnx"
    trt_path = args.onnx[:-4] + "trt"
    onnx_convert(args.onnx, trt_path, args.batch, args.fp16, verbose=1)

def generate_args():
    p = argparse.ArgumentParser(usage="magic command ..., magic -h for more details",)
    p.add_argument("-V", "--version",
                   action='version',
                   version='magic %s' % magic.__version__,
                   help="show version and exit")
    sub_parsers = p.add_subparsers(
        metavar='command',
        dest='cmd',
    )
    sub_parsers.required = True
    configure_parser_onnx2trt(sub_parsers)
    args = p.parse_args()
    return args

def main():
    args = generate_args()
    if args.cmd == "onnx2trt":
        execute_onnx2trt(args)

if __name__ == '__main__':
    main()
