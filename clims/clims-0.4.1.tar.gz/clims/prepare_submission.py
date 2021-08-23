from pathlib import Path
import os


def write_submission_file(
    header, mpi_command, aims_executable, output_name, error_name, path="."
):
    run_command = get_run_command(mpi_command, aims_executable, output_name, error_name)
    header += f"\n\n{run_command}"

    submit_name = Path(path) / "submit.sh"
    if not submit_name.is_file():
        with open(submit_name, "w") as submit_file:
            submit_file.write(header)
        st = os.stat(submit_name)
        os.chmod(submit_name, st.st_mode | 0o111)
    else:
        print("Submission file 'submit.sh' already exists. I'm not overwriting it.")


def get_run_command(mpi_command, aims_executable, output_name, error_name):
    run_command = f"{mpi_command} {aims_executable} > {output_name} 2> {error_name}"
    return run_command
