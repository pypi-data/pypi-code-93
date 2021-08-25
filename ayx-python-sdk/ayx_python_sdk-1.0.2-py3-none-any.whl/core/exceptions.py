# Copyright (C) 2021 Alteryx, Inc. All rights reserved.
#
# Licensed under the ALTERYX SDK AND API LICENSE AGREEMENT;
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.alteryx.com/alteryx-sdk-and-api-license-agreement
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Exception class definition."""


class WorkflowRuntimeError(Exception):
    """Exception for a workflow runtime error."""

    def __init__(self, msg: "str"):
        """
        Construct a workflow runtime error.

        Parameters
        ----------
        msg
            Human-readable description of the error that occurred.
        """
        super().__init__(str(msg))


class AnchorNotFoundException(Exception):
    """Exception for when a requested anchor can't be found for the tool."""
