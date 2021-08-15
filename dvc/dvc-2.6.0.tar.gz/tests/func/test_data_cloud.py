import logging
import os
import shutil

import pytest
from flaky.flaky_decorator import flaky

import dvc as dvc_module
from dvc.external_repo import clean_repos
from dvc.main import main
from dvc.stage.exceptions import StageNotFound
from dvc.utils.fs import move, remove
from dvc.utils.serialize import dump_yaml, load_yaml

all_clouds = [
    pytest.lazy_fixture(cloud)
    for cloud in [
        "s3",
        "gs",
        "azure",
        "ssh",
        "http",
        "hdfs",
        "webdav",
        "webhdfs",
        "oss",
        "gdrive",
    ]
]

# Clouds that implement the general methods that can be tested
# for functional tests that require extensive apis (e.g traversing
# via walk_files())
full_clouds = [
    pytest.lazy_fixture(cloud)
    for cloud in ["s3", "gs", "azure", "ssh", "hdfs"]
]


@pytest.mark.needs_internet
@pytest.mark.parametrize("remote", all_clouds, indirect=True)
def test_cloud(tmp_dir, dvc, remote):  # pylint:disable=unused-argument
    (stage,) = tmp_dir.dvc_gen("foo", "foo")
    out = stage.outs[0]
    cache = out.cache_path
    foo_hash = out.hash_info
    foo_hashes = out.get_used_objs().get(None, set())

    (stage_dir,) = tmp_dir.dvc_gen(
        {
            "data_dir": {
                "data_sub_dir": {"data_sub": "data_sub"},
                "data": "data",
                "empty": "",
            }
        }
    )
    out_dir = stage_dir.outs[0]
    cache_dir = out_dir.cache_path
    dir_hash = out_dir.hash_info
    dir_hashes = {dir_hash} | {
        entry_obj.hash_info for _, entry_obj in out_dir.obj
    }

    def _check_status(status, **kwargs):
        for key in ("ok", "missing", "new", "deleted"):
            expected = kwargs.get(key, set())
            assert expected == set(getattr(status, key))

    # Check status
    status = dvc.cloud.status(foo_hashes)
    _check_status(status, new={foo_hash})

    status_dir = dvc.cloud.status(dir_hashes)
    _check_status(status_dir, new=dir_hashes)

    # Move cache and check status
    # See issue https://github.com/iterative/dvc/issues/4383 for details
    backup_dir = dvc.odb.local.cache_dir + ".backup"
    move(dvc.odb.local.cache_dir, backup_dir)
    status = dvc.cloud.status(foo_hashes)
    _check_status(status, missing={foo_hash})

    status_dir = dvc.cloud.status(dir_hashes)
    _check_status(status_dir, missing=dir_hashes)

    # Restore original cache:
    remove(dvc.odb.local.cache_dir)
    move(backup_dir, dvc.odb.local.cache_dir)

    # Push and check status
    dvc.cloud.push(foo_hashes)
    assert os.path.exists(cache)
    assert os.path.isfile(cache)

    dvc.cloud.push(dir_hashes)
    assert os.path.isfile(cache_dir)

    status = dvc.cloud.status(foo_hashes)
    _check_status(status, ok={foo_hash})

    status_dir = dvc.cloud.status(dir_hashes)
    _check_status(status_dir, ok=dir_hashes)

    # Remove and check status
    remove(dvc.odb.local.cache_dir)

    status = dvc.cloud.status(foo_hashes)
    _check_status(status, deleted={foo_hash})

    status_dir = dvc.cloud.status(dir_hashes)
    _check_status(status_dir, deleted=dir_hashes)

    # Pull and check status
    dvc.cloud.pull(foo_hashes)
    assert os.path.exists(cache)
    assert os.path.isfile(cache)
    with open(cache) as fd:
        assert fd.read() == "foo"

    dvc.cloud.pull(dir_hashes)
    assert os.path.isfile(cache_dir)

    status = dvc.cloud.status(foo_hashes)
    _check_status(status, ok={foo_hash})

    status_dir = dvc.cloud.status(dir_hashes)
    _check_status(status_dir, ok=dir_hashes)


@pytest.mark.needs_internet
@pytest.mark.parametrize("remote", all_clouds, indirect=True)
def test_cloud_cli(tmp_dir, dvc, remote):
    args = ["-v", "-j", "2"]

    (stage,) = tmp_dir.dvc_gen("foo", "foo")
    cache = stage.outs[0].cache_path

    (stage_dir,) = tmp_dir.dvc_gen(
        {
            "data_dir": {
                "data_sub_dir": {"data_sub": "data_sub"},
                "data": "data",
                "empty": "",
            }
        }
    )
    assert stage_dir is not None
    cache_dir = stage_dir.outs[0].cache_path

    # FIXME check status output

    assert main(["push"] + args) == 0
    assert os.path.exists(cache)
    assert os.path.isfile(cache)
    assert os.path.isfile(cache_dir)

    remove(dvc.odb.local.cache_dir)

    assert main(["fetch"] + args) == 0
    assert os.path.exists(cache)
    assert os.path.isfile(cache)
    assert os.path.isfile(cache_dir)

    assert main(["pull"] + args) == 0
    assert os.path.exists(cache)
    assert os.path.isfile(cache)
    assert os.path.isfile(cache_dir)
    assert os.path.isfile("foo")
    assert os.path.isdir("data_dir")

    with open(cache) as fd:
        assert fd.read() == "foo"
    assert os.path.isfile(cache_dir)

    # NOTE: http doesn't support gc yet
    if remote.url.startswith("http"):
        return

    # NOTE: check if remote gc works correctly on directories
    assert main(["gc", "-cw", "-f"] + args) == 0
    shutil.move(dvc.odb.local.cache_dir, dvc.odb.local.cache_dir + ".back")

    assert main(["fetch"] + args) == 0

    assert main(["pull", "-f"] + args) == 0
    assert os.path.exists(cache)
    assert os.path.isfile(cache)
    assert os.path.isfile(cache_dir)
    assert os.path.isfile("foo")
    assert os.path.isdir("data_dir")


def test_data_cloud_error_cli(dvc):
    f = "non-existing-file"
    assert main(["status", "-c", f])
    assert main(["push", f])
    assert main(["pull", f])
    assert main(["fetch", f])


def test_warn_on_outdated_stage(tmp_dir, dvc, local_remote, caplog):
    stage = dvc.run(outs=["bar"], cmd="echo bar > bar", single_stage=True)
    assert main(["push"]) == 0

    stage_file_path = stage.relpath
    content = load_yaml(stage_file_path)
    del content["outs"][0]["md5"]
    dump_yaml(stage_file_path, content)

    with caplog.at_level(logging.WARNING, logger="dvc"):
        caplog.clear()
        assert main(["status", "-c"]) == 0
        expected_warning = (
            "Output 'bar'(stage: 'bar.dvc') is missing version info. "
            "Cache for it will not be collected. "
            "Use `dvc repro` to get your pipeline up to date."
        )

        assert expected_warning in caplog.text


def test_hash_recalculation(mocker, dvc, tmp_dir, local_remote):
    tmp_dir.gen({"foo": "foo"})
    test_file_md5 = mocker.spy(dvc_module.objects.stage, "file_md5")
    ret = main(["config", "cache.type", "hardlink"])
    assert ret == 0
    ret = main(["add", "foo"])
    assert ret == 0
    ret = main(["push"])
    assert ret == 0
    ret = main(["run", "--single-stage", "-d", "foo", "echo foo"])
    assert ret == 0
    assert test_file_md5.mock.call_count == 1


def test_missing_cache(tmp_dir, dvc, local_remote, caplog):
    from tests.utils import clean_staging

    tmp_dir.dvc_gen({"foo": "foo", "bar": "bar"})

    # purge cache
    remove(dvc.odb.local.cache_dir)
    clean_staging()

    header = (
        "Some of the cache files do not exist "
        "neither locally nor on remote. Missing cache files:\n"
    )
    foo = "name: bar, md5: 37b51d194a7513e45b56f6524f2d51f2\n"
    bar = "name: foo, md5: acbd18db4cc2f85cedef654fccc4a4d8\n"

    caplog.clear()
    dvc.push()
    assert header in caplog.text
    assert foo in caplog.text
    assert bar in caplog.text

    caplog.clear()
    dvc.fetch()
    assert header in caplog.text
    assert foo in caplog.text
    assert bar in caplog.text

    caplog.clear()
    assert dvc.status(cloud=True) == {
        "bar": "missing",
        "foo": "missing",
    }
    assert header not in caplog.text
    assert foo not in caplog.text
    assert bar not in caplog.text


def test_verify_hashes(
    tmp_dir, scm, dvc, mocker, tmp_path_factory, local_remote
):
    tmp_dir.dvc_gen({"file": "file1 content"}, commit="add file")
    tmp_dir.dvc_gen({"dir": {"subfile": "file2 content"}}, commit="add dir")
    dvc.push()

    # remove artifacts and cache to trigger fetching
    remove("file")
    remove("dir")
    remove(dvc.odb.local.cache_dir)

    hash_spy = mocker.spy(dvc_module.objects.stage, "file_md5")

    dvc.pull()
    assert hash_spy.call_count == 0

    # Removing cache will invalidate existing state entries
    remove(dvc.odb.local.cache_dir)

    dvc.config["remote"]["upstream"]["verify"] = True

    dvc.pull()
    assert hash_spy.call_count == 3


@flaky(max_runs=3, min_passes=1)
@pytest.mark.parametrize(
    "erepo", [pytest.lazy_fixture("git_dir"), pytest.lazy_fixture("erepo_dir")]
)
def test_pull_git_imports(tmp_dir, dvc, scm, erepo):
    with erepo.chdir():
        erepo.scm_gen({"dir": {"bar": "bar"}}, commit="second")
        erepo.scm_gen("foo", "foo", commit="first")

    dvc.imp(os.fspath(erepo), "foo")
    dvc.imp(os.fspath(erepo), "dir", out="new_dir", rev="HEAD~")

    assert dvc.pull()["fetched"] == 0

    for item in ["foo", "new_dir", dvc.odb.local.cache_dir]:
        remove(item)
    os.makedirs(dvc.odb.local.cache_dir, exist_ok=True)
    clean_repos()

    assert dvc.pull(force=True)["fetched"] == 3

    assert (tmp_dir / "foo").exists()
    assert (tmp_dir / "foo").read_text() == "foo"

    assert (tmp_dir / "new_dir").exists()
    assert (tmp_dir / "new_dir" / "bar").read_text() == "bar"


def test_pull_external_dvc_imports(tmp_dir, dvc, scm, erepo_dir):
    with erepo_dir.chdir():
        erepo_dir.dvc_gen({"dir": {"bar": "bar"}}, commit="second")
        erepo_dir.dvc_gen("foo", "foo", commit="first")

        os.remove("foo")
        shutil.rmtree("dir")

    dvc.imp(os.fspath(erepo_dir), "foo")
    dvc.imp(os.fspath(erepo_dir), "dir", out="new_dir", rev="HEAD~")

    assert dvc.pull()["fetched"] == 0

    clean(["foo", "new_dir"], dvc)

    assert dvc.pull(force=True)["fetched"] == 2

    assert (tmp_dir / "foo").exists()
    assert (tmp_dir / "foo").read_text() == "foo"

    assert (tmp_dir / "new_dir").exists()
    assert (tmp_dir / "new_dir" / "bar").read_text() == "bar"


def clean(outs, dvc=None):
    from tests.utils import clean_staging

    if dvc:
        outs = outs + [dvc.odb.local.cache_dir]
    for path in outs:
        print(path)
        remove(path)
    if dvc:
        os.makedirs(dvc.odb.local.cache_dir, exist_ok=True)
        clean_repos()
        clean_staging()


def recurse_list_dir(d):
    return [
        os.path.join(d, f) for _, _, filenames in os.walk(d) for f in filenames
    ]


def test_dvc_pull_pipeline_stages(tmp_dir, dvc, run_copy, local_remote):
    (stage0,) = tmp_dir.dvc_gen("foo", "foo")
    stage1 = run_copy("foo", "bar", single_stage=True)
    stage2 = run_copy("bar", "foobar", name="copy-bar-foobar")
    dvc.push()

    outs = ["foo", "bar", "foobar"]

    clean(outs, dvc)
    dvc.pull()
    assert all((tmp_dir / file).exists() for file in outs)

    for out, stage in zip(outs, [stage0, stage1, stage2]):
        for target in [stage.addressing, out]:
            clean(outs, dvc)
            stats = dvc.pull([target])
            assert stats["fetched"] == 1
            assert stats["added"] == [out]
            assert os.path.exists(out)
            assert not any(os.path.exists(out) for out in set(outs) - {out})

    clean(outs, dvc)
    stats = dvc.pull([stage2.addressing], with_deps=True)
    assert len(stats["added"]) == 3
    assert set(stats["added"]) == set(outs)

    clean(outs, dvc)
    stats = dvc.pull([os.curdir], recursive=True)
    assert set(stats["added"]) == set(outs)


def test_pipeline_file_target_ops(tmp_dir, dvc, run_copy, local_remote):
    path = local_remote.url
    tmp_dir.dvc_gen("foo", "foo")
    run_copy("foo", "bar", single_stage=True)

    tmp_dir.dvc_gen("lorem", "lorem")
    run_copy("lorem", "lorem2", name="copy-lorem-lorem2")

    tmp_dir.dvc_gen("ipsum", "ipsum")
    run_copy("ipsum", "baz", name="copy-ipsum-baz")

    outs = ["foo", "bar", "lorem", "ipsum", "baz", "lorem2"]

    remove(dvc.stage_cache.cache_dir)

    dvc.push()

    outs = ["foo", "bar", "lorem", "ipsum", "baz", "lorem2"]

    # each one's a copy of other, hence 3
    assert len(recurse_list_dir(path)) == 3

    clean(outs, dvc)
    assert set(dvc.pull(["dvc.yaml"])["added"]) == {"lorem2", "baz"}

    clean(outs, dvc)
    assert set(dvc.pull()["added"]) == set(outs)

    # clean everything in remote and push
    from tests.dir_helpers import TmpDir

    clean(TmpDir(path).iterdir())
    dvc.push(["dvc.yaml:copy-ipsum-baz"])
    assert len(recurse_list_dir(path)) == 1

    clean(TmpDir(path).iterdir())
    dvc.push(["dvc.yaml"])
    assert len(recurse_list_dir(path)) == 2

    with pytest.raises(StageNotFound):
        dvc.push(["dvc.yaml:StageThatDoesNotExist"])

    with pytest.raises(StageNotFound):
        dvc.pull(["dvc.yaml:StageThatDoesNotExist"])


@pytest.mark.parametrize(
    "fs, msg",
    [
        ({"foo": "foo", "bar": "bar"}, "2 files pushed"),
        ({"foo": "foo"}, "1 file pushed"),
        ({}, "Everything is up to date"),
    ],
)
def test_push_stats(tmp_dir, dvc, fs, msg, capsys, local_remote):
    tmp_dir.dvc_gen(fs)

    main(["push"])
    out, _ = capsys.readouterr()
    assert msg in out


@pytest.mark.parametrize(
    "fs, msg",
    [
        ({"foo": "foo", "bar": "bar"}, "2 files fetched"),
        ({"foo": "foo"}, "1 file fetched"),
        ({}, "Everything is up to date."),
    ],
)
def test_fetch_stats(tmp_dir, dvc, fs, msg, capsys, local_remote):
    tmp_dir.dvc_gen(fs)
    dvc.push()
    clean(list(fs.keys()), dvc)

    main(["fetch"])
    out, _ = capsys.readouterr()
    assert msg in out


def test_pull_stats(tmp_dir, dvc, capsys, local_remote):
    tmp_dir.dvc_gen({"foo": "foo", "bar": "bar"})
    dvc.push()
    clean(["foo", "bar"], dvc)
    (tmp_dir / "bar").write_text("foobar")

    assert main(["pull", "--force"]) == 0

    out, _ = capsys.readouterr()
    assert "M\tbar".expandtabs() in out
    assert "A\tfoo".expandtabs() in out
    assert "2 files fetched" in out
    assert "1 file added" in out
    assert "1 file modified" in out

    main(["pull"])
    out, _ = capsys.readouterr()
    assert "Everything is up to date." in out


@pytest.mark.parametrize(
    "key,expected", [("all_tags", 2), ("all_branches", 3), ("all_commits", 3)]
)
def test_push_pull_all(tmp_dir, scm, dvc, local_remote, key, expected):
    tmp_dir.dvc_gen({"foo": "foo"}, commit="first")
    scm.tag("v1")
    dvc.remove("foo.dvc")
    tmp_dir.dvc_gen({"bar": "bar"}, commit="second")
    scm.tag("v2")
    with tmp_dir.branch("branch", new=True):
        dvc.remove("bar.dvc")
        tmp_dir.dvc_gen({"baz": "baz"}, commit="branch")

    assert dvc.push(**{key: True}) == expected

    clean(["foo", "bar", "baz"], dvc)
    assert dvc.pull(**{key: True})["fetched"] == expected


def test_push_pull_fetch_pipeline_stages(tmp_dir, dvc, run_copy, local_remote):
    tmp_dir.dvc_gen("foo", "foo")
    run_copy("foo", "bar", no_commit=True, name="copy-foo-bar")

    dvc.push("copy-foo-bar")
    assert len(recurse_list_dir(local_remote.url)) == 1
    # pushing everything so as we can check pull/fetch only downloads
    # from specified targets
    dvc.push()
    clean(["foo", "bar"], dvc)

    dvc.pull("copy-foo-bar")
    assert (tmp_dir / "bar").exists()
    assert len(recurse_list_dir(dvc.odb.local.cache_dir)) == 1
    clean(["bar"], dvc)

    dvc.fetch("copy-foo-bar")
    assert len(recurse_list_dir(dvc.odb.local.cache_dir)) == 1


def test_pull_partial(tmp_dir, dvc, local_remote):
    tmp_dir.dvc_gen({"foo": {"bar": {"baz": "baz"}, "spam": "spam"}})
    dvc.push()
    clean(["foo"], dvc)

    stats = dvc.pull(os.path.join("foo", "bar"))
    assert stats["fetched"] == 1
    assert (tmp_dir / "foo").read_text() == {"bar": {"baz": "baz"}}


@pytest.mark.parametrize("remote", full_clouds, indirect=True)
def test_pull_00_prefix(tmp_dir, dvc, remote, monkeypatch):
    # Related: https://github.com/iterative/dvc/issues/6089

    fs_type = type(dvc.cloud.get_remote_odb("upstream").fs)
    monkeypatch.setattr(fs_type, "_ALWAYS_TRAVERSE", True, raising=False)
    monkeypatch.setattr(fs_type, "LIST_OBJECT_PAGE_SIZE", 256, raising=False)

    # foo's md5 checksum is 00411460f7c92d2124a67ea0f4cb5f85
    # bar's md5 checksum is 0000000018e6137ac2caab16074784a6
    tmp_dir.dvc_gen({"foo": "363", "bar": "jk8ssl"})

    dvc.push()
    clean(["foo", "bar"], dvc)

    stats = dvc.pull()
    assert stats["fetched"] == 2
    assert set(stats["added"]) == {"foo", "bar"}


@pytest.mark.parametrize("remote", full_clouds, indirect=True)
def test_pull_no_00_prefix(tmp_dir, dvc, remote, monkeypatch):
    # Related: https://github.com/iterative/dvc/issues/6244

    fs_type = type(dvc.cloud.get_remote_odb("upstream").fs)
    monkeypatch.setattr(fs_type, "_ALWAYS_TRAVERSE", True, raising=False)
    monkeypatch.setattr(fs_type, "LIST_OBJECT_PAGE_SIZE", 256, raising=False)

    # foo's md5 checksum is 14ffd92a6cbf5f2f657067df0d5881a6
    # bar's md5 checksum is 64020400f00960c0ef04052547b134b3
    tmp_dir.dvc_gen({"foo": "dvc", "bar": "cml"})

    dvc.push()
    clean(["foo", "bar"], dvc)

    stats = dvc.pull()
    assert stats["fetched"] == 2
    assert set(stats["added"]) == {"foo", "bar"}
