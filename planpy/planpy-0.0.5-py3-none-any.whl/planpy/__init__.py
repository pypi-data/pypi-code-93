
import weakref




class tools:


    """

    Main function class

    """

    def add_start_date(self, start_date):
        self.start_date = start_date
        return start_date


    def add_end_date(self, end_date):
        self.end_date = end_date
        return self.end_date

    def add_budget(self, budget):
        self.subject = subject
        return self.subject

    def assigned_to(self, assigned):
        self.assigned = assigned
        return self.assigned

    def business_owner(self, business_owner):
        self.business_owner = business_owner
        return self.business_owner


class risk(tools):
    """ Main risk class of library.

    """
    def __init__(self, name, project, progress):
        self.name = name
        self.project = project
        self.progress = progress



class task(tools):
    """Main task class of library.

            Inititlise a new project:
                Methods can then be added off task

    """
    def __init__(self, name, project, progress):
        self.name = name
        self.project = project
        self.progress = progress



class project(tools):

    """
    Main project class of library.

        Initialise a new project:
            Methods can then be added off the project and visualised.

    """
    projects = []

    def __init__(self,project_name):
        self.project_name = project_name
        self.__class__.projects.append(weakref.proxy(self))

    def __str__(self):
        for instance in self.projects:
            return instance.name
