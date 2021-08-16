import dataclasses
import json

@dataclasses.dataclass
class WxSeqItem(object):
    seq: int = None
    msgid: str = None
    publickey_ver: int = None
    encrypt_random_key: str = None
    encrypt_chat_msg: str = None

    def __repr__(self):
        return f'<Seq seq={self.seq} msg={self.msgid} ver={self.publickey_ver}>'

@dataclasses.dataclass
class WxRawData(object):
    # input
    errcode: int = None
    errmsg: str = None
    chatdata: list = None

    def __post_init__(self):
        if self.chatdata:
            for i, msg in enumerate(self.chatdata):
                if isinstance(msg, dict):
                    self.chatdata[i] = WxSeqItem(**msg)

    @property
    def max_seq(self):
        return self.chatdata[-1].seq if len(self.chatdata) > 0 else None

    @property
    def min_seq(self):
        return self.chatdata[0].seq if len(self.chatdata) > 0 else None

    def __repr__(self):
        return f'<Data errcode={self.errcode} errmsg={self.errmsg} chatdata(len={len(self.chatdata)} min_seq={self.min_seq} max_seq={self.max_seq})>'

@dataclasses.dataclass
class WxMsgItem(object):
    msgid: str = None
    action: str = None # send
    from_id: str = None
    to_ids: list = None
    roomid: str = None # only for room
    msgtime: int = None # timestamp: 1585113286223
    msgtype: str = None # text / ...
    text: dict = None # text_raw
    picture: dict = None # picture
    info: dict = None # markdown
    text_content: str = None # text_content
    md_content: str = None # text_content

    # analyze
    scenario_id: int = None # 识别出来的场景ID
    keywords: list = None   # 场景相关的关键词
    mood_level: int = None  # 情绪指标

    def __init__(self, decrypted: dict):
        self.msgid = decrypted.get('msgid')
        self.action = decrypted.get('action')
        self.from_id = decrypted.get('from')
        self.to_ids = decrypted.get('tolist')
        self.roomid = decrypted.get('roomid')
        self.msgtime = decrypted.get('msgtime')
        self.msgtype = decrypted.get('msgtype')
        self.text = decrypted.get('text')
        self.info = decrypted.get('info')
        if self.text:
            self.text_content = self.text.get('content')
        if self.info:
            self.md_content = self.info.get('content')
    
    def __repr__(self):
        return f'<Msg type={self.msgtype} from={self.from_id} to={self.to_ids} msg={self.text_content}>'