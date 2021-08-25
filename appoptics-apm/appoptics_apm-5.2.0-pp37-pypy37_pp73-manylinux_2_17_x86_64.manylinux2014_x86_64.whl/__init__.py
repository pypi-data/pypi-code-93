#    Copyright 2021 SolarWinds, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import appoptics_apm.ao_logging
import appoptics_apm.inst_logging
from appoptics_apm.util import *
from appoptics_apm.version import __version__

# API for agent-internal logger
disable_logger = appoptics_apm.ao_logging.disable_logger
logger = appoptics_apm.ao_logging.logger

# API for agent configuration
config = AppOpticsApmConfig()

# Intialize agent
appoptics_apm_init()

# Report an status event after everything is done.
report_layer_init('Python')

appoptics_apm.inst_logging.wrap_logging_module()

# API for trace context in logs
get_log_trace_id = appoptics_apm.inst_logging.get_log_trace_id
