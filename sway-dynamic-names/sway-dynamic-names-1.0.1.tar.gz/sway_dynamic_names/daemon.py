import re

from i3ipc import Event
from i3ipc.aio import Connection, Con
from i3ipc.events import IpcBaseEvent

from .config import Config


class Watcher:
    i3: Connection

    def __init__(self, config: Config):
        self.config = config
        self.commands = []

    async def start(self):
        self.i3 = await Connection().connect()
        for case in [Event.WINDOW_MOVE, Event.WINDOW_NEW, Event.WINDOW_TITLE, Event.WINDOW_CLOSE]:
            self.i3.on(case, self.callback)
        await self.rename_all()
        await self.i3.main()

    async def callback(self, conn: Connection, event: IpcBaseEvent):
        await self.rename_all()

    async def rename_all(self):
        tree = await self.i3.get_tree()
        workspaces = tree.workspaces()
        for num, workspace in enumerate(workspaces):
            await self.rename_workspace(workspace, num)
        await self.commit()

    async def rename_workspace(self, workspace: Con, num: int):
        symbols = []
        for leaf in workspace.leaves():
            leaf_symbol = self.get_symbol(leaf)
            if leaf_symbol:
                symbols.append(leaf_symbol)
        new_name = self.config.default_icon
        if symbols:
            new_name = self.config.delimiter.join(symbols)
        new_name = f"{num}:{new_name}"
        if workspace.name != new_name:
            workspace_name_san = workspace.name.replace('"', '\\"')
            new_name_san = new_name.replace('"', '\\"')
            self.commands.append(f'rename workspace "{workspace_name_san}" to "{new_name_san}"')

    def get_symbol(self, leaf: Con):
        for identifier in ('name', 'window_title', 'window_instance', 'window_class'):
            name = getattr(leaf, identifier, None)
            if name is None:
                continue
            for name_re, conf in self.config.client_configs.items():
                if re.match(name_re, name, re.IGNORECASE):
                    return conf.get_symbol(leaf)

    async def commit(self):
        await self.i3.command(u';'.join(self.commands))
        self.commands = []


async def start():
    config = Config()
    watcher = Watcher(config)
    await watcher.start()
