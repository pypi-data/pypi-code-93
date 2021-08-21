def Buttons(*_buttons):
    async def sendAll(ctx=None, content=None, id=None):
        i = 0

        r = []
        for button in _buttons:
            i += 1
            if i > 5:
                raise SyntaxError.msg == "You can only request 5 buttons at a time."
            self = button
            headers = {"Authorization": f"Bot {Token}"}
            headers["Content-Type"] = "application/json"
            channel_id: str
            if ctx is None and id is None:
                raise TypeError.msg == "Error: Code 10. Check out https://github.com/namuKR/d4-buttons/wiki#code-10 for more info."
            elif ctx is not None and id is not None:
                channel_id = ctx.channel.id
            elif ctx is None and id is not None:
                channel_id = id
            elif ctx is not None and id is None:
                channel_id = ctx.channel.id

            if content is None:
                print(
                    "Warning: Code 10. Check out https://github.com/namuKR/d4-buttons/wiki#code-10-1 for more info.")
                content = '​'  # zero width space inside it!

            if self["url"] is not None and self["customId"] is None and self["emoji"] is None:  # Link Button

                r[i] = {
                    "type": 2,
                    "label": self["text"],
                    "style": 5,
                    "url": self["url"],
                    "disabled": self["disabled"] if self["disabled"] else False
                }

            elif self["url"] is not None and self["customId"] is None and self["emoji"] is not None:

                r[i] = {
                    "type": 2,
                    "label": self["text"],
                    "style": 5,
                    "url": self["url"],
                    "disabled": self["disabled"] if self["disabled"] else False,
                    "emoji": self["emoji"]
                }

            elif self["emoji"] is not None:
                if self["customId"] is None:
                    raise TypeError.msg == "Buttons that are not Link style must have customId values."
                elif self["style"] is None or self["text"] is None:
                    raise TypeError.msg == "Button.style or Button.text missing"

                r[i] = {
                    "type": 2,
                    "label": self["text"],
                    "style": self["style"],
                    "emoji": self["emoji"],
                    "custom_id": self["customId"],
                    "disabled": self["disabled"] if self["disabled"] else False
                }

            elif self["url"] is not None and self["customId"] is not None:
                raise TypeError.msg == "Link Buttons should not have customId values."
            elif self["url"] is None and self["customId"] is None:
                raise TypeError.msg == "Buttons that are not Link style must have customId values."
            elif self["style"] is None or self["text"] is None:
                raise TypeError.msg == "Button.style or Button.text missing"
            elif type(self["style"]) is not int:
                raise TypeError.msg == "Button.style is not int - button style must be int type."
            else:

                r[i] = {
                    "type": 2,
                    "label": self["text"],
                    "style": self["style"],
                    "custom_id": self["customId"],
                    "disabled": self["disabled"] if self["disabled"] else False
                }

        rq: list
        for v in range(i):
            rq.append(r[v])

        req_body: dict = {
            "content": content,
            "tts": False,
            "components": [
                {
                    "type": 1,
                    "components": [

                    ]
                }
            ]

        }

        req_body["components"][0]["components"] = rq

        response = requests.post(
            v9_url + f"/channels/{channel_id}/messages", headers=headers, json=req_body)
        return response