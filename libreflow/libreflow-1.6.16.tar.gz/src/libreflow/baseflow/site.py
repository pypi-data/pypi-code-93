import os
import sys
import gazu
import time
from datetime import datetime, timedelta
import subprocess
import platform
from minio import Minio
import zipfile
import fnmatch
import re
import traceback

from kabaret import flow
from kabaret.flow_contextual_dict import ContextualView, get_contextual_dict
from kabaret.subprocess_manager.flow import RunAction

from ..utils.os import zip_folder, unzip_archive

from .dependency import get_dependencies
from .maputils import ItemMap, CreateGenericAction, ClearMapAction, RemoveGenericAction, SimpleCreateAction
from .runners import Runner, PythonRunner


class StaticSiteTypeChoices(flow.values.ChoiceValue):
    CHOICES = ['Studio', 'User']


class StaticSiteSyncStatusChoices(flow.values.ChoiceValue):
    CHOICES = ['NotAvailable', 'Requested', 'Available']


class StaticSiteSyncTransferStateChoices(flow.values.ChoiceValue):
    CHOICES = ['NC', 'UP_REQUESTED', 'DL_REQUESTED', 'UP_IN_PROGRESS', 'DL_IN_PROGRESS']


class LoadType(flow.values.ChoiceValue):

    CHOICES = ['Upload', 'Download']


class JobStatus(flow.values.ChoiceValue):

    CHOICES = ['WFA', 'WAITING', 'PROCESSED', 'ERROR', 'PAUSE', 'DONE']


class Job(flow.Object):

    type = flow.Param('Download', LoadType)
    status = flow.Param('WAITING', JobStatus)
    priority = flow.IntParam(50)
    emitter_oid = flow.Param()
    date = flow.Param("").ui(editor='datetime')
    date_end = flow.Param("").ui(editor='datetime')
    is_archived = flow.BoolParam()
    requested_by_user = flow.Param()
    requested_by_studio = flow.Param()
    log = flow.Param().ui(editor='textarea')

    def __repr__(self):
        job_repr = "%s(type=%s, status=%s, priority=%s, emitter=%s, date=%s, date_end=%s, is_archived=%s, requested_by_user=%s, requested_by_studio=%s)" % (
                self.__class__.__name__,
                self.type.get(),
                self.status.get(),
                self.priority.get(),
                self.emitter_oid.get(),
                self.date.get(),
                self.date_end.get(),
                self.is_archived.get(),
                self.requested_by_user.get(),
                self.requested_by_studio.get()
            )

        return job_repr


class JobQueue(flow.Map):

    @classmethod
    def mapped_type(cls):
        return Job
    
    def get_next_waiting_job(self):
        for job in reversed(self.mapped_items()):
            if job.status.get() == "WAITING":
                return job
        
        return None
    
    def jobs(self, type=None, status=None):
        jobs = self.mapped_items()

        if type:
            jobs = list(filter(lambda job: job.type.get() == type, jobs))
        if status:
            jobs = list(filter(lambda job: job.status.get() == status, jobs))
        
        return jobs
    
    def insert(self, name, priority=0):
        """
        Inserts a new job with given name and priority.
        """
        job = self.add(name)
        self._mapped_names.set_score(name, priority)

        return job
    
    def submit_job(self,
            emitter_oid,
            user,
            studio,
            date_end=-1,
            job_type='Download',
            init_status='WAITING',
            priority=50
        ):
        
        name = '%s_%s_%s_%i' % (
            emitter_oid[1:].replace('/', '_'),
            studio,
            job_type,
            time.time()
        )
        job = self.insert(name, priority)

        job.type.set(job_type)
        job.status.set(init_status)
        job.priority.set(priority)
        job.emitter_oid.set(emitter_oid)
        job.date.set(time.time())
        job.date_end.set(date_end)
        job.requested_by_user.set(user)
        job.requested_by_studio.set(studio)
        job.is_archived.set(False)
        job.log.set('?')

        self.root().session().log_info("Submitted job %s" % job)

        self.touch()

        return job
    
    def columns(self):
        return [
            "Type",
            "Status",
            "Priority",
            "Emitted on",
            "Expires on",
            "Requested by (site/user)",
        ]
    
    def _fill_row_cells(self, row, item):
        row["Type"] = item.type.get()
        row["Status"] = item.status.get()
        row["Priority"] = item.priority.get()
        row["Emitted on"] = datetime.fromtimestamp(item.date.get()).ctime()
        row["Expires on"] = "Never" if item.date_end.get() == -1 else item.date_end.get()
        row["Requested by (site/user)"] = "%s/%s" % (
            item.requested_by_studio.get(),
            item.requested_by_user.get()
        )


class ProcessJobs(flow.Action):

    def needs_dialog(self):
        return False

    def _process(self, job):
        raise NotImplementedError(
            "Must be implemented to process the given job"
        )
    
    def _get_jobs(self):
        current_site = self.root().project().get_current_site()
        return current_site.get_jobs()
    
    def run(self, button):
        for job in self._get_jobs():
            self.root().session().log_info("Processing job %s" % job)
            self._process(job)


class MinioFileUploader(PythonRunner):
    
    def argv(self):
        args = ["%s/../scripts/minio_file_uploader.py" % (
            os.path.dirname(__file__)
        )]
        args += self.extra_argv
        return args


class MinioFileDownloader(PythonRunner):
    
    def argv(self):
        args = ["%s/../scripts/minio_file_downloader.py" % (
            os.path.dirname(__file__)
        )]
        args += self.extra_argv
        return args


class MinioUploadFile(flow.Object):

    def upload(self, local_path, server_path):
        self.root().session().log_info(
            "Uploading file %s -> %s" % (
                local_path,
                server_path
            )
        )
        exchange_site = self.root().project().get_exchange_site()
        minioClient = Minio(
            exchange_site.server_url.get(),
            access_key=exchange_site.server_login.get(),
            secret_key=exchange_site.server_password.get(),
            secure=True
        )

        minioClient.fput_object(
            "testbucked",
            server_path,
            local_path
        )


class MinioDownloadFile(flow.Object):

    def download(self, server_path, local_path):
        self.root().session().log_info(
            "Downloading file %s -> %s" % (
                server_path,
                local_path
            )
        )
        exchange_site = self.root().project().get_exchange_site()
        minioClient = Minio(
            exchange_site.server_url.get(),
            access_key=exchange_site.server_login.get(),
            secret_key=exchange_site.server_password.get(),
            secure=True
        )

        minioClient.fget_object(
            "testbucked",
            server_path,
            local_path
        )


class Synchronize(ProcessJobs):

    uploader = flow.Child(MinioUploadFile).ui(hidden=True)
    downloader = flow.Child(MinioDownloadFile).ui(hidden=True)

    def _get_jobs(self):
        # Get current site's waiting jobs only
        current_site = self.root().project().get_current_site()
        return current_site.get_jobs(status="WAITING")

    def _get_sync_status(self, revision_oid, site_name=None, site_type="Studio"):
        if not site_name and site_type == "Exchange":
            exchange_site = self.root().project().get_exchange_site()
            if exchange_site:
                site_name = exchange_site.name()
            else:
                return "NotAvailable"

        sync_status = self.root().session().cmds.Flow.call(
            revision_oid, "get_sync_status",
            args={}, kwargs=dict(site_name=site_name)
        )
        return sync_status

    def _set_sync_status(self, revision_oid, status, site_name=None, site_type="Studio"):
        if not site_name and site_type == "Exchange":
            exchange_site = self.root().project().get_exchange_site()
            if exchange_site:
                site_name = exchange_site.name()
            else:
                self.root().session().log_error(
                    "No registered exchange site on this project !"
                )
                return

        self.root().session().cmds.Flow.call(
            revision_oid, "set_sync_status",
            args={status}, kwargs=dict(site_name=site_name)
        )
    
    def _touch(self, oid):
        oid = self.root().session().cmds.Flow.resolve_path(oid)
        self.root().session().cmds.Flow.call(
            oid, "touch", args={}, kwargs={}
        )

    def _process(self, job):
        if job.status.get() == "PROCESSED":
            self.root().session().log_warning(
                "Job %s already processed !" % job.name()
            )
            return

        local_path = self.root().session().cmds.Flow.call(
            job.emitter_oid.get(),
            "get_path",
            args={},
            kwargs={}
        )
        server_path = self.root().session().cmds.Flow.call(
            job.emitter_oid.get(),
            "get_relative_path",
            args={},
            kwargs={}
        )
        local_path = local_path.replace("\\", "/")
        server_path = server_path.replace("\\", "/")

        try:
            if job.type.get() == "Upload":
                # Check if local_path refers to a folder (.zip format)
                local_folder = os.path.dirname(local_path)
                
                if os.path.splitext(local_path)[1] == '.zip':
                    local_folder = os.path.dirname(local_path)
                    
                    if not os.path.exists(local_folder):
                        # Return if folder does not exist
                        self.root().session().log_error((
                            "Following folder requested for upload but does not exist !"
                            "\n>>>>> %s" % local_folder
                        ))
                        return
                    else:
                        # Zip folder files
                        zip_folder(local_folder, local_path)

                elif not os.path.exists(local_path):
                    self.root().session().log_error((
                        "Following file requested for upload but does not exist !"
                        "\n>>>>> %s" % local_path
                    ))
                    return

                self.uploader.upload(local_path, server_path)
                
                if os.path.splitext(local_path)[1] == '.zip':
                    os.remove(local_path)
                
                self._set_sync_status(job.emitter_oid.get(), "Available", site_type="Exchange")
                self._touch(job.emitter_oid.get() + "/..")
            elif job.type.get() == "Download":
                sync_status = self._get_sync_status(job.emitter_oid.get(), site_type="Exchange")
                
                if sync_status != "Available":
                    self.root().session().log_error((
                        "Following file requested for download "
                        "but not available on any exchange server !"
                        "\n>>>>> %s" % local_path
                    ))
                    return

                self.downloader.download(server_path, local_path)
                
                # If it's a folder revision, extract its archive content
                if os.path.splitext(local_path)[1] == '.zip':
                    unzip_archive(local_path, os.path.dirname(local_path))
                    os.remove(local_path)
                
                self._set_sync_status(job.emitter_oid.get(), "Available")
                self._touch(job.emitter_oid.get() + "/..")
                self._touch(job.emitter_oid.get() + "/../../../..")
        
        except Exception as err:
            job.log.set(traceback.format_exc())
            job.status.set('ERROR')
        else:
            job.status.set("PROCESSED")
        
        # Refresh project's sync section UI
        self.root().project().synchronization.touch()


class ActiveSiteChoiceValue(flow.values.SessionValue):
    
    DEFAULT_EDITOR = 'choice'
    
    _choices = flow.SessionParam(None).ui(editor='set')

    def choices(self):
        if self._choices.get() is None:
            working_sites = self.root().project().get_working_sites()
            names = working_sites.get_site_names(use_custom_order=True, active_only=True)
            self._choices.set(names)
        
        return self._choices.get()


class ActiveSiteAutoSelectChoiceValue(ActiveSiteChoiceValue):
    
    def choices(self):
        choices = super(ActiveSiteAutoSelectChoiceValue, self).choices()
        choices = ['Auto select'] + choices.copy()
        
        return choices


class ActiveSitesMultichoiceValue(ActiveSiteChoiceValue):
    
    DEFAULT_EDITOR = 'multichoice'
    
    exclude_choice = flow.SessionParam()
    
    def choices(self):
        if self._choices.get() is None:
            working_sites = self.root().project().get_working_sites()
            names = working_sites.get_site_names(use_custom_order=True, active_only=True)
            self._choices.set(names)
        
        choices = self._choices.get().copy()
        exclude_choice = self.exclude_choice.get()
        
        if exclude_choice is not None:
            try:
                choices.remove(exclude_choice)
            except ValueError:
                pass
        
        return choices


class ActiveSiteRevisionAvailableChoiceValue(flow.values.ChoiceValue):
    
    DEFAULT_EDITOR = 'choice'
    
    _choices = flow.SessionParam(None).ui(editor='set')
    _revision = flow.Parent(2)
    
    exclude_choice = flow.SessionParam(None).ui(hidden=False)

    def choices(self):
        if self._choices.get() is None:
            working_sites = self.root().project().get_working_sites()
            choices = working_sites.get_site_names(use_custom_order=True, active_only=True)
            exclude_choice = self.exclude_choice.get()
            
            if exclude_choice is not None:
                try:
                    choices.remove(exclude_choice)
                except ValueError:
                    pass
            
            choices_available = []
            
            for site_name in choices:
                if self._revision.get_sync_status(site_name) == 'Available':
                    choices_available.append(site_name)
            
            self._choices.set(choices_available)
        
        return self._choices.get()


class SiteSelection(flow.Object):
    
    source_site = flow.Param(None, ActiveSiteChoiceValue).watched()
    target_site = flow.Param(None, ActiveSiteChoiceValue).watched()
    auto_select_enabled = flow.SessionParam(False).watched().ui(
        editor='bool',
        hidden=True)
    
    def child_value_changed(self, child_value):
        if child_value in (self.source_site, self.target_site, self.auto_select_enabled):
            self.touch()
    
    def summary(self):
        if self.source_site.get() == self.target_site.get() and not self.auto_select_enabled.get():
            return '⚠️ Source and target sites can\'t be the same !'
        else:
            return ''


class RequestAs(flow.Action):

    _revision = flow.Parent()
    sites = flow.Child(SiteSelection).ui(expanded=True)
    priority = flow.IntParam(50)
    include_dependencies = flow.SessionParam(True).ui(editor='bool')
    
    def get_buttons(self):
        self.sites.source_site.set(self.root().project().get_current_site().name())
        target_site_choices = self.sites.target_site.choices()
        
        if not target_site_choices:
            msg = self.message.get()
            if msg is None:
                msg = ''
            
            msg += (
                '<h3><font color="#D5000D">Making requests is not possible since '
                'there is no other site defined for this project.</font></h3>'
            )
            self.message.set(msg)
            
            return ['Cancel']
        
        self.sites.target_site.set(target_site_choices[0])

        return ["Request", "Cancel"]
    
    def get_source_site_name(self):
        return self.sites.source_site.get()
    
    def get_target_site_name(self):
        return self.sites.target_site.get()
    
    def allow_context(self, context):
        return (
            context
            and not self._revision.is_working_copy()
            and self.root().project().get_current_site().request_files_from_anywhere.get()
        )

    def run(self, button):
        if button == "Cancel":
            return
        
        source_site_name = self.get_source_site_name()
        target_site_name = self.get_target_site_name()

        # Get requesting and requested sites
        sites = self.root().project().get_working_sites()
        target_site = sites[target_site_name]
        
        # Add a download job for the requesting site
        target_site.get_queue().submit_job(
            job_type="Download",
            init_status="WAITING",
            emitter_oid=self._revision.oid(),
            user=self.root().project().get_user(),
            studio=target_site_name,
            priority=self.priority.get(),
        )
        self._revision.set_sync_status("Requested", site_name=target_site_name)
        self._revision._revisions.touch()
        
        # Request dependencies if required
        if self.include_dependencies.get():
            request_deps = self._revision.request_dependencies
            request_deps.target_site.set(target_site_name)
            request_deps.predictive_only.set(False)
            request_deps.run(None)
        
        # Check if the version is not available on the exchange server
        exchange_site = self.root().project().get_exchange_site()
        revision_status = self._revision.get_sync_status(exchange=True)

        if revision_status == "Available":
            self.root().session().log_warning(
                "Revision already available on exchange server"
            )
            self.root().project().synchronization.touch()
            return self.get_result()
        
        # If enabled, automatically select source site
        if self.sites.auto_select_enabled.get():
            source_site_name = self._revision.site.get()
        
        source_site = sites[source_site_name]

        # Check if the source version upload is not already requested
        for job in source_site.get_jobs(type="Upload", status="WAITING"):
            if job.emitter_oid.get() == self._revision.oid():
                self.root().session().log_warning(
                    "Revision already requested for upload in source site"
                )
                self.root().project().synchronization.touch()
                return self.get_result()
        
        # Add an upload job for the requested site
        source_site.get_queue().submit_job(
            job_type="Upload",
            init_status="WAITING",
            emitter_oid=self._revision.oid(),
            user=self.root().project().get_user(),
            studio=target_site_name,
            priority=self.priority.get(),
        )

        # Refresh project's sync section UI
        self.root().project().synchronization.touch()


class Request(RequestAs):

    _revision = flow.Parent()
    priority = flow.IntParam(50)
    source_site = flow.Param(None, ActiveSiteRevisionAvailableChoiceValue)
    
    sites = flow.Child(SiteSelection).ui(hidden=True)

    def get_buttons(self):
        self.source_site.exclude_choice.set(self.root().project().get_current_site().name())
        source_site_choices = self.source_site.choices()
        
        if not source_site_choices:
            msg = self.message.get()
            if msg is None:
                msg = ''
            
            msg += (
                '<h3><font color="#D5000D">Making requests is not possible since '
                'the revision isn\'t available on any site.</font></h3>'
            )
            self.message.set(msg)
            
            return ['Cancel']
        
        self.source_site.set(source_site_choices[0])

        return ['Request', 'Cancel']
    
    def get_source_site_name(self):
        return self.source_site.get()
    
    def get_target_site_name(self):
        return self.root().project().get_current_site().name()
    
    def allow_context(self, context):
        return (
            context
            and not self._revision.is_working_copy()
            and not self._revision.get_sync_status() == "Available"
        )


class ResetJobStatuses(flow.Action):
    _site = flow.Parent()
    status = flow.Param("WAITING", JobStatus)

    def run(self, button):
        for job in self._site.get_jobs():
            job.status.set(self.status.get())
        
        self._site.get_queue().touch()


class CreateSite(flow.Action):

    ICON = ("icons.gui", "plus-sign-in-a-black-circle")

    _site_map = flow.Parent()
    site_name = flow.SessionParam("").ui(label="Name")

    def get_buttons(self):
        self.message.set("<h2>Create a site</h2>")
        return ["Create", "Cancel"]
    
    def run(self, button):
        if button == "Cancel":
            return
        
        site_name = self.site_name.get()

        if not site_name or self._site_map.has_mapped_name(site_name):
            if not site_name:
                msg = "Site name must not be empty."
            else:
                msg = f"Site {site_name} already exists."

            self.message.set((
                "<h2>Create a site</h2>"
                f"<font color=#D5000D>{msg}</font>"
            ))
            
            return self.get_result(close=False)

        site = self._site_map.add(site_name)
        self._site_map.touch()

        return self.get_result(next_action=site.configuration.oid())


class ConfigureSite(flow.Action):

    _site_map = flow.Parent(2)
    _site = flow.Parent()
    short_name = flow.SessionParam("").ui(label="Short name")
    description = flow.SessionParam("")

    def get_buttons(self):
        self.message.set(
            "<h2>Site <font color=#fff>%s</font></h2>" % self._site.name()
        )
        self._fill_action_fields()

        return ["Configure", "Cancel"]

    def _configure_site(self, site):
        '''
        This can be used by subclass to configure a mapped site.

        Default is to set site's short name and description.
        '''
        self._site.short_name.set(self.short_name.get())
        self._site.description.set(self.description.get())
    
    def _fill_action_fields(self):
        '''
        This can be used by subclass to fill action's parameters when
        dialog is displayed (e.g. to automatically show site parameters).

        Default is to fill site's short name and description.
        '''
        self.short_name.set(self._site.short_name.get())
        self.description.set(self._site.description.get())
    
    def allow_context(self, context):
        # Hide in map item submenus
        return False
    
    def run(self, button):
        if button == "Cancel":
            return
        
        self._configure_site(self._site)
        self._site.configured.touch()
        self._site_map.touch()


class ComputedBoolValue(flow.values.ComputedValue):

    DEFAULT_EDITOR = 'bool'


class Site(flow.Object):

    short_name = flow.Param("")
    description = flow.Param("")
    # Define conditions required for a site to be considered as correctly configured
    configured = flow.Computed(
        cached=True,
        store_value=True,
        computed_value_type=ComputedBoolValue
    )
    configuration = flow.Child(ConfigureSite)

    is_active = flow.BoolParam(True)

    def compute_child_value(self, child_value):
        if child_value is self.configured:
            self.configured.set(True)


class SiteMap(flow.Map):

    create_site = flow.Child(CreateSite)

    @classmethod
    def mapped_type(cls):
        return Site

    def mapped_names(self, page_num=0, page_size=None):
        return ["default"] + super(SiteMap, self).mapped_names(page_num, page_size)
    
    def columns(self):
        return ["Site"]
    
    def short_names(self):
        return [s.short_name.get() for s in self.mapped_items()]
    
    def get_site_names(self, use_custom_order=False, active_only=False, short_names=False):
        if not use_custom_order:
            sites = self.mapped_items()
        else:
            current_site = self.root().project().get_current_site()
            unordered_names = self.mapped_names()
            sites = []
            
            for name in current_site.get_ordered_site_names():
                if self.has_mapped_name(name):
                    sites.append(self.get_mapped(name))
                    unordered_names.remove(name)
            
            for name in unordered_names:
                sites.append(self.get_mapped(name))

        if active_only:
            sites = [s for s in sites if s.is_active.get()]
        
        if short_names:
            names = [s.short_name.get() for s in sites]
        else:
            names = [s.name() for s in sites]
        
        return names
    
    def _get_mapped_item_type(self, mapped_name):
        if mapped_name == "default":
            return self.mapped_type()

        return super(SiteMap, self)._get_mapped_item_type(mapped_name)
    
    def _fill_row_cells(self, row, item):
        row["Site"] = item.name()
        if not item.configured.get():
            row["Site"] += " ⚠️"
    
    def _fill_row_style(self, style, item, row):
        style["activate_oid"] = item.configuration.oid()


class ConfigureWorkingSite(ConfigureSite):

    site_type = flow.Param("Studio", StaticSiteTypeChoices)

    root_windows_folder = flow.SessionParam("")
    root_linux_folder = flow.SessionParam("")
    root_darwin_folder = flow.SessionParam("")
    
    sync_dl_max_connections = flow.SessionParam(1)
    sync_up_max_connections = flow.SessionParam(1)
    
    def _fill_action_fields(self):
        super(ConfigureWorkingSite, self)._fill_action_fields()
        self.site_type.set(self._site.site_type.get())
        self.root_windows_folder.set(self._site.root_windows_folder.get())
        self.root_linux_folder.set(self._site.root_linux_folder.get())
        self.root_darwin_folder.set(self._site.root_darwin_folder.get())
        self.sync_dl_max_connections.set(self._site.sync_dl_max_connections.get())
        self.sync_up_max_connections.set(self._site.sync_up_max_connections.get())

    def _configure_site(self, site):
        super(ConfigureWorkingSite, self)._configure_site(site)
        site.site_type.set(self.site_type.get())
        site.root_windows_folder.set(self.root_windows_folder.get())
        site.root_linux_folder.set(self.root_linux_folder.get())
        site.root_darwin_folder.set(self.root_darwin_folder.get())
        site.sync_dl_max_connections.set(self.sync_dl_max_connections.get())
        site.sync_up_max_connections.set(self.sync_up_max_connections.get())


class Queue(flow.Object):

    job_list = flow.Child(JobQueue).ui(label="Jobs", expanded=True)


class GotoQueue(flow.Action):

    _site = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        return self.get_result(goto=self._site.queue.oid())


class GotoCurrentSiteQueue(flow.Action):
    
    ICON = ('icons.flow', 'jobs')
    
    def needs_dialog(self):
        return False
    
    def run(self, button):
        current_site = self.root().project().get_current_site()
        return self.get_result(goto=current_site.queue.oid())


class ClearQueueJobStatus(flow.values.ChoiceValue):

    CHOICES = JobStatus.CHOICES + ["All"]


class ClearQueueLoadType(flow.values.ChoiceValue):

    CHOICES = LoadType.CHOICES + ["All"]


class ClearQueueAction(flow.Action):

    _site = flow.Parent()
    status = flow.Param("PROCESSED", ClearQueueJobStatus)
    type = flow.Param("All", ClearQueueLoadType)
    emitted_before = flow.SessionParam((datetime.now() - timedelta(days=1)).timestamp()).ui(
        editor='datetime'
    )

    def get_buttons(self):
        self.message.set(
            "<h2>Clear %s jobs</h2>" % self._site.name()
        )
        return ["Clear", "Cancel"]
    
    def run(self, button):
        queue = self._site.get_queue()
        status = self.status.get()
        type = self.type.get()

        if status == "All" and type == "All":
            queue.clear()
        else:
            for job in queue.jobs(status=self.status.get()):
                if job.date.get() < self.emitted_before.get():
                    queue.remove(job.name())

        queue.touch()


class RemoveEnvironmentVariableAction(flow.Action):

    _variable = flow.Parent().ui(hidden=True)
    _collection = flow.Parent(2).ui(hidden=True)

    def get_buttons(self):
        return ['Confirm', 'Cancel']

    def run(self, button):
        if button == 'Cancel':
            return

        self._collection.touch()
        self._collection.remove(self._variable.name())


class EnvironmentVariable(flow.Object):

    vars_collection = flow.Parent()
    variable = flow.Param("")
    value = flow.Param("")
    remove_variable = flow.Child(RemoveEnvironmentVariableAction)


class AddEnvironmentVariableAction(flow.Action):

    _vars_collection = flow.Parent().ui(hidden=True)
    variable = flow.Param("")
    value = flow.Param("")

    def get_buttons(self):
        return ['Create', 'Cancel']

    def run(self, button):
        var_name = self.variable.get().replace(' ', '_').upper()

        if button == 'Cancel':
            self.variable.set("")
            self.value.set("")
            return

        elif (len(var_name) == 0) or (len(self.value.get()) == 0) or (self._vars_collection.has_mapped_name(var_name)):
            self.variable.set("")
            self.value.set("")
            return

        else:
            new_var = self._vars_collection.add(var_name)
            
            new_var.variable.set(var_name)
            new_var.value.set(self.value.get())
            self.variable.set("")
            self.value.set("")
            self._vars_collection.touch()


class SiteEnvironment(flow.Map):
    
    add_environment_variable = flow.Child(AddEnvironmentVariableAction)

    @classmethod
    def mapped_type(cls):
        return EnvironmentVariable


    def columns(self):
        return ['Variable', 'Value']

    def _fill_row_cells(self, row, item):
        row['Variable'] = item.variable.get()
        row['Value'] = item.value.get()


class SiteJobsPoolNames(flow.values.ChoiceValue):
    
    def choices(self):
        site = self.root().project().get_current_site()
        return ['default'] + site.pool_names.get()


class WorkingSite(Site):
    
    _site_map = flow.Parent()
    
    site_type = flow.Param("Studio", StaticSiteTypeChoices)
    request_files_from_anywhere = flow.BoolParam(False).ui(
        tooltip=(
            "Allow the site to request files for any other site. "
            "Temporary option as long as synchronisation is manual."
        )
    )
    is_kitsu_admin = flow.BoolParam(False)

    root_folder = flow.Computed(cached=True)
    root_windows_folder = flow.Param()
    root_linux_folder = flow.Param()
    root_darwin_folder = flow.Param()
    
    ordered_site_names = flow.Param('')
    
    sync_dl_max_connections = flow.IntParam(1)
    sync_up_max_connections = flow.IntParam(1)
    pool_names = flow.OrderedStringSetParam()

    queue = flow.Child(Queue)

    configuration = flow.Child(ConfigureWorkingSite)
    goto_queue = flow.Child(GotoQueue).ui(
        label="Show job queue"
    )
    clear_queue = flow.Child(ClearQueueAction)
    site_environment = flow.Child(SiteEnvironment)

    def compute_child_value(self, child_value):
        if child_value is self.root_folder:
            root_dir = None
            # Get the operative system
            _os = platform.system()
            if _os == "Linux":
                root_dir = self.root_linux_folder.get()
            elif _os == "Windows":
                root_dir = self.root_windows_folder.get()
            elif _os == "Darwin":
                root_dir = self.root_darwin_folder.get()
            else:
                print("ERROR: Unrecognized operative system ?")
            
            if not root_dir or not os.path.exists(root_dir):
                print("WARNING: ROOT_DIR path DOES NOT EXISTS")

            child_value.set(root_dir)

        elif child_value is self.configured:
            self.configured.set(
                (
                    self.root_windows_folder.get()
                    or self.root_linux_folder.get()
                    or self.root_darwin_folder.get()
                )
            )
    
    def get_ordered_site_names(self):
        names_as_string = self.ordered_site_names.get()
        names_as_string = names_as_string.replace(' ','')
        
        return names_as_string.split(',')
    
    def get_queue(self):
        return self.queue.job_list
    
    def get_jobs(self, type=None, status=None):
        return self.get_queue().jobs(type=type, status=status)


class WorkingSites(SiteMap):

    ICON = ('icons.gui', 'home')

    @classmethod
    def mapped_type(cls):
        return WorkingSite

    def _configure_child(self, child):
        if child.name() == "default":
            child.short_name.set("dft")
            child.description.set("Default working site")
            child.site_type.set("Studio")
        else:
            super(WorkingSites, self)._configure_child(child)

    def _fill_row_style(self, style, item, row):
        super(WorkingSites, self)._fill_row_style(style, item, row)

        if item.site_type.get() == "User":
            style['icon'] = ('icons.gui', 'user')
        else:
            style['icon'] = ('icons.gui', 'home')


class ConfigureExchangeSite(ConfigureSite):

    server_url = flow.SessionParam("http://")
    server_login = flow.SessionParam("")
    server_password = flow.SessionParam("").ui(editor='password')

    def _fill_action_fields(self):
        super(ConfigureExchangeSite, self)._fill_action_fields()
        self.server_url.set(self._site.server_url.get())
        self.server_login.set(self._site.server_login.get())
        self.server_password.set(self._site.server_password.get())

    def _configure_site(self, site):
        super(ConfigureExchangeSite, self)._configure_site(site)
        site.server_url.set(self.server_url.get())
        site.server_login.set(self.server_login.get())
        site.server_password.set(self.server_password.get())


class ExchangeSite(Site):

    ICON = ('icons.libreflow', 'exchange')

    server_url = flow.Param("")
    server_login = flow.Param("")
    server_password = flow.Param("").ui(editor='password')

    configuration = flow.Child(ConfigureExchangeSite)

    def compute_child_value(self, child_value):
        if child_value is self.configured:
            self.configured.set(
                (
                    self.server_url.get()
                    and self.server_login.get()
                    and self.server_password.get()
                )
            )


class ExchangeSites(SiteMap):
    
    ICON = ('icons.libreflow', 'exchange')

    @classmethod
    def mapped_type(cls):
        return ExchangeSite

    def mapped_names(self, page_num=0, page_size=None):
        return ["default_exchange"] + super(SiteMap, self).mapped_names(page_num, page_size)

    def _configure_child(self, child):
        if child.name() == "default_exchange":
            child.short_name.set("dftx")
            child.description.set("Default exchange site")
        else:
            super(ExchangeSites, self)._configure_child(child)

    def _get_mapped_item_type(self, mapped_name):
        if mapped_name == "default_exchange":
            return self.mapped_type()

        return super(SiteMap, self)._get_mapped_item_type(mapped_name)


class SyncSiteStatus(flow.Object):
    status = flow.Param("NotAvailable", StaticSiteSyncStatusChoices)

    def get_short_name(self):
        working_sites = self.root().project().get_working_sites()
        exchange_sites = self.root().project().get_exchange_sites()

        if working_sites.has_mapped_name(self.name()):
            site = working_sites[self.name()]
        else:
            site = exchange_sites[self.name()]

        return site.short_name.get()


class SyncMap(flow.DynamicMap):
    version = flow.Parent()

    @classmethod
    def mapped_type(cls):
        return SyncSiteStatus

    def mapped_names(self, page_num=0, page_size=None):
        working_sites = self.root().project().get_working_sites()
        exchange_sites = self.root().project().get_exchange_sites()
        
        return working_sites.mapped_names() + exchange_sites.mapped_names()

    def columns(self):
        return ['Name', 'Status']

    def _fill_row_cells(self, row, item):
        row['Status'] = item.status.get()
        row['Name'] = item.name()

        if item.name() == self.version.site.get():
            row['Name'] += " (S)"


class RequestedRevisions(flow.DynamicMap):
    
    STYLE_BY_STATUS = {
        'Available': ('#45cc3d', ('icons.libreflow', 'blank')),
        'Requested': ('#b9c2c8', ('icons.libreflow', 'exclamation-sign-colored')),
        'NotAvailable': ('#cc3b3c', ('icons.libreflow', 'blank')),
        'Undefined': ('#cc3b3c', ('icons.libreflow', 'unavailable')),
    }
    
    request_action = flow.Parent()
    oids = flow.SessionParam([]).ui(editor='set')
    
    def mapped_names(self, page_num=0, page_size=None):
        return self.oids.get()
    
    def get_mapped(self, name):
        if not self.has_mapped_name(name):
            raise MappedNameError(self.oid(), name)

        try:
            obj = self._mng.get_object(name)
        except ValueError:
            raise

        return obj
    
    def columns(self):
        return ['Revision']
    
    def _fill_row_cells(self, row, item):
        row['Revision'] = item.oid()
    
    def _fill_row_style(self, style, item, row):
        status = 'Undefined'
        
        if hasattr(item, 'request_as'):
            status = item.get_sync_status(site_name=self.request_action.sites.target_site.get())
            
        style['Revision_foreground-color'] = self.STYLE_BY_STATUS[status][0]
        style['Revision_icon'] = self.STYLE_BY_STATUS[status][1]


class RequestRevisions(flow.Action):
    
    ICON = ('icons.gui', 'share-option')

    pattern = flow.SessionParam("").ui(
        placeholder="Revision oid pattern"
    )
    
    sites = flow.Child(SiteSelection).ui(expanded=True)
    revisions = flow.Child(RequestedRevisions).ui(expanded=True)
    
    def allow_context(self, context):
        current_site = self.root().project().get_current_site()
        return context and current_site.request_files_from_anywhere.get()
    
    def _get_oid(self, pattern_str):
        oids = []
        patterns = []
        
        for pattern in pattern_str.split(';'):
            patterns += self.resolve_pattern(pattern)
        
        for pattern in patterns:
            oids += self.glob(self.root().project().oid(), pattern, 0)
        
        return oids

    def get_buttons(self):
        self.sites.source_site.set(self.root().project().get_current_site().name())
        target_site_choices = self.sites.target_site.choices()
        
        if not target_site_choices:
            msg = self.message.get()
            if msg is None:
                msg = ''
            
            msg += (
                '<h3><font color="#D5000D">Making requests is not possible since '
                'there is no other site defined for this project.</font></h3>'
            )
            self.message.set(msg)
            
            return ['Close']
        
        self.sites.target_site.set(target_site_choices[0])

        return ["Request", "Refresh revision list", "Close"]
    
    def ls(self, root_oid):
        related_info, mapped_names = self.root().session().cmds.Flow.ls(root_oid)
        relation_oids = [rel_info[0] for rel_info in related_info]
        mapped_oids = ["%s/%s" % (root_oid, name) for name in mapped_names]
        
        return relation_oids + mapped_oids
    
    def get_last_publication(self, file_oid):
        o = self.root().get_object(file_oid)
        
        try:
            head = o.get_head_revision()
        except AttributeError:
            return None
        
        if not head:
            return None
        
        return head.name()
    
    def glob(self, root_oid, pattern, level):
        if level >= pattern.count("/") - 1:
            return [root_oid]

        matches = []
        level_pattern = "/".join(pattern.split("/")[:level + 3])

        if level_pattern.endswith("[last]"):
            file_oid = self.root().session().cmds.Flow.resolve_path(root_oid + "/../..")
            head_name = self.get_last_publication(file_oid)

            if not head_name:
                return []
            
            pattern = pattern.replace("[last]", head_name)
            level_pattern = level_pattern.replace("[last]", head_name)
        
        for oid in self.ls(root_oid):
            if fnmatch.fnmatch(oid, level_pattern):
                matches += self.glob(oid, pattern, level + 1)
        
        return matches
    
    def resolve_pattern(self, pattern_oid):
        '''
        Returns a list of patterns which correspond to all substitution combinations of `pattern_oid`.
        Substitute string are specified in `pattern_oid` between brackets and separated with comas (`{s0, s1, ...}`).
        '''
        match = re.search(r'{[^{}]+}', pattern_oid)

        if not match:
            return [pattern_oid]

        substitutes = match.group()[1:-1].split(',')
        substitutes = [sub.replace(' ', '') for sub in substitutes]

        sub_oids = [pattern_oid.replace(match.group(), sub, 1) for sub in substitutes]
        oids = []

        for sub_oid in sub_oids:
            oids += self.resolve_pattern(sub_oid)
        
        return oids
    
    def run(self, button):
        if button == "Close":
            return
        elif button == "Refresh revision list":
            self.revisions.oids.revert_to_default()
            oids = self._get_oid(self.pattern.get())
            self.revisions.oids.set(oids)
            self.revisions.touch()
            
            return self.get_result(close=False)
        
        source_site = self.sites.source_site.get()
        target_site = self.sites.target_site.get()
        
        for obj in self.revisions.mapped_items():
            # Skip objects which are not file revisions
            if not hasattr(obj, 'request_as'):
                continue
            # Skip revisions which are not available on selected source site
            if obj.get_sync_status(site_name=source_site) != 'Available':
                continue

            # Skip revisions which are already available on selected target site
            status = obj.get_sync_status(site_name=target_site)
            if status == 'Requested' or status == 'Available':
                continue
            
            obj.request_as.sites.source_site.set(source_site)
            obj.request_as.sites.target_site.set(target_site)
            obj.request_as.include_dependencies.set(False)
            obj.request_as.run(None)
        
        self.revisions.touch()

        return self.get_result(close=False)


class SiteMultiSelection(flow.Object):
    
    source_site = flow.Param(None, ActiveSiteAutoSelectChoiceValue).watched()
    target_sites = flow.Param([], ActiveSitesMultichoiceValue)
    
    def child_value_changed(self, child_value):
        if child_value is self.source_site:
            source_site = self.source_site.get()
            
            if source_site == 'Auto select':
                self.target_sites.exclude_choice.set(None)
            else:
                self.target_sites.exclude_choice.set(self.source_site.get())
            
            self.target_sites.touch()


class MultiRequestedRevisions(RequestedRevisions):
    
    STYLE_BY_STATUS = {
        'Available': ('#45cc3d', ('icons.libreflow', 'checked-symbol-colored')),
        'Requested': ('#b9c2c8', ('icons.libreflow', 'exclamation-sign-colored')),
        'NotAvailable': ('#cc3b3c', ('icons.libreflow', 'blank')),
        'Undefined': ('#cc3b3c', ('icons.libreflow', 'unavailable')),
    }
    
    request_action = flow.Parent()
    
    def columns(self):
        return ['Revision'] + self.request_action.sites.target_sites.get()
    
    def _fill_row_cells(self, row, item):
        row['Revision'] = item.oid()
        
        for col in self.columns()[1:]:
            row[col] = ''
    
    def _fill_row_style(self, style, item, row):
        style['Revision_icon'] = ('icons.libreflow', 'blank')
        
        if not hasattr(item, 'request_as'):
            style['Revision_icon'] = self.STYLE_BY_STATUS['Undefined'][1]
            return
        
        for site_name in self.request_action.sites.target_sites.get():
            status = item.get_sync_status(site_name=site_name)
            style[site_name + '_icon'] = self.STYLE_BY_STATUS[status][1]


class MultiRequestRevisions(RequestRevisions):
    
    ICON = ('icons.libreflow', 'multi-share-option')
    
    sites = flow.Child(SiteMultiSelection).ui(expanded=True)
    revisions = flow.Child(MultiRequestedRevisions).ui(expanded=True)
    
    def get_buttons(self):
        self.sites.source_site.set(self.root().project().get_current_site().name())
        target_sites_choices = self.sites.target_sites.choices()
        
        if not target_sites_choices:
            msg = self.message.get()
            if msg is None:
                msg = ''
            
            msg += (
                '<h3><font color="#D5000D">Making requests is not possible since '
                'there is no other site defined for this project.</font></h3>'
            )
            self.message.set(msg)
            
            return ['Close']

        return ['Request', 'Refresh revision list', 'Close']
    
    def run(self, button):
        if button == 'Close':
            return
        elif button == 'Refresh revision list':
            self.revisions.oids.revert_to_default()
            oids = self._get_oid(self.pattern.get())
            self.revisions.oids.set(oids)
            self.revisions.touch()
            
            return self.get_result(close=False)
        
        source_site = self.sites.source_site.get()
        auto_select_enabled = (source_site == 'Auto select')
        
        for obj in self.revisions.mapped_items():
            # Skip objects which are not file revisions
            if not hasattr(obj, 'request_as'):
                continue
            # Skip revisions which are not available on selected source site
            if not auto_select_enabled and obj.get_sync_status(site_name=source_site) != 'Available':
                continue
            
            for target_site in self.sites.target_sites.get():
                # Skip revisions which are already available on selected target site
                status = obj.get_sync_status(site_name=target_site)
                if status == 'Requested' or status == 'Available':
                    continue
                
                if not auto_select_enabled:
                    obj.request_as.sites.source_site.set(source_site)
                
                obj.request_as.sites.target_site.set(target_site)
                obj.request_as.sites.auto_select_enabled.set(auto_select_enabled)
                obj.request_as.include_dependencies.set(False)
                obj.request_as.run(None)
        
        self.revisions.touch()

        return self.get_result(close=False)


class UploadRevision(flow.Action):
    
    _revision = flow.Parent()
    _revisions = flow.Parent(2)
    
    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return context and not self._revision.is_working_copy()
    
    def run(self, button):
        current_site = self.root().project().get_current_site()
        # Add an upload job for the current site
        job = current_site.get_queue().submit_job(
            job_type='Upload',
            init_status='WAITING',
            emitter_oid=self._revision.oid(),
            user=self.root().project().get_user(),
            studio=current_site.name(),
        )
        process_jobs_action = self.root().project().admin.process_jobs
        process_jobs_action._process(job)
        
        self._revisions.touch()
