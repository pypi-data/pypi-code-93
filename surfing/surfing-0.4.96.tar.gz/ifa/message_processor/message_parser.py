from .nlp.qabot import QaBot

class WechatMessageParser(object):
    def __init__(self):
        super().__init__()
        self.bot = QaBot()

    def parse(self, msg_from, msg_to, msg_content):
        rule = self.bot.text_parser(msg_content)
        return rule