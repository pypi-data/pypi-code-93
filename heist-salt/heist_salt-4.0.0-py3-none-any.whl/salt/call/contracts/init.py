def pre(hub, ctx):
    run_dir = ctx.get_arguments()["run_dir"]
    target_os = ctx.get_arguments()["target_os"]
    if not hub.tool.path.clean_path(
        hub.heist.init.default(target_os, "run_dir_root"), run_dir
    ):
        raise ValueError(f"The {run_dir} is not valid")
