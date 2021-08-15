import threading

class createThread:
    def __init__(self, command, args):
        """
        creates a Thread
        :param command: Command

        :param args: Args

        """
        self.command = command
        self.args = args
        self.x = threading.Thread(target=command, args=args)

    def run(self):
        """
        run the Thread
        :return:
        """
        self.x.start()

    def join(self):
        """
        join the Thread
        :return:
        """
        self.x.join()


