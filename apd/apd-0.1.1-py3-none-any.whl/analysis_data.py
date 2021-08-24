###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

# ("Charm", "D2HH", use_both_polarities=True)
# Calling "datasets" returns a list of PFNs corrosponding to the requested dataset
# Keyword arguments are interpreted as tags
# Combining all of the tags must give a unique dataset or an error is raised
# To get PFNs from multiple datasets pass lists as the arguments this is
# equivalent. i.e.
#     datasets(eventtype="27163904", year=[2017, 2018], polarity=["magup", "magdown"])
# is the same as:
#     datasets(eventtype="27163904", year=2017, polarity="magup") +
#     datasets(eventtype="27163904", year=2017, polarity="magdown") +
#     datasets(eventtype="27163904", year=2018, polarity="magup") +
#     datasets(eventtype="27163904", year=2018, polarity="magdown")
import logging

from apd.ap_info import SampleList, fetch_ap_info, load_ap_info

logger = logging.getLogger("apd")


class AnalysisData:
    """ Class allowing to access the metadata for a specific analysis """

    def __init__(
        self,
        working_group,
        analysis,
        metadata_cache=None,
        api_url="https://lbap.app.cern.ch",
    ):
        """Constructor that can either fetch the data from the AP service
        or load from the cache.
        """
        self.working_group = working_group
        self.analysis = analysis
        if metadata_cache:
            logger.debug("Using metadata cache %s", metadata_cache)
            self.samples = load_ap_info(metadata_cache, working_group, analysis)
        else:
            logger.debug("Fetching Analysis Production data from %s", api_url)
            self.samples = fetch_ap_info(working_group, analysis, None, api_url)

    def __call__(self, tag=None, value=None, eventtype=None, year=None, polarity=None):
        """ Main method that returns the dataset info """

        def process_arg(metadata_attr, arg_val, pinfo):
            if isinstance(arg_val, (list, tuple)):
                # Here we do the union of all requests
                # Could be done better by extra method on ProductionsInfo
                ret = SampleList()
                for v in arg_val:
                    ret = ret.union(pinfo.filter(metadata_attr, v))
            else:
                ret = pinfo.filter(metadata_attr, arg_val)
            return ret

        samples = self.samples
        if tag:
            if value:
                logger.debug("Filtering for tag %s/%s", tag, value)
                samples = process_arg(tag, value, samples)
            else:
                raise Exception(f"Please specify value for tag {tag}")
        if eventtype:
            logger.debug("Filtering for eventype %s", eventtype)
            samples = process_arg("eventtype", eventtype, samples)
        if year:
            logger.debug("Filtering for year %s", year)
            samples = process_arg("datatype", year, samples)
        if polarity:
            logger.debug("Filtering for polarity %s", polarity)
            samples = process_arg("polarity", lambda x: polarity in x, samples)

        return samples.PFNs()
