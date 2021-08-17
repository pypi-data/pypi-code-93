
import os
import yaml
import click
from normandy.engine.pipeline import pipeline
from normandy.engine.errors import excecution_error

def rur_pipe(tags, env, global_params, log_level, threads):
    pipe = pipeline(env = env, tags = tags, global_params = global_params, log_level = log_level, threads = threads)
    pipe.start_pipeline()

def create_framework(project_path):
    actual_path = os.getcwd()
    try:
        os.chdir(project_path)
    except:
        os.mkdir(project_path)
    finally:
        os.chdir(project_path)

    # Create pieline folder and basic confs
    os.mkdir("pipeline")
    os.mkdir("pipeline/step_1")
    basic_confs = {
        "flows" : {
            "my-flow" : {
                "tags" : ["deafult"],
                "step_1" : {
                    "steps" : ["process_1", "process_2"],
                }
            }
        },
        "confs" : {
            "path": project_path,
            "envs" : {
                "dev" : "dev confs",
                "prod" : "prod confs",
            }
        }
    }
    with open("pipeline/pipeline_conf.yml", "w") as file:
        yaml.dump(basic_confs, file, default_flow_style = False)

    # Create extra folders
    os.mkdir("logs")
    os.mkdir("temp")

    os.chdir(actual_path)
    print("Normandy folder structure created")


@click.command()
@click.option("--create-project", "create_project", is_flag = True, help = "Used to create a Normandy project structure in the specify directory.")
@click.option("-project-path", "project_path", default = None, help = "Path where to start Normandy project.")
@click.option("--run-pipeline", "run_pipeline", is_flag = True, help = "Execute the pipeline.")
@click.option("-tags", default = ["default"], help = "Flows with this tag will run.", show_default = True, multiple=True)
@click.option("-env", default = "dev", help = "Enviroment to run.", show_default=True)
@click.option("-param", default = None, help = "Set global parameters.", show_default=True, multiple=True, nargs=2)
@click.option("-log-level", "log_level", default = None, help = "Overwrite log level configuration.")
@click.option("-threads", default = None, help = "Overwrite max thread number configuration.")
def run(create_project, project_path, run_pipeline, tags, env, param, log_level, threads):
    if create_project and run_pipeline:
        raise excecution_error("Cannot use create-project and run-pipeline at the same time")
    if run_pipeline:
        rur_pipe(tags, env, param, log_level, threads)
    elif create_project:
        if project_path is None:
            raise excecution_error("Project path must be specify")
        create_framework(project_path)
    else:
        raise excecution_error("No option selected")
