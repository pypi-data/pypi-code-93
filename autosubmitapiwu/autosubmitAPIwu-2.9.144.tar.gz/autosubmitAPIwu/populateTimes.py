import autosubmitAPIwu.experiment.common_requests as ExperimentUtils


def main():
    """
    Updates STATUS of experiments.
    """
    ExperimentUtils.update_running_experiments()


if __name__ == "__main__":
    main()
