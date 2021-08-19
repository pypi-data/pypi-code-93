import json


class SourcesMixin(object):
    def get_sources(
        self,
        project_id,
        include_config=None,
        include_run_stats=None,
        include_pipeline_backlog=None,
    ):
        """Get all sources for the provided project.

        :param project_id: Project identifier.
        :param include_config: Bool, whether or not to include the config for
            all the Sources.
        :param include_run_stats: Bool, whether or not to include the run stats
            for all the Sources.
        :param include_pipeline_backlog: Bool, whether or not to include the
            the backlog of items in the data pipeline for sources.

        :returns: A list of sources.

        Example::

            >>> client.get_sources(
            ...    project_id='Vlg5Z1hOShm0eYmjtsqSqg',
            ...    include_config=True,
            ...    include_run_stats=True,
            ...    include_pipeline_backlog=True)

            [
              {
                "items_fetched_total": 2,
                "last_error": "",
                "last_check_at": "2019-01-23T10:23:23",
                "paused": false,
                "error_count": 0,
                "id": "pqTn4vBZRdS5hYw0TBt0pQ",
                "total_error_count": 0,
                "project_id": "Vlg5Z1hOShm0eYmjtsqSqg",
                "config": {
                  "dataloader_plugin_options": {
                    "source_file": "path:/tmp/test.csv"
                  },
                  "dataloader_options": {
                    "map_title": "title",
                    "project_id": "Vlg5Z1hOShm0eYmjtsqSqg",
                    "plugin_name": "csv_plugin"
                  }
                },
                "status": "complete",
                "total_runs": 1,
                "pipeline_workflow_id": "S0fVQ-K0TmS1UgT0msZRBA",
                "last_error_at": null,
                "last_update_at": "2019-01-23T10:23:23",
                "last_success_at": "2019-01-23T10:23:23",
                "items_fetched_last_run": 2,
                "tenant": "squirro",
                "next_run_time_at": "2019-01-23T10:52:51",
                "name": "test source",
                "scheduling_options": {
                  "repeat": "30m",
                  "schedule": true
                },
                "created_at": "2019-01-23T10:23:23",
                "modified_at": "2019-01-23T10:23:23",
                "processed": true,
                "pipeline_backlog": 10
              }
            ]
        """

        url = "%(ep)s/%(version)s/%(tenant)s" "/projects/%(project_id)s" "/sources"
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        params = {}
        if include_config:
            params["include_config"] = include_config
        if include_run_stats:
            params["include_run_stats"] = include_run_stats
        if include_pipeline_backlog:
            params["include_pipeline_backlog"] = include_pipeline_backlog

        res = self._perform_request("get", url, params=params)
        return self._process_response(res)

    def get_source(
        self,
        project_id,
        source_id,
        include_config=None,
        include_run_stats=None,
        include_pipeline_backlog=None,
    ):
        """Get source details.

        :param project_id: Project identifier.
        :param source_id: Source identifier.
        :param include_config: Bool, whether or not to include the config for
            the Source.
        :param include_run_stats: Bool, whether or not to include the run stats
            for the Source.
        :param include_pipeline_backlog: Bool, whether or not to include the
            the backlog of items in the data pipeline for this source.
        :returns: A dictionary which contains the source.

        Example::

            >>> client.get_source(
            ...     project_id='Vlg5Z1hOShm0eYmjtsqSqg',
            ...     source_id='pqTn4vBZRdS5hYw0TBt0pQ',
            ...     include_config=True,
            ...     include_run_stats=True,
            ...     include_pipeline_backlog=True)

            {
              "items_fetched_total": 2,
              "last_error": "",
              "last_check_at": "2019-01-23T10:23:23",
              "paused": false,
              "error_count": 0,
              "id": "pqTn4vBZRdS5hYw0TBt0pQ",
              "total_error_count": 0,
              "project_id": "Vlg5Z1hOShm0eYmjtsqSqg",
              "config": {
                "dataloader_plugin_options": {
                  "source_file": "path:/tmp/test.csv"
                },
                "dataloader_options": {
                  "map_title": "title",
                  "project_id": "Vlg5Z1hOShm0eYmjtsqSqg",
                  "plugin_name": "csv_plugin"
                }
              },
              "status": "complete",
              "total_runs": 1,
              "pipeline_workflow_id": "S0fVQ-K0TmS1UgT0msZRBA",
              "last_error_at": null,
              "last_update_at": "2019-01-23T10:23:23",
              "last_success_at": "2019-01-23T10:23:23",
              "items_fetched_last_run": 2,
              "tenant": "squirro",
              "next_run_time_at": "2019-01-23T10:52:51",
              "name": "test source",
              "scheduling_options": {
                "repeat": "30m",
                "schedule": true
              },
              "created_at": "2019-01-23T10:23:23",
              "modified_at": "2019-01-23T10:23:23",
              "processed": true,
              "pipeline_backlog": 10
            }
        """

        url = (
            "%(ep)s/%(version)s/%(tenant)s"
            "/projects/%(project_id)s"
            "/sources/%(source_id)s"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
            "source_id": source_id,
        }

        params = {}
        if include_config:
            params["include_config"] = include_config
        if include_run_stats:
            params["include_run_stats"] = include_run_stats
        if include_pipeline_backlog:
            params["include_pipeline_backlog"] = include_pipeline_backlog

        res = self._perform_request("get", url, params=params)
        return self._process_response(res)

    def new_source(
        self,
        project_id,
        name,
        config,
        scheduling_options=None,
        pipeline_workflow_id=None,
        source_id=None,
        paused=False,
        use_default_options=None,
    ):
        """Create a new source.

        :param project_id: Project identifier.
        :param name: Name for the Source.
        :param config: dict, config including dataloader_options and
            dataloader_plugin_options for the Source.
        :param scheduling_options: dict, scheduling options for the run of a
            Source.
        :param pipeline_workflow_id: Optional id of the pipeline workflow to
            apply to the data of this Source. If not specified, then the
            default workflow of the project with `project_id` will be applied.
        :param source_id: Optional string parameter to create the
            source with the provided id. The length of the parameter must
            be 22 characters. Useful when exporting and importing projects
            across multiple Squirro servers.
        :param paused: Optional boolean. Indicate whether to immediately start
            data loading, or rather create the source in a paused state
        :param use_default_options: Optional boolean. Indicate whether or not to use
            the default mappings for facets, fields, scheduling_options and pipeline
            workflow provided by the dataloader plugin itself.
            Setting this to `True` will throw a 400 HTTP error code if these default
            mappings are not available for a specific plugin
        :returns: A dictionary which contains the new source.

        Example::

            >>> client.new_source(
            ...     project_id='Vlg5Z1hOShm0eYmjtsqSqg',
            ...     name='test source',
            ...     config={
            ...         "dataloader_plugin_options": {
            ...             "source_file": "path:/tmp/test.csv"
            ...         },
            ...         "dataloader_options": {
            ...             "plugin_name": "csv_plugin",
            ...             "project_id": 'Vlg5Z1hOShm0eYmjtsqSqg',
            ...             "map_title": "title"
            ...             }
            ...         },
            ...     scheduling_options={'schedule': True, 'repeat': '30m'})

            {
              "items_fetched_total": 0,
              "last_error": "",
              "last_check_at": null,
              "paused": false,
              "error_count": 0,
              "id": "601AoqmkSFWGt4sAwaX8ag",
              "total_error_count": 0,
              "project_id": "Vlg5Z1hOShm0eYmjtsqSqg",
              "status": "queued",
              "total_runs": 0,
              "pipeline_workflow_id": "S0fVQ-K0TmS1UgT0msZRBA",
              "last_error_at": null,
              "last_update_at": null,
              "last_success_at": null,
              "items_fetched_last_run": 0,
              "tenant": "squirro",
              "next_run_time_at": "2019-01-23T10:32:13",
              "name": "test source",
              "scheduling_options": {
                "repeat": "30m",
                "schedule": true
              },
              "created_at": "2019-01-23T10:32:13",
              "modified_at": "2019-01-23T10:32:13",
              "processed": false
            }
        """
        headers = {"Content-Type": "application/json"}
        url = "%(ep)s/%(version)s/%(tenant)s/projects/%(project_id)s/sources"
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        # build data
        data = {"config": config, "name": name, "paused": paused}
        if source_id is not None:
            data["source_id"] = source_id
        if pipeline_workflow_id is not None:
            data["pipeline_workflow_id"] = pipeline_workflow_id
        if scheduling_options is not None:
            data["scheduling_options"] = scheduling_options
        if use_default_options is not None:
            data["use_default_options"] = use_default_options

        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [200, 201])

    def modify_source(
        self,
        project_id,
        source_id,
        name=None,
        config=None,
        scheduling_options=None,
        pipeline_workflow_id=None,
        enable_scheduling=None,
        validate_schema=None,
    ):
        """Modify an existing source.

        :param project_id: Project identifier.
        :param source_id: Source identifier.
        :param pipeline_workflow_id: Optional pipeline workflow id to change
            the source to.
        :param config: Changed config of the source.

        :returns: A dictionary which contains the source.

        Example::

            >>> client.modify_source(
            ...     project_id='Vlg5Z1hOShm0eYmjtsqSqg',
            ...     source_id='601AoqmkSFWGt4sAwaX8ag',
            ...     name="new name")

            {
              "pipeline_workflow_id": "S0fVQ-K0TmS1UgT0msZRBA",
              "name": "new name",
              "scheduling_options": {
                "repeat": "30m",
                "schedule": true
              },
              "created_at": "2019-01-23T10:32:13",
              "modified_at": "2019-01-23T10:34:41",
              "paused": false,
              "processed": true,
              "project_id": "Vlg5Z1hOShm0eYmjtsqSqg",
              "id": "601AoqmkSFWGt4sAwaX8ag",
              "tenant": "squirro"
            }

        """

        headers = {"Content-Type": "application/json"}
        url = (
            "%(ep)s/%(version)s/%(tenant)s"
            "/projects/%(project_id)s/sources/%(source_id)s"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
            "source_id": source_id,
        }

        # build data
        data = {}
        if name is not None:
            data["name"] = name
        if config is not None:
            data["config"] = config
        if scheduling_options is not None:
            data["scheduling_options"] = scheduling_options
        if pipeline_workflow_id is not None:
            data["pipeline_workflow_id"] = pipeline_workflow_id
        if enable_scheduling is not None:
            data["enable_scheduling"] = enable_scheduling
        if validate_schema is not None:
            data["validate_schema"] = validate_schema

        res = self._perform_request("put", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [200])

    def delete_source(self, project_id, source_id):
        """Delete an existing Source.

        :param project_id: Project identifier.
        :param source_id: Source identifier.

        Example::

            >>> client.delete_source('Vlg5Z1hOShm0eYmjtsqSqg',
            ...                      'oTvI6rlaRmKvmYCfCvLwpw')

        """

        url = (
            "%(ep)s/%(version)s/%(tenant)s"
            "/projects/%(project_id)s"
            "/sources/%(source_id)s"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
            "source_id": source_id,
        }

        res = self._perform_request("delete", url)
        self._process_response(res, [204])

    def get_source_logs(self, project_id, source_id, last_n_log_lines):
        """Get the run logs of a particular source run.

        :param project_id: Project identifier.
        :param source_id: Source identifier.
        :param last_n_log_lines: Last n log lines from the last run of the source.

        Example::

            >>> client.get_source_logs('Vlg5Z1hOShm0eYmjtsqSqg',
            ...                     'hw8j7LUBRM28-jAellgQdA',
            ...                     10)
        """

        url = (
            "%(ep)s/%(version)s/%(tenant)s/projects/%(project_id)s"
            "/sources/%(source_id)s/logs"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
            "source_id": source_id,
        }

        params = {}
        if last_n_log_lines:
            params["last_n_log_lines"] = last_n_log_lines

        res = self._perform_request("get", url, params=params)
        return self._process_response(res)

    def kill_source(self, project_id, source_id):
        """Try to terminate (SIGTERM) a dataload job if it is already running. After a
        fixed timeout, a SIGKILL signal is sent instead.

        :param project_id: Project identifier.
        :param source_id: Source identifier.

        Example::

            >>> client.kill_source('Vlg5Z1hOShm0eYmjtsqSqg',
            ...                     'hw8j7LUBRM28-jAellgQdA')
        """

        url = (
            "%(ep)s/%(version)s/%(tenant)s/projects/%(project_id)s"
            "/sources/%(source_id)s/kill"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
            "source_id": source_id,
        }

        res = self._perform_request("post", url)
        self._process_response(res, [200, 204])

    def pause_source(self, project_id, source_id):
        """Pause a source.

        :param project_id: Project identifier.
        :param source_id: Source identifier.

        Example::

            >>> client.pause_source('Vlg5Z1hOShm0eYmjtsqSqg',
            ...                     'hw8j7LUBRM28-jAellgQdA')
        """

        url = (
            "%(ep)s/%(version)s/%(tenant)s/projects/%(project_id)s"
            "/sources/%(source_id)s/pause"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
            "source_id": source_id,
        }

        res = self._perform_request("put", url)
        self._process_response(res, [200, 204])

    def resume_source(self, project_id, source_id):
        """Resume a paused source.

        :param project_id: Project identifier.
        :param source_id: Source identifier.

        Example::

            >>> client.resume_source(
            ...     'Vlg5Z1hOShm0eYmjtsqSqg',
            ...     'hw8j7LUBRM28-jAellgQdA')
        """

        url = (
            "%(ep)s/%(version)s/%(tenant)s"
            "/projects/%(project_id)s"
            "/sources/%(source_id)s/resume"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
            "source_id": source_id,
        }

        res = self._perform_request("put", url)
        self._process_response(res, [200, 204])

    def run_source(self, project_id, source_id):
        """Runs a source now.

        :param project_id: Project identifier.
        :param source_id: Source identifier.

        Example::

            >>> client.run_source(
            ...     'Vlg5Z1hOShm0eYmjtsqSqg',
            ...     'hw8j7LUBRM28-jAellgQdA')
        """

        url = (
            "%(ep)s/%(version)s/%(tenant)s"
            "/projects/%(project_id)s"
            "/sources/%(source_id)s/run"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
            "source_id": source_id,
        }
        res = self._perform_request("put", url)
        self._process_response(res, [200, 204])

    def reset_source(self, project_id, source_id, delete_source_data=None):
        """Resets and run the source.

        :param project_id: Project identifier.
        :param source_id: Source identifier.
        :param delete_source_data: Bool, to determine whether to delete the
            data associated with a source or not

        Example::

            >>> client.reset_source(
            ...     'Vlg5Z1hOShm0eYmjtsqSqg',
            ...     'hw8j7LUBRM28-jAellgQdA')
        """

        url = (
            "%(ep)s/%(version)s/%(tenant)s"
            "/projects/%(project_id)s"
            "/sources/%(source_id)s/reset"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
            "source_id": source_id,
        }
        params = {}

        if delete_source_data:
            params["delete_source_data"] = delete_source_data

        res = self._perform_request("put", url, params=params)
        self._process_response(res, [200, 204])

    def get_max_inc(self, project_id, source_id):
        """Fetches the maximum incremental value of a source.

        :param project_id: Project identifier.
        :param source_id: Source identifier.

        Example::

            >>> client.get_max_inc(
            ...     'Vlg5Z1hOShm0eYmjtsqSqg',
            ...     'hw8j7LUBRM28-jAellgQdA')
        """

        url = (
            "%(ep)s/%(version)s/%(tenant)s"
            "/projects/%(project_id)s"
            "/sources/%(source_id)s/max_inc_value"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
            "source_id": source_id,
        }
        res = self._perform_request("get", url)
        return self._process_response(res)

    def set_max_inc(self, project_id, source_id, max_inc_value):
        """Sets the maximum incremental value of the incremental
        column of a source.

        :param project_id: Project identifier.
        :param source_id: Source identifier.
        :param max_inc_val: The maximum incremental value to be set.

        Example::

            >>> client.set_max_inc(
            ...     'Vlg5Z1hOShm0eYmjtsqSqg',
            ...     'hw8j7LUBRM28-jAellgQdA',
            ...     '2020-08-17T19:10:33')
        """

        url = (
            "%(ep)s/%(version)s/%(tenant)s"
            "/projects/%(project_id)s"
            "/sources/%(source_id)s/max_inc_value"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
            "source_id": source_id,
        }
        data = {"data": {"max_inc_value": max_inc_value}}
        res = self._perform_request("put", url, data=json.dumps(data))
        self._process_response(res, [200, 204])

    def get_preview(self, project_id, config):

        """Preview the source configuration.

        :param project_id: Project identifier.
        :param config: Provider configuration.
        :returns: A dictionary which contains the source preview items.

        Example::

            >>> client.get_preview(
            ...     project_id,
            ...     config={
            ...         "dataloader_plugin_options": {
            ...             "source_file": "path:/tmp/test.csv"
            ...         },
            ...         "dataloader_options": {
            ...             "plugin_name": "csv_plugin",
            ...             "project_id": project_id,
            ...             "map_title": "title"
            ...             }
            ...         })

            {
              "count": 2,
              "items": [
                {
                  "id": "CTHQDLwzQsOq93zHAUcCRg",
                  "name": "name01",
                  "title": "title01"
                },
                {
                  "id": ",yYNWBDgQQ2Uhuz32boDAg",
                  "name": "name02",
                  "title": "title02"
                }
              ],
              "data_schema": [
                "name",
                "title"
              ]
            }
        """

        url = ("%(ep)s/%(version)s/%(tenant)s/projects/%(project_id)s/" "preview") % {
            "ep": self.topic_api_url,
            "project_id": project_id,
            "version": self.version,
            "tenant": self.tenant,
        }

        # build params
        params = {"config": json.dumps(config)}

        res = self._perform_request("get", url, params=params)
        return self._process_response(res)
