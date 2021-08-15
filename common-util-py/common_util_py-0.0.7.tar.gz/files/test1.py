from files import write_to_file
import threading

threads = []
for i in range(1, 50):
    t = threading.Thread(target=write_to_file, args=('hi.txt', 'test ' + str(i), ))
    threads.append(t)
    t.start()
[thread.join() for thread in threads]
