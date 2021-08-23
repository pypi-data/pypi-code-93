import argparse
import logging
import numpy as np
import os
import random
import torch

from tqdm import tqdm


def set_seed(args):
    """Set random seeds for training

    :param args: (argparse.Arguments) arguments passed from the command line.
    """
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if args.n_gpu > 0:
        torch.cuda.manual_seed_all(args.seed)


def parse_input_arguments(additional_arg_parser):
    """Parses arguments passed from the command line.

    :param additional_arg_parser: (def) A custom argument parser created by the user that accepts additional arguments
                                  from the command line, outside the default arguments.
    :return: args: (argparse.Arguments) Command line arugments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--model", type=str, default='', required=True,
                        help='Name of the model to be used. A model dictionary must be provided to DLTrainer '
                             'for looking up the model class.')
    parser.add_argument("--data_dir", type=str, default="data", help="The path to the data folder")
    parser.add_argument("--save_dir", type=str, default="save", help="The path where the model and log will be saved.")
    parser.add_argument("--run_name", type=str, default='baseline', help="Name of your model training run.")
    parser.add_argument('--recompute-features', action='store_true',
                        help="Whether to recompute dataset features if they exist. "
                             "This argument can be used by your Dataset class.")
    parser.add_argument('--load_pretrained', action='store_true', help='Whether to load pretrained model')
    parser.add_argument('--pretrained_checkpoint', type=str, default='',
                        help="Directory of pretrained model. Required if load_pretrained is included.")
    parser.add_argument('--do_train', action='store_true', help="Whether to run training.")
    parser.add_argument('--do_eval', action='store_true', help="Whether to run evaluation.")
    parser.add_argument('--do_test', action='store_true', help="Whether to run test.")
    parser.add_argument('--no_eval_during_training', action='store_true',
                        help='Whether to block evaluation during training.')

    parser.add_argument('--load_optimizer', action='store_true', help='Load saved optimizer from pretrained-checkpoint')
    parser.add_argument('--load_scheduler', action='store_true', help='Load saved scheduler from pretrained-checkpoint')

    parser.add_argument('--train_batch_size', type=int, default=16,
                        help='Batch size for training, and evaluation if eval_batch_size=0')
    parser.add_argument('--eval_batch_size', type=int, default=0, help='Batch size for evaluation')
    parser.add_argument('--num_train_epochs', type=int, default=1)
    parser.add_argument('--gradient_accumulation_steps', type=int, default=1,
                        help='Number of updates steps to accumulate before performing backward & update steps.')
    parser.add_argument('--lr', type=float, default=5e-5, help='Initial learning rate for Adam.')
    parser.add_argument('--weight_decay', type=float, default=0.0, help='Weight decay if we apply some')
    parser.add_argument('--adam_epsilon', type=float, default=1e-8, help='Epsilon for Adam optimizer')
    parser.add_argument('--max_grad_norm', type=float, default=1.0, help='Max gradient norm')
    parser.add_argument('--warmup_steps', type=int, default=0, help='Linear warmup over warmup_steps')

    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--eval_every', type=int, default=5000)
    parser.add_argument('--logging_steps', type=int, default=1000, help='Log every X update steps')

    parser.add_argument('--no_early_stopping', action='store_true',
                        help='Prevent trainer from stopping early when model performance converges on Dev set.')
    parser.add_argument('--early_stopping_steps', type=int, default=10,
                        help='Stop training early if model does not exceed --early_stopping_tol for X steps.')
    parser.add_argument('--early_stopping_tol', type=float, default=1e-5,
                        help='Stop training early if model does not exceed X for --early_stopping_steps steps.')

    parser.add_argument('--no_cuda', action='store_true', help='Avoid using CUDA when available')

    parser.add_argument('--fp16', action='store_true',
                        help='Whether to use 16-bit (mixed) precision (through NVIDIA apex) instead of 32-bit')
    parser.add_argument('--fp16_opt_level', type=str, default='01',
                        help='For fp16: Apex AMP optimization level selected in options. '
                             'See details at https://nvidia.github.io/apex/amp.html')
    parser.add_argument('--local_rank', type=int, default=-1, help="For distributed training: local_rank")
    parser.add_argument('--node_index', type=int, default=-1, help='node index if multi-node_running')
    parser.add_argument('--gpu_per_node', type=int, default=-1, help='num of gpus per node')

    if additional_arg_parser is not None:
        parser = additional_arg_parser(parser)

    args = parser.parse_args()
    return args


def train_setup(additional_arg_parser=None, args=None):
    """Parsing the training arguments from the command line.
    Setups up GPU training if applicable.
    Creates a logger for training/evaluation.

    :param additional_arg_parser: (def) A custom argument parser created by the user that accepts additional arguments
                                  from the command line, outside the default arguments.
    :return: args: (argparse.Arguments) Command line arugments
    :return: logger: (logging.Logger) Logger instance for logging events.

    """
    if args is None:
        args = parse_input_arguments(additional_arg_parser)
    if args.do_eval or args.do_test:
        args.load_pretrained = True
    if args.load_pretrained and args.pretrained_checkpoint == '':
        raise ValueError('Must provide --pretrained_checkpoint when using --load_pretrained')
    if args.eval_batch_size == 0:
        args.eval_batch_size = args.train_batch_size
    if args.load_pretrained:
        args.save_dir = "/".join(args.pretrained_checkpoint.split('/')[:-1])
    else:
        args.save_dir = get_save_dir(args.save_dir, args.run_name)
        if not os.path.exists(args.save_dir):
            os.makedirs(args.save_dir)
    args.start_epoch = 0
    args.start_step = 0

    split_name = 'train' if args.do_train else 'validation' if args.do_eval else 'test'
    logger = get_logger(args.save_dir, 'log_train')

    logger.info("local_rank: %d, node_index: %d, gpu_per_node: %d"%(args.local_rank, args.node_index, args.gpu_per_node))
    # Setup CUDA, GPU & distributed training
    if args.local_rank == -1 or args.no_cuda:
        device = torch.device("cuda" if torch.cuda.is_available() and not args.no_cuda else "cpu")
        args.n_gpu = torch.cuda.device_count()
    else:  # Initializes the distributed backend which will take care of sychronizing nodes/GPUs
        torch.cuda.set_device(args.local_rank)
        device = torch.device("cuda", args.local_rank)
        torch.distributed.init_process_group(backend='nccl')
        args.local_rank += args.node_index * args.gpu_per_node
        args.n_gpu = 1
    args.device = device

    logger.info("Process rank: %s, device: %s, n_gpu: %s, distributed training: %s, 16-bits training: %s, world size: %s",
                   args.local_rank, device, args.n_gpu, bool(args.local_rank != -1), args.fp16,
                   torch.distributed.get_world_size() if args.local_rank != -1 else 1)

    set_seed(args)

    return args, logger


def get_logger(log_dir, name):
    """Get a `logging.Logger` instance that prints to the console
    and an auxiliary file.

    :param log_dir: (str) Directory in which to create the log file.
    :param name: (str)Name to identify the logs.
    :return: logger: (logging.Logger) Logger instance for logging events.
    """
    class StreamHandlerWithTQDM(logging.Handler):
        """Let `logging` print without breaking `tqdm` progress bars.
        See Also:
            > https://stackoverflow.com/questions/38543506
        """
        def emit(self, record):
            try:
                msg = self.format(record)
                tqdm.write(msg)
                self.flush()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.handleError(record)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Log everything (i.e., DEBUG level and above) to a file
    log_path = os.path.join(log_dir, f'{name}.txt')
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)

    # Log everything except DEBUG level (i.e., INFO level and above) to console
    console_handler = StreamHandlerWithTQDM()
    console_handler.setLevel(logging.INFO)

    # Create format for the logs
    file_formatter = logging.Formatter('[%(asctime)s] %(message)s',
                                       datefmt='%m.%d.%y %H:%M:%S')
    file_handler.setFormatter(file_formatter)
    console_formatter = logging.Formatter('[%(asctime)s] %(message)s',
                                          datefmt='%m.%d.%y %H:%M:%S')
    console_handler.setFormatter(console_formatter)

    # add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_save_dir(base_dir, name, id_max=100):
    """Creates a directory name for a given model name. Adds a numeric suffix to distinguish models
    under the same name.

    :param base_dir: (str) base save directory
    :param name: (str) name of the model
    :param id_max: (int) maximum number of models under the same name
    :return:
    """
    for uid in range(1, id_max):
        save_dir = os.path.join(base_dir, f'{name}-{uid:02d}')
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            return save_dir

    raise RuntimeError('Too many save directories created with the same name. \
                       Delete old save directories or use another name.')