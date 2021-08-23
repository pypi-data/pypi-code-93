from . import trainer_utils

import dill
import os
import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader, SequentialSampler, RandomSampler
from torch.utils.data.distributed import DistributedSampler
from transformers import get_linear_schedule_with_warmup
from tensorboardX import SummaryWriter
from tqdm import tqdm


class DLTrainer:
    """
    Base trainer class for training deep learning models.
    """
    def __init__(self, MODELS, metric_fn=None, additional_arg_parser=None, args=None):
        """Constructor

        :param MODELS:
        :param additional_arg_parser:
        :param metric_fn
        """
        self.args, self.logger = trainer_utils.train_setup(additional_arg_parser, args)
        self.metric_fn = metric_fn

        # Barrier to make sure only the first process in distributed training downloads model & vocab
        if self.args.local_rank not in [-1, 0]:
            torch.distributed.barrier()

        self.model_checkpoint = os.path.join(self.args.save_dir, 'checkpoint') if self.args.pretrained_checkpoint == '' \
            else self.args.pretrained_checkpoint

        classes = MODELS[self.args.model]
        if len(classes) == 4:
            config_class, model_class, dataset_class, tokenizer_class = classes
            # tokenizer must be pretrained and placed in model_checkpoint folder
            tokenizer = tokenizer_class.from_pretrained(self.model_checkpoint)
        elif len(classes) == 3:
            config_class, model_class, dataset_class = classes
        else:
            raise ValueError(f"MODELS class list must contain either 4 elements for NLP or 3 elements otherwise. "
                             "Received {len(classes)} elements.")
        if self.args.load_pretrained:
            if callable(getattr(model_class, "from_pretrained", None)):
                self.config = config_class.from_pretrained(self.model_checkpoint)
                self.model = model_class.from_pretrained(self.model_checkpoint)
            else:
                self.model, self.config = self.load_model(model_class)
        else:
            self.config = config_class(self.args)
            self.model = model_class(self.config)

        num_params = sum([p.numel() for p in self.model.parameters()])
        self.logger.info(f"Model has a total of {num_params} trainable parameters.")

        # End of distributed training barrier
        if self.args.local_rank == 0:
            torch.distributed.barrier()

        self.logger.info("Training/evaluation parameters %s", self.args)

        # Training
        if self.args.do_train:
            if not os.path.exists(self.args.save_dir):
                os.makedirs(self.args.save_dir)

            train_dataset = dataset_class(self.args, 'train')
            collate_fn = train_dataset.collate_fn if hasattr(train_dataset, 'collate_fn') else None
            train_sampler = RandomSampler(train_dataset)
            train_dataloader = DataLoader(train_dataset, sampler=train_sampler, batch_size=self.args.train_batch_size,
                                          collate_fn=collate_fn)
            val_dataloader = None
            if not self.args.no_eval_during_training:
                pass
                val_dataset = dataset_class(self.args, 'dev')
                val_sampler = SequentialSampler(val_dataset) if self.args.local_rank == -1 else DistributedSampler(
                    val_dataset)
                val_dataloader = DataLoader(val_dataset, sampler=val_sampler, batch_size=self.args.eval_batch_size,
                                            collate_fn=collate_fn)
            self.train(train_dataloader, val_dataloader)

        if self.args.do_eval or self.args.do_test:
            eval_dataset = dataset_class(self.args, 'dev' if self.args.do_eval else 'test')
            eval_sampler = SequentialSampler(eval_dataset) if self.args.local_rank == -1 else DistributedSampler(
                eval_dataset)
            eval_dataloader = DataLoader(eval_dataset, sampler=eval_sampler, batch_size=self.args.eval_batch_size,
                                         collate_fn=collate_fn)
            results = self.evaluate(eval_dataloader)
            print(results)

    def _default_optimizer(self, t_total):
        no_decay = ['bias', 'LayerNorm.weight']
        optimizer_grouped_parameters = [
            {'params': [p for n, p in self.model.named_parameters() if not any(nd in n for nd in no_decay)],
             'weight_decay': self.args.weight_decay},
            {'params': [p for n, p in self.model.named_parameters() if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
        ]
        optimizer = AdamW(optimizer_grouped_parameters, lr=self.args.lr, eps=self.args.adam_epsilon)
        scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=self.args.warmup_steps,
                                                    num_training_steps=t_total)
        return optimizer, scheduler

    def create_optimizer(self, t_total):
        """Create optimizer for training.

        Should be overwritten for special cases.

        :param model: (Any) model to train
        :param t_total: (int) total number of training steps
        :return:
        """
        self.optimizer, self.scheduler = self._default_optimizer(t_total)

    def _default_process_batch(self, batch):
        inputs = [x.to(self.args.device) for x in batch[0] if x is not None]
        labels = batch[1].to(self.args.device)
        return inputs, labels

    def process_batch(self, batch):
        """Process data batch for model input
        Sends each tensor to the model device.

        Should be overwritten for special cases.

        :param batch: (list) The batch from the dataloader
        :return: batch: (list) The batch to be input into the model, with each tensor on the model device
        """
        return self._default_process_batch(batch)

    def train_step(self, inputs, labels):
        """Perform a training step.

        Can be overwritten for special cases.

        :param inputs: (list) Batch inputs
        :return: loss: (Any) training loss
        """
        inputs += [labels]
        outputs = self.model(*inputs)
        loss = outputs[0]

        # mean() to average on multi-gpu parallel training
        if self.args.n_gpu > 1:
            loss = loss.mean()
        if self.args.gradient_accumulation_steps > 1:
            loss = loss / self.args.gradient_accumulation_steps

        self.optimizer.zero_grad()
        if self.args.fp16:
            with amp.scale_loss(loss, self.optimizer) as scaled_loss:
                scaled_loss.backward()
            torch.nn.utils.clip_grad_norm_(amp.master_params(self.optimizer), self.args.max_grad_norm)
        else:
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.args.max_grad_norm)

        return loss

    def train(self, train_dataloader, val_dataloader):
        self.model.to(self.args.device)
        if self.args.local_rank in [-1, 0]:
            tbx_path = self.args.save_dir + '/tensorboard'
            if not os.path.exists(tbx_path):
                os.makedirs(tbx_path)
            tbx = SummaryWriter(tbx_path)

        if self.args.local_rank not in [-1, 0]:
            torch.distributed.barrier()

        # Prepare optimizer and schedule (linear warmup and decay)
        total_examples = len(train_dataloader.dataset) * (
            torch.distributed.get_world_size() if self.args.local_rank != -1 else 1)
        batch_size = self.args.train_batch_size * self.args.gradient_accumulation_steps * (
            torch.distributed.get_world_size() if self.args.local_rank != -1 else 1)
        t_total = total_examples // batch_size * self.args.num_train_epochs

        self.create_optimizer(t_total)
        optimizer_checkpoint = os.path.join(self.model_checkpoint, 'optimizer.pt')
        scheduler_checkpoint = os.path.join(self.model_checkpoint, 'scheduler.pt')

        if self.args.load_optimizer and os.path.exists(optimizer_checkpoint):
            self.logger.info(f"Loading optimizer from {optimizer_checkpoint}")
            self.optimizer.load_state_dict(torch.load(optimizer_checkpoint, map_location="cpu"))
        if self.args.load_scheduler and os.path.exists(scheduler_checkpoint):
            self.logger.info(f"Loading scheduler from {scheduler_checkpoint}")
            self.scheduler.load_state_dict(torch.load(scheduler_checkpoint, map_location="cpu"))

        if self.args.local_rank == 0:
            torch.distributed.barrier()

        if self.args.fp16:
            try:
                from apex import amp
            except ImportError:
                raise ImportError("Please install apex from https://www.github.com/nvidia/apex to use fp16 training.")
            self.model, self.optimizer = amp.initialize(self.model, self.optimizer, opt_level=self.args.fp16_opt_level)

        # multi-gpu training (should be after apex fp16 initialization)
        if self.args.n_gpu > 1:
            self.model = torch.nn.DataParallel(self.model)

        # Distributed training (should be after apex fp16 initialization)
        if self.args.local_rank != -1:
            model = torch.nn.parallel.DistributedDataParallel(self.model,
                                                              device_ids=[self.args.local_rank % self.args.gpu_per_node],
                                                              output_device=self.args.local_rank % self.args.gpu_per_node,
                                                              find_unused_parameters=True)

        # Train!
        self.logger.info("***** Running training *****")
        self.logger.info("  Num examples = %d", total_examples)
        self.logger.info("  Num epoch = %d", t_total * batch_size // total_examples)
        self.logger.info("  Instantaneous batch size per GPU = %d", self.args.train_batch_size)
        self.logger.info("  Total train batch size (w. parallel, distributed & accumulation) = %d", batch_size)
        self.logger.info("  Gradient Accumulation steps = %d", self.args.gradient_accumulation_steps)
        self.logger.info("  Total optimization steps = %d", t_total)

        global_step = self.args.start_step
        tr_loss, logging_loss, avg_loss, tr_nb = 0.0, 0.0, 0.0, global_step
        eval_steps_no_increase = 0
        best_score = -float('inf')
        for epoch in range(self.args.start_epoch, self.args.num_train_epochs):
            for step, batch in enumerate(train_dataloader):
                # batch should be tuple of length 2 (inputs, gold_labels)
                self.model.train()
                self.optimizer.zero_grad()
                inputs, labels = self.process_batch(batch)
                loss = self.train_step(inputs, labels)
                tr_loss += loss.item()

                if (step +1) % self.args.gradient_accumulation_steps == 0:
                    self.optimizer.step()
                    self.scheduler.step()
                    global_step += 1

                    avg_loss = round((tr_loss - logging_loss) / (global_step - tr_nb), 4)
                    if global_step % self.args.logging_steps == 0:
                        self.logger.info(" steps: %s loss; %s", global_step, avg_loss)
                    if self.args.local_rank in [-1, 0] and self.args.logging_steps > 0 \
                        and global_step % self.args.logging_steps == 0:
                        # log metrics
                        tbx.add_scalar('lr', self.scheduler.get_last_lr()[0], global_step)
                        tbx.add_scalar('loss', (tr_loss - logging_loss) / self.args.logging_steps)
                        logging_loss = tr_loss
                        tr_nb = global_step
                    if self.args.local_rank in [-1, 0] and self.args.eval_every > 0 \
                            and global_step % self.args.eval_every == 0:
                        # save model checkpoint
                        if not self.args.no_eval_during_training:
                            results = self.evaluate(val_dataloader)
                            for key, value in results.items():
                                tbx.add_scalar('eval_{}'.format(key), value, global_step)
                                self.logger.info(" %s = %s, best_score = %s", key, round(value, 4), round(best_score, 4))

                            score = results[list(results.keys())[0]]

                            if score < best_score + self.args.early_stopping_tol:
                                eval_steps_no_increase += 1
                            else:
                                eval_steps_no_increase = 0

                            if score > best_score:
                                best_score = score
                                self.save_model()
                                self.logger.info("Saving model checkpoint to %s", self.model_checkpoint)

                            if eval_steps_no_increase > self.args.early_stopping_steps:
                                self.logger.info(f"Stopping at step {global_step} in epoch {epoch}. "
                                                 f"Validation did not improve by {self.args.early_stopping_tol} for "
                                                 f"more than {self.args.early_stopping_steps} steps.")
                                return
                        else:
                            self.save_model()
                            self.logger.info("Saving model checkpoint to %s", self.model_checkpoint)

    def eval_step(self, inputs, labels=None):
        """Perform a eval step.

        Can be overwritten for special cases.

        :param inputs: (list) Batch inputs
        :param labels: (torch.tensor) Gold labels for task, if provided
        :return: loss: (Any) training loss
        """
        if labels is not None:
            inputs += [labels]
        outputs = self.model(*inputs)
        return outputs

    def evaluate(self, eval_dataloader):
        # Eval!
        split = 'validation' if self.args.do_train or self.args.do_eval else 'test'
        self.logger.info("***** Running evaluation {} *****".format(split))
        self.logger.info("  Num examples = %d", len(eval_dataloader.dataset))
        self.logger.info("  Batch size = %d", self.args.eval_batch_size)
        eval_loss = 0.0
        nb_eval_steps = 0
        self.model.eval()

        all_outputs = []
        all_labels = []
        for batch in tqdm(eval_dataloader):
            # batch should be tuple of length 2 (inputs, gold_labels)
            inputs, labels = self.process_batch(batch)
            with torch.no_grad():
                outputs = self.eval_step(inputs, labels)
            loss = outputs[0]
            if loss is not None:
                eval_loss += loss.mean().item()
            nb_eval_steps += 1

            if labels is not None:
                all_outputs.append(outputs[1].cpu())
                all_labels.append(labels.cpu())

        all_outputs = torch.cat(all_outputs, dim=0)
        all_labels = torch.cat(all_labels, dim=0)

        eval_loss = eval_loss / nb_eval_steps
        if self.metric_fn is None:
            results = {'eval_loss': -eval_loss}
        else:
            results = self.metric_fn(all_outputs, all_labels)
        return results

    def load_model(self, model_class):
        config = dill.load(open(f'{self.model_checkpoint}/config.pt', 'rb'))
        model = model_class(config)
        model.load_state_dict(torch.load(f'{self.model_checkpoint}/pytorch_model.bin', map_location=torch.device('cpu')))
        return model, config

    def save_model(self):
        """Save a checkpoint in the output directory"""
        if os.path.isfile(self.model_checkpoint):
            return
        os.makedirs(self.model_checkpoint, exist_ok=True)

        # Only save the model itself if we are using distributed training
        model_to_save = self.model.module if hasattr(self.model, "module") else self.model

        state_dict = model_to_save.state_dict()
        torch.save(state_dict, f'{self.model_checkpoint}/pytorch_model.bin')

        # save config
        dill.dump(self.config, open(f'{self.model_checkpoint}/config.pt', 'wb'))
        # save optimizer
        torch.save(self.optimizer.state_dict(), f'{self.model_checkpoint}/optimizer.pt')
        # save scheduler
        torch.save(self.scheduler.state_dict(), f'{self.model_checkpoint}/scheduler.pt')

