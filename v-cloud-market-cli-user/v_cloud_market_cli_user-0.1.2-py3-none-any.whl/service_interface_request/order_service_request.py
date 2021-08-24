from rich.console import Console

class OrderRequest:

    def __init__(self, console: Console):
        self.console = console

    def get_order_id(self) -> str:
        msg = 'Please enter the order id: '
        return self.console.input(msg)