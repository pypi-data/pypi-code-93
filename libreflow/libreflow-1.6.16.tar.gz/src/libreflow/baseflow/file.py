import os
import sys
import getpass
import time
import datetime
import shutil
import glob
import string
import re
import hashlib
import timeago
import zipfile
import fnmatch
import subprocess
import pathlib
import mimetypes

import kabaret.app.resources as resources
from kabaret import flow
from kabaret.flow_contextual_dict import ContextualView, get_contextual_dict
# from kabaret.subprocess_manager.flow import RunAction
# from kabaret.jobs import jobs_flow
import psutil

from .maputils import SimpleCreateAction, ClearMapAction

from .site import SyncMap, Request, RequestAs, UploadRevision, SiteJobsPoolNames, ActiveSiteChoiceValue
from .runners import LaunchSessionWorker, CHOICES, CHOICES_ICONS
from .kitsu import KitsuTaskStatus
from .dependency import DependencyView

from ..resources.mark_sequence import fields

from ..utils.b3d import wrap_python_expr
from ..utils.kabaret.subprocess_manager.flow import RunAction
from ..utils.kabaret.jobs import jobs_flow
from ..utils.os import zip_folder, remove_folder_content, hash_folder

pyversion = sys.version_info


class CreateWorkingCopyBaseAction(flow.Action):

    _file = flow.Parent()

    def _get_file(self):
        return self._file

    def allow_context(self, context):
        settings = self.root().project().admin.project_settings
        patterns = settings.non_editable_files.get().split(",")

        for pattern in patterns:
            pattern = pattern.encode('unicode-escape').decode().replace(" ", "")
            if fnmatch.fnmatch(self._get_file().display_name.get(), pattern):
                return False
        
        return True


class RevisionsChoiceValue(flow.values.ChoiceValue):

    STRICT_CHOICES = False

    _file = flow.Parent(2)

    def choices(self):
        return self._file.get_revision_names(sync_status='Available')

    def revert_to_default(self):
        if self._file.is_empty():
            self.set('')
            return

        revision = self._file.get_head_revision(sync_status='Available')
        revision_name = ''
        
        if revision is None:
            choices = self.choices()
            if choices:
                revision_name = choices[0]
        else:
            revision_name = revision.name()
        
        self.set(revision_name)


class CreateWorkingCopyFromRevision(CreateWorkingCopyBaseAction):

    _revision = flow.Parent()

    def _get_file(self):
        return self._revision._file

    def get_buttons(self):
        msg = "<h3>Create a working copy</h3>"

        if self._revision._file.has_working_copy(from_current_user=True):
            msg += "<font color=#D66700>WARNING: You already have a working copy to your name. \
                    Choosing to create a new one will overwrite your changes.</font>"
        self.message.set(msg)

        return ["Create", "Cancel"]

    def needs_dialog(self):
        return self._revision._file.has_working_copy(from_current_user=True)

    def run(self, button):
        if button == "Cancel":
            return

        file = self._revision._file
        working_copy = file.create_working_copy(reference_name=self._revision.name())
        file.set_current_user_on_revision(working_copy.name())
        file.touch()
        file.get_revisions().touch()


class MakeCurrentRevisionAction(flow.Action):

    _revision = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        file = self._revision._file
        file.make_current(self._revision)
        file.get_revisions().touch()
        file.touch()


class GenericRunAction(RunAction):

    _file = flow.Parent()

    def runner_name_and_tags(self):
        ext = self._file.format.get()
        default_applications = self.root().project().admin.default_applications
        runner_name = default_applications[ext].runner_name.get()
        
        return runner_name, []

    def check_env_priority(self, runner_name):
        target_var = "%s_EXEC_PATH" % runner_name.upper()

        sys_env = os.environ
        usr_env = self.root().project().admin.user_environment
        name_site = self.root().project().admin.multisites.current_site_name.get()
        site_env = self.root().project().admin.multisites.working_sites[name_site].site_environment

        if (target_var in sys_env) and (len(sys_env[target_var]) > 0):
            # Highest priority: Already defined, we don't do anything
            pass

        elif (usr_env.has_mapped_name(target_var)) and (len(usr_env[target_var].get()) > 0):
            # Mid priority: We fill the environment
            sys_env[target_var] = usr_env[target_var].get()

        elif (site_env.has_mapped_name(target_var)) and (len(site_env[target_var].value.get()) > 0):
            # Lowest priority
            sys_env[target_var] = site_env[target_var].value.get()

        else:
            # Problem: No path defined for the application.
            # We reserve the key with an empty value to avoid a MissingKeyException
            sys_env[target_var] = ""

    def extra_env(self):
        env = get_contextual_dict(self, "settings")
        env["USER_NAME"] = self.root().project().get_user()
        root_path = self.root().project().get_root()
        
        if root_path:
            env["ROOT_PATH"] = root_path

        return env

    def get_version(self, button):
        ext = self._file.format.get()
        default_applications = self.root().project().admin.default_applications
        runner_version = default_applications[ext].runner_version.get()

        return runner_version

    def get_buttons(self):
        ext = self._file.format.get()
        default_applications = self.root().project().admin.default_applications

        if not default_applications[ext].runner_name.get():
            self.message.set(
                "<h3>No default application for .%s file format.</h3>" % ext
            )
            return ["Cancel"]

        return super(GenericRunAction, self).get_buttons()

    def needs_dialog(self):
        ext = self._file.format.get()
        default_applications = self.root().project().admin.default_applications
        has_default_app = default_applications[ext].runner_name.get()

        return not has_default_app
    
    def run(self, button):
        '''
        Sets the environment variable which contains the runner executable path
        before launching the runner.
        '''
        name, tags = self.runner_name_and_tags()
        self.check_env_priority(name)
        
        rid = self.root().session().cmds.SubprocessManager.run(
            runner_name=name,
            tags=tags,
            version=self.get_version(button),
            label=self.get_run_label(),
            extra_argv=self.extra_argv(),
            extra_env=self.extra_env(),
        )
        return self.get_result(runner_id=rid)


class OpenRevision(GenericRunAction):
    
    _file = flow.Parent(4)
    _revision = flow.Parent()
    
    def extra_argv(self):
        return [self._revision.get_path()]


class ComputeRevisionHash(LaunchSessionWorker):
    _revision = flow.Parent()

    def get_run_label(self):
        return 'Compute revision hash'

    def allow_context(self, context):
        return False

    def launcher_oid(self):
        return self._revision.oid()

    def launcher_exec_func_name(self):
        return "update_hash"


class CheckRevisionHash(flow.Action):
    _revision = flow.Parent()

    def get_buttons(self):
        self.message.revert_to_default()
        return ["Check", "Close"]
    
    def run(self, button):
        if button == "Close":
            return

        if self._revision.hash_is_valid():
            color = "029600"
            msg = "Hash is valid !"
        else:
            color = "D5000D"
            msg = "Invalid hash"

        self.message.set((
            f"<h3><font color=#{color}>"
            f"{msg}</font></h3>"
        ))

        return self.get_result(close=False)


class PublishFileAction(LaunchSessionWorker):

    ICON = ("icons.libreflow", "publish")

    _file = flow.Parent()

    comment = flow.SessionParam("")
    keep_editing = flow.SessionParam(True).ui(
        editor='bool',
        tooltip='If disabled, delete your working copy after publication'
    )
    upload_after_publish = flow.BoolParam(False)

    def get_run_label(self):
        return 'Upload and save dependencies'

    def get_buttons(self):
        msg = "<h2>Publish</h2>"

        working_copies = self._file.get_working_copies()
        if working_copies:
            user_names = [wc.user.get() for wc in working_copies]
            user_names = ["<b>"+n+"</b>" for n in user_names]
            msg += (
                "<h3><font color=#D66500><br>"
                "This file is actually edited by one or more users (%s)."
                "</font></h3>"
                % ', '.join(user_names)
            )

        self.message.set(msg)
        
        return ['Publish', 'Cancel']

    def allow_context(self, context):
        return context and self._file.has_working_copy(True)
    
    def launcher_oid(self):
        return self.oid()

    def launcher_exec_func_name(self):
        return "_process_revision"
    
    def _target_file(self):
        return self._file
    
    def _revision_to_process(self):
        return self._target_file().get_head_revision()
    
    def _process_revision(self):
        file = self._target_file()
        rev = self._revision_to_process()
        
        if self.upload_after_publish.get():
            self._upload(rev)
        
        if file.format.get() == 'blend':
            self._save_blend_dependencies(rev)
    
    def _upload(self, revision):
        current_site = self.root().project().get_current_site()

        upload_job = current_site.get_queue().submit_job(
            emitter_oid=revision.oid(),
            user=self.root().project().get_user(),
            studio=current_site.name(),
            job_type='Upload',
            init_status='WAITING'
        )
        process_jobs_action = self.root().project().admin.process_jobs
        process_jobs_action._process(upload_job)
    
    def _save_blend_dependencies(self, revision):
        from blender_asset_tracer import trace, bpathlib
        from pathlib import Path
        import collections

        path = Path(revision.get_path())
        report = collections.defaultdict(list)

        for usage in trace.deps(path):
            filepath = usage.block.bfile.filepath.absolute()
            asset_path = str(usage.asset_path).replace('//', '')
            report[str(filepath)].append(asset_path)
        
        revision.dependencies.set(dict(report))

    def run(self, button):
        if button == "Cancel":
            return
        
        target_file = self._target_file()
        
        target_file.lock()
        keep_editing = self.keep_editing.get()
        published_revision = target_file.publish(
            comment=self.comment.get(),
            keep_editing=keep_editing
        )

        if not keep_editing:
            target_file.set_current_user_on_revision(published_revision.name())
            target_file.unlock()

        published_revision.make_current.run(None)
        target_file.touch()

        super(PublishFileAction, self).run(None)


class PublishFileFromWorkingCopy(PublishFileAction):

    _revision = flow.Parent()
    _file = flow.Parent(4)
    _department = flow.Parent(6)

    def allow_context(self, context):
        return context and self._revision.is_working_copy(from_current_user=True)

    def run(self, button):
        if button == "Cancel":
            return
        
        # Store grand-parents to keep access to them after revision is removed
        file = self._file
        department = self._department
        upload_after_publish = self.upload_after_publish.get()

        file.lock()
        keep_editing = self.keep_editing.get()

        published_revision = file.publish(
            comment=self.comment.get(),
            keep_editing=keep_editing,
        )

        if not keep_editing:
            file.set_current_user_on_revision(published_revision.name())
            file.unlock()

        if department.auto_current.get():
            published_revision.make_current.run(None)

        file.touch()

        if upload_after_publish:
            super(PublishFileAction, self).run(None)


class SiteName(flow.values.ChoiceValue):
    
    def choices(self):
        sites = self.root().project().get_working_sites()
        return sites.mapped_names()
    
    def revert_to_default(self):
        site = self.root().project().get_current_site()
        self.set(site.name())


class RevisionActionDependencyView(DependencyView):
    
    _parent = flow.Parent(5)
    
    def get_site_name(self):
        return self._action.target_site.get()
    
    def get_revision_name(self):
        return self._action.revision.name()


class RequestRevisionDependencies(flow.Action):
    
    revision = flow.Parent().ui(hidden=True)
    target_site = flow.Param(None, ActiveSiteChoiceValue).watched()
    dependencies = flow.Child(RevisionActionDependencyView)
    predictive_only = flow.SessionParam(False).ui(editor='bool').watched()
    
    def child_value_changed(self, child_value):
        if child_value in [self.target_site, self.predictive_only]:
            self.update_dependencies()
    
    def update_dependencies(self):
        self.dependencies.update_dependencies_data()
        self.dependencies.touch()
    
    def get_buttons(self):
        choices = self.target_site.choices()
        
        if not choices:
            return ['Cancel']
        
        self.target_site.set(choices[0])
        
        return ['Proceed', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        target_site = self.target_site.get()
        
        for d in self.dependencies.mapped_items():
            revision_oid = d.revision_oid.get()
            if revision_oid is not None and d.in_breakdown.get():
                rev = self.root().get_object(revision_oid)
                status = rev.get_sync_status(site_name=target_site)
                
                if status == 'NotAvailable':
                    rev.request_as.sites.target_site.set(target_site)
                    rev.request_as.sites.source_site.set(d.source_site.get())
                    rev.request_as.run(None)
        
        return self.get_result(close=False)


class Revision(flow.Object):

    _revisions = flow.Parent()
    _file = flow.Parent(3)

    user = flow.Param().ui(editable=False)
    date = flow.IntParam().ui(editable=False, editor="datetime")
    comment = flow.Param("").ui(editable=False)
    path = flow.Computed(cached=True)
    file_name = flow.Computed()
    hash = flow.Param("").ui(editable=False)

    site = flow.Param()
    sync = flow.Child(SyncMap).ui(expanded=True)
    ready_for_sync = flow.BoolParam(True)

    open = flow.Child(OpenRevision)
    make_current = flow.Child(MakeCurrentRevisionAction)
    publish = flow.Child(PublishFileFromWorkingCopy)
    create_working_copy = flow.Child(CreateWorkingCopyFromRevision)
    request = flow.Child(Request)
    request_as = flow.Child(RequestAs)
    request_dependencies = flow.Child(RequestRevisionDependencies)
    upload = flow.Child(UploadRevision)
    compute_hash_action = flow.Child(ComputeRevisionHash)
    check_hash = flow.Child(CheckRevisionHash)
    dependencies = flow.Param("").ui(editor='textarea', editable=False)

    def get_path(self):
        return os.path.join(self.path.get(), self.file_name.get())
    
    def get_relative_path(self):
        return os.path.join(
            self._file.path.get(),
            self.name(),
            self.file_name.get()
        )

    def is_current(self):
        return self.name() == self._file.current_revision.get()

    def is_working_copy(self, from_current_user=False):
        if from_current_user:
            return self.name() == self.root().project().get_user()

        return re.match(r'v\d\d\d', self.name()) is None

    def get_sync_status(self, site_name=None, exchange=False):
        """
        Returns revision's status on the site identified
        by the given name, or the project's exchange site
        if `exchange` is True.

        If site_name is None, this method returns its status
        on the current site.
        """
        if exchange:
            exchange_site_name = self.root().project().get_exchange_site().name()
            return self.sync[exchange_site_name].status.get()

        if not site_name:
            site_name = self.root().project().get_current_site().name()
        return self.sync[site_name].status.get()

    def set_sync_status(self, status, site_name=None, exchange=False):
        """
        Sets revision's status on the site identified
        by the given name, or the project's exchange site
        if `exchange` is True, to the given status.

        If site_name is None, this method sets its status
        on the current site.
        """
        if exchange:
            exchange_site_name = self.root().project().get_exchange_site().name()
            return self.sync[exchange_site_name].status.get()

        if not site_name:
            site_name = self.root().project().get_current_site().name()
        self.sync[site_name].status.set(status)

    def get_last_edit_time(self):
        if self.exists():
            return os.path.getmtime(self.get_path())
        
        return 0
    
    def exists(self):
        return os.path.exists(self.get_path())
    
    def compute_hash(self):
        path = self.get_path()
        
        if os.path.exists(path):
            with open(path, "rb") as f:
                content = f.read()

            return hashlib.md5(content).hexdigest()
    
    def update_hash(self):
        self.hash.set(self.compute_hash())
        self.hash.touch()
    
    def hash_is_valid(self):
        return self.hash.get() == self.compute_hash()

    def compute_child_value(self, child_value):
        if child_value is self.is_current:
            child_value.set(self.name() == self._file.current_revision.get())
        elif child_value is self.path:
            path = os.path.join(
                self.root().project().get_root("UNKNOWN_ROOT_DIR"),
                self._file.path.get(),
                self.name(),
            )
            child_value.set(path)
        elif child_value is self.file_name:
            name = "{filename}_{revision}.{ext}".format(
                filename=self._file.complete_name.get(),
                revision=self.name(),
                ext=self._file.format.get(),
            )
            child_value.set(name)
        elif child_value is self.playblast_path:
            child_value.set(
                os.path.join(
                    os.path.dirname(self._file.get_path()),
                    "preview",
                    "%s_%s-movie.mov" % (self._file.complete_name.get(), self.name()),
                )
            )


class ToggleSyncStatuses(flow.Action):
    _revisions = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        self._revisions.show_sync_statuses.set(
            not self._revisions.show_sync_statuses.get()
        )
        self._revisions.touch()


class ToggleShortNames(flow.Action):
    _revisions = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        self._revisions.enable_short_names.set(
            not self._revisions.enable_short_names.get()
        )
        self._revisions.touch()


class TogglePublicationDateFormat(flow.Action):
    
    ICON = ('icons.libreflow', 'time_format')
    
    _revisions = flow.Parent()
    
    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return context and context.endswith('.inline')
    
    def run(self, button):
        enabled = self._revisions.time_ago_enabled.get()
        self._revisions.time_ago_enabled.set(not enabled)
        self._revisions.touch()


class ToggleActiveSites(flow.Action):

    ICON = ('icons.libreflow', 'active_site')

    _revisions = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        active_sites_only = self._revisions.active_sites_only
        active_sites_only.set(not active_sites_only.get())
        self._revisions.touch()


class Revisions(flow.Map):

    _file = flow.Parent(2)
    show_sync_statuses = flow.SessionParam(True).ui(hidden=True, editor='bool')
    enable_short_names = flow.SessionParam(True).ui(hidden=True, editor='bool')
    time_ago_enabled = flow.SessionParam(False).ui(hidden=True, editor='bool')
    active_sites_only = flow.SessionParam(True).ui(hidden=True, editor='bool')

    toggle_sync_statuses = flow.Child(ToggleSyncStatuses)
    toggle_short_names = flow.Child(ToggleShortNames)
    toggle_date_format = flow.Child(TogglePublicationDateFormat)
    toggle_active_sites = flow.Child(ToggleActiveSites)

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(Revision)
    
    def _site_names(self, active_only=False, short_names=False):
        working_sites = self.root().project().get_working_sites()
        current_site = self.root().project().get_current_site()
        exchange_site = self.root().project().get_exchange_site()
        
        if short_names:
            current_site_name = current_site.short_name.get()
            exchange_site_name = exchange_site.short_name.get()
        else:
            current_site_name = current_site.name()
            exchange_site_name = exchange_site.name()
        
        site_names = working_sites.get_site_names(True, active_only, short_names)
        
        try:
            site_names.remove(current_site_name)
        except ValueError:
            pass
        
        site_names = [current_site_name, exchange_site_name] + site_names
        
        return site_names

    def columns(self):
        columns = ["Revision", "Created by", "When"]
        
        if self.show_sync_statuses.get():
            columns += self._site_names(
                active_only=self.active_sites_only.get(),
                short_names=self.enable_short_names.get()
            )
        
        columns.append("Comment")

        return columns

    def add(self, name=None, object_type=None, ready_for_sync=True):
        publication_count = sum(
            list(map(lambda rev: int(not rev.is_working_copy()), self.mapped_items()))
        )

        if not name:
            name = "v{:03d}".format(publication_count + 1)

        rev = super(Revisions, self).add(name, object_type)
        rev.user.set(self.root().project().get_user())
        rev.date.set(time.time())
        rev.site.set(self.root().project().get_current_site().name())
        rev.ready_for_sync.set(ready_for_sync)

        return rev

    def _fill_row_cells(self, row, item):
        item_name = item.name()
        if item.is_working_copy():
            item_name += " ("
            if item.is_working_copy(from_current_user=True):
                item_name += "your "
            item_name += "working copy)"
        
        if item.get_sync_status() == "Requested":
            item_name += " ⏳"

        row.update(
            {
                "Revision": item_name,
                "Created by": item.user.get(),
                "When": datetime.datetime.fromtimestamp(item.date.get()),
                "Comment": item.comment.get(),
            }
        )
        
        if self.time_ago_enabled.get():
            row['When'] = timeago.format(row['When'], datetime.datetime.now())

        if self.show_sync_statuses.get():
            names = self._site_names(
                active_only=self.active_sites_only.get(),
                short_names=self.enable_short_names.get()
            )
            
            d = dict.fromkeys(names, "")
            row.update(d)

    def _fill_row_style(self, style, item, row):
        seen_name = self._file.current_user_sees.get()
        if item.is_current():
            if item.name() == seen_name or seen_name == "current":
                style["icon"] = ('icons.libreflow', 'circular-shape-right-eye-silhouette')
            else:
                style["icon"] = ('icons.libreflow', 'circular-shape-silhouette')
        else:
            if item.name() == seen_name:
                style["icon"] = ('icons.libreflow', 'circle-shape-right-eye-outline')
            else:
                style["icon"] = ('icons.libreflow', 'circle-shape-outline')

        color_and_icon_by_status = {
            "Available": ("#45cc3d", ("icons.libreflow", "checked-symbol-colored")),
            "Requested": ("#cc3b3c", ("icons.libreflow", "exclamation-sign-colored")),
            "NotAvailable": ("#cc3b3c", ("icons.libreflow", "blank"))
        }
        style["foreground-color"] = color_and_icon_by_status[item.get_sync_status()][0]

        if self.show_sync_statuses.get():
            site_names = self._site_names(active_only=self.active_sites_only.get())

            for sync_status in item.sync.mapped_items():
                if sync_status.name() in site_names:
                    if self.enable_short_names.get():
                        name = sync_status.get_short_name()
                    else:
                        name = sync_status.name()
            
                    style[name + "_icon"] = color_and_icon_by_status[sync_status.status.get()][1]
        
        style["Revision_activate_oid"] = item.open.oid()


class History(flow.Object):

    revisions = flow.Child(Revisions).injectable().ui(expanded=True)
    department = flow.Parent(3)


class FileFormat(flow.values.ChoiceValue):
    CHOICES = CHOICES

class CreateTrackedFileAction(flow.Action):

    ICON = ("icons.gui", "plus-sign-in-a-black-circle")

    _files = flow.Parent()

    file_name = flow.Param("")
    file_format = flow.Param("blend", FileFormat).ui(
        choice_icons=CHOICES_ICONS
    )

    def get_buttons(self):
        self.message.set("<h3>Create tracked file</h3>")
        return ["Create", "Cancel"]

    def run(self, button):
        if button == "Cancel":
            return

        settings = get_contextual_dict(self, "settings")
        file_category = settings.get("file_category", None)

        name = self.file_name.get()
        prefix = ""

        if file_category is not None:
            if file_category == "PROD":
                prefix = "{file_category}_{sequence}_{shot}_{department}_"
            elif file_category == "LIB":
                prefix = "{file_category}_{asset_name}_{department}_"

            prefix = prefix.format(**settings)

        self.root().session().log_debug(
            "Creating file %s.%s" % (name, self.file_format.get())
        )

        self._files.add_tracked_file(name, self.file_format.get(), prefix + name)
        self._files.touch()


class CreateWorkingCopyAction(CreateWorkingCopyBaseAction):

    _file = flow.Parent()

    from_revision = flow.Param(None, RevisionsChoiceValue).ui(label="Reference")

    def get_buttons(self):
        msg = "<h3>Create a working copy</h3>"

        if self._file.has_working_copy(from_current_user=True):
            msg += "<font color=#D66700>WARNING: You already have a working copy to your name. \
                    Choosing to create a new one will overwrite your changes.</font>"
        self.message.set(msg)

        self.from_revision.revert_to_default()

        return ["Create", "Create from scratch", "Cancel"]

    def needs_dialog(self):
        return not self._file.is_empty() or self._file.has_working_copy(
            from_current_user=True
        )

    def run(self, button):
        if button == "Cancel":
            return
        
        if button == "Create from scratch":
            working_copy = self._file.create_working_copy()
        else:
            ref_name = self.from_revision.get()

            if ref_name == "" or self._file.is_empty():
                ref_name = None
            elif not self._file.has_revision(ref_name):
                msg = self.message.get()
                msg += (
                    "<br><br><font color=#D5000D>There is no revision %s for this file.</font>"
                    % ref_name
                )
                self.message.set(msg)

                return self.get_result(close=False)

            working_copy = self._file.create_working_copy(reference_name=ref_name)

        self._file.set_current_user_on_revision(working_copy.name())
        self._file.touch()
        self._file.get_revisions().touch()


class SeeRevisionAction(flow.Action):

    ICON = ("icons.libreflow", "watch")

    _file = flow.Parent()
    revision_name = flow.Param(None, RevisionsChoiceValue).ui(label="Revision")

    def allow_context(self, context):
        return False

    def get_buttons(self):
        self.message.set("<h3>Choose a revision to open</h3>")

        if self._file.is_empty():
            self.message.set("<h3>This file has no revision</h3>")
            return ["Cancel"]

        seen_name = self._file.current_user_sees.get()
        if seen_name != "current" or self._file.has_current_revision():
            if seen_name == "current":
                seen_name = self._file.current_revision.get()
            self.revision_name.set(seen_name)
        else:
            self.revision_name.set(self._file.get_revisions().mapped_names[0])

        return ["See", "Cancel"]

    def run(self, button):
        if button == "Cancel":
            return

        name = self.revision_name.get()

        if self._file.get_revision(name).is_current():
            name = "current"

        self._file.set_current_user_on_revision(name)
        self._file.touch()


class OpenFileAction(GenericRunAction):
    def extra_argv(self):
        return [self._file.get_path()]


class OpenTrackedFileAction(GenericRunAction):

    _to_open = flow.Param("")
    revision_name = flow.Param(None, RevisionsChoiceValue).ui(label="Revision")

    def get_run_label(self):
        return 'Open file'

    def get_buttons(self):
        if super(OpenTrackedFileAction, self).needs_dialog():
            return super(OpenTrackedFileAction, self).get_buttons()

        self.revision_name.revert_to_default()

        # At least one existing revision
        buttons = ["Open revision", "Cancel"]
        user_sees = self._file.current_user_sees.get()

        # Check if user's working copy already exists
        if not self._file.has_working_copy(from_current_user=True):
            buttons.insert(1, "Create a working copy")

        if user_sees == "current":
            if not self._file.has_current_revision():
                msg = "<h3>No active revision</h3>"
                self.message.set(msg)

                return buttons

            user_sees = self._file.current_revision.get()

        # Current user is seeing a revision
        revision = self._file.get_revision(user_sees)

        if not revision.is_working_copy(from_current_user=True):
            msg = "<h3>Read-only mode</h3>"
            msg += "You're about to open this file in read-only mode. If you want to edit it, you can open your working copy or create one."
            self.message.set(msg)

        return buttons

    def needs_dialog(self):
        seen_name = self._file.current_user_sees.get()
        if seen_name == "current":
            seen = self._file.get_current_revision()
        else:
            seen = self._file.get_revision(seen_name)

        return not self._file.is_empty() and (
            seen is None or not seen.is_working_copy(from_current_user=True)
        )

    def extra_argv(self):
        revision = self._file.get_revision(self._to_open.get())
        return [revision.get_path()]

    def run(self, button):
        if button == "Cancel":
            return

        if button == "Create a working copy" or self._file.is_empty():
            ref_name = None if self._file.is_empty() else self.revision_name.get()
            working_copy = self._file.create_working_copy(reference_name=ref_name)
            revision_name = working_copy.name()
        elif button == "Open revision":
            revision_name = self.revision_name.get()
        else:
            revision_name = self._file.current_user_sees.get()

        self._file.set_current_user_on_revision(revision_name)
        self._to_open.set(revision_name)
        result = super(OpenTrackedFileAction, self).run(button)

        self._file.touch()

        return result


class OpenWithDefaultApp(RunAction):

    def runner_name_and_tags(self):
        return "DefaultEditor", []

    def extra_env(self):
        env = get_contextual_dict(self, "settings")
        env["USER_NAME"] = self.root().project().get_user()
        root_path = self.root().project().get_root()

        if root_path:
            env["ROOT_PATH"] = root_path

        return env


class OpenWithAction(OpenTrackedFileAction):
    
    def runner_name_and_tags(self):
        raise NotImplementedError()

    def allow_context(self, context):
        return context and self._file.format.get() in self.supported_extensions()

    @classmethod
    def supported_extensions(cls):
        raise NotImplementedError()


class OpenWithBlenderAction(OpenWithAction):

    ICON = ("icons.libreflow", "blender")

    def runner_name_and_tags(self):
        return "Blender", []

    @classmethod
    def supported_extensions(cls):
        return ["blend"]


class OpenWithKritaAction(OpenWithAction):

    ICON = ("icons.libreflow", "krita")

    def runner_name_and_tags(self):
        return "Krita", []

    @classmethod
    def supported_extensions(cls):
        return ["kra", "png", "jpg"]


class OpenWithVSCodiumAction(OpenWithAction):

    ICON = ("icons.libreflow", "vscodium")

    def runner_name_and_tags(self):
        return "VSCodium", []

    @classmethod
    def supported_extensions(cls):
        return ["txt"]


class OpenWithNotepadPPAction(OpenWithAction):

    ICON = ("icons.flow", "notepad")

    def runner_name_and_tags(self):
        return "NotepadPP", []

    @classmethod
    def supported_extensions(cls):
        return ["txt"]


class MakeFileCurrentAction(flow.Action):

    _file = flow.Parent()

    def needs_dialog(self):
        return False

    def allow_context(self, context):
        head_revision = self._file.get_head_revision()
        return (
            context and head_revision is not None and not head_revision.is_current()
        )  # And user is admin ?

    def run(self, button):
        self.root().session().log_debug(
            "Make latest revision of file %s current" % self._file.name()
        )

        self._file.make_current(self._file.get_head_revision())
        self._file.touch()


class GotoHistory(flow.Action):

    ICON = ("icons.gui", "ui-layout")

    _file = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        return self.get_result(goto=self._file.history.oid())


class LockAction(flow.Action):

    ICON = ("icons.gui", "padlock")

    _file = flow.Parent()

    def allow_context(self, context):
        return context and not self._file.is_locked()
    
    def needs_dialog(self):
        return False

    def run(self, button):
        self._file.lock()
        self._file._map.touch()


class UnlockAction(flow.Action):

    ICON = ("icons.gui", "open-padlock-silhouette")

    _file = flow.Parent()

    def allow_context(self, context):
        return self._file.is_locked(by_current_user=True)
    
    def needs_dialog(self):
        return False

    def run(self, button):
        self._file.unlock()
        self._file._map.touch()


class UserSees(flow.values.Value):
    pass


class ActiveUsers(flow.Map):
    @classmethod
    def mapped_type(cls):
        return UserSees

    def columns(self):
        return ["User", "Revision"]

    def _fill_row_cells(self, row, item):
        row["User"] = item.name()
        row["Revision"] = item.get()


class RevealInExplorer(RunAction):

    ICON = ('icons.flow', 'explorer')

    _item = flow.Parent()

    def runner_name_and_tags(self):
        return "DefaultEditor", []

    def extra_argv(self):
        path = self._item.get_path()
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        
        return [path]

    def needs_dialog(self):
        return False


class FileSystemItem(flow.Object):

    _department = flow.Parent(2)
    settings = flow.Child(ContextualView).ui(hidden=True)
    path = flow.Computed(cached=True)

    def get_name(self):
        return self.name()

    def get_path(self):
        return os.path.join(
            self.root().project().get_root(),
            self.path.get()
        )

    def get_last_edit_time(self):
        path = self.get_path()
        if os.path.exists(path):
            return os.path.getmtime(path)
        
        return 0
    
    def compute_child_value(self, child_value):
        if child_value is self.path:
            child_value.set(os.path.join(
                self._department.path.get(),
                self.get_name()
            ))


class File(FileSystemItem):

    format = flow.Param("blend", FileFormat).ui(editable=False).injectable()
    display_name = flow.Computed()
    open = flow.Child(OpenFileAction)
    reveal = flow.Child(RevealInExplorer).ui(label="Reveal in explorer")

    def get_name(self):
        return "%s.%s" % (self.name(), self.format.get())

    def get_template_path(self):
        try:
            return resources.get("file_templates", "template.%s" % self.format.get())
        except resources.NotFoundError:
            raise resources.NotFoundError(
                "No template file for '%s' format." % self.format.get()
            )

    def compute_child_value(self, child_value):
        if child_value is self.display_name:
            file_name = "_".join(self.name().split("_")[:-1])
            child_value.set("%s.%s" % (file_name, self.format.get()))
        else:
            super(File, self).compute_child_value(child_value)


class SearchExistingRevisions(flow.Action):

    _file = flow.Parent()

    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return False

    def run(self, button):
        folders = [
            f for f in os.listdir(self._file.get_path()) if re.search(r"^v\d\d\d$", f)
        ]
        revisions = self._file.get_revisions()

        for name in folders:
            try:
                revisions.add(name)
            except ValueError:
                pass

        revisions.touch()


class FileJob(jobs_flow.Job):

    _file = flow.Parent(2)
    
    def get_log_filename(self):
        root = str(pathlib.Path.home()) + "/.libreflow/log/"
        dt = datetime.datetime.fromtimestamp(self.get_created_on())
        dt = dt.astimezone().strftime("%Y-%m-%dT%H-%M-%S%z")
        
        path = os.path.join(root, '%s_%s.log' % (self.__class__.__name__, dt))
        return path


class PlayblastJob(FileJob):

    revision = flow.Param().ui(editable=False)
    use_simplify = flow.BoolParam().ui(editable=False)

    def _do_job(self):
        # Job is to wait until the playblast is ended
        render_playblast = self._file.render_playblast
        render_playblast.revision_name.set(self.revision.get())
        render_playblast.use_simplify.set(self.use_simplify.get())
        
        result = render_playblast.run('Render')
        rid = result['runner_id']

        runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)

        while runner_info['is_running']:
            self.show_message("Waiting for runner %s to finish" % rid)
            time.sleep(1)
            
            runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)
        
        self.show_message("Runner %s finished !" % rid)


class FileJobs(jobs_flow.Jobs):

    @classmethod
    def job_type(cls):
        return FileJob

    def create_job(self, job_type=None):
        name = '{}{:>05}'.format(self._get_job_prefix(), self._get_next_job_id())
        job = self.add(name, object_type=job_type)
        return job


class RenderBlenderPlayblastAction(OpenWithBlenderAction):

    _files = flow.Parent(2)
    revision_name = flow.Param("", RevisionsChoiceValue).watched()
    use_simplify = flow.SessionParam(False).ui(
        tooltip="Use low-definition rigs",
        editor='bool',
    )

    def get_run_label(self):
        return 'Render playblast'

    def _sequence_number_from_name(self, sequence_name):
        tmp = re.findall(r"\d+", sequence_name)
        numbers = list(map(int, tmp))
        return numbers[0]

    def get_buttons(self):
        self.revision_name.revert_to_default()
        buttons = ['Render', 'Cancel']

        if self._file.has_working_copy(from_current_user=True):
            buttons.insert(1, 'Publish first')
        
        current_site = self.root().project().get_current_site()
        if current_site.site_type.get() == 'Studio':
            buttons.insert(1, 'Submit job')
        
        return buttons

    def needs_dialog(self):
        return True

    def allow_context(self, context):
        return (
            super(RenderBlenderPlayblastAction, self).allow_context(context)
            and not self._file.is_empty()
        )
    
    def playblast_infos_from_revision(self, revision_name):
        filepath = self._file.path.get()
        filename = "_".join(self._file.name().split("_")[:-1])

        playblast_filename = filename + "_movie"
        playblast_revision_filename = self._file.complete_name.get() + "_movie.mov"
        
        playblast_filepath = os.path.join(
            self.root().project().get_root(),
            os.path.dirname(filepath),
            playblast_filename + "_mov",
            revision_name,
            playblast_revision_filename
        )

        return playblast_filepath, playblast_filename

    def child_value_changed(self, child_value):
        if child_value is self.revision_name:
            msg = "<h2>Render playblast</h2>"
            playblast_path, _ = self.playblast_infos_from_revision(child_value.get())

            # Check if revision playblast exists
            if os.path.exists(playblast_path):
                msg += (
                    "<font color=#D50000>"
                    "Choosing to render a revision's playblast "
                    "will override the existing one."
                    "</font>"
                )

            self.message.set(msg)

    def extra_argv(self):
        file_settings = get_contextual_dict(
            self._file, "settings", ["sequence", "shot"]
        )
        project_name = self.root().project().name()
        revision = self._file.get_revision(self.revision_name.get())
        python_expr = """import bpy
bpy.ops.lfs.playblast(do_render=True, filepath='%s', studio='%s', project='%s', sequence='s%04i', scene='%s', do_simplify=%s, version='%s')""" % (
            self.output_path,
            self.root().project().get_current_site().name(),
            project_name,
            self._sequence_number_from_name(file_settings["sequence"]),
            file_settings["shot"],
            str(self.use_simplify.get()),
            self.revision_name.get(),
        )

        return [
            "-b",
            revision.get_path(),
            "--addons",
            "mark_sequence",
            "--python-expr",
            wrap_python_expr(python_expr),
        ]

    def run(self, button):
        if button == "Cancel":
            return
        elif button == "Publish first":
            return self.get_result(
                next_action=self._file.publish_and_render_playblast.oid()
            )
        elif button == "Submit job":
            submit_action = self._file.submit_playblast_job
            submit_action.revision_name.set(self.revision_name.get())
            submit_action.use_simplify.set(self.use_simplify.get())
            
            return self.get_result(
                next_action=submit_action.oid()
            )

        revision_name = self.revision_name.get()
        playblast_path, playblast_name = self.playblast_infos_from_revision(
            revision_name
        )

        # Get or create playblast file
        if not self._files.has_mapped_name(playblast_name + "_mov"):
            playblast_file = self._files.add_tracked_file(
                name=playblast_name,
                extension="mov",
                complete_name=self._file.complete_name.get() + "_movie"
            )
        else:
            playblast_file = self._files[playblast_name + "_mov"]
        
        # Get or add playblast revision
        if playblast_file.has_revision(revision_name):
            playblast_revision = playblast_file.get_revision(
                revision_name
            )
        else:
            playblast_revision = playblast_file.get_revisions().add(
                name=revision_name
            )
        
        # Configure playblast revision
        revision = self._file.get_revision(revision_name)
        playblast_revision.comment.set(revision.comment.get())
        playblast_revision.set_sync_status("Available")

        # Store revision path as playblast output path
        self.output_path = playblast_revision.get_path().replace("\\", "/")
        
        # Ensure playblast revision folder exists and is empty
        if not os.path.exists(playblast_revision.path.get()):
            os.makedirs(playblast_revision.path.get())
        elif os.path.exists(self.output_path):
            os.remove(self.output_path)

        result = super(RenderBlenderPlayblastAction, self).run(button)
        self._files.touch()
        return result


class SubmitBlenderPlayblastJob(flow.Action):
    
    _file = flow.Parent()
    
    pool = flow.Param('default', SiteJobsPoolNames)
    priority = flow.SessionParam(10).ui(editor='int')
    
    revision_name = flow.Param().ui(hidden=True)
    use_simplify = flow.Param().ui(hidden=True)
    
    def get_buttons(self):
        self.message.set('<h2>Submit playblast to pool</h2>')
        return ['Submit', 'Cancel']
    
    def allow_context(self, context):
        return False
    
    def _get_job_label(self):
        label = f'Render playblast - {self._file.display_name.get()}'
        
        settings = get_contextual_dict(self, 'settings')
        category = settings['file_category']
        
        if category == 'PROD':
            film = settings['film']
            seq = settings['sequence']
            shot = settings['shot']
            dept = settings['department']
            label += f' (from {film}/{seq}/{shot}/{dept})'
        elif category == 'LIB':
            type = settings['asset_type']
            family = settings['asset_family']
            asset = settings['asset_name']
            dept = settings['department']
            label += f' (from {type}/{family}/{asset}/{dept})'
        
        return label
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        job = self._file.jobs.create_job(job_type=PlayblastJob)
        job.revision.set(self.revision_name.get())
        job.use_simplify.set(self.use_simplify.get())
        site_name = self.root().project().get_current_site().name()        

        job.submit(
            pool=site_name + '_' + self.pool.get(),
            priority=self.priority.get(),
            label=self._get_job_label(),
            creator=self.root().project().get_user(),
            owner=self.root().project().get_user(),
            paused=False,
            show_console=False,
        )


class PublishAndRenderPlayblastAction(PublishFileAction):
    
    use_simplify = flow.SessionParam(False).ui(
        tooltip="Use low-definition rigs",
        editor='bool',
    )

    def allow_context(self, context):
        return (
            context
            and self._file.format.get() == "blend"
            and self._file.has_working_copy(from_current_user=True)
        )

    def run(self, button):
        if button == "Cancel":
            return self.get_result(next_action=self._file.render_playblast.oid())

        super(PublishAndRenderPlayblastAction, self).run(button)
        published_revision = self._file.get_head_revision()

        self._file.render_playblast.revision_name.set(published_revision.name())
        self._file.render_playblast.use_simplify.set(self.use_simplify.get())

        return self._file.render_playblast.run("Render")


class FileRevisionNameChoiceValue(flow.values.ChoiceValue):

    STRICT_CHOICES = False
    action = flow.Parent()

    def get_file(self):
        return self.action._file

    def choices(self):
        if self.get_file() is None:
            return []
        
        return self.get_file().get_revision_names(
            sync_status='Available',
            published_only=True
        )
    
    def revert_to_default(self):
        source_file = self.get_file()
        
        if not source_file:
            self.set(None)
            return
        
        revision = source_file.get_head_revision(sync_status="Available")
        self.set(revision.name() if revision else None)


class KitsuShotTaskType(flow.values.ChoiceValue):

    STRICT_CHOICES = False
    _file = flow.Parent(2)
    
    def choices(self):
        site = self.root().project().get_current_site()

        if site.is_kitsu_admin.get():
            # Return shot types if current site is 
            kitsu_api = self.root().project().kitsu_api()
            return kitsu_api.get_shot_task_types()
        else:
            kitsu_bindings = self.root().project().kitsu_bindings()
            choice = kitsu_bindings.get_task_type(
                self._file.display_name.get()
            )
            return [choice]

    def revert_to_default(self):
        kitsu_bindings = self.root().project().kitsu_bindings()
        default_value = kitsu_bindings.get_task_type(
            self._file.display_name.get()
        )
        self.set(default_value or '')


class UploadPlayblastToKitsu(flow.Action):
    
    ICON = ('icons.libreflow', 'kitsu')
    
    _file = flow.Parent()
    
    revision_name = flow.Param(None, FileRevisionNameChoiceValue)
    kitsu_settings = flow.Label('<h3>Kitsu settings</h3>').ui(icon=('icons.libreflow', 'kitsu'))
    current_task_status = flow.Computed()
    target_task_type = flow.Param(None, KitsuShotTaskType)
    target_task_status = flow.Param('Work In Progress', KitsuTaskStatus)
    comment = flow.SessionParam("").ui(editor='textarea')
    
    def __init__(self, parent, name):
        super(UploadPlayblastToKitsu, self).__init__(parent, name)
        self._kitsu_entity = None
    
    def _ensure_kitsu_entity(self):
        if self._kitsu_entity is None:
            kitsu_bindings = self.root().project().kitsu_bindings()
            file_settings = get_contextual_dict(self._file, 'settings')
            entity_data = kitsu_bindings.get_entity_data(file_settings)
            self._kitsu_entity = kitsu_bindings.get_kitsu_entity(entity_data)
        
        return self._kitsu_entity
    
    def allow_context(self, context):
        kitsu_config = self.root().project().admin.kitsu
        patterns = kitsu_config.uploadable_files.get().split(',')

        for pattern in patterns:
            pattern = pattern.replace(' ', '')
            if not fnmatch.fnmatch(self._file.display_name.get(), pattern):
                return False
        
        return not self._file.is_empty(on_current_site=True)
    
    def get_buttons(self):
        # Reset params to defaults
        self.revision_name.revert_to_default()
        self.target_task_type.revert_to_default()
        self.target_task_status.revert_to_default()
        
        # Check if the file is linked to a Kitsu entity
        task_type = self.target_task_type.get()
        kitsu_entity = self._ensure_kitsu_entity()
        
        msg = "<h2>Upload playblast to Kitsu</h2>"
        
        if kitsu_entity is None or task_type is None:
            msg += (
                "<h3><font color=#D5000D>The Kitsu entity %s belongs to "
                "couldn't be detected. Please contact the "
                "support on the chat.</font></h3>" % self._file.display_name.get()
            )
            self.message.set(msg)
            return ['Cancel']
        
        # Check if current user is assigned to a Kitsu task this file is made for
        kitsu_api = self.root().project().kitsu_api()
        user = kitsu_api.get_user()
        task = kitsu_api.get_task(kitsu_entity, task_type)
        
        if user is None:
            msg += (
                "<h3><font color=#D5000D>It seems you (%s) have no "
                "user profile on Kitsu. Please contact the "
                "support on the chat.</font></h3>" % self.root().project().get_user()
            )
            self.message.set(msg)
            return ['Cancel']
        
        if task is None:
            msg += (
                "<h3><font color=#D5000D>This file is not linked to any "
                "task on Kitsu.</font></h3>"
            )
            self.message.set(msg)
            return ['Cancel']
        
        # Check if user is assigned to the task or have sufficient rights
        is_assigned = kitsu_api.user_is_assigned(user, task)
        user_role = user.get('role', None)
        
        if not is_assigned:
            if not user_role in ['admin', 'manager']:
                msg += (
                    "<h3><font color=#D5000D>You (%s) are not assigned to "
                    "the task this file has been created for.</font></h3>"
                    % self.root().project().get_user()
                )
                self.message.set(msg)
                return ['Cancel']
            else:
                user_roles = {
                    'admin': 'studio manager',
                    'manager': 'supervisor'
                }
                msg += (
                    "<h3>As %s, you can upload a preview for this file.</h3>"
                    % user_roles[user_role]
                )

        self.message.set(msg)
        
        return ['Upload', 'Cancel']
    
    def compute_child_value(self, child_value):
        kitsu_entity = self._ensure_kitsu_entity()
        
        if kitsu_entity is None:
            child_value.set(None)
            return
        
        kitsu_api = self.root().project().kitsu_api()
        kitsu_bindings = self.root().project().kitsu_bindings()
        
        # if child_value is self.target_task_type:
        #     task_type = kitsu_bindings.get_task_type(
        #         self._file.display_name.get()
        #     )
        #     self.target_task_type.set(task_type)
        if child_value is self.current_task_status:
            task_status = kitsu_api.get_task_current_status(
                kitsu_entity,
                self.target_task_type.get()
            )
            self.current_task_status.set(task_status)
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        file_path = self._file.get_revision(self.revision_name.get()).get_path()
        kitsu_api = self.root().project().kitsu_api()
        
        kitsu_entity = self._ensure_kitsu_entity()
        
        if kitsu_entity is None:
            self.root().session().log_error('No Kitsu entity for file ' + self._file.oid())
            return self.get_result(close=False)
        
        success = kitsu_api.upload_preview(
            kitsu_entity=kitsu_entity,
            task_type_name=self.target_task_type.get(),
            task_status_name=self.target_task_status.get(),
            file_path=self._file.get_revision(self.revision_name.get()).get_path(),
            comment=self.comment.get(),
        )
        
        if not success:
            self.message.set((
                "<h2>Upload playblast to Kitsu</h2>"
                "<font color=#D5000D>An error occured "
                "while uploading the preview.</font>"
            ))
            return self.get_result(close=False)


class RenderWithAfterEffect(GenericRunAction):
    
    ICON = ('icons.libreflow', 'afterfx')

    target_revision_path = flow.Computed().ui(hidden=True)
    
    revision_name = flow.Param(None, FileRevisionNameChoiceValue).watched()
    
    with flow.group('Render options'):
        start_frame = flow.SessionParam(0).ui(editor='int')
        end_frame = flow.SessionParam(0).ui(editor='int')

    def get_buttons(self):
        return ["Render", "Cancel"]

    def runner_name_and_tags(self):
        return "AfterEffectsRender", []

    def get_run_label(self):
        return 'Render image sequence'

    @classmethod
    def supported_extensions(cls):
        return ["aep"]
    
    def allow_context(self, context):
        return (
            context
            and self._file.format.get() in self.supported_extensions()
        )


class WaitProcess(LaunchSessionWorker):
    '''
    Launch a `SessionWorker` which waits for the process identified
    by the ID `pid` to end. It is up to the user of this action to set
    the latter param before the action runs.
    
    Since a `SessionWorker` runs in its own session, params of this class
    and its subclasses must be stored in the DB in order to remain
    accessible to the underlying subprocess.
    '''
    pid = flow.IntParam()
    
    def allow_context(self, context):
        return False
    
    def launcher_oid(self):
        return self.oid()
    
    def launcher_exec_func_name(self):
        return 'wait'
    
    def wait(self):
        pid = self.pid.get()
        
        if pid is None:
            raise Exception('A process ID must be explicitly set in the pid param.')
        
        # os.waitpid(pid, 0)
        while psutil.pid_exists(pid):
            time.sleep(1.0)
        
        # Reset pid for the next calls to this method
        self.pid.set(None)
        self._do_after_process_ends()
    
    def _do_after_process_ends(self):
        '''
        Subclasses may redefine this method to perform a particular
        processing after the subprocess ending.
        '''
        pass


class ZipFolder(WaitProcess):
    
    folder_path = flow.Param()
    output_path = flow.Param()
    
    def allow_context(self, context):
        return False
    
    def get_run_label(self):
        return 'Zip rendered images'
    
    def _do_after_process_ends(self):
        folder_path = self.folder_path.get()
        output_path = self.output_path.get()
        
        if os.path.exists(folder_path):
            zip_folder(self.folder_path.get(), self.output_path.get())


class MarkSequenceAfterRender(WaitProcess):
    
    folder_oid = flow.Param()
    revision_name = flow.Param()
    
    site_name = flow.Param().ui(hidden=True)
    user_name = flow.Param().ui(hidden=True)
    
    def allow_context(self, context):
        return False
    
    def get_run_label(self):
        return 'Generate playblast'
    
    def _do_after_process_ends(self):
        folder = self.root().get_object(self.folder_oid.get())
        
        site_name = self.site_name.get()
        user_name = self.user_name.get()
        
        # Use the user and site of the current context if they have
        # not been set from elsewhere (e.g., another session)
        if site_name is None:
            site_name = self.root().project().get_current_site().name()
        if user_name is None:
            user_name = self.root().project().get_user()
        
        folder.submit_mark_sequence_job.revision_name.set(self.revision_name.get())
        folder.submit_mark_sequence_job.site_name.set(site_name)
        folder.submit_mark_sequence_job.user_name.set(user_name)
        folder.submit_mark_sequence_job.run('Submit job')
        
        self.site_name.revert_to_default()
        self.user_name.revert_to_default()


class RenderImageSequence(RenderWithAfterEffect):
    
    _files = flow.Parent(2)
    mark_sequence = flow.Child(MarkSequenceAfterRender)
    
    site_name = flow.Param().ui(hidden=True)
    user_name = flow.Param().ui(hidden=True)

    def get_buttons(self):
        self.revision_name.revert_to_default()
        buttons = ['Render', 'Cancel']

        if self._file.has_working_copy(from_current_user=True):
            buttons.insert(1, 'Publish first')
        
        current_site = self.root().project().get_current_site()
        if current_site.site_type.get() == 'Studio':
            buttons.insert(1, 'Submit job')
        
        return buttons

    def needs_dialog(self):
        return True

    def allow_context(self, context):
        return (
            super(RenderImageSequence, self).allow_context(context)
            and not self._file.is_empty()
        )

    def child_value_changed(self, child_value):
        if child_value is self.revision_name:
            msg = "<h2>Render image sequence</h2>"
            # Check if revision playblast exists
            revision_path = self._target_revision_path()
            
            if revision_path is not None and os.path.exists(revision_path):
                msg += (
                    "<font color=#D50000>"
                    "Choosing to render the image sequence of a revision "
                    "will override the existing one."
                    "</font>"
                )

            self.message.set(msg)
    
    def _target_revision_path(self):
        file_name = self._file.display_name.get().split('.')[0]
        
        if not self._files.has_mapped_name(file_name + '_render'):
            return None
        
        folder = self._files[file_name + '_render']
        
        if not folder.has_revision(self.revision_name.get()):
            return
        
        revision = folder.get_revision(self.revision_name.get())
        
        return revision.get_path()
    
    def _ensure_folder(self, name):
        if not self._files.has_mapped_name(name):
            self._files.create_folder.folder_name.set(name)
            self._files.create_folder.run(None)
        
        return self._files[name]
    
    def _ensure_revision(self, folder, revision_name):
        revisions = folder.get_revisions()
        
        if not folder.has_revision(revision_name):
            revision = revisions.add(revision_name)
        else:
            revision = revisions[revision_name]
        
        return revision

    def extra_argv(self):
        settings = get_contextual_dict(self._file, 'settings')
        sequence_name = settings['sequence']
        shot_name = settings['shot']
        revision = self._file.get_revision(self.revision_name.get())
        
        project_path = revision.get_path()
        comp_name = f'{sequence_name}_{shot_name}'
        output_name = comp_name + '.[####].exr'
        output_path = os.path.join(self._output_folder, output_name)
        
        argv = [
            '-project', project_path,
            '-comp', comp_name,
            '-RStemplate', 'siren_compo_render',
            '-OMtemplate', 'siren_compo_output',
            '-output', output_path
        ]
        
        if self.start_frame.get() != self.end_frame.get():
            argv += [
                '-s', self.start_frame.get(),
                '-e', self.end_frame.get()
            ]
        
        return argv

    def run(self, button):
        if button == "Cancel":
            return
        elif button == "Submit job":
            submit_action = self._file.submit_render_images_job
            submit_action.revision_name.set(self.revision_name.get())
            submit_action.start_frame.set(self.start_frame.get())
            submit_action.end_frame.set(self.end_frame.get())
            
            return self.get_result(next_action=submit_action.oid())
        
        site_name = self.site_name.get()
        user_name = self.user_name.get()
        
        # Use the user and site of the current context if they have
        # not been set from elsewhere (e.g., another session)
        if site_name is None:
            site_name = site_name
        if user_name is None:
            user_name = self.root().project().get_user()
        
        # Ensure render folder exists
        file_name = self._file.display_name.get().split('.')[0]
        folder = self._ensure_folder(file_name + '_render')
        
        # Create target revision
        revision_name = self.revision_name.get()
        source_revision = self._file.get_revision(revision_name)
        target_revision = self._ensure_revision(folder, revision_name)
        target_revision.comment.set(source_revision.comment.get())
        target_revision.set_sync_status('Available')
        folder.set_user_on_revision(user_name, revision_name)
        
        self._output_folder = target_revision.path.get().replace('\\', '/')
        
        # Ensure playblast revision folder exists and is empty
        if not os.path.exists(self._output_folder):
            os.makedirs(self._output_folder)
        else:
            remove_folder_content(self._output_folder)

        result = super(RenderImageSequence, self).run(button)
        self._files.touch()
        
        # Generate movie in post-rendering process
        runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(result['runner_id'])
        pid = runner_info['pid']
        
        self.mark_sequence.pid.set(pid)
        self.mark_sequence.folder_oid.set(folder.oid())
        self.mark_sequence.revision_name.set(revision_name)
        self.mark_sequence.site_name.set(site_name)
        self.mark_sequence.user_name.set(user_name)
        self.mark_sequence.run(None)
        
        return result


class RenderImageSequenceJob(FileJob):
    
    revision = flow.Param().ui(editable=False)
    start_frame = flow.Param().ui(editable=False)
    end_frame = flow.Param().ui(editable=False)
    
    site_name = flow.Param().ui(hidden=True)
    user_name = flow.Param().ui(hidden=True)

    def _do_job(self):
        # Job is to wait until the playblast is ended
        render_image_sequence = self._file.render_image_sequence
        render_image_sequence.revision_name.set(self.revision.get())
        render_image_sequence.start_frame.set(self.start_frame.get())
        render_image_sequence.end_frame.set(self.end_frame.get())
        render_image_sequence.site_name.set(self.site_name.get())
        render_image_sequence.user_name.set(self.user_name.get())
        
        result = render_image_sequence.run('Render')
        rid = result['runner_id']

        runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)

        while runner_info['is_running']:
            self.show_message("Waiting for runner %s to finish" % rid)
            time.sleep(1)
            
            runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)
        
        self.show_message("Runner %s finished !" % rid)


class SubmitRenderImageSequenceJob(flow.Action):
    
    _file = flow.Parent()
    
    pool = flow.Param('default', SiteJobsPoolNames)
    priority = flow.SessionParam(10).ui(editor='int')
    
    revision_name = flow.Param().ui(hidden=True)
    start_frame = flow.Param().ui(hidden=True)
    end_frame = flow.Param().ui(hidden=True)
    
    def get_buttons(self):
        self.message.set('<h2>Submit rendering to pool</h2>')
        return ['Submit', 'Cancel']
    
    def allow_context(self, context):
        return False
    
    def _get_job_label(self):
        label = f'Render image sequence - {self._file.display_name.get()}'
        
        settings = get_contextual_dict(self, 'settings')
        category = settings['file_category']
        
        if category == 'PROD':
            film = settings['film']
            seq = settings['sequence']
            shot = settings['shot']
            dept = settings['department']
            label += f' (from {film}/{seq}/{shot}/{dept})'
        elif category == 'LIB':
            type = settings['asset_type']
            family = settings['asset_family']
            asset = settings['asset_name']
            dept = settings['department']
            label += f' (from {type}/{family}/{asset}/{dept})'
        
        return label
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        site_name = self.root().project().get_current_site().name()
        user_name = self.root().project().get_user()
        
        job = self._file.jobs.create_job(job_type=RenderImageSequenceJob)
        job.revision.set(self.revision_name.get())
        job.start_frame.set(self.start_frame.get())
        job.end_frame.set(self.end_frame.get())
        job.site_name.set(site_name)
        job.user_name.set(user_name)

        job.submit(
            pool=site_name + '_' + self.pool.get(),
            priority=self.priority.get(),
            label=self._get_job_label(),
            creator=user_name,
            owner=user_name,
            paused=False,
            show_console=False,
        )


def list_digits(s, _nsre=re.compile('([0-9]+)')):
    '''
    List all digits contained in a string
    '''
    return [int(text) for text in _nsre.split(s) if text.isdigit()]


class MarkSequence(GenericRunAction):
    
    _file = flow.Parent()
    _files = flow.Parent(2)
    _departments = flow.Parent(4)
    
    revision_name = flow.Param(None, FileRevisionNameChoiceValue)
    
    def runner_name_and_tags(self):
        return 'MarkSequenceRunner', []
    
    def get_run_label(self):
        return 'Mark image sequence'
    
    def allow_context(self, context):
        return context and len(self._file.get_revision_names(sync_status='Available')) > 0
    
    def needs_dialog(self):
        return True
    
    def get_buttons(self):
        self.revision_name.revert_to_default()
        buttons = ['Render', 'Cancel']

        if self._file.has_working_copy(from_current_user=True):
            buttons.insert(1, 'Publish first')
        
        current_site = self.root().project().get_current_site()
        if current_site.site_type.get() == 'Studio':
            buttons.insert(1, 'Submit job')
        
        return buttons
    
    def _ensure_file(self, name, extension):
        mapped_name = '%s_%s' % (name, extension)
        
        if not self._files.has_mapped_name(mapped_name):
            self._files.create_file.file_name.set(name)
            self._files.create_file.file_format.set(extension)
            self._files.create_file.run(None)
        
        return self._files[mapped_name]
    
    def _ensure_revision(self, file, revision_name):
        revisions = file.get_revisions()
        
        if not file.has_revision(revision_name):
            revision = revisions.add(revision_name)
            revision.set_sync_status('Available')
            # revision.ready_for_sync.set(False)
            
            file.set_current_user_on_revision(revision_name)
        else:
            revision = revisions[revision_name]
        
        return revision
    
    def extra_argv(self):
        argv = super(MarkSequence, self).extra_argv()
        
        settings = get_contextual_dict(self, 'settings')
        category = settings['file_category']
        
        if category != 'PROD':
            return argv
        
        argv += [
            '-o', self._extra_argv['video_output'],
            '-t', resources.get('mark_sequence.fields', 'compositing.json'),
            '--project', settings['film'],
            '--sequence', list_digits(settings['sequence'])[0],
            '--scene', settings['shot'],
            '--version', self.revision_name.get(),
            '--studio', self.root().project().get_current_site().name(),
            '--file-name', self._extra_argv['file_name'],
            '--frame_rate', 24.0,
            self._extra_argv['image_path']
        ]
        
        audio_path = self._extra_argv['audio_file']
        if audio_path:
            argv += ['--audio-file', audio_path]
        
        return argv
    
    def _get_first_image_path(self, revision_name):
        revision = self._file.get_revision(revision_name)
        img_folder_path = revision.path.get()
        
        for f in os.listdir(img_folder_path):
            file_path = os.path.join(img_folder_path, f)
            file_type = mimetypes.guess_type(file_path)[0].split('/')[0]
            
            if file_type == 'image':
                return file_path
        
        return None
    
    def run(self, button):
        if button == 'Cancel':
            return
        elif button == 'Submit job':
            submit_action = self._file.submit_mark_sequence_job
            submit_action.revision_name.set(self.revision_name.get())
            
            return self.get_result(next_action=submit_action.oid())
        
        revision_name = self.revision_name.get()
        
        # Compute playblast prefix
        prefix = self._file.name()
        
        if prefix.endswith('_render'):
            prefix = prefix.replace('_render', '')
        
        playblast_file = self._ensure_file(prefix + '_movie', 'mov')
        target_revision = self._ensure_revision(playblast_file, revision_name)
        
        # Get the path of the first image in folder
        img_path = self._get_first_image_path(revision_name)
        
        # Get original file name to print on frames
        if self._files.has_mapped_name(prefix + '_aep'):
            scene = self._files[prefix + '_aep']
            file_name = scene.complete_name.get() + '.' + scene.format.get()
        else:
            file_name = self._file.complete_name.get()
        
        # Get audio file path
        audio_path = ''
        
        if self._departments.misc.files.has_mapped_name('audio_wav'):
            audio_file = self._departments.misc.files['audio_wav']
            head_revision = audio_file.get_head_revision()
            
            if head_revision is not None:
                audio_path = head_revision.get_path()
        
        self._extra_argv = {
            'image_path': img_path,
            'video_output': target_revision.get_path(),
            'file_name': file_name,
            'audio_file': audio_path
        }
        
        return super(MarkSequence, self).run(button)


class MarkSequenceJob(FileJob):
    
    revision = flow.Param().ui(editable=False)

    def _do_job(self):
        # Job is to wait until the playblast is ended
        mark_image_sequence = self._file.mark_image_sequence
        mark_image_sequence.revision_name.set(self.revision.get())
        
        result = mark_image_sequence.run('Mark images')
        rid = result['runner_id']

        runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)

        while runner_info['is_running']:
            self.show_message("Waiting for runner %s to finish" % rid)
            time.sleep(1)
            
            runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)
        
        self.show_message("Runner %s finished !" % rid)


class SubmitMarkSequenceJob(flow.Action):
    
    _file = flow.Parent()
    
    pool = flow.Param('default', SiteJobsPoolNames)
    priority = flow.SessionParam(10).ui(editor='int')
    
    revision_name = flow.Param().ui(hidden=True)
    
    site_name = flow.Param().ui(hidden=True)
    user_name = flow.Param().ui(hidden=True)
    
    def get_buttons(self):
        self.message.set('<h2>Submit image marking to pool</h2>')
        return ['Submit', 'Cancel']
    
    def allow_context(self, context):
        return False
    
    def _get_job_label(self):
        label = 'Generate playblast - ' + self._file.display_name.get()
        
        settings = get_contextual_dict(self, 'settings')
        category = settings['file_category']
        
        if category == 'PROD':
            film = settings['film']
            seq = settings['sequence']
            shot = settings['shot']
            dept = settings['department']
            label += f' ({film}/{seq}/{shot}/{dept})'
        elif category == 'LIB':
            type = settings['asset_type']
            family = settings['asset_family']
            asset = settings['asset_name']
            dept = settings['department']
            label += f' ({type}/{family}/{asset}/{dept})'
        
        return label
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        job = self._file.jobs.create_job(job_type=MarkSequenceJob)
        job.revision.set(self.revision_name.get())

        site_name = self.site_name.get()
        user_name = self.user_name.get()
        
        # Use the user and site of the current context if they have
        # not been set from elsewhere (e.g., another session)
        if site_name is None:
            site_name = self.root().project().get_current_site().name()
        if user_name is None:
            user_name = self.root().project().get_user()

        job.submit(
            pool=site_name + '_' + self.pool.get(),
            priority=self.priority.get(),
            label=self._get_job_label(),
            creator=user_name,
            owner=user_name,
            paused=False,
            show_console=False,
        )
        
        # Reset param values
        self.site_name.revert_to_default()
        self.user_name.revert_to_default()


class RequestTrackedFileAction(flow.Action):

    _file = flow.Parent()
    _files = flow.Parent(2)

    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return False
    
    def run(self, button):
        head = self._file.get_head_revision()
        exchange_site_name = self.root().project().get_exchange_site().name()

        if not head or head.get_sync_status() != "NotAvailable" or head.get_sync_status(site_name=exchange_site_name) != "Available":
            return
        
        head.request.sites.target_site.set(
            self.root().project().get_current_site().name()
        )
        head.request.run(None)
        self._files.touch()


class TrackedFile(File):

    ICON = ("icons.gui", "text-file-1")

    _map = flow.Parent()
    _department = flow.Parent(2)
    _locked_by = flow.Param("")

    complete_name = flow.Param("").ui(editable=False)
    state = flow.Computed()

    history = flow.Child(History)
    current_revision = flow.Param("").ui(editable=False)

    active_users = flow.Child(ActiveUsers)
    current_user_sees = flow.Computed()

    jobs = flow.Child(FileJobs)

    show_history = flow.Child(GotoHistory)
    publish_action = flow.Child(PublishFileAction).injectable().ui(label="Publish")
    create_working_copy_action = flow.Child(CreateWorkingCopyAction).ui(
        label="Create working copy"
    )
    open = flow.Child(OpenTrackedFileAction)
    see_revision = flow.Child(SeeRevisionAction).ui(label="See revision...")
    reveal = flow.Child(RevealInExplorer).ui(label="Reveal in explorer")
    make_current_action = flow.Child(MakeFileCurrentAction).ui(
        label="Set last as current"
    )
    lock_action = flow.Child(LockAction).ui(label="Lock")
    unlock_action = flow.Child(UnlockAction).ui(label="Unlock")
    search_existing_revisions = flow.Child(SearchExistingRevisions)
    request = flow.Child(RequestTrackedFileAction)
    upload_playblast = flow.Child(UploadPlayblastToKitsu).ui(
        label="Upload to Kitsu"
    )

    with flow.group("Open with"):
        open_with_blender = flow.Child(OpenWithBlenderAction).ui(label="Blender")
        open_with_krita = flow.Child(OpenWithKritaAction).ui(label="Krita")
        open_with_vscodium = flow.Child(OpenWithVSCodiumAction).ui(label="VSCodium")
        open_with_notepadpp = flow.Child(OpenWithNotepadPPAction).ui(label="Notepad++")

    with flow.group("Advanced"):
        create_working_copy_from_file = flow.Child(None).ui(label="Create working copy from another file")
        publish_into_file = flow.Child(None).ui(label="Publish to another file")
        render_image_sequence = flow.Child(RenderImageSequence)
        submit_render_images_job = flow.Child(SubmitRenderImageSequenceJob)
    
    with flow.group("Advanced/Playblast"):
        render_playblast = flow.Child(RenderBlenderPlayblastAction)
        submit_playblast_job = flow.Child(SubmitBlenderPlayblastJob)
        publish_and_render_playblast = flow.Child(PublishAndRenderPlayblastAction)

    def get_name(self):
        return "%s_%s" % (self.complete_name.get(), self.format.get())

    def is_locked(self, by_current_user=False):
        if by_current_user:
            return self.locked_by() == self.root().project().get_user()

        return bool(self._locked_by.get())

    def locked_by(self):
        return self._locked_by.get()

    def lock(self):
        current_user = self.root().project().get_user()
        self._locked_by.set(current_user)

    def unlock(self):
        self._locked_by.set("")

    def has_working_copy(self, from_current_user=False):
        if from_current_user:
            user = self.root().project().get_user()
            return user in self.get_revisions().mapped_names()

        for revision in self.get_revisions().mapped_items():
            if revision.is_working_copy():
                return True

        return False

    def set_current_user_on_revision(self, revision_name):
        current_user = self.root().project().get_user()
        self.set_user_on_revision(current_user, revision_name)

    def set_user_on_revision(self, user_name, revision_name):
        if self.has_active_user(user_name):
            active_user = self.active_users[user_name]
        else:
            active_user = self.active_users.add(user_name)

        active_user.set(revision_name)
        self.get_revisions().touch()

    def remove_active_user(self, user_name):
        self.active_users.remove(user_name)

    def has_active_user(self, user_name):
        return user_name in self.active_users.mapped_names()

    def get_seen_revision(self):
        name = self.current_user_sees.get()

        if name == "current":
            if self.has_current_revision():
                return self.get_current_revision()
            else:
                return None
        else:
            return self.get_revision(name)

    def has_current_revision(self):
        return bool(self.current_revision.get())

    def get_revision(self, name):
        return self.history.revisions[name]

    def get_revisions(self):
        return self.history.revisions
    
    def get_working_copies(self, sync_status=None):
        working_copies = []
        
        for r in self.get_revisions().mapped_items():
            if not r.is_working_copy() or r.is_working_copy(from_current_user=True):
                continue
            
            if sync_status is None or r.get_sync_status() == sync_status:
                working_copies.append(r)
        
        return working_copies
    
    def get_revision_names(self, sync_status=None, published_only=False):
        if sync_status is None and not published_only:
            return self.get_revisions().mapped_names()

        revisions = self.get_revisions().mapped_items()

        if published_only:
            revisions = filter(lambda r: not r.is_working_copy(), revisions)

        if sync_status is not None:
            revisions = filter(lambda r: r.get_sync_status() == sync_status, revisions)
        
        return [r.name() for r in revisions]
    
    def get_revision_statuses(self, published_only=False):
        revisions = self.get_revisions().mapped_items()
        
        if published_only:
            revisions = filter(lambda r: not r.is_working_copy(), revisions)
        
        return [(r.name(), r.get_sync_status()) for r in revisions]

    def has_revision(self, name, sync_status=None):
        exists = (name in self.history.revisions.mapped_names())

        if exists and sync_status:
            exists = exists and (self.history.revisions[name].get_sync_status() == sync_status)
        
        return exists

    def is_empty(self, on_current_site=True):
        revisions = self.get_revisions()
        
        if not on_current_site:
            return not bool(revisions.mapped_names())
        
        for r in revisions.mapped_items():
            if r.get_sync_status() == 'Available':
                return False
        
        return True

    def get_last_edit_time(self):
        seen_name = self.current_user_sees.get()
        current = self.get_current_revision()

        if seen_name == "current":
            if current is None:
                if os.path.exists(self.get_path()):
                    return os.path.getmtime(self.get_path())
                else:
                    return 0
            else:
                return current.get_last_edit_time()
        else:
            seen = self.get_revision(seen_name)
            return seen.get_last_edit_time()

    def get_last_comment(self):
        seen_name = self.current_user_sees.get()
        current = self.get_current_revision()

        if seen_name == "current":
            if current is None:
                return "NO PUBLISH YET"
            else:
                return current.comment.get()
        else:
            seen = self.get_revision(seen_name)

            if seen.is_working_copy():
                return "WORKING COPY (%s)" % seen.user.get()
            else:
                return seen.comment.get()

    def create_working_copy(self, reference_name=None, source_path=None, user_name=None):
        if user_name is None:
            user_name = self.root().project().get_user()

        revisions = self.get_revisions()

        # Overwrite current working copy
        try:
            working_copy = revisions[user_name]
        except flow.exceptions.MappedNameError:
            # No working copy, will be created below
            pass
        else:
            try:
                shutil.rmtree(working_copy.path.get())
            except FileNotFoundError:
                self.root().session().log_warning(
                    "File '{}' no longer exists".format(working_copy.path.get())
                )

            revisions.remove(user_name)

        working_copy = revisions.add(user_name, ready_for_sync=False)
        working_copy.set_sync_status("Available")

        try:
            os.makedirs(working_copy.path.get())
        except OSError:
            self.root().session().log_error(
                "Creation of working copy folder '%s' failed\n\n==> TRACEBACK\n"
                % working_copy.path.get()
            )
            raise

        working_copy_path = working_copy.get_path()

        # If source path is given, ignore reference revision
        if not source_path:
            if reference_name is None:
                # Create working copy from scratch
                source_path = self.get_template_path()
                self.root().session().log_debug(
                    "Copy template {} to {}".format(source_path, working_copy_path)
                )
            else:
                reference = self.get_revision(reference_name)
                source_path = reference.get_path()

                self.root().session().log_debug(
                    "Copy current revision {} to {}".format(
                        source_path, working_copy_path
                    )
                )

        try:
            shutil.copy2(source_path, working_copy_path)
        except OSError:
            self.root().session().log_error(
                "Copy of source file '{}' failed\n\n==> TRACEBACK\n".format(source_path)
            )
            raise

        return working_copy

    def publish(self, revision_name=None, source_path=None, comment="", keep_editing=False, ready_for_sync=True):
        revisions = self.get_revisions()
        head_revision = revisions.add(revision_name, ready_for_sync=ready_for_sync)
        head_revision.comment.set(comment)
        head_revision_path = head_revision.get_path()
        head_revision.set_sync_status("Available")

        self.root().session().log_debug(
            "Create head revision folder {}".format(head_revision.path.get())
        )

        try:
            os.makedirs(head_revision.path.get())
        except OSError:
            self.root().session().log_error(
                "Creation of head revision folder '{}' failed\n\n==> TRACEBACK\n".format(
                    head_revision.path.get()
                )
            )
            raise

        # If source path is given, ignore working copy
        if source_path:
            shutil.copy2(source_path, head_revision_path)
        else:
            working_copy = self.get_working_copy()
            working_copy_path = working_copy.get_path()

            if keep_editing:
                self.root().session().log_debug(
                    "Copy working copy {} to {}".format(
                        working_copy_path, head_revision_path
                    )
                )

                shutil.copy2(working_copy_path, head_revision_path)
            else:
                self.root().session().log_debug(
                    "Copy working copy {} to {}".format(
                        working_copy_path, head_revision_path
                    )
                )
                self.root().session().log_debug(
                    "Remove working copy folder {}".format(working_copy.path.get())
                )

                shutil.move(working_copy_path, head_revision_path)
                shutil.rmtree(working_copy.path.get())

                revisions.remove(working_copy.name())

        revisions.touch()

        # Compute published revision hash
        head_revision.compute_hash_action.run(None)

        return head_revision

    def make_current(self, revision):
        revision_path = os.path.join(revision.path.get(), revision.file_name.get())
        current_path, current_name = self.get_current_revision_params()
        current_revision_path = os.path.join(current_path, current_name)

        if not os.path.exists(current_path):
            os.makedirs(current_path)

        try:
            # TODO: make it work
            self.root().session().log_debug(
                "Create symlink {} pointing to {}".format(
                    revision.path.get(), current_path
                )
            )
            os.symlink(revision.path.get(), current_path, target_is_directory=True)
        except OSError:
            self.root().session().log_warning("Symbolic link privilege not held...")

            try:
                self.root().session().log_debug(
                    "Copy working copy {} to {}".format(
                        revision_path, current_revision_path
                    )
                )
                shutil.copy2(revision_path, current_revision_path)
            except OSError:
                self.root().session().log_error(
                    "Copy of head revision '{}' to current failed".format(
                        revision_path
                    )
                )
                raise

        self.current_revision.set(revision.name())
        self.get_revisions().touch()

    def get_working_copy(self, user_name=None):
        if user_name is None:
            user_name = self.root().project().get_user()
        try:
            return self.get_revision(user_name)
        except flow.exceptions.MappedNameError:
            return None

    def get_head_revision(self, sync_status=None):
        revisions = self.get_revisions()

        for revision in reversed(revisions.mapped_items()):
            if not revision.is_working_copy() and (not sync_status or revision.get_sync_status() == sync_status):
                return revision

        return None

    def get_current_revision(self):
        try:
            return self.get_revision(self.current_revision.get())
        except flow.exceptions.MappedNameError:
            return None

    def get_current_revision_params(self):
        revision_path = os.path.join(self.get_path(), "current")
        revision_name = "%s_current.%s" % (self.complete_name.get(), self.format.get())

        return revision_path, revision_name

    def compute_child_value(self, child_value):
        current_user = self.root().project().get_user()

        if child_value is self.current_user_sees:
            try:
                child_value.set(self.active_users[current_user].get())
            except flow.exceptions.MappedNameError:
                child_value.set("current")

        elif child_value is self.state:
            seen_name = self.current_user_sees.get()

            if seen_name == "current":
                if self.has_current_revision():
                    if self.get_head_revision().is_current():
                        child_value.set("<o>")
                    else:
                        child_value.set("o>")
                else:
                    if self.has_working_copy():
                        child_value.set("-o")
                    else:
                        child_value.set("--")
            else:
                seen = self.get_revision(seen_name)
                head = self.get_head_revision()
                current = self.get_current_revision()

                # Consider by default we're on our working copy more recent than the current
                child_value.set(">")

                if seen.is_working_copy(from_current_user=True):
                    if (
                        head is not None
                        and seen.get_last_edit_time() < head.get_last_edit_time()
                    ):
                        child_value.set("< !")
                    elif (
                        current is not None
                        and seen.get_last_edit_time() == current.get_last_edit_time()
                    ):
                        child_value.set("=")
                else:  # Read-only revision
                    if seen.is_working_copy():
                        # Seen working copy more recent than head by default
                        child_value.set("<o %s" % seen.name())

                        if head is None:
                            if seen.get_last_edit_time() < head.get_last_edit_time():
                                child_value.set("o> %s" % seen.name())
                            elif seen.get_last_edit_time() == head.get_last_edit_time():
                                child_value.set("<o> %s" % seen.name())
                    else:
                        child_value.set(
                            "<o %s" % seen.name()
                        )  # Seen publication more recent than current by default

                        if head is not None and current is not None:
                            if seen.get_last_edit_time() < head.get_last_edit_time():
                                child_value.set("o> %s" % seen.name())
                            elif (
                                seen.get_last_edit_time()
                                == current.get_last_edit_time()
                                and seen.get_last_edit_time()
                                == head.get_last_edit_time()
                            ):
                                child_value.set("<o> %s" % seen.name())
        else:
            super(TrackedFile, self).compute_child_value(child_value)


class FileRefRevisionNameChoiceValue(FileRevisionNameChoiceValue):

    def get_file(self):
        return self.action.source_file.get()


class ResetRef(flow.Action):

    _ref = flow.Parent()

    def allow_context(self, context):
        return context and context.endswith(".inline")
    
    def needs_dialog(self):
        return False
    
    def run(self, button):
        self._ref.set(None)
        return self.get_result(refresh=True)


class ResetableTrackedFileRef(flow.values.Ref):

    SOURCE_TYPE = TrackedFile
    reset = flow.Child(ResetRef)


class PublishIntoFile(PublishFileAction):

    source_file = flow.SessionParam("").ui(
        editable=False,
        tooltip="File to publish to.",
    )
    source_revision_name = flow.Param(None, FileRevisionNameChoiceValue).watched().ui(
        label="Source revision"
    )
    target_file = flow.Connection(ref_type=ResetableTrackedFileRef).watched()
    revision_name = flow.Param("").watched()
    comment = flow.Param("")
    keep_editing = flow.SessionParam(True).ui(hidden=True)
    upload_after_publish = flow.BoolParam(False)

    def get_buttons(self):
        self.message.set("<h2>Publish from an existing file</h2>")
        self.target_file.set(None)
        self.source_file.set(self._file.display_name.get())
        self.source_revision_name.revert_to_default()

        return ["Publish", "Cancel"]

    def allow_context(self, context):
        return None

    def check_file(self, file):
        expected_format = self._file.format.get()
        msg = "<h2>Publish from an existing file</h2>"
        error_msg = ""

        if not file:
            error_msg = "A target file must be set."
        elif file.format.get() != expected_format:
            error_msg = f"Target file must be in {expected_format} format."
        elif not self.source_revision_name.choices():
            error_msg = f"Target file has no revision available on current site."
        
        if error_msg:
            self.message.set(
                f"{msg}<font color=#D5000D>{error_msg}</font>"
            )
            return False
        
        # Check if other users are editing the target file
        working_copies = file.get_working_copies()
        if working_copies:
            user_names = [wc.user.get() for wc in working_copies]
            user_names = ["<b>"+n+"</b>" for n in user_names]
            msg += (
                "<h3><font color=#D66500><br>"
                "Target file <b>%s</b> is actually edited by one or more users (%s)."
                "</font></h3>"
                % (file.display_name.get(), ', '.join(user_names))
            )
        
        self.message.set(msg)
        return True
    
    def check_revision_name(self, name):
        msg = self.message.get()
        target_file = self.target_file.get()

        if not self.check_file(target_file):
            return False

        if target_file.has_revision(name):
            msg += (
                "<font color=#D5000D>"
                f"Target file already has a revision {name}."
                "</font>"
            )
            self.message.set(msg)

            return False
        
        self.message.set(msg)
        return True
    
    def _target_file(self):
        return self.target_file.get()
    
    def _revision_to_process(self):
        revision_name = self.revision_name.get()
        if not revision_name:
            revision_name = self.source_revision_name.get()

        return self._target_file().get_revision(revision_name)

    def child_value_changed(self, child_value):
        self.message.set("<h2>Publish from an existing file</h2>")

        if child_value is self.target_file:
            self.check_file(self.target_file.get())
            self.check_revision_name(self.source_revision_name.get())
        elif child_value is self.source_revision_name:
            value = self.source_revision_name.get()
            self.revision_name.set(value)
            self.comment.set("Created from %s (%s)" % (
                self._file.display_name.get(),
                value,
            ))
        elif child_value is self.revision_name:
            revision_name = self.revision_name.get()
            self.check_revision_name(revision_name)

    def run(self, button):
        if button == "Cancel":
            return

        target_file = self.target_file.get()

        # Check source file
        if not self.check_file(target_file):
            return self.get_result(close=False)
        
        revision_name = self.revision_name.get()
        if not revision_name:
            revision_name = self.source_revision_name.get()
        
        # Check choosen revision name
        if not self.check_revision_name(revision_name):
            return self.get_result(close=False)
        
        source_revision_name = self.source_revision_name.get()
        source_revision = self._file.get_revision(source_revision_name)
        
        # Publish in target file
        target_file.lock()

        publication = target_file.publish(
            revision_name=revision_name,
            source_path=source_revision.get_path(),
            comment=self.comment.get(),
        )
        target_file.make_current(publication)
        target_file.unlock()
        target_file._map.touch()

        if self.upload_after_publish.get():
            super(PublishFileAction, self).run(None)


class CreateWorkingCopyFromFile(CreateWorkingCopyBaseAction):

    _file = flow.Parent()
    source_file = flow.Connection(ref_type=ResetableTrackedFileRef).watched()
    source_revision_name = flow.Param(None, FileRefRevisionNameChoiceValue).ui(
        label="Source revision"
    )
    target_file = flow.SessionParam("").ui(
        editable=False,
        tooltip="File in which the working copy will be created.",
    )

    def get_buttons(self):
        msg = "<h2>Create working copy from another file</h2>"
        self.source_file.set(None)
        self.target_file.set(self._file.display_name.get())

        if self._file.has_working_copy(from_current_user=True):
            msg += (
                "<font color=#D66700>"
                "You already have a working copy on %s. "
                "Creating a working copy will overwrite the current one."
                "</font><br>" % self._file.display_name.get()
            )
        else:
            msg += "<br>"
        
        self.message.set(msg)

        return ["Create", "Cancel"]
    
    def child_value_changed(self, child_value):
        if child_value is self.source_file:
            self.check_file(self.source_file.get())

            self.source_revision_name.touch()
            self.source_revision_name.revert_to_default()

    def check_file(self, file):
        expected_format = self._file.format.get()
        msg = "<h2>Create working copy from another file</h2>"
        error_msg = ""

        if self._file.has_working_copy(from_current_user=True):
            msg += (
                "<font color=#D66700>"
                "You already have a working copy on %s. "
                "Creating a working copy will overwrite the current one."
                "</font><br>" % self._file.display_name.get()
            )
        else:
            msg += "<br>"

        if not file:
            error_msg = "A source file must be set."
        elif file.format.get() != expected_format:
            error_msg = f"Source file must be in {expected_format} format."
        elif not self.source_revision_name.choices():
            error_msg = f"Source file has no revision available on current site."
        
        if error_msg:
            self.message.set(
                f"{msg}<font color=#D5000D>{error_msg}</font>"
            )
            return False

        self.message.set(msg + "<br><br>")
        
        return True
    
    def run(self, button):
        if button == "Cancel":
            return

        source_file = self.source_file.get()

        if not self.check_file(source_file):
            return self.get_result(close=False)
        
        source_revision = source_file.get_revision(self.source_revision_name.get())
        working_copy = self._file.create_working_copy(source_path=source_revision.get_path())

        self._file.set_current_user_on_revision(working_copy.name())
        self._file.touch()
        self._file.get_revisions().touch()


TrackedFile.create_working_copy_from_file.set_related_type(CreateWorkingCopyFromFile)
TrackedFile.publish_into_file.set_related_type(PublishIntoFile)


class ClearFileSystemMapAction(ClearMapAction):
    def run(self, button):
        for item in self._map.mapped_items():
            if hasattr(item, "state") and hasattr(item, "current_user_sees"):
                item.get_revisions().clear()
                item.current_revision.set("")
                item.active_users.clear()

        super(ClearFileSystemMapAction, self).run(button)


class CreateFileSystemItemAction(SimpleCreateAction):
    def get_buttons(self):
        self.message.set("<h2>Create %s</h2>" % self.item_type().__name__.lower())

        return ["Create", "Cancel"]

    @classmethod
    def item_type(cls):
        return FileSystemItem

    def _add_item(self, name):
        raise NotImplementedError(
            "Needs to be implemented by calling the proper add method in the FileSystemMap"
        )

    def run(self, button):
        if button == "Cancel":
            return

        if self.entity_name.get() == "":
            msg = self.message.get()
            msg += (
                "<font color=#D5000D>%s name must be not empty.</font>"
                % self.item_type().__name__
            )
            self.message.set(msg)

            return self.get_result(close=False)

        self._add_item(self.entity_name.get())
        self._map.touch()


class Folder(FileSystemItem):

    _department = flow.Parent(2)
    open = flow.Child(RevealInExplorer)


class OpenTrackedFolderRevision(RevealInExplorer):

    _revision = flow.Parent()

    def extra_argv(self):
        return [os.path.normpath(self._revision.path.get())]


class TrackedFolderRevision(Revision):

    open = flow.Child(OpenTrackedFolderRevision)
    
    def get_last_edit_time(self):
        if self.exists():
            return os.path.getmtime(self.path.get())
        
        return 0
    
    def exists(self):
        return os.path.exists(self.path.get())
    
    def compute_hash(self):
        return hash_folder(self.path.get())


class TrackedFolderRevisions(Revisions):

    @classmethod
    def mapped_type(cls):
        return TrackedFolderRevision


class TrackedFolderHistory(flow.Object):

    revisions = flow.Child(TrackedFolderRevisions)


class OpenTrackedFolderAction(RevealInExplorer):

    _folder = flow.Parent()
    
    def get_buttons(self):
        self.message.set("You aren't seeing any revision...")
        return ["See a revision", "Create a working copy", "Cancel"]

    def needs_dialog(self):
        seen_revision = self._folder.get_seen_revision()
        return (
            not seen_revision
            or not os.path.exists(seen_revision.path.get())
        )
    
    def run(self, button):
        if button == "Cancel":
            return
        elif button == "See a revision":
            return self.get_result(next_action=self._folder.see_revision)
        elif button == "Create a working copy":
            return self.get_result(next_action=self._folder.create_working_copy_action)
        
        # Else open seen revision
        self._folder.get_seen_revision().open.run(None)


class FolderAvailableRevisionName(FileRevisionNameChoiceValue):

    action = flow.Parent()

    def get_file(self):
        return self.action._folder


class ResizeTrackedFolderImages(RunAction):
    '''
    Computes half-resized versions of all PNG images contained in a source tracked folder
    in another tracked folder suffixed with `_half`.
    '''
    _folder = flow.Parent()
    _files = flow.Parent(2)
    revision_name = flow.Param(None, FolderAvailableRevisionName).watched()
    publish_comment = flow.SessionParam("")

    def runner_name_and_tags(self):
        return 'ImageMagick', []
    
    def get_run_label(self):
        return 'Resize images'
    
    def extra_argv(self):
        in_pattern = '{}/*.png[{}]'.format(self._source_folder_path, self._resize_format)
        out_pattern = '{}/%[filename:base].png'.format(self._target_folder_path)
        return ['convert', in_pattern, '-set', 'filename:base', '%[basename]', out_pattern]
    
    def get_buttons(self):
        self.message.set((
            "<h2>Resize images in {0}</h2>"
            "Every PNG image included in this folder will have a resized version placed in the <b>{0}_half</b> folder.".format(
                self._folder.name()
            )
        ))
        self.revision_name.revert_to_default()

        return ['Resize images', 'Cancel']
    
    def child_value_changed(self, child_value):
        if child_value is self.revision_name:
            self.publish_comment.set(
                "Half-resized images from %s folder" % self._folder.name()
            )
    
    def _get_image_dimensions(self, img_path):
        exec_path = self.root().project().admin.user_environment['IMAGEMAGICK_EXEC_PATH'].get()
        
        dims = subprocess.check_output([exec_path, 'convert', img_path, '-format', '%wx%h', 'info:'])
        dims = dims.decode('UTF-8').split('x')

        return tuple(map(int, dims))
    
    def run(self, button):
        if button == 'Cancel':
            return

        # Setup target folder
        target_folder_name = self._folder.name() + '_half'
        
        if not self._files.has_mapped_name(target_folder_name):
            self._files.create_folder.folder_name.set(target_folder_name)
            self._files.create_folder.run(None)
        
        target_folder = self._files[target_folder_name]
        publication = target_folder.publish(
            revision_name=self.revision_name.get(),
            source_path=self._folder.get_revision(self.revision_name.get()).path.get(),
            comment=self.publish_comment.get()
        )

        # Cache source and target folder paths
        self._source_folder_path = self._folder.get_revision(self.revision_name.get()).path.get()
        self._target_folder_path = publication.path.get()
        
        # Get dimensions of the first image
        image_paths = glob.glob("%s/*.png" % self._source_folder_path)
        width, height = self._get_image_dimensions(image_paths[0])

        # Cache dimensions
        if height > width:
            self._resize_format = "x%s" % min(int(0.5 * height), 3840)
        else:
            self._resize_format = "%sx" % min(int(0.5 * width), 3840)
        
        super(ResizeTrackedFolderImages, self).run(button)

        self._files.touch()


class TrackedFolder(TrackedFile):

    open = flow.Child(OpenTrackedFolderAction)
    history = flow.Child(TrackedFolderHistory)
    resize_images = flow.Child(ResizeTrackedFolderImages).ui(group='Advanced')
    mark_image_sequence = flow.Child(MarkSequence).ui(group='Advanced')
    submit_mark_sequence_job = flow.Child(SubmitMarkSequenceJob).ui(group='Advanced', hidden=True)
    
    def get_name(self):
        return self.complete_name.get()
    
    def create_working_copy(self, reference_name=None, user_name=None):
        if user_name is None:
            user_name = self.root().project().get_user()

        revisions = self.get_revisions()
        working_copy = self.get_working_copy()

        # TODO: Remove working copy more intelligently
        if working_copy is not None and working_copy.exists():
            shutil.rmtree(working_copy.path.get())
            working_copy.set_sync_status('NotAvailable')
        
        if working_copy is not None:            
            # Update working copy params
            working_copy.user.set(self.root().project().get_user())
            working_copy.site.set(self.root().project().get_current_site().name())
            working_copy.date.set(time.time())
            working_copy.ready_for_sync.set(False)
        else:
            working_copy = revisions.add(user_name, ready_for_sync=False)

        if reference_name is None:
            # Create an empty working copy folder
            os.makedirs(working_copy.path.get())
        else:
            # Copy files from reference revision folder into working copy folder
            reference_revision = self.get_revision(reference_name)
            
            if reference_revision is None:
                self.root().session().log_warning((
                    f'TrackedFolder {self.oid()}:\n'
                    f'Couldn\'t find reference revision {reference_name} to create a working copy. '
                    'The created working copy will be empty.'
                ))
                os.makedirs(working_copy.path.get())
            else:
                try:
                    shutil.copytree(reference_revision.path.get(), working_copy.path.get())
                except FileNotFoundError:
                    self.root().session().log_error((
                        f'TrackedFolder {self.oid()}:\n'
                        f'Couldn\'t find reference revision {reference_name} folder ({reference_revision.path.get()}). '
                        'The created working copy will be empty.'
                    ))

        # Update sync status when disk operations are done
        working_copy.set_sync_status('Available')

        return working_copy

    def publish(self, revision_name=None, source_path=None, comment="", keep_editing=False, ready_for_sync=True):
        revisions = self.get_revisions()
        head_revision = revisions.add(revision_name, ready_for_sync=ready_for_sync)
        head_revision.comment.set(comment)

        if source_path:
            try:
                shutil.copytree(source_path, head_revision.path.get())
            except shutil.Error:
                self.root().session().log_error((
                    f'TrackedFolder {self.oid()}:\n'
                    f'Invalid source path {source_path} used to publish'
                ))
        else:
            working_copy = self.get_working_copy()
            
            if working_copy is None:
                user_name = self.root().project().get_user()
                self.root().session().log_error((
                    f'TrackedFolder {self.oid()}:\n'
                    f'Cannot publish a file with no working copy from the current user {user_name}'
                ))
                return None
            
            # Copy/move working copy files to head revision
            if keep_editing:
                shutil.copytree(working_copy.path.get(), head_revision.path.get())
            else:
                shutil.move(working_copy.path.get(), head_revision.path.get())
                revisions.remove(working_copy.name())

        # Compute published revision hash
        head_revision.compute_hash_action.run(None)
        
        # Update sync status when disk operations are done
        head_revision.set_sync_status('Available')
        revisions.touch()

        return head_revision

    def make_current(self, revision):
        current_revision_path = os.path.join(self.get_path(), 'current')

        if os.path.exists(current_revision_path):
            shutil.rmtree(current_revision_path)
        
        try:
            shutil.copytree(revision.path.get(), current_revision_path)
        except:
            self.root().session().log_error((
                f'TrackedFolder {self.oid()}:\n'
                f'Failed to define revision {revision.name()} as current'
            ))
            return

        self.current_revision.set(revision.name())
        self.get_revisions().touch()

    def compute_child_value(self, child_value):
        if child_value is self.display_name:
            child_value.set(self.name())
        else:
            TrackedFile.compute_child_value(self, child_value)


mapping = {r.name: r.index for r in TrackedFile._relations}
for relation in TrackedFolder._relations:
    if relation.name in ["open", "history"]:
        relation.index = mapping.get(relation.name)


class CreateFileAction(CreateFileSystemItemAction):

    format = flow.Param("blend", FileFormat)

    @classmethod
    def item_type(cls):
        return File

    def _add_item(self, name):
        return self._map.add_file(name, self.format.get())


class CreateFolderAction(CreateFileSystemItemAction):
    @classmethod
    def item_type(cls):
        return Folder

    def _add_item(self, name):
        return self._map.add_folder(name)


class CreateTrackedFolderAction(flow.Action):

    ICON = ("icons.gui", "plus-sign-in-a-black-circle")

    _files = flow.Parent()

    folder_name = flow.Param("")

    def get_buttons(self):
        self.message.set("<h3>Create folder</h3>")
        return ["Create", "Cancel"]

    def run(self, button):
        if button == "Cancel":
            return

        settings = get_contextual_dict(self, "settings")
        file_category = settings.get("file_category", None)

        name = self.folder_name.get()
        prefix = ""

        if file_category is not None:
            if file_category == "PROD":
                prefix = "{file_category}_{sequence}_{shot}_{department}_"
            elif file_category == "LIB":
                prefix = "{file_category}_{asset_name}_{department}_"

            prefix = prefix.format(**settings)

        self.root().session().log_debug(
            "Creating folder %s" % name
        )

        self._files.add_tracked_folder(name, prefix + name)
        self._files.touch()


class FileInfos(flow.Object):

    action = flow.Parent(2).ui(label="files")

    path = flow.SessionParam("")
    basename = flow.SessionParam("")
    type = flow.SessionParam("")
    extension = flow.SessionParam("")


class DragFiles(flow.ConnectAction):

    _file_map = flow.Parent()

    def accept_label(self, objects, urls):
        if not len(urls):
            return None
        
        return "Drop %i file(s)/folder(s) here" % len(urls)

    def run(self, objects, urls):
        urls = list(map(lambda url: url.replace("file:///", ""), urls))
        paths = ";".join(urls).lstrip(";").rstrip(";")
        self._file_map.paths.set(paths)
        self._file_map.touch()


class FilesToAdd(flow.DynamicMap):

    paths = flow.SessionParam("")
    drag_files = flow.Child(DragFiles)

    def mapped_names(self, page_num=0, page_size=None):
        # Count number of non empty paths
        path_count = sum(map(bool, self.paths.get().split(";")))
        return ["file_%03i" % i for i in range(path_count)]
    
    @classmethod
    def mapped_type(cls):
        return FileInfos
    
    def _configure_child(self, child):
        index = self.mapped_names().index(child.name())
        paths = self.paths.get().split(";")
        path = paths[index]
        fsname, ext = os.path.splitext(path)
        
        child.path.set(path)
        child.basename.set(os.path.basename(fsname))
        child.type.set(
            "file" if os.path.isfile(path) else "folder"
        )
        child.extension.set(ext[1:] if ext else "")


class AddFilesFromExisting(flow.Action):

    files = flow.Child(FilesToAdd)


class FileSystemMap(flow.Map):

    create_file = flow.Child(CreateTrackedFileAction).injectable()
    create_folder = flow.Child(CreateTrackedFolderAction).injectable()
    create_untracked_folder = flow.Child(CreateFolderAction)
    create_untracked_file = flow.Child(CreateFileAction)
    add_files_from_existing = flow.Child(AddFilesFromExisting)

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(FileSystemItem)

    def columns(self):
        return ["Lock", "Name", "Last comment", "Latest"]

    def _fill_row_cells(self, row, item):
        if isinstance(item, File):
            row["Name"] = item.display_name.get()
        else:
            row["Name"] = item.name()

        if hasattr(item, "state") and hasattr(item, "get_last_comment"):
            row["Lock"] = ""
            # row["State"] = item.state.get()
            row["Last comment"] = item.get_last_comment()
        else:
            row["Lock"] = "-"
            # row["State"] = "-"
            row["Last comment"] = "-"

        row['Last edit'] =  timeago.format(datetime.datetime.fromtimestamp(item.get_last_edit_time()), datetime.datetime.now())
        
        if isinstance(item, TrackedFile):
            head = item.get_head_revision()
            row["Latest"] = head.name() if head else ""
        else:
            row["Latest"] = "-"

    def _fill_row_style(self, style, item, row):
        style["icon"] = ("icons.libreflow", "blank")
        style["Name_icon"] = ("icons.gui", "folder-white-shape")

        if isinstance(item, TrackedFile) or isinstance(item, TrackedFolder):
            if item.is_locked():
                if item.is_locked(by_current_user=True):
                    style["icon"] = ("icons.libreflow", "padlock_green")
                else:
                    style["icon"] = ("icons.libreflow", "padlock_red")

            head = item.get_head_revision()
            exchange_site_name = self.root().project().get_exchange_site().name()

            if head:
                head_sync_status = head.get_sync_status()

                if head_sync_status == "NotAvailable":
                    if head.get_sync_status(site_name=exchange_site_name) == "Available":
                        sync_icon = ('icons.libreflow', 'downloadable')
                    else:
                        sync_icon = ('icons.libreflow', 'blank')
                    
                    style["Latest_foreground-color"] = "#777"
                elif head_sync_status == "Requested":
                    sync_icon = ('icons.libreflow', 'waiting')
                    style["Latest_foreground-color"] = "#777"
                else:
                    sync_icon = ('icons.libreflow', 'blank')
            else:
                sync_icon = ('icons.libreflow', 'blank')
            
            style["Latest_icon"] = sync_icon
            style["Latest_activate_oid"] = item.request.oid()
            style["Last comment_activate_oid"] = item.show_history.oid()

        if isinstance(item, File):
            default_applications = self.root().project().admin.default_applications
            try:
                default_app = default_applications[item.format.get()]
            except flow.exceptions.MappedNameError:
                pass
            else:
                try:
                    style["Name_icon"] = default_app.get_runner().runner_icon()
                except AttributeError:
                    pass

        style["Name_activate_oid"] = item.open.oid()
        

    def _parse_filename(self, filename, **params):
        formatted_name, extension = tuple(filename.split("."))

        # Remove arguments in file formatted_name not provided
        for _, arg, _, _ in string.Formatter().parse(formatted_name):
            if not arg in params:
                formatted_name.replace("{{arg}}".format(arg=arg), "")

        formatted_name.replace("__", "_")
        name = re.sub("{.*}", "", formatted_name)

        if name.startswith("_"):
            name = name[1:]
        if name.endswith("_"):
            name = name[:-1]

        name = re.sub("-", "_", name)
        complete_name = formatted_name.format(**params)

        return name, complete_name, extension

    def add_from_filename(self, filename, params=None, object_type=None):
        if params is None:
            params = {}

        name, complete_name, extension = self._parse_filename(filename, **params)

        file = self.add_tracked_file(name, extension, complete_name)
        file.unlock()

        return file

    def add_file(self, name, extension):
        key = "%s_%s" % (name, extension)
        file = self.add(key, object_type=File)
        file.format.set(extension)

        # Create file's parent folder
        parent_folder = os.path.abspath(os.path.join(file.get_path(), ".."))
        try:
            os.makedirs(parent_folder)
        except OSError:
            # Folder already created
            pass

        # Create file from template
        try:
            shutil.copyfile(file.get_template_path(), file.get_path())
        except OSError:
            self.root().session().log_error(
                "File %s already exists" % file.get_path()
            )
            raise

        return file

    def add_folder(self, name):
        folder = self.add(name, object_type=Folder)

        try:
            if os.path.exists(folder.get_path()):
                print("Folder %s already exists" % folder.get_path())
            else:
                os.makedirs(folder.get_path())
        except OSError:
            self.root().session().log_error(
                "Error while creating folder %s" % folder.get_path()
            )
            raise

        return folder

    def add_tracked_file(self, name, extension, complete_name):
        key = "%s_%s" % (name, extension)
        file = self.add(key, object_type=flow.injection.injectable(TrackedFile))
        file.format.set(extension)
        file.complete_name.set(complete_name)

        # Create file folder
        try:
            self.root().session().log_debug(
                "Create file folder '{}'".format(file.get_path())
            )
            os.makedirs(file.get_path())
        except OSError:
            self.root().session().log_error(
                "Creation of file folder '{}' failed.".format(file.get_path())
            )
            pass

        # Create current revision folder
        current_revision_folder = os.path.join(file.get_path(), "current")

        try:
            self.root().session().log_debug(
                "Create current revision folder '{}'".format(
                    current_revision_folder
                )
            )
            os.mkdir(current_revision_folder)
        except OSError:
            self.root().session().log_error(
                "Creation of current revision folder '{}' failed".format(
                    current_revision_folder
                )
            )
            pass

        return file

    def add_tracked_folder(self, name, complete_name):
        folder = self.add(name, object_type=TrackedFolder)
        folder.format.set("zip")
        folder.complete_name.set(complete_name)

        # Create file folder
        try:
            self.root().session().log_debug(
                "Create tracked folder '{}'".format(folder.get_path())
            )
            os.makedirs(folder.get_path())
        except OSError:
            self.root().session().log_error(
                "Creation of tracked folder '{}' failed.".format(folder.get_path())
            )
            pass

        # Create current revision folder
        current_revision_folder = os.path.join(folder.get_path(), "current")

        try:
            self.root().session().log_debug(
                "Create current revision folder '{}'".format(
                    current_revision_folder
                )
            )
            os.mkdir(current_revision_folder)
        except OSError:
            self.root().session().log_error(
                "Creation of current revision folder '{}' failed".format(
                    current_revision_folder
                )
            )
            pass

        return folder

    def clear(self):
        for item in self.mapped_items():
            try:
                if type(item) is File:
                    os.remove(item.get_path())
                else:
                    shutil.rmtree(item.get_path())
            except FileNotFoundError:
                self.root().session().log_warning(
                    "%s %s no longer exists"
                    % (item.__class__.__name__, item.get_path())
                )

        super(FileSystemMap, self).clear()
