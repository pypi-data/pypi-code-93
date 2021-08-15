# -*- coding: utf-8 -*-
import pickle
import torch,random
from torch import nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, random_split,TensorDataset
import pytorch_lightning as pl
from pytorch_lightning import Trainer, seed_everything
from pytorch_lightning.callbacks import ModelCheckpoint,LearningRateMonitor
# 自动停止
# https://pytorch-lightning.readthedocs.io/en/1.2.1/common/early_stopping.html
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
import torch.optim as optim
from tqdm.auto import tqdm
import torchmetrics

from tkitbilstm import BiLSTMAttention as Bilstm
from torchcrf import CRF



class autoModel(pl.LightningModule):
    """
    继承自bertlm模型
    https://colab.research.google.com/drive/1-OEwiD9ouGjWrSFEWhgEnWiNvwwxlqd7#scrollTo=no6DwOqaE9Jw
    做预测
    
    https://github.com/lucidrains/performer-pytorch
    """
# class COCO(nn.Module):
    def __init__(
        self,learning_rate=3e-4,T_max=5,hidden_size=256,vocab_size=21128,ignore_index=0,out_num_classes=12,en_num_layers=2,de_num_layers=2,optimizer_name="AdamW",dropout=0.2,
        batch_size=2,trainfile="./data/train.pkt",valfile="./data/val.pkt",testfile="./data/test.pkt", **kwargs):
        super().__init__()
        self.save_hyperparameters()
        # SRC_SEQ_LEN=128
        # TGT_SEQ_LEN=128
        # DE_SEQ_LEN=128
        # EN_SEQ_LEN=128
        # self.hparams.hidden_size
        print(self.hparams)
        # self.model=Bilstm(
        #                   vocab_size=self.hparams.vocab_size,
        #                   dim=self.hparams.hidden_size,
        #                   n_hidden=self.hparams.hidden_size,out_num_classes=self.hparams.out_num_classes,embedding_enabled=True,
        #                   attention=False)
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        self.model=nn.LSTM(hidden_size,hidden_size,dropout=dropout,
                           num_layers=6,
                           batch_first=False,
                           bidirectional=True
        )
        
        
        self.c=nn.Sequential(
            nn.Dropout(self.hparams.dropout),
            nn.Tanh(),
            nn.Linear(self.hparams.hidden_size*2,self.hparams.out_num_classes),
            nn.Dropout(self.hparams.dropout),
            nn.Tanh(),
            
            
        )
        self.d=nn.Dropout(self.hparams.dropout)
        self.decoder = CRF(self.hparams.out_num_classes,batch_first=False)
        
        # self.accuracy = torchmetrics.Accuracy(ignore_index=self.hparams.ignore_index)
        self.accuracy = torchmetrics.Accuracy()
#         self.encoder_hidden = self.enc.initHidden()
        # print(self)

    def forward(self, x,y,x_attention_mask,y_attention_mask, decode=False):
        x=self.embedding(x)
        y=y.permute(1,0)
        x=x.permute(1,0,2)
        x=self.d(x)
        x,_=self.model(x)
        
        x=self.c(x)
        
        # print(x.size())
        
        
        loss = self.decoder (x, y,reduction="token_mean")
        loss=loss*-1
        if decode:
            pred=self.decoder.decode(x)
            return pred, loss
            pass
        else:
            return loss


    def training_step(self, batch, batch_idx):
        # training_step defined the train loop.
        # It is independent of forward
        x,x_attention_mask,y,y_attention_mask = batch
        loss  = self(x,y,x_attention_mask,y_attention_mask)
        self.log('train_loss',loss)
        return  loss
    def validation_step(self, batch, batch_idx):
        # training_step defined the train loop.
        # It is independent of forward
        x,x_attention_mask,y,y_attention_mask = batch
        pred,loss  = self(x,y,x_attention_mask,y_attention_mask,decode=True)
#         print("outputs",outputs.size())
        acc=self.accuracy(torch.Tensor(pred).to(self.device).view(-1), y.reshape(-1))
        metrics = {"val_acc": acc, "val_loss": loss}
        # print(pred)
        # metrics = { "val_loss": loss}
        self.log_dict(metrics)
        return metrics

    def test_step(self, batch, batch_idx):
        # training_step defined the train loop.
        # It is independent of forward
        x,x_attention_mask,y,y_attention_mask = batch
        pred,loss  = self(x,y,x_attention_mask,y_attention_mask,decode=True)
#         print("outputs",outputs.size())
        acc=self.accuracy(torch.Tensor(pred).to(self.device).view(-1), y.reshape(-1))
        metrics = {"test_acc": acc, "test_loss": loss}
        self.log_dict(metrics)
        return metrics
        
    def train_dataloader(self):
        train=torch.load(self.hparams.trainfile)
        return DataLoader(train, batch_size=int(self.hparams.batch_size),num_workers=2,pin_memory=True, shuffle=True)
    def val_dataloader(self):
        val=torch.load(self.hparams.valfile)
        return DataLoader(val, batch_size=int(self.hparams.batch_size),num_workers=2,pin_memory=True)
    def test_dataloader(self):
        val=torch.load(self.hparams.testfile)
        return DataLoader(val, batch_size=int(self.hparams.batch_size),num_workers=2,pin_memory=True)

    
    def configure_optimizers(self):
            """优化器 # 类似于余弦，但其周期是变化的，初始周期为T_0,而后周期会✖️T_mult。每个周期学习率由大变小； https://www.notion.so/62e72678923f4e8aa04b73dc3eefaf71"""
    #         optimizer = torch.optim.AdamW(self.parameters(), lr=(self.learning_rate))

            #只优化部分
#             optimizer = torch.optim.AdamW(self.parameters(), lr=(self.hparams.learning_rate))
            optimizer = getattr(optim, self.hparams.optimizer_name)(self.parameters(), lr=self.hparams.learning_rate)
            #         使用自适应调整模型
            T_mult=2
            scheduler =torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer,T_0=self.hparams.T_max,T_mult=T_mult,eta_min=0 ,verbose=False)
    #         https://github.com/PyTorchLightning/pytorch-lightning/blob/6dc1078822c33fa4710618dc2f03945123edecec/pytorch_lightning/core/lightning.py#L1119

            lr_scheduler={
    #            'optimizer': optimizer,
               'scheduler': scheduler,
#                 'reduce_on_plateau': True, # For ReduceLROnPlateau scheduler
                'interval': 'epoch', #epoch/step
                'frequency': 1,
                'name':"lr_scheduler",
                'monitor': 'train_loss', #监听数据变化
                'strict': True,
            }
    #         return [optimizer], [lr_scheduler]
            return {"optimizer": optimizer, "lr_scheduler": lr_scheduler}