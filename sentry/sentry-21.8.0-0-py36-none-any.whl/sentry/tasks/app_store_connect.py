"""Tasks for managing Debug Information Files from Apple App Store Connect.

Users can instruct Sentry to download dSYM from App Store Connect and put them into Sentry's
debug files.  These tasks enable this functionality.
"""

import logging
import pathlib
import tempfile
from typing import List, Mapping, Tuple

import requests
import sentry_sdk
from django.utils import timezone

from sentry import projectoptions
from sentry.lang.native import appconnect
from sentry.models import (
    AppConnectBuild,
    LatestAppConnectBuildsCheck,
    Project,
    ProjectOption,
    debugfile,
)
from sentry.tasks.base import instrumented_task
from sentry.utils import json, sdk
from sentry.utils.appleconnect import itunes_connect

logger = logging.getLogger(__name__)


# Sadly this decorator makes this entire function untyped for now as it does not itself have
# typing annotations.  So we do all the work outside of the decorated task function to work
# around this.
# Since all these args must be pickled we keep them to built-in types as well.
@instrumented_task(name="sentry.tasks.app_store_connect.dsym_download", queue="appstoreconnect", ignore_result=True)  # type: ignore
def dsym_download(project_id: int, config_id: str) -> None:
    inner_dsym_download(project_id=project_id, config_id=config_id)


def inner_dsym_download(project_id: int, config_id: str) -> None:
    """Downloads the dSYMs from App Store Connect and stores them in the Project's debug files."""
    with sdk.configure_scope() as scope:
        scope.set_tag("project", project_id)
        scope.set_tag("config_id", config_id)

    project = Project.objects.get(pk=project_id)
    config = appconnect.AppStoreConnectConfig.from_project_config(project, config_id)
    client = appconnect.AppConnectClient.from_config(config)

    listed_builds = client.list_builds()
    builds = process_builds(project=project, config=config, to_process=listed_builds)

    if not builds:
        # No point in trying to see if we have valid iTunes credentials.
        return
    try:
        itunes_client = client.itunes_client()
    except itunes_connect.SessionExpiredError:
        logger.debug("No valid iTunes session, can not download dSYMs")
        return
    for i, (build, build_state) in enumerate(builds):
        with sdk.configure_scope() as scope:
            scope.set_context("dsym_downloads", {"total": len(builds), "completed": i})
        with tempfile.NamedTemporaryFile() as dsyms_zip:
            try:
                itunes_client.download_dsyms(build, pathlib.Path(dsyms_zip.name))
            except appconnect.NoDsymsError:
                logger.debug("No dSYMs for build %s", build)
            except itunes_connect.SessionExpiredError:
                logger.debug("Error fetching dSYMs: expired iTunes session")
                # we early-return here to avoid trying all the other builds
                # as well, since an expired token will error for all of them.
                # we also swallow the error and not report it because this is
                # a totally expected error and not actionable.
                return
            except itunes_connect.ForbiddenError:
                sentry_sdk.capture_message(
                    "Forbidden iTunes dSYM download, probably switched to wrong org", level="info"
                )
                return
            except requests.RequestException as e:
                # Assume these are errors with the server side and do not abort all the
                # pending downloads.
                sdk.capture_exception(e)
                continue
            else:
                create_difs_from_dsyms_zip(dsyms_zip.name, project)
                logger.debug("Uploaded dSYMs for build %s", build)

        # If we either downloaded, or didn't need to download the dSYMs
        # (there was no dSYM url), we check off this build.
        build_state.fetched = True
        build_state.save()


def create_difs_from_dsyms_zip(dsyms_zip: str, project: Project) -> None:
    with sentry_sdk.start_span(op="dsym-difs", description="Extract difs dSYM zip"):
        with open(dsyms_zip, "rb") as fp:
            created = debugfile.create_files_from_dif_zip(fp, project, accept_unknown=True)
            for proj_debug_file in created:
                logger.debug("Created %r for project %s", proj_debug_file, project.id)


def get_or_create_persisted_build(
    project: Project, config: appconnect.AppStoreConnectConfig, build: appconnect.BuildInfo
) -> AppConnectBuild:
    """Fetches the sentry-internal :class:`AppConnectBuild`.

    The build corresponds to the :class:`appconnect.BuildInfo` as returned by the
    AppStore Connect API. If no build exists yet, a new "pending" build is created.
    """
    try:
        build_state = AppConnectBuild.objects.get(
            project=project,
            app_id=int(build.app_id),
            platform=build.platform,
            bundle_short_version=build.version,
            bundle_version=build.build_number,
        )
    except AppConnectBuild.DoesNotExist:
        build_state = AppConnectBuild(
            project=project,
            app_id=int(build.app_id),
            bundle_id=config.bundleId,
            platform=build.platform,
            bundle_short_version=build.version,
            bundle_version=build.build_number,
            uploaded_to_appstore=build.uploaded_date,
            first_seen=timezone.now(),
            fetched=False,
        )
        build_state.save()
    return build_state


def process_builds(
    project: Project,
    config: appconnect.AppStoreConnectConfig,
    to_process: List[appconnect.BuildInfo],
) -> List[Tuple[appconnect.BuildInfo, AppConnectBuild]]:
    """Returns a list of builds whose dSYMs need to be updated or fetched.

    This will create a new "pending" :class:`AppConnectBuild` for any :class:`appconnect.BuildInfo`
    that cannot be found in the DB. These pending :class:`AppConnectBuild`s are immediately saved
    upon creation.
    """

    pending_builds = []

    with sentry_sdk.start_span(
        op="appconnect-update-builds", description="Update AppStoreConnect builds in database"
    ):
        for build in to_process:
            build_state = get_or_create_persisted_build(project, config, build)
            if not build_state.fetched:
                pending_builds.append((build, build_state))

    # All existing usages of this option are internal, so it's fine if we don't carry these over
    # to the table
    # TODO: Clean this up by App Store Connect GA
    if projectoptions.isset(project, appconnect.APPSTORECONNECT_BUILD_REFRESHES_OPTION):
        project.delete_option(appconnect.APPSTORECONNECT_BUILD_REFRESHES_OPTION)

    LatestAppConnectBuildsCheck.objects.create_or_update(
        project=project, source_id=config.id, values={"last_checked": timezone.now()}
    )

    return pending_builds


# Untyped decorator would stop type-checking of entire function, split into an inner
# function instead which can be type checked.
@instrumented_task(  # type: ignore
    name="sentry.tasks.app_store_connect.refresh_all_builds",
    queue="appstoreconnect",
    ignore_result=True,
)
def refresh_all_builds() -> None:
    inner_refresh_all_builds()


def inner_refresh_all_builds() -> None:
    """Refreshes all AppStoreConnect builds for all projects.

    This iterates over all the projects configured in Sentry and for any which has an
    AppStoreConnect symbol source configured will poll the AppStoreConnect API to check if
    there are new builds.
    """
    # We have no way to query for AppStore Connect symbol sources directly, but
    # getting all of the project options that have custom symbol sources
    # configured is a reasonable compromise, as the number of those should be
    # low enough to traverse every hour.
    # Another alternative would be to get a list of projects that have had a
    # previous successful import, as indicated by existing `AppConnectBuild`
    # objects. But that would miss projects that have a valid AppStore Connect
    # setup, but have not yet published any kind of build to AppStore.
    options = ProjectOption.objects.filter(key=appconnect.SYMBOL_SOURCES_PROP_NAME)
    for option in options:
        with sdk.push_scope() as scope:
            scope.set_tag("project", option.project_id)
            try:
                if not option.value:
                    # An empty string set as option value, the UI does this when deleting
                    # all sources.  This is not valid JSON.
                    continue
                # We are parsing JSON thus all types are Any, so give the type-checker some
                # extra help.  We are maybe slightly lying about the type, but the
                # attributes we do access are all string values.
                all_sources: List[Mapping[str, str]] = json.loads(option.value)
                for source in all_sources:
                    try:
                        source_id = source["id"]
                        source_type = source["type"]
                    except KeyError:
                        logger.exception("Malformed symbol source")
                        continue
                    if source_type == appconnect.SYMBOL_SOURCE_TYPE_NAME:
                        dsym_download.apply_async(
                            kwargs={
                                "project_id": option.project_id,
                                "config_id": source_id,
                            }
                        )
            except Exception:
                logger.exception("Failed to refresh AppStoreConnect builds")
