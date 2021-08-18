# Created by Jan Rummens at 8/01/2021
from nemonet.runner.vision_runner import Runner
import typer
import traceback

app = typer.Typer()

@app.command()
def scenario(name: str, useconfig: bool = False):
    try:
        if useconfig:
            runner = Runner(runner_config="runner_config.json")
        else:
            runner = Runner()
        runner.execute_scenario(name)
    except ValueError:
        typer.echo(f"invalid commandline")
    except FileNotFoundError as e:
        typer.echo(e)
    except Exception as err:
        traceback.print_tb(err.__traceback__)
    finally:
        pass
