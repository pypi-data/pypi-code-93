from znth.cli.default import DefaultProcessor
from znth.command.project import *
from znth.factory.project import ProjectFactory


class ProjectProcessor(DefaultProcessor):
    def activate(self, name: str) -> None:
        context = DatabaseContext()
        context["project_name"] = name

        runner = ProjectFactory.create_activate(self.log_level)
        runner.execute(context)

    def create(self, name: str) -> None:
        context = DatabaseContext()
        context["project_name"] = name

        runner = ProjectFactory.create_create(self.log_level)
        runner.execute(context)

    def read(self, name: str) -> None:
        context = DatabaseContext()
        context["project_name"] = name

        runner = ProjectFactory.create_read(self.log_level)
        runner.execute(context)

        self.display(context)

    def update(self, name: str) -> None:
        context = DatabaseContext()
        context["project_name"] = name

        runner = ProjectFactory.create_read(self.log_level)
        runner.execute(context)

        project = context["project"]
        context["project_description"] = self.input("Description: ", project.project_description)
        context["project_remark"] = self.input("Remark: ", project.project_remark)

        runner = ProjectFactory.create_update(self.log_level)
        runner.execute(context)

        runner = ProjectFactory.create_read(self.log_level)
        runner.execute(context)

        self.display(context)

    def delete(self, name: str) -> None:
        context = DatabaseContext()
        context["project_name"] = name

        runner = ProjectFactory.create_delete(self.log_level)
        runner.execute(context)

    def list(self) -> None:
        context = DatabaseContext()

        runner = ProjectFactory.create_list(self.log_level)
        runner.execute(context)

        self.display(context)

    def display(self, context: DatabaseContext) -> None:
        if "project" in context:
            project = context["project"]
            if project:
                print(f"""\
Client:      {project.client.client_name}
ID:          {project.project_id}
UUID:        {project.project_uuid}
Name:        {project.project_name}
Active:      {project.project_active}
Description: {project.project_description or ''}

{project.project_remark or ''}""")
        elif "projects" in context:
            projects = context["projects"]
            if len(projects):
                print(f"Client: {projects[0].client.client_name}")
            for project in projects:
                if project.project_active:
                    msg = f"+ {project.project_id} + {project.project_name} + {project.project_uuid}"
                else:
                    msg = f"- {project.project_id} - {project.project_name} - {project.project_uuid}"
                print(msg)
