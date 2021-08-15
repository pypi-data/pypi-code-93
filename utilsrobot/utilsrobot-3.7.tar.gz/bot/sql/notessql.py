from sqlalchemy import Column, LargeBinary, Numeric, String, UnicodeText

from bot.sql import BASE, SESSION


class Notes(BASE):
    __tablename__ = "notes"
    chat_id = Column(String(14), primary_key=True)
    keyword = Column(UnicodeText, primary_key=True)
    reply = Column(UnicodeText)
    snip_type = Column(Numeric)
    media_id = Column(UnicodeText)
    media_access_hash = Column(UnicodeText)
    media_file_reference = Column(LargeBinary)

    def __init__(
        self,
        chat_id,
        keyword,
        reply,
        snip_type,
        media_id=None,
        media_access_hash=None,
        media_file_reference=None,
    ):
        self.chat_id = chat_id
        self.keyword = keyword
        self.reply = reply
        self.snip_type = snip_type
        self.media_id = media_id
        self.media_access_hash = media_access_hash
        self.media_file_reference = media_file_reference


Notes.__table__.create(checkfirst=True)


def get_snips(chat_id, keyword):
    try:
        return SESSION.query(Notes).get((str(chat_id), keyword))
    except:
        return None
    finally:
        SESSION.close()


def get_all_snips(chat_id):
    try:
        return SESSION.query(Notes).filter(Notes.chat_id == str(chat_id)).all()
    except:
        return None
    finally:
        SESSION.close()


def add_snip(
    chat_id,
    keyword,
    reply,
    snip_type,
    media_id,
    media_access_hash,
    media_file_reference,
):
    adder = SESSION.query(Notes).get((str(chat_id), keyword))
    if adder:
        adder.reply = reply
        adder.snip_type = snip_type
        adder.media_id = media_id
        adder.media_access_hash = media_access_hash
        adder.media_file_reference = media_file_reference
    else:
        adder = Notes(
            chat_id,
            keyword,
            reply,
            snip_type,
            media_id,
            media_access_hash,
            media_file_reference,
        )
    SESSION.add(adder)
    SESSION.commit()


def remove_snip(chat_id, keyword):
    saved_filter = SESSION.query(Notes).get((str(chat_id), keyword))
    if saved_filter:
        SESSION.delete(saved_filter)
        SESSION.commit()


def remove_all_snip(chat_id):
    saved_filter = SESSION.query(Notes).filter(Notes.chat_id == str(chat_id))
    if saved_filter:
        saved_filter.delete()
        SESSION.commit()
