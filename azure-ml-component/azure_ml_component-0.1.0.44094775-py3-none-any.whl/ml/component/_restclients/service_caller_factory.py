# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from .service_caller import DesignerServiceCaller
import _thread


class _DesignerServiceCallerFactory:

    caller_cache_by_workspace_id = {}

    @staticmethod
    def get_instance(workspace, from_cli=False):
        """Get a instance of designer service caller.

        :param workspace: workspace
        :param from_cli: mark if this service caller is used from cli.
        """
        workspace_id = workspace._workspace_id
        cache = _DesignerServiceCallerFactory.caller_cache_by_workspace_id
        if workspace_id not in cache:
            cache[workspace_id] = DesignerServiceCaller(workspace)
            if from_cli:
                cache[workspace_id]._set_from_cli_for_telemetry()
            else:
                # For SDK, we cache all the computes at the initialization of designer service caller
                _thread.start_new_thread(cache_all_computes, (cache[workspace_id], ))
        return cache[workspace_id]


def cache_all_computes(service_caller):
    try:
        service_caller.cache_all_computes_in_workspace()
    except Exception:
        # Catch all exceptions here
        pass
