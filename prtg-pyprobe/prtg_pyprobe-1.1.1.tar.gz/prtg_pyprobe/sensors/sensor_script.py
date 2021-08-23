import asyncio
import logging
import shlex
import json

from prtg_pyprobe.sensors.helpers import (
    SensorData,
    SensorDefinitionGroup,
    SensorDefinition,
)
from prtg_pyprobe.sensors.sensor import SensorBase


class Sensor(SensorBase):
    @property
    def name(self) -> str:
        return "Script (Probe)"

    @property
    def kind(self) -> str:
        return "mpscript"

    @property
    def definition(self) -> dict:
        script_def = SensorDefinition(
            name=self.name,
            kind=self.kind,
            description="Execute shell scripts on the probe system",
            sensor_help="Execute shell scripts on the probe system",
            tag="mpscriptsensor",
        )
        script_def_group_settings = SensorDefinitionGroup(name="scriptsettings", caption="Script Settings")
        script_def_group_settings.add_field_timeout(10, 10, 900)
        script_def_group_settings.add_field(
            field_type="edit",
            name="script_name",
            caption="Script Name",
            required="1",
            help="Enter the name of the script located in /var/prtg/scripts "
            "(you might have to mount the directory when running the pyprobe container)",
        )
        script_def_group_settings.add_field(
            field_type="edit",
            name="script_args",
            caption="Script Arguments",
            help="Enter the arguments which should be passed to your script",
        )
        script_def_group_settings.add_field(
            field_type="edit",
            name="script_out_unit",
            caption="Script output unit",
            help="Enter the unit which should be displayed for your script values.",
        )
        script_def_group_settings.add_field(
            field_type="radio",
            name="output_type",
            caption="Script output type",
            required="1",
            options={"BASIC": "BASIC", "JSON": "JSON"},
            default="BASIC",
            help="Choose which output your script producse. BASIC -> 'channelname:value' or "
            "JSON -> check docs for format.",
        )
        script_def.add_group(group=script_def_group_settings)
        return script_def.data

    async def work(self, task_data: dict, q: asyncio.Queue) -> None:
        script_path = "/var/prtg/scripts/"
        script_data = SensorData(sensor_id=task_data["sensorid"])
        try:
            if "./" in task_data["script_name"] or ".." in task_data["script_name"] or "~" in task_data["script_name"]:
                raise ValueError("The script name cannot contain ./ or ..")
            shlex_cmd = 'bash -c "{} {}"'.format(
                shlex.quote(script_path + task_data["script_name"]), task_data["script_args"]
            )
            proc = await asyncio.create_subprocess_shell(
                shlex_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if stderr:
                raise OSError(stderr.decode("utf-8"))
            script_data.message = f"Running script {task_data['script_name']}. OK."

            for line in stdout.decode("utf-8").split("\n"):
                if line:
                    if task_data["output_type"] == "BASIC":
                        script_data.add_channel(
                            name=line.split(":")[0],
                            mode="float",
                            kind="Custom",
                            unit="Custom",
                            customunit=task_data["script_out_unit"],
                            value=float(line.split(":")[1]),
                        )
                    else:
                        print(line)
                        line_json = json.loads(line)
                        script_data.add_channel(
                            name=line_json["name"],
                            mode="float",
                            value=float(line_json["value"]),
                            kind="Custom",
                            unit="Custom",
                            customunit=task_data["script_out_unit"],
                        )

        except ValueError:
            script_data.error = "Exception"
            script_data.error_code = 1
            script_data.message = "The script name provided is in wrong format, please use the format script.sh"
            logging.exception("Script name wrong.")
        except OSError:
            script_data.error = "Exception"
            script_data.error_code = 1
            script_data.message = "Executing script produced an error on stderr"
            logging.exception("Script execution produced an error.")
        except KeyError:
            script_data.error = "Exception"
            script_data.error_code = 1
            script_data.message = "Executing script produced an error on stderr"
            logging.exception("Script execution produced an error.")

        await q.put(script_data.data)
        q.task_done()
