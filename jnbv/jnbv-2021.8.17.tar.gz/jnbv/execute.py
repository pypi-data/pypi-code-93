import logging
import papermill as pm

from .utils import BLUE, LIGHTPURPLE, NC, RED


def execute_ipynb_pm(input_name, output_name, kernel_name, debug):

    if debug:
        print("input_name:  ", input_name)
        print("output_name: ", output_name)
        print("kernel_name: ", kernel_name)

    print("")
    print(LIGHTPURPLE, "*".center(80, "*"), NC)
    print(LIGHTPURPLE, "Executing notebook ", NC, input_name)
    print(BLUE, "Using kernel       ", NC, kernel_name)

    logging.info("Executing notebook: " + str(input_name))

    successful_execution = True
    try:
        # For options see:
        #   https://github.com/nteract/papermill/blob/main/papermill/execute.py
        pm.execute_notebook(
            input_name,
            output_name,
            kernel_name=kernel_name,
            progress_bar=False,
            log_output=True,
            report_mode=False,
        )
    except ModuleNotFoundError as e:
        print(RED)
        print("ModuleNotFoundError")
        print(e)
        print(NC)
        logging.error("ModuleNotFoundError")
        logging.error(e)
        successful_execution = False
    except BaseException as e:
        print(RED)
        print("Unknown error")
        print(e)
        print(NC)
        logging.error("Unknown error")
        logging.error(e)
        successful_execution = False

    logging.info("Done executing notebook: " + str(input_name))
    logging.info("Output saved to: " + str(output_name))

    print(LIGHTPURPLE, "Done executing")
    print(LIGHTPURPLE, "Output Saved to    ", NC, output_name)
    print(LIGHTPURPLE, "*".center(80, "*"), NC)
    print("")

    return successful_execution
