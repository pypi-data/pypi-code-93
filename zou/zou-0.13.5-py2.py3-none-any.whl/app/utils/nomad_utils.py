import base64
import json

from zou.app import config


def execute_nomad_job(job, previews, params, movie_file_path):
    import nomad

    bucket_prefix = config.FS_BUCKET_PREFIX
    params = {
        "version": "1",
        "bucket_prefix": bucket_prefix,
        "output_filename": Path(movie_file_path).name,
        "output_key": file_store.make_key("playlists", job["id"]),
        "input": previews,
        "width": params.width,
        "height": params.height,
        "fps": params.fps,
        "FS_BACKEND": config.FS_BACKEND,
    }
    if config.FS_BACKEND == "s3":
        params.update(
            {
                "S3_ENDPOINT": config.FS_S3_ENDPOINT,
                "AWS_DEFAULT_REGION": config.FS_S3_REGION,
                "AWS_ACCESS_KEY_ID": config.FS_S3_ACCESS_KEY,
                "AWS_SECRET_ACCESS_KEY": config.FS_S3_SECRET_KEY,
            }
        )
    elif config.FS_BACKEND == "swift":
        params.update(
            {
                "OS_USERNAME": config.FS_SWIFT_USER,
                "OS_PASSWORD": config.FS_SWIFT_KEY,
                "OS_AUTH_URL": config.FS_SWIFT_AUTHURL,
                "OS_TENANT_NAME": config.FS_SWIFT_TENANT_NAME,
                "OS_REGION_NAME": config.FS_SWIFT_REGION_NAME,
            }
        )

    data = json.dumps(params).encode("utf-8")
    payload = base64.b64encode(data).decode("utf-8")
    ncli = nomad.Nomad(timeout=5)

    # don't use 'app.config' because the webapp doesn't use this variable,
    # only the rq worker does.
    nomad_job = os.getenv("ZOU_NOMAD_PLAYLIST_JOB", "zou-playlist")
    response = ncli.job.dispatch_job(nomad_job, payload=payload)
    nomad_jobid = response["DispatchedJobID"]

    while True:
        summary = ncli.job.get_summary(nomad_jobid)
        task_group = list(summary["Summary"])[0]
        status = summary["Summary"][task_group]
        if status["Failed"] != 0 or status["Lost"] != 0:
            logger.debug("Nomad job %r failed: %r", nomad_jobid, status)
            out, err = get_nomad_job_logs(ncli, nomad_jobid)
            out = textwrap.indent(out, "\t")
            err = textwrap.indent(err, "\t")
            raise Exception(
                "Job %s is 'Failed' or 'Lost':\nStatus: "
                "%s\nerr:\n%s\nout:\n%s" % (nomad_jobid, status, err, out)
            )
        if status["Complete"] == 1:
            logger.debug("Nomad job %r: complete", nomad_jobid)
            break

        # there isn't a timeout here but python rq jobs have a timeout. Nomad
        # jobs have a timeout too.
        time.sleep(1)

    # fetch movie from object storage
    with open(movie_file_path, "wb") as movie_file:
        for chunk in file_store.open_movie("playlists", job["id"]):
            movie_file.write(chunk)


def get_nomad_job_logs(ncli, nomad_jobid):
    allocations = ncli.job.get_allocations(nomad_jobid)
    last = max(
        [(alloc["CreateIndex"], idx) for idx, alloc in enumerate(allocations)]
    )[1]
    alloc_id = allocations[last]["ID"]
    # logs aren't available when the task isn't started
    task = allocations[last]["TaskStates"]["zou-playlist"]
    if not task["StartedAt"]:
        out = "\n".join([x["DisplayMessage"] for x in task["Events"]])
        err = ""
    else:
        err = ncli.client.stream_logs.stream(alloc_id, "zou-playlist", "stderr")
        out = ncli.client.stream_logs.stream(alloc_id, "zou-playlist", "stdout")
        if err:
            err = json.loads(err).get("Data", "")
            err = base64.b64decode(err).decode("utf-8")
        if out:
            out = json.loads(out).get("Data", "")
            out = base64.b64decode(out).decode("utf-8")
    return out.rstrip(), err.rstrip()
