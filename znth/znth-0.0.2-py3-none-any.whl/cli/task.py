from znth.command.database import DatabaseContext
from znth.cli.default import DefaultProcessor
from znth.factory.task import TaskFactory


class TaskProcessor(DefaultProcessor):
    def new(self) -> None:
        context = DatabaseContext()

        runner = TaskFactory.create_new(self.log_level)
        runner.execute(context)

        self.display(context)

    def start(self, id: int) -> None:
        context = DatabaseContext()
        context["task_id"] = id

        runner = TaskFactory.create_start(self.log_level)
        runner.execute(context)

        self.display(context)

    def stop(self, id: int) -> None:
        context = DatabaseContext()
        context["task_id"] = id

        runner = TaskFactory.create_stop(self.log_level)
        runner.execute(context)

        self.display(context)

    def read(self, id: int) -> None:
        context = DatabaseContext()
        context["task_id"] = id

        runner = TaskFactory.create_read(self.log_level)
        runner.execute(context)

        self.display(context)

    def update(self, id: int) -> None:
        context = DatabaseContext()
        context["task_id"] = id

        runner = TaskFactory.create_read(self.log_level)
        runner.execute(context)

        task = context["task"]
        context["task_name"] = self.input("Name: ", task.task_name)
        context["task_description"] = self.input("Description: ", task.task_description)
        context["task_remark"] = self.input("Remark: ", task.task_remark)

        runner = TaskFactory.create_update(self.log_level)
        runner.execute(context)

        runner = TaskFactory.create_read(self.log_level)
        runner.execute(context)

        self.display(context)

    def delete(self, id: int) -> None:
        context = DatabaseContext()
        context["task_id"] = id

        runner = TaskFactory.create_delete(self.log_level)
        runner.execute(context)

    def list(self) -> None:
        context = DatabaseContext()

        runner = TaskFactory.create_list(self.log_level)
        runner.execute(context)

        self.display(context)

    def display(self, context: DatabaseContext) -> None:
        if "task" in context:
            task = context["task"]
            if task:
                if task.task_start:
                    stime = f"{task.task_start:%Y-%m-%d %H:%M:%S}"
                else:
                    stime = "-"

                if task.task_finish:
                    ftime = f"{task.task_finish:%Y-%m-%d %H:%M:%S}"
                else:
                    ftime = "-"

                print(f"""\
Client:      {task.project.client.client_name}
Project:     {task.project.project_name}
ID:          {task.task_id}
UUID:        {task.task_uuid}
Name:        {task.task_name}
Active:      {task.task_active}
State:       {task.task_state}
Start time:  {stime}
Finish time: {ftime}
Duration:    {task.task_duration}
Description: {task.task_description or ''}

{task.task_remark or ''}""")
        elif "tasks" in context:
            tasks = context["tasks"]
            if len(tasks):
                print(f"Client: {tasks[0].project.client.client_name}")
                print(f"Project: {tasks[0].project.project_name}")
            for task in tasks:
                if task.task_active:
                    msg = f"+ {task.task_id} + {task.task_name} + {task.task_uuid} + {task.task_state}"
                else:
                    msg = f"- {task.task_id} - {task.task_name} - {task.task_uuid} - {task.task_state}"
                print(msg)
