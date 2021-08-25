import sys

from whizbang.container.application_container import ApplicationContainer
from whizbang.domain.menu.menu_invoker import MenuInvoker
 
from whizbang.util.json_helpers import import_local_json

# see: https://python-dependency-injector.ets-labs.org/examples/decoupled-packages.html
def start_interactive():
    # todo: will need an override
    menu: MenuInvoker = createContainer().menu_package.menu_invoker()
    menu.display_menu()

def execute(solution_type, solution_directory):
    print("executing command line mode")
    container = createContainer(solution_directory)
    solution_factory = container.solution_factory()
    solution = solution_factory.get_solution(solution_type)
    solution.deploy()

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args)==0:  
        start_interactive()
    elif args[0].upper() == 'RUN':
        execute(args)
        
def createContainer(solution_directory):
    # app_config_json = import_local_json('whizbang/config/app_config.json')
    # todo: support passing in a solution directory
    # app_config = AppConfig(solution_rel_path=current_dir_path)

    current_dir_path = str.replace(solution_directory, '\\', '/')
    print(current_dir_path)
    app_config_json = {
        "current_dir_path": current_dir_path
    }

    environment_config_json = import_local_json(f'{current_dir_path}/env_config.json')
    container = ApplicationContainer()
    container.config.app_config.from_dict(app_config_json)
    container.config.environment_config.from_dict(environment_config_json)
    container.wire(modules=[sys.modules[__name__]])
    return container


if __name__ == '__main__':
     # sys.exit(main())
    main()


