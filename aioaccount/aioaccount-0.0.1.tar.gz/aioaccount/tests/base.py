import asynctest

from .. import (
    AccountHandler,
    MongoEngine,
    SQLEngine,
    Database,
    SmtpClient
)

from .args import MONGO_SETTINGS, SQL_CONNECTION, SMTP_SETTINGS


class TestBase(asynctest.TestCase):
    use_default_loop = True
    use_sql = False
    use_smtp = False

    handler: AccountHandler

    async def setUp(self) -> None:
        engine = MongoEngine(
            **MONGO_SETTINGS
        ) if not self.use_sql else SQLEngine(
            Database(SQL_CONNECTION)
        )
        self.handler = AccountHandler(
            engine=engine,
            smtp=SmtpClient(
                **SMTP_SETTINGS
            ) if self.use_smtp else None
        )

        await self.handler.start()

    async def tearDown(self) -> None:
        await self.handler.close()
