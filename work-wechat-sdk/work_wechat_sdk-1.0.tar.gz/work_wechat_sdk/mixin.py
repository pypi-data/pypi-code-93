class SendMessageMixin:
    """
    doc_links: https://open.work.weixin.qq.com/api/doc/90000/90135/90196
    """

    def get_word(self, msgtype, *args, **kwargs):
        fun = getattr(self, "get_%s_word" % msgtype)
        return fun(*args, **kwargs)

    def get_text_word(self, content):
        """
        Generate a text word format
        :param content: The text content
        :return: word
        """
        word = {"content": content}
        return word

    def get_image_word(self, media_id):
        """
        Generate a image word format
        :param media_id: The image media_id
        :return: word
        """
        word = {"media_id": media_id}
        return word

    def get_voice_word(self, media_id):
        """
        Generate a voice word format
        :param media_id: The voice media_id
        :return: word
        """
        word = {"media_id": media_id}
        return word

    def get_video_word(self, media_id, title=None, description=None):
        """
        Generate a video word format
        :param media_id: The video media_id
        :param title: The title of the video word
        :param description: The description of the video word
        :return: content
        """
        word = {"media_id": media_id}
        if title is not None:
            word.update({"title": title})
        if description is not None:
            word.update({"description": description})
        return word

    def get_file_word(self, media_id):
        """
        Generate a file word format
        :param media_id: The file media_id
        :return: word
        """
        word = {"media_id": media_id}
        return word

    def get_textcard_word(self, title, description, url, btntxt=None):
        """
        Generate a textcard word format
        :param title: The title of the textcard word
        :param description: The description of the textcard word
        :param url: Click on the link after the jump
        :param btntxt: Button text
        :return: word
        """
        word = {
            "title": title,
            "description": description,
            "url": url
        }

        if btntxt is not None:
            word.update({"btntxt": btntxt})
        return word

    def get_news_word(self, title, url, description=None, picurl=None, word=None):
        """
        Generate a news content format
        :param title: The title of the news word
        :param url: Click on the link after the jump
        :param description: The title of the description word
        :param picurl: Image links to graphic content
        :param word: Assembled messages; contains articles or is None
        :return: word
        """
        word = word or {}
        articles = word.get("articles", [])

        if not isinstance(articles, list):
            raise TypeError("articles type is list")

        articles_dict = {
            "title": title,
            "url": url,
        }

        if description is not None:
            articles_dict.update({"description": description})
        if picurl is not None:
            articles_dict.update({"picurl": picurl})

        word.update({"articles": articles})
        articles.append(articles_dict)
        return word

    def get_mpnews_word(self, title, thumb_media_id, content,
                        author=None, content_source_url=None,
                        digest=None, word=None):
        """
        Generate a mpnews word format
        :param title: The title of the mpnews word
        :param thumb_media_id: Media_id of the content thumbnail
        :param content: The content of a mpnews content
        :param author: The author of a mpnews content
        :param content_source_url: Text word click the page link after "read the original"
        :param digest: Description of a mpnews word
        :param word: Assembled word; contains articles or is None
        :return: word
        """
        word = word or {}
        articles = word.get("articles", [])

        if not isinstance(articles, list):
            raise TypeError("articles type is list")

        articles_dict = {
            "title": title,
            "thumb_media_id": thumb_media_id,
            "content": content
        }

        if author is not None:
            articles_dict.update({"author": author})
        if content_source_url is not None:
            articles_dict.update({"content_source_url": content_source_url})
        if digest is not None:
            articles_dict.update({"digest": digest})

        word.update({"articles": articles})
        articles.append(articles_dict)
        return word

    def get_markdown_word(self, content):
        """
        Generate a markdown word format; Support for markDown syntax
        :param content: Markdown word
        :return: word
        """
        word = {"content": content}
        return word

    def get_miniprogram_notice_word(self, appid, title,
                                    page=None, description=None,
                                    emphasis_first_item=True, key_value=None):
        """
        Generate a miniprogram_notice word format
        :param appid: Small program appid
        :param title: The title of a miniprogram_notice word
        :param page: Click on the applet page behind the word card
        :param description: The description of a miniprogram_notice word
        :param emphasis_first_item: Whether to enlarge the first content_item
        :param key_value: Displays the key-value pairs of information
        :return: word
        """
        key_value = key_value or {}
        content_item = []

        if not isinstance(key_value, dict):
            raise TypeError("key_value type is dict")
        for k, v in key_value.items():
            content_item.append({"key": k, "value": v})

        word = {
            "appid": appid,
            'title': title,
            "emphasis_first_item": emphasis_first_item
        }

        if page is not None:
            word.update({"page": page})
        if description is not None:
            word.update({"description": description})

        return word

    def get_message(self, msgtype, *args, **kwargs):
        fun = getattr(self, "get_%s_message" % msgtype)
        return fun(*args, **kwargs)

    def get_text_message(self, word, **message):
        """
        :param word: The text content
        :param message: optional and default
            default:
                safe: 0 or 1 ;default 0
                enable_id_trans: 0 or 1 ;default 0
                enable_duplicate_check: 0 or 1 ;default 0
                duplicate_check_interval: max->14400 ;default 1800
        :return: kwargs
        """
        message.update({
            "msgtype": "text",
            "text": word,
        })
        return message

    def get_image_message(self, word, **message):
        """
        :param word: The image media_id
        :param message: optional and default
            default:
                safe: 0 or 1 ;default 0
                enable_duplicate_check: 0 or 1 ;default 0
                duplicate_check_interval: max->14400 ;default 1800
        :return: kwargs
        """
        message.update({
            "msgtype": "image",
            "image": word,
        })
        return message

    def get_voice_message(self, word, **message):
        """
        :param word: The voice media_id
        :param message: optional and default
            default:
                enable_duplicate_check: 0 or 1 ;default 0
                duplicate_check_interval: max->14400 ;default 1800
        :return: kwargs
        """
        message.update({
            "msgtype": "voice",
            "voice": word,
        })
        return message

    def get_video_message(self, word, **message):
        """
        :param word: The video media_id, title and description
        :param message: optional and default
            default:
                safe: 0 or 1 ;default 0
                enable_duplicate_check: 0 or 1 ;default 0
                duplicate_check_interval: max->14400 ;default 1800
        :return: kwargs
        """
        message.update({
            "msgtype": "video",
            "video": word,
        })
        return message

    def get_file_message(self, word, **message):
        """
        :param word: The file media_id
        :param message: optional and default
            default:
                safe: 0 or 1 ;default 0
                enable_duplicate_check: 0 or 1 ;default 0
                duplicate_check_interval: max->14400 ;default 1800
        :return: kwargs
        """
        message.update({
            "msgtype": "file",
            "file": word,
        })
        return message

    def get_textcard_message(self, word, **message):
        """
        :param word: The textcard title, description, url and btntxt
        :param message: optional and default
            default:
                enable_id_trans: 0 or 1 ;default 0
                enable_duplicate_check: 0 or 1 ;default 0
                duplicate_check_interval: max->14400 ;default 1800
        :return: kwargs
        """
        message.update({
            "msgtype": "textcard",
            "textcard": word
        })
        return message

    def get_news_message(self, word, **message):
        """
        :param word: The news articles
        :param message: optional and default
            default:
                enable_id_trans: 0 or 1 ;default 0
                enable_duplicate_check: 0 or 1 ;default 0
                duplicate_check_interval: max->14400 ;default 1800
        :return: kwargs
        """
        message.update({
            "msgtype": "news",
            "news": word,
        })
        return message

    def get_mpnews_message(self, word, **message):
        """
        :param word: The mpnews articles
        :param message: optional and default
            default:
                safe: 0 or 1 ;default 0
                enable_id_trans: 0 or 1 ;default 0
                enable_duplicate_check: 0 or 1 ;default 0
                duplicate_check_interval: max->14400 ;default 1800
        :return: kwargs
        """
        message.update({
            "msgtype": "mpnews",
            "mpnews": word,
        })
        return message

    def get_markdown_message(self, word, **message):
        """
        :param word: The markdown articles
        :param message: optional and default
            default:
                enable_duplicate_check: 0 or 1 ;default 0
                duplicate_check_interval: max->14400 ;default 1800
        :return: kwargs
        """
        message.update({
            "msgtype": "markdown",
            "markdown": word,
        })
        return message

    def get_miniprogram_notice_message(self, word, **message):
        """
        :param word: The miniprogram_notice articles
        :param message: optional and default
            default:
                enable_duplicate_check: 0 or 1 ;default 0
                duplicate_check_interval: max->14400 ;default 1800
        :return: kwargs
        """
        message.update({
            "msgtype": "miniprogram_notice",
            "miniprogram_notice": word,
        })
        return message
