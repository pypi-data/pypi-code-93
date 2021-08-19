import json


class PipelineWorkflowMixin(object):

    #
    # Pipeline Workflows
    #

    def get_pipeline_workflows(self, project_id, omit_steps=False, omit_sources=False):
        """Return all pipeline workflows for project with `project_id`.

        :param project_id: id of the project within tenant
        :param omit_steps: whether to omit steps in the response for better
                           performance.
        :param omit_sources: whether to omit in the response the data sources
                             which are configured to use each pipeline
                             workflow.
        :return: A list of pipeline workflow dictionaries.

        Example::

            >>> client.get_pipeline_workflows('project_id_1')
            [{'id': 'pipeline_workflow_id_1',
              'project_id': 'project_id_1',
              'name': 'Pipeline Workflow 1',
              'project_default': True,
              'steps': [
                 {"name": "Pipelet",
                  "type": "pipelet",
                  "display_name": "PermID OpenCalais",
                  "id": "XPOxEgNSR3W4TirOwOA-ng",
                  "config": {"config": {"api_key": "AGa865", "confidence": 0.7},
                             "pipelet": "searches/PermID Entities Enrichment"},
                 },
                 {"name": "Index",
                  "type": "index",
                  ...
                 }
              ]
             },
             {'id': 'pipeline_workflow_id_2',
              ...
             },
             ...
            ]
        """
        headers = {"Content-Type": "application/json"}

        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/" "pipeline_workflows" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        data_dict = dict(omit_steps=omit_steps, omit_sources=omit_sources)

        res = self._perform_request(
            "get", url, data=json.dumps(data_dict), headers=headers
        )

        return self._process_response(res)

    def get_pipeline_workflow(
        self, project_id, workflow_id, omit_steps=False, omit_sources=False
    ):
        """Return a specific pipeline workflow `workflow_id` in project with `project_id`.

        :param project_id: project id
        :param workflow_id: pipeline workflow id
        :param omit_steps: whether to omit steps in the response for better
                           performance.
        :param omit_sources: whether to omit in the response the data sources which are
                             configured to use this pipeline workflow.
        :return: A dictionary of the pipeline workflow.

        Example::

            >>> client.get_pipeline_workflow('project_id_1', 'workflow_id_1')
            {'id': 'pipeline_workflow_id_1',
             'project_id': 'project_id_1',
             'name': 'Pipeline Workflow 1',
             'steps': [
                {"name": "Pipelet",
                 "type": "pipelet",
                 "display_name": "PermID OpenCalais",
                 "id": "XPOxEgNSR3W4TirOwOA-ng",
                 "config": {"config": {"api_key": "AGa8A65", "confidence": 0.7},
                            "pipelet": "searches/PermID Entities Enrichment"},
                },
                {"name": "Index",
                 "type": "index",
                  ...
                }
             ]
            }
        """
        headers = {"Content-Type": "application/json"}

        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "pipeline_workflows/%(workflow_id)s"
            % {
                "ep": self.topic_api_url,
                "tenant": self.tenant,
                "project_id": project_id,
                "workflow_id": workflow_id,
            }
        )

        data_dict = dict(omit_steps=omit_steps, omit_sources=omit_sources)

        res = self._perform_request(
            "get", url, data=json.dumps(data_dict), headers=headers
        )

        return self._process_response(res)

    def new_pipeline_workflow(self, project_id, name, steps=None):
        """Creates a new pipeline workflow.

        :param project_id: project id
        :param name: name of workflow
        :param steps: list of sets of properties that require at least the
            step `type` to be specified and be one of a list of known
            types. Steps need to be ordered in a specific way. If `steps` is
            None or the empty list, the default steps will be set.

        Example::

            >>> client.new_pipeline_workflow(
            >>>     project_id='project_id_1',
            >>>     name='Pipeline Workflow 1',
            >>>     steps=[{"name": "Index",
            >>>             "type": "index"}])
        """
        if name is None:
            raise ValueError("Name needs to be specified.")

        data_dict = dict(name=name)

        if steps is not None:
            if not isinstance(steps, list):
                raise ValueError("Steps need to be a list of dicts")
            if steps:
                data_dict["steps"] = steps

        headers = {"Content-Type": "application/json"}

        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/" "pipeline_workflows" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        res = self._perform_request(
            "post", url, data=json.dumps(data_dict), headers=headers
        )

        return self._process_response(res, [201])

    def modify_pipeline_workflow(
        self, project_id, workflow_id, name=None, steps=None, project_default=None
    ):
        """Updates a pipeline workflow

        :param project_id: project id
        :param workflow_id: pipeline workflow id
        :param name: name of workflow or None if no change
        :param steps: list of sets of properties that require at least the
            step `type` to be specified and be one of a list of known
            types. Steps need to be ordered in a specific way. Can be None if no
            change.
        :param project_default: whether pipeline workflow should become the new
            project default workflow. Allowed values are True or None. It is not
            possible to clear the project_default because at any time exactly
            one project default pipeline workflow needs to exist. To change the
            project default workflow, instead set True on the new default
            workflow which will as a side-effect clear the previous default.

        Example::

            >>> client.modify_pipeline_workflow(
            >>>     project_id='project_id_1',
            >>>     workflow_id='pipeline_workflow_id_1',
            >>>     name='Pipeline Workflow 1',
            >>>     steps=[{"name": "Index",
            >>>             "type": "index"}])
        """
        data_dict = {}

        if name is not None:
            data_dict["name"] = name

        if steps is not None:
            data_dict["steps"] = steps

        if project_default is not None:
            data_dict["project_default"] = project_default

        headers = {"Content-Type": "application/json"}

        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "pipeline_workflows/%(workflow_id)s"
            % {
                "ep": self.topic_api_url,
                "tenant": self.tenant,
                "project_id": project_id,
                "workflow_id": workflow_id,
            }
        )

        res = self._perform_request(
            "put", url, data=json.dumps(data_dict), headers=headers
        )

        return self._process_response(res, [200])

    def delete_pipeline_workflow(self, project_id, workflow_id):
        """Deletes a pipeline workflow as long as it is no longer needed.
        Project default workflows cannot be deleted and neither can workflows
        that still have sources referring to them.

        :param project_id: project id
        :param workflow_id: pipeline workflow id
        :return: 204 if deletion has been successful

        Example::

            >>> client.delete_pipeline_workflow(
            >>>     project_id='project_id_1',
            >>>     workflow_id='pipeline_workflow_id_1',
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "pipeline_workflows/%(workflow_id)s"
            % {
                "ep": self.topic_api_url,
                "tenant": self.tenant,
                "project_id": project_id,
                "workflow_id": workflow_id,
            }
        )

        res = self._perform_request("delete", url)

        return self._process_response(res, [204])

    def move_pipeline_workflow_step(self, project_id, workflow_id, step_id, after):
        """Move a pipelet step within a workflow.

        :param project_id: id of project that owns the workflow
        :param workflow_id: pipeline workflow id
        :param step_id: id of the pipelet step to move
        :param after: id of the step after which the pipelet step
                      should be moved or None if pipelet is supposed to be first
        :return: updated workflow

        Example::

            >>> client.move_pipeline_workflow_step('2aEVClLRRA-vCCIvnuEAvQ',
            ...                                    'Ue1OceLkQlyz21wpPqml9Q',
            ...                                    'nJXpKUSERmSgQRjxX7LrZw',
            ...                                    'language-detection')
        """
        headers = {"Content-Type": "application/json"}

        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "pipeline_workflows/%(workflow_id)s/steps/%(step_id)s/move"
            % {
                "ep": self.topic_api_url,
                "tenant": self.tenant,
                "project_id": project_id,
                "workflow_id": workflow_id,
                "step_id": step_id,
            }
        )

        res = self._perform_request(
            "put", url, data=json.dumps({"after": after}), headers=headers
        )

        return self._process_response(res, [202])

    def get_pipeline_workflows_presets(self, project_id):
        """Return a list of pre-made pipeline workflows for covering various use cases.

        :param project_id: the Id of the project
        :return: a list of dictionaries where each dictionary represents a pipeline
                 workflow preset.
        """
        headers = {"Accept": "application/json"}

        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/pipeline_workflows/presets"
            % {
                "ep": self.topic_api_url,
                "tenant": self.tenant,
                "project_id": project_id,
            }
        )

        res = self._perform_request("get", url, headers=headers)

        return self._process_response(res)

    def rerun_pipeline_workflow(self, project_id, workflow_id, from_index=False):
        """Rerun a pipeline workflow using the data of its configured data sources.

        :param project_id: the Id of the project that this workflow belongs to.
        :param workflow_id: the Id of the pipeline workflow to rerun.
        :param from_index: if True then this flag indicates that rerun will use the
            indexed Squirro items as input to the workflow for ingestion.
        """
        headers = {"Accept": "application/json"}

        params = {"from_index": from_index}

        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/"
            "pipeline_workflows/%(workflow_id)s/rerun"
            % {
                "ep": self.topic_api_url,
                "tenant": self.tenant,
                "project_id": project_id,
                "workflow_id": workflow_id,
            }
        )

        res = self._perform_request("post", url, params=params, headers=headers)

        return self._process_response(res)
