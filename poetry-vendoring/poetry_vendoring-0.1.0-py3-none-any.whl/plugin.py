from typing import Optional

from cleo.commands.command import Command
from poetry_bundle_plugin.plugin import ApplicationPlugin

class VendorCommand(Command):
    
    name = "vendor"

    def handle(self) -> Optional[int]:
        self.line("Calling vendor")
        return super().handle()

def factory():
    return VendorCommand()

class VendorPlugin(ApplicationPlugin):
    def activate(self, application):
        application.command_loader.register_factory("vendor", factory)