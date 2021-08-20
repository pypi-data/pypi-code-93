from typing import Callable, Dict, Tuple

class CliMenu:
    def __init__(self, menu_header: str,
                 definition: Dict[str,
                                  Tuple[str,
                                         Callable[[], None]
                                        ]
                                ],
                 notify_user_provider: Callable[[str], None]):
        self.notify_user_provider = notify_user_provider

        self.menu_header = menu_header
        self.menu_items = definition

    def register(self, menu_text, user_entry, action):
        self.menu_items[user_entry] = (menu_text, action)

    def loop(self, switch, request):
        while True:
            action = switch(request())
            if action is None:
                return
            elif action == "INVALID":
                self.notify_user_provider("Invalid Entry...")
            elif action is not None:
                action()
            else:
                raise NotImplementedError("Unhandled response type")


    def print_menu(self):
        print(f"\n{self.menu_header}")
        print("Please select option\n")

        for item, tup in self.menu_items.items():
            print(tup[0])

    def get_input_from_user(self):
        self.print_menu()
        return input("").upper()

    def run(self):
        switch = lambda x: {item: tup[1] for item, tup in self.menu_items.items()}.get(x, "INVALID")
        self.loop(switch, self.get_input_from_user)