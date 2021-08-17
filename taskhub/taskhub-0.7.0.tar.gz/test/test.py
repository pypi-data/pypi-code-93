from taskhub.connector import connect
from taskhub.hub import Task

hub = connect("127.0.0.1", 2334, "1231")
node_id = 1

def test_add():
    key = "taskkey"
    priority = 1
    data = {
        "abc": 123
    }
    task = Task(key,priority,data)
    r = hub.add(task)
    print(r)


    

test_add()
task = hub.get(node_id)
print(task)
task.data = {"hahha":123}
print(task)
r = hub.upload(task)
print(r)
