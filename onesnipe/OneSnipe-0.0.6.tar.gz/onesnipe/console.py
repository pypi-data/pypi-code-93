#   Copyright 2021 Geographs
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import logging


class ColoredFormatter(logging.Formatter):
    def __init__(self) -> None:
        """
        Initializes ColoredFormatter class

        :return none:
        """
        logging.Formatter.__init__(
            self, f"[\u001b[36mOneSnipe\u001b[0m] [%(levelname)s] %(message)s"
        )

        self.colors = {
            "WARNING": "\u001b[33m",
            "INFO": "\u001b[34;1m",
            "CRITICAL": "\u001b[31;1m",
            "ERROR": "\u001b[31m"
        }

    def format(self, record) -> str:
        """
        Formats the message

        :param record:
        :return message:
        """
        record.levelname = self.colors[record.levelname] + record.levelname + "\u001b[0m"
        return logging.Formatter.format(self, record)


console = logging.getLogger("main")
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter())
console.addHandler(handler)
console.setLevel(logging.DEBUG)
