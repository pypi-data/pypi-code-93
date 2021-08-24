from threading import Thread


def calculate_common_pool(thread_list):
    for j in thread_list:
        j.start()
    for t in thread_list:
        t.join()
    return [i.get_result() for i in thread_list]


class MyThread(Thread):

    def __init__(self, target, args=()):
        super(MyThread, self).__init__()
        self.func = target
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        return self.result
