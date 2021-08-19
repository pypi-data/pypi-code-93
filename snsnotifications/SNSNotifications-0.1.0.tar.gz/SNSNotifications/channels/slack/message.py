from typing import Optional, List

__all__ = ['SlackMessage']


class SlackMessage:
    def __init__(self, text: str = None,
                 blocks: Optional[List] = None,
                 has_link=False,
                 mentions: Optional[List[str]] = None,
                 channel=None):
        self.text = text
        self.blocks = blocks
        self.has_link = has_link
        self.mentions = mentions

        self.channel = channel
        if self.has_mentions:
            self.has_link = True
        if self.text is None:
            self.text = ''

    @property
    def has_mentions(self) -> bool:
        return self.mentions is not None and len(self.mentions) > 0

    @property
    def has_blocks(self):
        return self.blocks is not None and len(self.blocks) > 0

    def with_mentions(self, message_data):
        mentions = self._mention_text()
        if isinstance(message_data, str):
            return '{} {}'.format(mentions, message_data)
        if isinstance(message_data, list):
            return [{'type': 'section', 'text': {"type": "mrkdwn", "text": mentions}}] + message_data
        return message_data

    def _mention_text(self):
        mentions = map(lambda x: '@{}'.format(x), self.mentions)
        return ', '.join(mentions)
