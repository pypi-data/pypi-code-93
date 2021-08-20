from loguru import logger
from cdApi.base import base
import json

class home(base):
    def __init__(self, token):
        super().__init__(token)

    def get(self):
        api_name = "info"
        return self.request(
            api_name=api_name,
            params={
                "isUsed": 1,
                "id": self.template_id,
                "type": 0,
                "isPreview": 0,
            },
        )

    def update(self, data):
        api_name = "update"
        response = self.request(
            api_name=api_name,
            method="POST",
            json=data,
        )
        status = response.get("status")
        if status == 200:
            return response
        logger.error(response)


class homeH5Content(home):
    def __init__(self, token, template_id):
        self.token = token
        self.template_id = template_id

    def add(self, h5_content):
        response = self.get()
        data = response.get("data")
        content = data.get("content")
        if content:
            j = json.loads(content)
            j.append(h5_content)
            data["id"] = self.template_id
            data["content"] = json.dumps(j)
            response = self.update(data)
            doc = {
                "msg": "增加外链",
                "request": data,
                "id": self.template_id,
                "response": response,
            }
            if response:
                doc["request"] = str(data)[:20]
                logger.success(doc)
            else:
                logger.error(doc)
        else:
            doc = {
                "template_id": self.template_id,
                "msg": "content不存在",
            }
            logger.error(doc)

    def delete(self, keyword):
        response = self.get()
        data = response.get("data")
        content = data.get("content")
        if content:
            j = json.loads(content)
            if keyword in content:
                for idx, row in enumerate(j):
                    if self.keyword in str(row):
                        j.pop(idx)
                        content = ",".join([str(row) for row in j])
                        data["content"] = json.dumps(j[:-1])
                        response = self.update(data)
                        doc = {
                            "msg": "删除外链",
                            "id": self.template_id,
                            "response": response,
                        }
                        if response:
                            logger.success(doc)
                        else:
                            doc["request"] = data
                            logger.error(doc)
                        break
            else:
                doc = {
                    "template_id": self.template_id,
                    "msg": "content不存在",
                }
                logger.error(doc)
