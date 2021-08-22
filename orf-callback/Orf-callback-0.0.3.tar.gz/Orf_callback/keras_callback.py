from keras.callbacks import Callback
from Orf_sendMsg.wxSend import WeChat
import datetime
import matplotlib.pyplot as plt
import os

class WXPush(Callback):

    def __init__(self, log_dir, key, digest, title, epochs=None, every_epoch=1):
        self.wechat = WeChat(key)
        self.curr_time = datetime.datetime.now().timestamp()
        self.log_dir = log_dir
        self.epoch_finish_list = []
        self.cost_time = []
        self.nums = 1
        self.losses = []
        self.val_loss = []
        self.img_urls = []
        self.epochs = epochs
        self.every_epoch = every_epoch
        self.digest = digest
        self.title = title

    def on_train_begin(self, logs=None):
        self.epoch_finish_list.append(datetime.datetime.now().timestamp())

    def on_epoch_end(self, epoch, logs=None):
        current_epoch = self.nums
        train_loss = logs.get("loss")
        val_loss = logs.get("val_loss")
        self.losses.append(train_loss)
        self.val_loss.append(val_loss)
        self.epoch_finish_list.append(datetime.datetime.now().timestamp())
        self.cost_time.append(self.epoch_finish_list[-1] - self.epoch_finish_list[-2])  # 计算epoch耗时
        mean_time = sum(self.cost_time[-3:]) / len(self.cost_time[-3:])  # 计算平均时间
        img_path = self.loss_plot()  # 生成图片
        if self.epochs:
            eval_time = mean_time * (self.epochs - self.nums) / 60
        else:
            eval_time = None
        m, s = divmod(self.cost_time[-1], 60)
        h, m = divmod(m, 60)
        if self.nums % self.every_epoch == 0:
            try:
                imgurl = self.wechat.get_media_url(img_path)  # 获取图片url
                self.img_urls.append(imgurl)
                digest = f"""
    ╒═══╤═════╤════╤═════╕
         轮  次   |         {str(self.nums).zfill(3)}        |     损   失    |        {str(val_loss)[:6]}
    ├───┼─────┼────┼─────┤
         耗  时   |        %02d 时             %02d 分             %02d 秒
    ├───┼────────────────┤
         日  期   |                {datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S")}
    ╘═══╧════════════════╛
     """ % (h, m, s)
                content = "<style>table{{border-collapse:collapse;font-family:Futura,Arial,sans-serif;margin:auto;}}caption{{font" \
                          "-size:larger;margin:1em auto;}}th,td{{padding:.65em;text-align:center;}}th{{background:#111;color:#fff" \
                          ";}}tbodytr:nth-child(odd){{background:#ccc;}}th:first-child{{border-radius:9px 0 0 0;}}th:last-child{{" \
                          "border-radius:0 9px 0 0;}} tr:last-child td:first-child {{border-radius:0 0 0 9px;}} tr:last-child td:" \
                          "last-child{{border-radius:0 0 9px 0;}} .imgcenter{{text-align:center;}}</style><div class=\"imgcenter\"" \
                          "><img src=\"{0}\"></div><table><thead><tr><th>名称<th>数值<th>名称<th>数值</thead><tbody><tr><td>训练损失<t" \
                          "d>{1}<td>验证损失<td>{2}<tr><td>消耗时间<td>{3}<td>平均耗时<td>{4}<tr><td>训练轮次<td>{5}<td>预计剩余<td>{6}</" \
                          "tbody></table>".format(imgurl, str(train_loss)[:6], str(val_loss)[:6],
                                                  round(self.cost_time[-1], 2), round(mean_time, 2), current_epoch,
                                                  round(eval_time, 2))
                self.wechat.send_mpnews(thumb_img="msg.png", title=self.title + f"第{self.nums}次训练结束", digest=self.digest, content=content)
            except Exception as e:
                print(e)
        self.nums += 1

    def on_train_end(self, logs=None):
        img_style = "<style> .imgcenter{{text-align:center;}}</style>"
        img_div = ["<div class=\"imgcenter\"><img src=\"{}\"></div>".format(i) for i in self.img_urls]
        content = img_style + "".join(img_div)
        digest = "训练结束"
        try:
            self.wechat.send_mpnews(thumb_img="msg.png", title=self.title, digest=digest, content=content)
        except Exception as e:
            print(e)

    def loss_plot(self):
        iters = range(len(self.losses))
        plt.figure()
        plt.plot(iters, self.losses, 'red', linewidth=2, label='train loss')
        plt.plot(iters, self.val_loss, 'green', linewidth=2, label='val loss')
        plt.grid(True)
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('A Loss Curve')
        plt.legend(loc="upper right")
        img_path = os.path.join(self.log_dir, "epoch_nums_" + str(self.nums) + ".png")
        plt.savefig(img_path)
        plt.cla()
        plt.close("all")
        return img_path
