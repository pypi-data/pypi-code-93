# coding: utf-8
"""
    assetic.layertools  (layertools.py)
    Tools to assist with using arcgis integration with assetic
"""
from __future__ import absolute_import

import arcpy
import sys
import logging
from assetic import FunctionalLocationRepresentation, \
    AssetToolsCompleteAssetRepresentation
from assetic.tools.functional_location_tools import FunctionalLocationTools

try:
    import pythonaddins
except ImportError:
    # ArcGIS Pro doesn't have this library
    pass
from typing import List, Any
import assetic
import six
from arcgis2geojson import arcgis2geojson
import json
from ..config import Config
from .commontools import CommonTools
from .gis_tools import GISTools
from .calculation_tools import CalculationTools


class LayerTools(object):
    """
    Class to manage processes that relate to a GIS layer

    layerconfig arg is not mandatory and during testing is not passed in.
    """

    # define error codes for the asset creation
    results = {
        "success": 0,
        "error": 1,
        "skip": 2,
        "partial": 3,
    }

    def __init__(self, layerconfig=None):

        self._is_valid_config = True
        self.config = Config()

        self.logger = logging.getLogger(__name__)
            
        if layerconfig is None:
            if not self.config.layerconfig:
                self._is_valid_config = False
                self.logger.error(
                    "Assetic ESRI package missing layer configuration")
                return
            self._layerconfig = self.config.layerconfig
        else:
            self._layerconfig = layerconfig

        self._assetconfig = self._layerconfig.assetconfig
        self.asseticsdk = self.config.asseticsdk

        # initialise common tools so can use messaging method
        self.commontools = CommonTools()
        self.commontools.force_use_arcpy_addmessage = \
            self.config.force_use_arcpy_addmessage
        # instantiate assetic.AssetTools
        self.assettools = assetic.AssetTools(self.asseticsdk.client)

        # get logfile name to help user find it
        self.logfilename = ""
        for h in self.logger.handlers:
            try:
                self.logfilename = h.baseFilename
            except:
                pass

        # self.odata = assetic.tools.odata.OData()
        # self._layerconfig = None

        self.fltools = FunctionalLocationTools(self.asseticsdk.client)
        self.gis_tools = GISTools(self._layerconfig, self.asseticsdk.client)

        if self.config.layerconfig.calculations_plugin:
            try:
                global_namespace = {
                    "__file__": __file__,
                    "__name__": "custom",
                }
                exec(compile(open(self.config.layerconfig.calculations_plugin,
                                   "rb").read(),
                              self.config.layerconfig.calculations_plugin,
                              'exec'), global_namespace)
            except Exception as ex:
                self.logger.error(str(ex))
                self._calc_tools = CalculationTools()
            else:
                try:
                    self._calc_tools = global_namespace["FieldCalculations"]()
                except Exception as ex:
                    self.logger.error(str(ex))
                    self._calc_tools = CalculationTools()
        else:
            self._calc_tools = CalculationTools()

        self._bulk_threshold = 250
        if self._layerconfig.bulk_threshold:
            self._bulk_threshold = self._layerconfig.bulk_threshold

    @property
    def is_valid_config(self):
        # type: () -> bool
        """
        Asset Layer Configuration
        Cache the XML content so that we don't continually reload it as we
        access it in _get_cat_config
        :return:
        """
        return self._is_valid_config

    @property
    def layerconfig(self):
        # type: () -> dict
        """
        Asset Layer Configuration
        Cache the XML content so that we don't continually reload it as we
        access it in _get_cat_config
        :return:
        """
        if self._layerconfig is None:
            self._layerconfig = \
                self.config.layerconfig.get_asset_config_for_layers()

        return self._layerconfig

    @property
    def fl_layerconfig(self):
        # type: () -> dict
        """
        Functional Location Layer configuration
        Cache the XML content so that we don't continually reload it
        :return:
        """
        return self.config.layerconfig.fcnlayerconfig

    @property
    def bulk_threshold(self):
        """Gets the minimum threshold before bulk operation applied.
        :return: The integer to set for minimum threshold
        :rtype: int
        """
        return self._bulk_threshold

    @bulk_threshold.setter
    def bulk_threshold(self, value):
        """Sets the minimum threshold before bulk operation applied.
        :param value: The integer to set for minimum threshold
        :type: int
        """
        self._bulk_threshold = value

    def _get_fl_layer_config(self, lyr, purpose):
        # type: (Any, str) -> (dict, List[str],str)
        """
        Returns the configuration for dedicated functional location
        layer, as well as the fields to be retrieved from the cursor.

        :param lyr: arcgis layer
        :param purpose:
        :return: dict defining config as well as a list of fields
        in the layer
        """

        lyrs = [l for l in self.config.layerconfig.fcnlayerconfig
                if l['layer'] == lyr.name]

        if len(lyrs) == 0:
            return None, None, None

        lyr_config = lyrs[0]

        actuallayerflds = []
        if 'arcpy' in sys.modules:
            for fld in arcpy.Describe(lyr).Fields:
                actuallayerflds.append(str(fld.Name))
        else:
            # useful for debugging
            actuallayerflds.extend(list(lyr.df.columns))

        if purpose in ["create", "update"]:
            cf = list(six.viewvalues(lyr_config["fl_corefields"]))
            af = list(six.viewvalues(lyr_config['fl_attributefields']))

            fields = cf + af

            missing = []
            for f in fields:
                if f not in actuallayerflds:
                    missing.append(f)

            if len(missing) > 0:
                msg = ("Following fields defined in the XML configuration "
                       "({0}) missing from layer. "
                       "Unable to process.".format(', '.join(missing)))
                self.logger.error(msg)
                return None, None, None
        else:
            fields = None

        idfield = None
        if purpose in ["delete", "display"]:
            # get the Assetic unique ID column in ArcMap
            if "id" in lyr_config["fl_corefields"]:
                idfield = lyr_config["fl_corefields"]["id"]
            else:
                if "functional_location_id" in lyr_config["fl_corefields"]:
                    idfield = \
                        lyr_config["fl_corefields"]["functional_location_id"]
                else:
                    msg = "Functional Location ID and/or GUID field " \
                          "must be defined for layer {0}".format(lyr.name)
                    self.commontools.new_message(msg)
                    self.logger.warning(msg)
                    return None, None, None

        if idfield is not None and idfield not in actuallayerflds:
            msg = "Functional Location ID Field [{0}] is defined in " \
                  "configuration but is not" \
                  " in layer {1}, check logfile '{2}' for field list" \
                  "".format(idfield, lyr.name, self.logfilename)
            self.commontools.new_message(msg)
            self.logger.warning(msg)
            msg = "Fields in layer {0} are: {1}".format(
                lyr.name, actuallayerflds)
            self.logger.warning(msg)
            return None, None, None

        return lyr_config, fields, idfield

    def get_layer_config(self, lyr, purpose):
        """
        For the given layer get the config settings. Depending on purpose not
        all config is required, so only get relevant config
        :param lyr: is the layer to process (not layer name but ArcMap layer)
        :param purpose: one of 'create','update','delete','display'
        """
        lyr_config_list = [
            j for j in self._assetconfig if j["layer"] == lyr.name]
        if len(lyr_config_list) == 0:
            if purpose not in ["delete"]:
                msg = "No configuration for layer {0}".format(lyr.name)
                self.commontools.new_message(msg)
            return None, None, None

        lyr_config = lyr_config_list[0]

        # create a list of the fields in the layer to compare config with
        actuallayerflds = list()

        if 'arcpy' in sys.modules:
            for fld in arcpy.Describe(lyr).Fields:
                actuallayerflds.append(str(fld.Name))
        else:
            actuallayerflds.extend(list(lyr.df.columns))

        if purpose in ["create", "update"]:
            # from config file build list of arcmap fields to query
            fields = list(six.viewvalues(lyr_config["corefields"]))
            if fields is None:
                msg = "missing 'corefields' configuration for layer {0}" \
                      "".format(lyr.name)
                self.commontools.new_message(msg)
                return None, None, None
            if "attributefields" in lyr_config:
                attfields = list(six.viewvalues(lyr_config["attributefields"]))
                if attfields != None:
                    fields = fields + attfields

            for component in lyr_config["components"]:
                compflds = list(six.viewvalues(component["attributes"]))
                if compflds:
                    fields = fields + compflds
                for dimension in component["dimensions"]:
                    dimflds = list(six.viewvalues(dimension["attributes"]))
                    if dimflds:
                        fields = fields + dimflds
            if "addressfields" in lyr_config.keys():
                addrfields = list(six.viewvalues(lyr_config["addressfields"]))
                if addrfields is not None:
                    fields = fields + addrfields
            if "functionallocation" in lyr_config.keys():
                flfields = list(
                    six.viewvalues(lyr_config['functionallocation']))
                if flfields is not None:
                    fields = fields + flfields

            calc_output_fields = list()
            if "calculations" in lyr_config.keys():
                for calculation in lyr_config["calculations"]:
                    calc_inputs = calculation["input_fields"]
                    if calc_inputs:
                        fields = fields + calc_inputs
                    calc_output = calculation['output_field']
                    calc_output_fields.append(calc_output)
                    if calc_output in actuallayerflds:
                        # field exists so include, optional since calc field
                        fields.append(calc_output)
            lyr_config["all_calc_output_fields"] = calc_output_fields

            # check fields from config are in layer
            if fields is not None:
                # create unique list (may not be unique if components or
                # dimensions config use same field for common elements
                fields = list(set(fields))
                # loop through list and check fields are in layer
                missing_fields = []
                for configfield in fields:
                    if configfield not in actuallayerflds and \
                            configfield not in calc_output_fields:
                        missing_fields.append(configfield)

                if len(missing_fields) > 0:
                    msg = "Fields [{0}] is defined in configuration but is " \
                          "not in layer {1}, check log file '{2}' for field " \
                          "list".format(', '.join(missing_fields)
                                        , lyr.name, self.logfilename)
                    self.commontools.new_message(msg)
                    self.logger.warning(msg)
                    msg = "Fields in layer {0} are: {1}".format(
                        lyr.name, actuallayerflds)
                    self.logger.warning(msg)
                    return None, None, None

                # remove any calc fields from the list
                fields[:] = [x for x in fields if x in actuallayerflds]
            # add these special fields if there as a geometry, to get geometry
            # and centroid data
            if 'geometry' in [x.type.lower()
                              for x in arcpy.Describe(lyr).Fields]:
                fields.append("SHAPE@")
                fields.append("SHAPE@XY")
            else:
                self.logger.debug("geometry type not found in layer, "
                                  "assuming this is a table i.e no features")
        else:
            fields = None

        idfield = None
        if purpose in ["delete", "display"]:
            # get the Assetic unique ID column in ArcMap
            assetid = None
            if "id" in lyr_config["corefields"]:
                idfield = lyr_config["corefields"]["id"]
            else:
                if "asset_id" in lyr_config["corefields"]:
                    idfield = lyr_config["corefields"]["asset_id"]
                else:
                    msg = "Asset ID and/or Asset GUID field must be defined " \
                          "for layer {0}".format(lyr.name)
                    self.commontools.new_message(msg)
                    self.logger.warning(msg)
                    return None, None, None

        if idfield is not None and idfield not in actuallayerflds:
            msg = "Asset ID Field [{0}] is defined in configuration but is not" \
                  " in layer {1}, check logfile '{2}' for field list".format(
                idfield, lyr.name, self.logfilename)
            self.commontools.new_message(msg)
            self.logger.warning(msg)
            msg = "Fields in layer {0} are: {1}".format(
                lyr.name, actuallayerflds)
            self.logger.warning(msg)
            return None, None, None

        return lyr_config, fields, idfield

    def _ind_update_assets(self, cursor, lyr, dialog):
        """
        Invidividually updates each asset using the passed in cursor
        object and layer information.

        :param cursor: database cursor with attached layer information
        :param lyr: <Layer>
        :param dialog: allows interacting with the ArcGIS console
        :return:
        """

        # create and asset pass and fail counters
        iFail = 0
        iPass = 0

        sel_set = lyr.getSelectionSet()
        if sel_set is None:
            self.logger.error(
                "No features selected.")
            return
        else:
            # get number of records to process for use with timing dialog
            if sel_set:
                selcount = len(sel_set)
            else:
                # haven't run query yet so just set a dummy count.
                selcount = 1

        lyr_config, fields, idfield = self.get_layer_config(lyr, "update")

        cnt = 1.0

        for row in cursor:
            chk = self._update_asset(row, lyr_config, fields)

            if self.commontools.is_desktop:
                if self.config.force_use_arcpy_addmessage:
                    # Using the progressor
                    arcpy.SetProgressorLabel(
                        "Updating Assets for layer {0}.\nProcessing "
                        "feature {1} of {2}".format(
                            lyr.name, int(cnt), selcount))
                    arcpy.SetProgressorPosition()
                else:
                    dialog.description = \
                        "Updating Assets for layer {0}." \
                        "\nProcessing feature {1} of {2}".format(
                            lyr.name, int(cnt), selcount)
                    dialog.progress = cnt / selcount * 100
            else:
                msg = "Updating Assets for layer {0}." \
                      "\nProcessing feature {1} of {2}".format(
                    lyr.name, int(cnt), selcount)
                self.commontools.new_message(msg)
                self.logger.info(msg)
            if not chk:
                iFail = iFail + 1
            else:
                iPass = iPass + 1

            # increment counter
            cnt = cnt + 1

        return iFail, iPass

    def create_asset(self, lyr, query=None):
        # type: (arcpy._mp.Layer, str) -> None
        """
        For the given layer create new assets for the selected features only if
        features have no assetic guid.

        :param lyr: is the layer to process (not layer name but ArcMap layer)
        :param query: optionally apply query filter
        """
        if not self._is_valid_config:
            self.logger.error("Invalid or missing configuration file, "
                        "asset creation aborted.")
            return
        self.logger.debug("create_asset. Layer={0}".format(lyr.name))

        # get configuration for layer
        lyr_config, fields, idfield = self.get_layer_config(lyr, "create")

        if lyr_config is None:
            self.logger.error("Returning early as layerfile "
                                         "has been misconfigured. See log output.")
            return

        # get number of records to process for use with timing dialog
        sel_set = lyr.getSelectionSet()
        if sel_set is None and query is None:
            self.logger.debug(
                "No features selected - must pass in valid 'where clause'.")
            return
        else:
            # get number of records to process for use with timing dialog
            if sel_set:
                selcount = len(sel_set)
            else:
                # haven't run query yet so just set a dummy count.
                selcount = 1

        progress_tool = self.commontools.get_progress_dialog(
            self.config.force_use_arcpy_addmessage, lyr.name, selcount)

        if self.commontools.is_desktop is False:
            selcount = 0

        prog_cnter = {
            "pass_cnt": 0,
            "fail_cnt": 0,
            "skip_cnt": 0,
            "partial_cnt": 0,
        }

        with progress_tool as dialogtools:
            if self.commontools.is_desktop and \
                    not self.config.force_use_arcpy_addmessage:
                dialog = dialogtools
                dialog.title = "Assetic Integration"
                dialog.description = "Creating Assets for layer {0}.".format(
                    lyr.name)
                dialog.canCancel = False

            # create an update cursor to allow updating
            with arcpy.da.UpdateCursor(lyr, fields, query) as cursor:

                # iterator to count number rows processed
                cnt = 1.0
                for row in cursor:
                    if self.commontools.is_desktop:
                        if self.config.force_use_arcpy_addmessage:
                            # Using the progressor
                            arcpy.SetProgressorLabel(
                                "Creating Assets for layer {0}.\nProcessing "
                                "feature {1} of {2}".format(
                                    lyr.name, int(cnt), selcount))
                            arcpy.SetProgressorPosition()
                        else:
                            dialog.description = \
                                "Creating Assets for layer {0}." \
                                "\nProcessing feature {1} of {2}".format(
                                    lyr.name, int(cnt), selcount)
                            dialog.progress = cnt / selcount * 100

                    drow = dict(zip(fields, row))

                    # attempt to create asset, components, dimensions
                    result_code = self._new_asset(drow, lyr_config, fields)

                    if result_code in \
                            [self.results['success'], self.results['partial']]:
                        # convert to a list in order of fields
                        lrow = [drow[f] for f in fields]

                        if result_code == self.results['success']:
                            suc = "successful"
                            prog_cnter['pass_cnt'] += 1
                        else:
                            suc = "partially successful"
                            prog_cnter['partial_cnt'] += 1
                        self.logger.debug(
                            "Update of asset ID {0}, updating ArcGIS row."
                            "".format(suc))

                        cursor.updateRow(lrow)

                    elif result_code == self.results['skip']:
                        prog_cnter['skip_cnt'] += 1
                    else:
                        prog_cnter['fail_cnt'] += 1

                    cnt = cnt + 1

        msg = ("Finished {0} Asset Creation: {1} Assets created ({2} partially"
               " created), {3} skipped (already created)"
               .format(lyr.name, str(prog_cnter['pass_cnt'])
                       , str(prog_cnter['partial_cnt'])
                       , str(prog_cnter['skip_cnt'])
                       ))

        if prog_cnter['fail_cnt'] > 0:
            msg = msg + ", {0} failed. See log for further details ({1})." \
                        "".format(
                            str(prog_cnter['fail_cnt']), self.logfilename)

        self.commontools.new_message(msg)

    @staticmethod
    def get_rows(lyr, fields, query=None):
        """
        A method to retrieve rows from a cursor and return them in
        dict form, if arcpy is imported.

        If not, expects lyr object to be iterable and return dicts
        of {col: val}.

        :param lyr:
        :param fields:
        :param query:
        :return:
        """
        rows = []

        if 'arcpy' in sys.modules:
            with arcpy.da.SearchCursor(lyr, fields, query) as cursor:

                # extract all of the important information out of the
                # cursor object
                for row in cursor:
                    # create a dict object from the cursor fields and
                    # the row values

                    dict_row = dict(zip(fields, row))

                    rows.append(dict_row)
        else:
            for row in lyr:
                rows.append(row)

        return rows

    def bulk_update_rows(self, rows, lyr, lyr_config):
        """
        Initiate bulk update of assets and components etc via Data Exchange
        :param rows: list of dictionaries, each row is a record from GIS
        :param lyr: the GIS layer being processed
        :param lyr_config: The configuration settings for the layer from
        the XML file
        :return: valid rows - the rows for where the asset actually exists
        """
        if len(lyr_config["all_calc_output_fields"]) > 0:
            # there are calculated fields to manage
            for row in rows:
                for calculation in lyr_config["calculations"]:
                    calc_val = self._calc_tools.run_calc(
                        calculation["calculation_tool"],
                        calculation["input_fields"]
                        , row, lyr_config["layer"])
                    if calc_val:
                        row[calculation["output_field"]] = calc_val

        lyr_name = lyr.name
        message = 'Commencing Data Exchange bulk update initiation'
        self.commontools.new_message(message, "Assetic Integration")

        # Bulk update assets will return valid rows, invalid rows are asset id
        # not found or disposed assets
        chk, valid_rows = self.gis_tools.bulk_update_assets(rows, lyr_name)
        if chk != 0:
            message = "Error encountered bulk updating assets"
            self.commontools.new_message(message, "Assetic Integration")
        if len(valid_rows) == 0:
            self.commontools.new_message("No valid assets for update"
                                         , "Assetic Integration")
        self.gis_tools.bulk_update_components(valid_rows, lyr_name)
        self.gis_tools.bulk_update_addresses(valid_rows, lyr_name)
        self.gis_tools.bulk_update_networkmeasures(valid_rows, lyr_name)
        self.gis_tools.bulk_update_asset_fl_assoc(valid_rows, lyr_name)
        if lyr_config["upload_feature"]:
            self.bulk_update_spatial(valid_rows, lyr, lyr_config)

        message = 'Completed initiating Data Exchange updates, updates may ' \
                  'still be in progress. Check Data Exchange History page'
        self.commontools.new_message(message, "Assetic Integration")
        return chk, valid_rows

    def individually_update_rows(self, rows, lyr_config, fields, dialog):
        # type: (List[dict], dict, List[str], Any) -> None
        """
        Iterates over the rows of the layerfile and updates each asset
        using API calls.

        :param rows: <List[dict]> a list of dicts where keys are the
        column names and values are cell contents
        :param lyr_config: <dict> dict defining the relationship
        between xml nodes and the layer's column values
        :param fields: <List[str]> a list of column names from the layer
        :param dialog: <Unsure> arcpy dialog object that allows arcpy
        messages to be pushed to console
        :return:
        """

        lyrname = lyr_config['layer']

        total = len(rows)

        # initialise counters for the log messages
        num_pass = 0
        num_fail = 0

        for i, row in enumerate(rows):
            success = self._update_asset(row, lyr_config, fields)

            if self.commontools.is_desktop:
                if self.config.force_use_arcpy_addmessage:
                    # Using the progressor
                    arcpy.SetProgressorLabel(
                        "Updating Assets for layer {0}.\nProcessing "
                        "feature {1} of {2}".format(
                            lyrname, i + 1, total))
                    arcpy.SetProgressorPosition()
                else:
                    dialog.description = \
                        "Updating Assets for layer {0}." \
                        "\nProcessing feature {1} of {2}".format(
                            lyrname, i + 1, total)
                    dialog.progress = (i + 1 / total) * 100
            else:
                msg = "Updating Assets for layer {0}." \
                      "\nProcessing feature {1} of {2}".format(
                    lyrname, i + 1, total)
                self.commontools.new_message(msg)
                self.logger.info(msg)

            if success:
                num_pass = num_pass + 1
            else:
                num_fail = num_fail + 1

        message = "Finished {0} Asset Update, {1} assets updated".format(
            lyrname, str(num_pass))

        if num_fail > 0:
            message = "{0}, {1} assets not updated. (Check log file '{2}')" \
                      "".format(message, str(num_fail), self.logfilename)

        self.commontools.new_message(message, "Assetic Integration")

    def update_assets(self, lyr, query=None):
        """
        For the given layer update assets for the selected features only
        where features have an assetic guid/asset id.
        :param lyr: is the layer to process (not layer name but ArcMap layer)
        :param query: optional attribute query to get selection
        """
        if not self._is_valid_config:
            self.logger.error("Invalid or missing configuration file, "
                        "asset update aborted.")
            return
        # get layer configuration from xml file
        lyr_config, fields, idfield = self.get_layer_config(lyr, "update")

        if lyr_config is None:
            return

        # "returns the layer's selection as a python set of object IDs"
        sel_set = lyr.getSelectionSet()
        if sel_set is None and query is None:
            self.logger.debug("No features selected - must pass in valid"
                                         " 'where clause'.")
            return
        else:
            # get number of records to process for use with timing dialog
            if sel_set:
                selcount = len(sel_set)
            else:
                # haven't run query yet so just set a dummy count.
                selcount = 1

        progress_tool = self.commontools.get_progress_dialog(
            self.config.force_use_arcpy_addmessage, lyr.name, selcount)

        with progress_tool as dialog:
            if self.commontools.is_desktop and \
                    not self.config.force_use_arcpy_addmessage:
                dialog.title = "Assetic Integration"
                dialog.description = "Updating assets for layer {0}".format(
                    lyr.name)
                dialog.canCancel = False

            # retrieve rows from layer
            rows = self.get_rows(lyr, fields, query)

            if len(rows) > self._bulk_threshold:
                chk, valid_rows = self.bulk_update_rows(rows, lyr, lyr_config)
            else:
                self.individually_update_rows(rows, lyr_config, fields, dialog)

    def display_in_assetic(self, lyr):
        """
        Open Assetic and display the first selected feature in layer
        Use config to determine if Asset or FL
        :param lyr: The layer find selected features.  Not layer name,
        layer object
        """

        # is it an asset layer?
        for j in self._assetconfig:
            if j["layer"] == lyr.name:
                self.display_asset(lyr)
        else:
            lyr_config, fields, idfield = self._get_fl_layer_config(
                lyr, "display")
            if lyr_config:
                self.display_fl(lyr, lyr_config, idfield)

    def display_asset(self, lyr, lyr_config=None, idfield=None):
        """
        Open assetic and display the first selected feature in layer
        :param lyr_config: config for layer as read from XML
        :param idfield: the assetic ID field
        :return:
        :param lyr: The layer find selected assets.  Not layer name,layer object
        """
        # get layer config details
        if not lyr_config:
            lyr_config, fields, idfield = self.get_layer_config(lyr, "display")
        if not lyr_config:
            return

        self.logger.debug("Layer: {0}, id field: {1}".format(
            lyr.name, idfield))
        try:
            features = arcpy.da.SearchCursor(lyr, idfield)
            row = features.next()
            assetid = str(row[0])
        except Exception as ex:
            msg = "Unexpected Error Encountered, check log file '{0}'".format(
                self.logfilename)
            self.commontools.new_message(msg)
            self.logger.error(str(ex))
            return
        if assetid is None or assetid.strip() == "":
            msg = "Asset ID or Asset GUID is NULL.\nUnable to display asset"
            self.commontools.new_message(msg)
            self.logger.warning(str(msg))
            return
        self.logger.debug("Selected Asset to display: [{0}]".format(
            assetid))
        # Now launch Assetic
        apihelper = assetic.APIHelper(self.asseticsdk.client)
        apihelper.launch_assetic_asset(assetid)

    def display_fl(self, lyr, lyr_config=None, idfield=None):
        """
        Open assetic and display the first selected feature in layer
        :param lyr: The layer find selected assets. Not layer name,layer object
        :param lyr_config: config for layer as read from XML
        :param idfield: the assetic ID field
        :return:
        """
        # get layer config details
        if not lyr_config:
            lyr_config, fields, idfield = self._get_fl_layer_config(
                lyr, "display")
        if not lyr_config:
            return

        self.logger.debug("Layer: {0}, id field: {1}".format(
            lyr.name, idfield))
        try:
            features = arcpy.da.SearchCursor(lyr, idfield)
            row = features.next()
            flid = str(row[0])
        except Exception as ex:
            msg = "Unexpected Error Encountered, check log file '{0}'".format(
                self.logfilename)
            self.commontools.new_message(msg)
            self.logger.error(str(ex))
            return
        if flid is None or flid.strip() == "":
            msg = "Functional Location ID or GUID is NULL.\nUnable to " \
                  "display Functional Location"
            self.commontools.new_message(msg)
            self.logger.warning(str(msg))
            return
        self.logger.debug(
            "Selected Functional Location to display: [{0}]".format(flid))
        # Now launch Assetic
        apihelper = assetic.APIHelper(self.asseticsdk.client)
        apihelper.launch_assetic_functional_location(flid)

    def _new_asset(self, row, lyr_config, fields):
        """
        Create a new asset for the given search result row

        :param row: a layer search result row, to create the asset for
        :param lyr_config: configuration object for asset field mapping
        :param fields: list of attribute fields
        :returns: Boolean True if success, else False
        """

        # Add calculated output fields to field list so that they are
        # considered valid
        all_calc_output_fields = lyr_config["all_calc_output_fields"]

        if all_calc_output_fields:
            fields = list(set(all_calc_output_fields + fields))

        complete_asset_obj = self.get_asset_obj_for_row(row, lyr_config, fields)

        # alias core fields for readability
        corefields = lyr_config["corefields"]

        # verify it actually needs to be created
        if "id" in corefields and corefields["id"] in fields:
            if not complete_asset_obj.asset_representation.id:
                # guid field exists in ArcMap and is empty
                newasset = True
            else:
                # guid id populated, must be existing asset
                # return early with passed error code
                newasset = False
        else:
            # guid not used, what about asset id?
            if "asset_id" in corefields and corefields["asset_id"] in fields:
                # asset id field exists in Arcmap
                if not complete_asset_obj.asset_representation.asset_id:
                    # asset id is null, must be new asset
                    newasset = True
                else:
                    # test assetic for the asset id.
                    # Perhaps user is not using guid
                    # and is manually assigning asset id.
                    chk = self.assettools.get_asset(
                        complete_asset_obj.asset_representation.asset_id)
                    if not chk:
                        newasset = True
                    else:
                        # asset id already exists.  Not a new asset
                        newasset = False
            else:
                # there is no field in ArcMap representing either GUID or
                # Asset ID, so can't proceed.
                self.logger.error(
                    "Asset not created because there is no configuration "
                    "setting for <id> or <asset_id> or the field is not in "
                    "the layer")

                return self.results["error"]

        if not newasset:
            self.logger.warning(
                "Did not attempt to create asset because it already has the "
                "following values: Asset ID={0},Asset GUID={1}".format(
                    complete_asset_obj.asset_representation.asset_id
                    , complete_asset_obj.asset_representation.id))

            return self.results["skip"]

        # set status
        complete_asset_obj.asset_representation.status = \
            lyr_config["creation_status"]

        # Create new asset
        asset_repr = self.assettools.create_complete_asset(complete_asset_obj)

        if asset_repr is None:
            # this occurs when the asset creation has failed
            # components/dimensions - no attempt was made to create
            self.commontools.new_message(
                "Asset Not Created - Check log file '{0}'".format(
                    self.logfilename))

            return self.results['error']

        # apply asset guid and/or assetid
        if "id" in corefields:
            row[corefields["id"]] = asset_repr.asset_representation.id
        if "asset_id" in corefields:
            row[corefields["asset_id"]] = asset_repr.asset_representation.asset_id

        # apply component id
        for component_dim_obj in asset_repr.components:
            for component_config in lyr_config["components"]:
                component_type = None
                if "component_type" in component_config["attributes"]:
                    component_type = component_config["attributes"][
                        "component_type"]
                elif "component_type" in component_config["defaults"]:
                    component_type = component_config["defaults"][
                        "component_type"]

                # Apply the component GUID to the feature
                if ("id" in component_config["attributes"]) and (component_type
                                                                 == component_dim_obj.component_representation.component_type):
                    row[component_config["attributes"]["id"]] = \
                        component_dim_obj.component_representation.id

                # Apply the component friendly id to the feature
                if "name" in component_config["attributes"] and \
                        component_type \
                        == component_dim_obj.component_representation \
                        .component_type:
                    row[component_config["attributes"]["name"]] = \
                        component_dim_obj.component_representation.name

        # apply FL ids to feature
        if asset_repr.functional_location_representation:
            fl_resp = asset_repr.functional_location_representation
            fl_conf = lyr_config["functionallocation"]
            # apply guid if there is a field for it
            if "id" in fl_conf and fl_conf["id"] in row:
                row[fl_conf["id"]] = fl_resp.id
            # apply friendly id if there is a field for it
            if "functional_location_id" in fl_conf and \
                    fl_conf["functional_location_id"] in row:
                row[fl_conf["functional_location_id"]] = \
                    fl_resp.functional_location_id

        # Now check config and update Assetic with spatial data and/or address
        addr = None
        geojson = None
        if len(lyr_config["addressfields"]) > 0 \
                or len(lyr_config["addressdefaults"]) > 0:
            # get address details
            addr = assetic.CustomAddress()
            # get address fields from the attribute fields of the feature
            for k, v in six.iteritems(lyr_config["addressfields"]):
                if k in addr.to_dict() and v in fields:
                    setattr(addr, k, row[v])
            # get address defaults
            for k, v in six.iteritems(lyr_config["addressdefaults"]):
                if k in addr.to_dict():
                    setattr(addr, k, v)

        if lyr_config["upload_feature"] and "SHAPE@" in row \
                and "SHAPE@XY" in row:
            geometry = row['SHAPE@']
            centroid = row['SHAPE@XY']
            geojson = self.get_geom_geojson(4326, geometry, centroid)

        if addr or geojson:
            chk = self.assettools.set_asset_address_spatial(
                asset_repr.asset_representation.id, geojson, addr)
            if chk > 0:
                e = ("Error attempting creation of complete asset '{0}' - "
                     "asset creation successful but failed during creation "
                     "of spatial data. See log.".format(
                      asset_repr.asset_representation.asset_id))
                self.logger.error(e)

                return self.results['partial']

        if asset_repr.error_code in [2, 4, 16]:
            # component (2), or dimension (4) or Fl (16) error
            return self.results['partial']

        return self.results['success']

    def _attach_functionallocation(self, asset_repr, row, lyr_config):
        # type: (AssetToolsCompleteAssetRepresentation, dict, dict) -> int
        """
        Retrieves the functional location information relating to the asset
        from the row and attaches it to the asset representation

        :param asset_repr: <AssetToolsCompleteAssetRepresentation>
        :param row: <dict> arcpy row
        :param lyr_config: <dic> customer defined config values
        :return: None - object modified in place
        """

        flfields = lyr_config['functionallocation']

        flid = None
        flname = None
        fltype = None
        if "functional_location_id" in flfields and \
                flfields['functional_location_id'] in row:
            flid = row[flfields['functional_location_id']]
        if "functional_location_name" in flfields and \
                flfields['functional_location_name'] in row:
            flname = row[flfields['functional_location_name']]
        if "functional_location_type" in flfields and \
                flfields['functional_location_type'] in row:
            fltype = row[flfields['functional_location_type']]

        if flname not in ['', None] and fltype not in ['', None]:
            # User has specified name and type indicating a requirement to
            # create the FL if not exist.
            # First check if FL already exists
            flrepr = self.fltools.get_functional_location_by_name_and_type(
                flname, fltype)

            if flrepr is None:
                # e.g. the FL doesn't exist
                f = FunctionalLocationRepresentation()

                fltypeid = self.fltools.get_functional_location_type_id(fltype)

                f.functional_location_id = flid
                f.functional_location_type = fltype
                f.functional_location_name = flname
                f.functional_location_type_id = fltypeid

                flrepr = self.fltools.create_functional_location(f)
                if flrepr is None:
                    # e.g. an error occurred while creating
                    return 1

        elif flid not in ['', None]:
            flrepr = self.fltools.get_functional_location_by_id(flid)

        else:
            # No config for FL.  not an error though.
            return 0

        asset_repr.functional_location_representation = flrepr

        return 0

    def retrieve_asset_id(self, asset_representation):
        chk = self.assettools.get_asset(
            asset_representation.asset_id)

        if chk:
            # set the guid, need it later if doing spatial load
            asset_representation.id = chk["Id"]

    def _update_components(self, complete_asset_obj):
        # type: (AssetToolsCompleteAssetRepresentation) -> None
        """
        Iterate over components retrieved for asset and update any changes.

        :param complete_asset_obj: <AssetToolsCompleteAssetRepresentation>
        :return: None
        """

        # have components, assume network measure needed, also assume we
        # don't have Id's for the components which are needed for update
        current_complete_asset = self.assettools.get_complete_asset(
            complete_asset_obj.asset_representation.id, []
            , ["components", "dimensions"])

        # get an asset ID to use for messaging if error
        asset_id = complete_asset_obj.asset_representation.asset_id
        if not asset_id:
            asset_id = complete_asset_obj.asset_representation.id

        for component in reversed(complete_asset_obj.components):
            # get the id from the current record, matching on
            # component type
            new_comp = component.component_representation
            for current_comp_rep in current_complete_asset.components:
                current_comp = current_comp_rep.component_representation
                if (current_comp.component_type == new_comp.component_type
                        and current_comp.label == new_comp.label) \
                        or current_comp.id == new_comp.id:
                    # set the id and label, type in case they are undefined
                    new_comp.id = current_comp.id
                    new_comp.label = current_comp.label
                    new_comp.component_type = current_comp.component_type

                    # Look for dimensions and set dimension Id
                    for dimension in reversed(component.dimensions):
                        count_matches = 0
                        for current_dim in current_comp_rep.dimensions:
                            # match on id or (nm type and record
                            # type and shape name)
                            if not dimension.id and \
                                    dimension.network_measure_type == \
                                    current_dim.network_measure_type and \
                                    dimension.record_type == \
                                    current_dim.record_type and \
                                    dimension.shape_name == \
                                    current_dim.shape_name:
                                # set dimension id and component id
                                dimension.id = current_dim.id
                                dimension.component_id = new_comp.id
                                count_matches += 1
                        if not dimension.id or count_matches > 1:
                            # couldn't find unique id. remove
                            component.dimensions.remove(dimension)
                            self.logger.warning(
                                "Unable to update dimension for "
                                "asset '{1}' component '{0}' because no "
                                "existing or distinct dimension record was "
                                "found".format(
                                    new_comp.label, asset_id))
            if not new_comp.id:
                # couldn't find component - remove
                complete_asset_obj.components.remove(component)
                self.logger.warning(
                    "Unable to update component for asset '{0}' becuase "
                    "no existing or unique component of type '{1}' and "
                    "name '{2}' was found".format(
                        asset_id
                        , new_comp.component_type, new_comp.label
                    ))

    def upload_features(self, row, complete_asset_obj, lyr_config, fields):
        # type: (dict, AssetToolsCompleteAssetRepresentation, dict, List[str]) -> bool
        """
        Uploads the address and point data against the asset defined
        in the complete_asset_obj.

        :param row: row representing a layer row
        :param complete_asset_obj: object representing asset with attached
        components, dimensions, functiona location, etc.
        :param lyr_config: customer-defined configuration found in xml file
        :param fields:
        """

        # get an asset ID to use for messaging if error
        asset_id = complete_asset_obj.asset_representation.asset_id
        if not asset_id:
            asset_id = complete_asset_obj.asset_representation.id

        # get address details
        addr = assetic.CustomAddress()
        # get address fields the attribute fields of the feature
        for k, v in six.iteritems(
                lyr_config["addressfields"]):
            if k in addr.to_dict() and v in fields:
                setattr(addr, k, row[v])
        # get address defaults
        for k, v in six.iteritems(
                lyr_config["addressdefaults"]):
            if k in addr.to_dict():
                setattr(addr, k, v)
        if 'SHAPE@' in row and 'SHAPE@XY' in row:
            geometry = row['SHAPE@']
            centroid = row['SHAPE@XY']
            geojson = self.get_geom_geojson(4326, geometry, centroid)
        else:
            geojson = None
        chk = self.assettools.set_asset_address_spatial(
            complete_asset_obj.asset_representation.id, geojson, addr)
        if chk > 0:
            self.commontools.new_message(
                "Error Updating Asset Address/Location:{0}, Asset: {1}"
                "".format(
                    complete_asset_obj.asset_representation.asset_id
                    , complete_asset_obj.asset_representation.id))
            return False

        return True

    def _update_asset(self, row, lyr_config, fields):
        # type: (dict, dict, list) -> bool
        """
        Update an existing asset for the given arcmap row

        :param row: a layer search result row, to create the asset for
        :param lyr_config: configuration object for asset field mapping
        :param fields: list of attribute fields
        :returns: Boolean True if success, else False
        """
        # Add calculated output fields to field list so that they are
        # considered valid
        all_calc_output_fields = lyr_config["all_calc_output_fields"]
        if all_calc_output_fields:
            fields = list(set(all_calc_output_fields + fields))

        # retrieve all of the asset info from the row and attach
        complete_asset_obj = self.get_asset_obj_for_row(row, lyr_config, fields)

        if complete_asset_obj.asset_representation.id is None:
            if complete_asset_obj.asset_representation.asset_id:
                chk = self.assettools.get_asset(
                    complete_asset_obj.asset_representation.asset_id)

                if chk:
                    # set the guid, need it later if doing spatial load
                    complete_asset_obj.asset_representation.id = chk["Id"]

        # if still no ID, return false and exit
        if complete_asset_obj.asset_representation.id is None:
            self.logger.warning(
                "Asset not updated because it is undefined or not in Assetic. "
                "Asset ID={0}".format(
                    complete_asset_obj.asset_representation.asset_id))
            return False

        # attach functional location representation to the asset using
        # row info (creates funcloc if it doesn't exist)
        errcode = self._attach_functionallocation(complete_asset_obj, row, lyr_config)

        if errcode > 0:
            return False

        if len(complete_asset_obj.components) > 0:
            self._update_components(complete_asset_obj)

        # update the asset attributes
        chk = self.assettools.update_complete_asset(complete_asset_obj)

        if chk > 0:
            self.commontools.new_message(
                "Error Updating Asset:{0}, Asset GUID={1}".format(
                    complete_asset_obj.asset_representation.asset_id
                    , complete_asset_obj.asset_representation.id))
            return False

        if lyr_config["upload_feature"]:
            chk = self.upload_features(row, complete_asset_obj, lyr_config, fields)

            if not chk:
                # self.commontools.new_message(
                #    "Error Updating Asset Address/Location:{0},
                #    Asset GUID={1}"
                #    "".format(
                #        complete_asset_obj.asset_representation.asset_id
                #        , complete_asset_obj.asset_representation.id))
                return False

        return True

    def bulk_update_spatial(self, rows, lyr, lyr_config):
        # type: (list, str, dict) -> int
        """
        For the given rows use dataExchange to bulk upload spatial
        :param rows: a list of rows from layer
        :param lyr: the layer being processed
        :param lyr_config: the XML config for the layer
        :return: 0=success, else error
        """
        # get some info about the layer
        desc = arcpy.Describe(lyr)
        shape_type = desc.shapeType

        # will need to project to EPSG4326 for output
        tosr = arcpy.SpatialReference(4326)

        spatial_rows = list()
        # loop through rows and get WKT
        for row in rows:
            if "SHAPE@" in row:
                row_dict = dict()
                polygonwkt = ""
                linewkt = ""
                if "asset_id" in lyr_config["corefields"]:
                    asset_id = row[lyr_config["corefields"]["asset_id"]]
                elif "id" in lyr_config["corefields"]:
                    asset_guid = row[lyr_config["corefields"]["asset_id"]]
                    asset = self.assettools.get_asset(asset_guid)
                    if asset != None:
                        asset_id = asset["AssetId"]
                    else:
                        msg = "Asset with ID [{0}] not found".format(
                            asset_guid)
                        self.logger.warning(msg)
                        continue
                else:
                    self.logger.warning(
                        "No asset ID field for spatial upload.  No upload "
                        "performed")
                    return 1

                # get geometry and process
                geometry = row['SHAPE@']
                new_geom = geometry.projectAs(tosr)
                if shape_type == "Polygon":
                    polygonwkt = new_geom.WKT
                elif shape_type == "Polyline":
                    linewkt = new_geom.WKT

                # define the point for all feature types
                pt_geometry = arcpy.PointGeometry(geometry.centroid
                                                  , geometry.spatialReference)
                pointwkt = pt_geometry.projectAs(tosr).WKT

                row_dict["Asset ID"] = asset_id
                row_dict["Point"] = pointwkt
                row_dict["Polygon"] = polygonwkt
                row_dict["Line"] = linewkt
                spatial_rows.append(row_dict)
            else:
                # missing spatial data
                self.logger.warning(
                    "Missing spatial data in bulk upload, no bulk update "
                    "performed")
                return 1

        if len(spatial_rows) > 0:
            self.gis_tools.bulk_update_spatial(spatial_rows)
        return 0

    def get_asset_obj_for_row(self, row, lyr_config, fields):
        """
        Prepare a complete asset for the given search result row using data
        from within the row

        :param row: a layer search result row, to create the asset for
        :param lyr_config: configuration object for asset field mapping
        :param fields: list of attribute fields in the layer
        :returns: assetic.AssetToolsCompleteAssetRepresentation() or None
        """
        # instantiate the complete asset representation to return
        complete_asset_obj = AssetToolsCompleteAssetRepresentation()

        # create an instance of the complex asset object
        asset = assetic.models.ComplexAssetRepresentation()

        # set status (mandatory field)
        # asset.status = "Active"

        asset.asset_category = lyr_config["asset_category"]

        # apply field calculations first
        for calculation in lyr_config["calculations"]:
            calc_val = self._calc_tools.run_calc(
                calculation["calculation_tool"], calculation["input_fields"]
                , row, lyr_config["layer"])
            if calc_val:
                row[calculation["output_field"]] = calc_val
        # set core field values from arcmap fields
        for xml, lyrcol in six.iteritems(lyr_config["corefields"]):
            chk_xml = xml in asset.to_dict().keys()
            chk_lyr = lyrcol in fields
            chk_lyr_none = row[lyrcol] is not None
            chk_str_null = str(row[lyrcol]).strip() != ""
            if all([chk_xml, chk_lyr, chk_lyr_none, chk_str_null]):
                setattr(asset, xml, row[lyrcol])

        # set core field values from defaults
        for xml, lyrcol in six.iteritems(lyr_config["coredefaults"]):
            if xml in asset.to_dict() and str(lyrcol).strip() != "":
                setattr(asset, xml, lyrcol)

        attributes = {}
        # set attributes values from arcmap fields
        if "attributefields" in lyr_config:
            for xml, lyrcol in six.iteritems(lyr_config["attributefields"]):
                if lyrcol in fields and row[lyrcol] is not None and \
                        str(row[lyrcol]).strip() != "":
                    attributes[xml] = row[lyrcol]
        # set attribute values from defaults
        for xml, lyrcol in six.iteritems(lyr_config["attributedefaults"]):
            if str(lyrcol).strip() != "":
                attributes[xml] = lyrcol
        # add the attributes to the asset and the asset to the complete object
        asset.attributes = attributes
        complete_asset_obj.asset_representation = asset

        # create component representations
        for component in lyr_config["components"]:
            comp_tool_rep = assetic.AssetToolsComponentRepresentation()
            comp_tool_rep.component_representation = \
                assetic.ComponentRepresentation()
            for xml, lyrcol in six.iteritems(component["attributes"]):
                if lyrcol in fields and row[lyrcol] is not None and \
                        str(row[lyrcol]).strip() != "":
                    setattr(comp_tool_rep.component_representation, xml
                            , row[lyrcol])
            for xml, lyrcol in six.iteritems(component["defaults"]):
                if xml in comp_tool_rep.component_representation.to_dict():
                    setattr(comp_tool_rep.component_representation, xml, lyrcol)

            # add dimensions to component
            if component["dimensions"] and len(component["dimensions"]) > 0:
                # create an array for the dimensions to be added
                # to the component
                dimlist = list()
                for dimension in component["dimensions"]:
                    # Create an instance of the dimension and set minimum fields
                    dim = assetic.ComponentDimensionRepresentation()
                    for xml, lyrcol in six.iteritems(dimension["attributes"]):

                        # only set attribute on dimension repr. if column defined
                        # in xml and is not None or ''
                        if (lyrcol in fields) and (row[lyrcol] is not None) and \
                                (str(row[lyrcol]).strip() != ""):
                            setattr(dim, xml, row[lyrcol])
                    for xml, lyrcol in six.iteritems(dimension["defaults"]):
                        if xml in dim.to_dict():
                            setattr(dim, xml, lyrcol)

                    # if comp_tool_rep.component_representation.dimension_unit is None:
                        # try to set the componenent's dimension to the thing
                        # todo - is it correct defining dimension unit within the
                        # comp_tool_rep.component_representation.dimension_unit = dim.dimension_unit
                        # comp_tool_rep.component_representation.network_measure_type = dim.network_measure_type

                    dimlist.append(dim)

                # Add the dimension array to the component
                comp_tool_rep.dimensions = dimlist

            # add the component array
            complete_asset_obj.components.append(comp_tool_rep)

        # add functional location to representation
        self._attach_functionallocation(complete_asset_obj, row, lyr_config)

        return complete_asset_obj

    def get_geom_wkt(self, outsrid, geometry):
        """
        Get the well known text for a geometry in 4326 projection
        :param outsrid: The projection EPSG code to export WKT as (integer)
        :param geometry: The input geometry
        :returns: wkt string of geometry in the specified projection
        """
        tosr = arcpy.SpatialReference(outsrid)
        new_geom = geometry.projectAs(tosr)
        wkt = new_geom.WKT
        return wkt

    def get_geom_geojson(self, outsrid, geometry, centroid=None):
        """
        Get the geojson for a geometry in 4326 projection
        :param outsrid: The projection EPSG code to export WKT as (integer)
        :param geometry: The input geometry
        :param centroid: The geometry centroid, use for polygons in case polygon
        orientation is wrong.  Optional
        :returns: wkt string of geometry in the specified projection
        """
        tosr = arcpy.SpatialReference(outsrid)

        if "curve" in geometry.JSON:
            # arcs and circles not supported by geoJson
            # the WKT doesn't define arcs so use it
            simple_geom = arcpy.FromWKT(geometry.WKT,
                                        geometry.spatialReference)
            new_geom = simple_geom.projectAs(tosr)
        else:
            new_geom = geometry.projectAs(tosr)
        # now convert to geojson
        geojsonstr = arcgis2geojson(new_geom.JSON)
        geojson = json.loads(geojsonstr)
        centroid_geojson = None
        if "type" in geojson and geojson["type"].lower() == "polygon":
            if isinstance(centroid, tuple) and len(centroid) == 2:
                point = arcpy.Point(centroid[0], centroid[1])
                pt_geometry = arcpy.PointGeometry(point
                                                  , geometry.spatialReference)
                new_centroid = pt_geometry.projectAs(tosr)
                centroid_geojson_str = arcgis2geojson(new_centroid.JSON)
                centroid_geojson = json.loads(centroid_geojson_str)
        if "GeometryCollection" not in geojson:
            # Geojson is expected to include collection, but arcgis2geojson
            # does not include it
            if centroid_geojson:
                fullgeojson = {
                    "geometries": [geojson, centroid_geojson]
                    , "type": "GeometryCollection"}
            else:
                fullgeojson = {
                    "geometries": [geojson]
                    , "type": "GeometryCollection"}
        else:
            # not try to include centroid, too messy.  Am not expecting to hit
            # this case unless arcgis2geojson changes
            fullgeojson = geojson

        return fullgeojson

    def GetEventAssetID(self, geometryObj, oidList, layerList):
        """
        Gets the guid for an asset feature that has been deleted or moved
        https://github.com/savagemat/PythonEditCounter/blob/master/Install/PythonEditCounter_addin.py
        :param geometryObj: The feature that was deleted or moved
        :param oidList: A list of OIDs as integers
        :param layerList: Layers in the workspace
        :returns: Unique Assetic ID of the feature that was deleted/moved
        """
        assetlayers = {}
        for lyr in layerList:
            if lyr.isFeatureLayer:
                ##get layer config details
                lyr_config, fields, idfield = self.get_layer_config(
                    lyr, "delete")
                if idfield != None:
                    oidField = arcpy.Describe(lyr).OIDFieldName
                    query = "{0} in {1}".format(oidField, str(oidList).replace(
                        '[', '(').replace(']', ')'))
                    with arcpy.da.SearchCursor(lyr,
                                               [oidField, "SHAPE@", idfield],
                                               where_clause=query) as rows:
                        for row in rows:
                            geom = row[1]
                            if geom.JSON == geometryObj.JSON:
                                ##return the assetid and the layer it belongs to
                                return row[2], lyr

        # feature is not a valid asset so return nothing
        return None, None

    def undo_edit(self, lyr):
        """
        Not implemented.  Works outside of edit session but not in
        need to figure out how to access
        """
        desc = arcpy.Describe(lyr)
        workspace = desc.path
        with arcpy.da.Editor(workspace) as edit:
            edit.abortOperation()

    def get_layer_asset_guid(self, assetid, lyr_config):
        """
        Get the asset guid for an asset.  Used where "id" is not in the
        configuration.  If it is then it is assumed the assetid is a guid
        :param assetid: The assetid - may be guid or friendly
        :param lyr_config: the layer
        :returns: guid or none
        """
        # alias core fields object for readability
        corefields = lyr_config["corefields"]
        if "id" not in corefields:
            ##must be using asset_id (friendly).  Need to get guid
            asset = self.assettools.get_asset(assetid)
            if asset != None:
                assetid = asset["Id"]
            else:
                msg = "Asset with ID [{0}] not found in Assetic".format(
                    assetid)
                self.logger.warning(msg)
                return None
        return assetid

    def set_asset_address_spatial(self, assetid, lyr_config, geojson,
                                  addr=None):
        """
        Set the address and/or spatial definition for an asset
        :param assetid: The asset GUID (TODO support friendly ID)
        :param lyr_config: The settings defined for the layer
        :param geojson: The geoJson representation of the feature
        :param addr: Address representation.  Optional.
        assetic.CustomAddress
        :returns: 0=no error, >0 = error
        """
        if addr is not None and \
                not isinstance(addr, assetic.CustomAddress):
            msg = "Format of address incorrect,expecting " \
                  "assetic.CustomAddress"
            self.logger.debug(msg)
            return 1
        else:
            addr = assetic.CustomAddress()

        ##get guid
        assetguid = self.get_layer_asset_guid(assetid, lyr_config)
        if assetguid == None:
            msg = "Unable to obtain asset GUID for assetid={0}".format(assetid)
            self.logger.error(msg)
            return 1
        chk = self.assettools.set_asset_address_spatial(assetguid, geojson,
                                                        addr)
        return 0

    def decommission_asset(self, assetid, lyr_config, comment=None):
        """
        Set the status of an asset to decommisioned
        :param assetid: The asset GUID (TODO support friendly ID)
        :param lyr_config: config details for layer
        :param comment: A comment to accompany the decommision
        :returns: 0=no error, >0 = error
        """

        return 1

    @staticmethod
    def get_fl_layer_fields_dict(lyr_config):

        cores = lyr_config['fl_corefields']
        coredefs = lyr_config['fl_coredefaults']

        layer_dict = {
            'id': cores['id'],
            'functional_location_id': cores['functional_location_id'],
            'functional_location_name': cores['functional_location_name'],
            'functional_location_type': coredefs['functional_location_type'],
        }

        return layer_dict

    @staticmethod
    def find_funcloc(flreprs, **attrs):

        for fl in flreprs:
            matchs = []
            for attr, attrval in attrs.items():
                matchs.append(fl.__getattribute__(attr) == attrval)

            if all(matchs):
                return fl

        return None

    @staticmethod
    def _get_fl_attrvals(row, attrs, defattrs):
        # type: (dict, dict, dict) -> dict
        """
        Creates a dictionary of attributes from row values
        to attach to a functional location representation.
        :param row: row representation

        :param attrs: dict defining relationship between odata
        value and the layer column name
        :param defattrs: dict defining relationship between odata
        value and the default value
        :return: dict containing attributes
        """

        attrvals = {}

        for cloud, lyrcol in six.iteritems(attrs):
            val = row[lyrcol]

            if val in ['', None]:
                # don't want blank values causing potential errors
                continue

            attrvals[cloud] = val

        attrvals.update(defattrs)

        return attrvals

    def _create_fl_from_row(self, row, fl_fields, fltype, attrs, def_attrs):
        # type: (dict, dict, str, dict, dict) -> FunctionalLocationRepresentation
        """
        Retrieves information from a cursor row and attempts to create
        a functional location from the data.

        :param row: arcgis layer row, converted to a dictionary
        :param fl_fields: dict that defines relationship between functional
        location fields and the layer column names
        :param fltype: valid FL cloud type
        :param attrs: FL attributes, in form of {oData val: layer column}
        :param def_attrs: FL default attributes, in form of {oData val:
        default val}
        :return:
        """

        # instantiate representation
        new_flepr = FunctionalLocationRepresentation()

        if "functional_location_id" in fl_fields and \
                fl_fields['functional_location_id'] in row:
            # set the user friendly FL ID.  It is not required if auto-id on
            new_flepr.functional_location_id = row[fl_fields[
                'functional_location_id']]

        new_flepr.functional_location_name = row[fl_fields[
            'functional_location_name']]

        try:
            fltype_id = self.fltools.get_functional_location_type_id(fltype)
        except KeyError:
            msg = ("Failed to find Functional Location Type Id for FL "
                   "{0}, which is an invalid FL Type.".format(fltype))
            self.logger.error(msg)
            return None

        new_flepr.functional_location_type = fltype
        new_flepr.functional_location_type_id = fltype_id
        attr_vals = self._get_fl_attrvals(row, attrs, def_attrs)
        new_flepr.attributes = attr_vals
        flrepr = self.fltools.create_functional_location(new_flepr)

        return flrepr

    @staticmethod
    def _retrieve_fl_attrs_from_row(row, attrs, def_attrs):

        attrvals = {}
        for od, lyrcol in six.iteritems(attrs):
            attrvals[od] = row[lyrcol]

        attrvals.update(def_attrs)

        return attrvals

    def create_funclocs_from_layer(self, lyr, query=None):
        # type: (Any, str) -> (int, int)
        """
        Iterates over the rows in a passed in layer (narrowed down by
        optional query) and creates functional locations defined in
        the data.

        Returns the number of successful and failed functional
        locations.

        :param lyr: passed in arcgis layerfile
        :param query: query to select certain attributes
        :return: number created, number failed
        """
        if not self._is_valid_config:
            self.logger.error("Invalid or missing configuration file, "
                        "functional location creation aborted.")
            return

        lyr_config, fields, idfield = self._get_fl_layer_config(lyr, "create")
        if lyr_config is None and fields is None:
            self.commontools.new_message(
                "Unable to process functional location layer '{0}' due to "
                "missing configuration".format(lyr.name))
            # return indication that nothing was processed
            return 0, 0

        fl_corefields = lyr_config['fl_corefields']
        fl_coredefaults = lyr_config['fl_coredefaults']

        has_lyr_fl_type = 'functional_location_type' in fl_corefields

        attrs = lyr_config['fl_attributefields']
        def_attrs = lyr_config['fl_attributedefaults']

        success = 0
        fail = 0
        with arcpy.da.UpdateCursor(lyr, fields, query) as cursor:
            for row in cursor:

                if has_lyr_fl_type:
                    # many fltypes in a single layer
                    fltype = row[fields.index(
                        fl_corefields['functional_location_type'])]
                else:
                    # single fltype per layer
                    fltype = fl_coredefaults['functional_location_type']

                drow = dict(zip(fields, row))

                flid = drow[fl_corefields['functional_location_id']]

                if flid in ['', None]:
                    # no FL ID defined. attempt to retrieve by name and type
                    flrepr = self.fltools.get_functional_location_by_name_and_type(
                        drow[fl_corefields['functional_location_name']]
                        , fltype)
                else:
                    # FL ID defined. attempt to retrieve by ID
                    # if FL doesn't exist we assume that autoid generation
                    # is off which is why the ID is already set in the layer
                    flrepr = self.fltools.get_functional_location_by_id(flid)

                if flrepr is not None:
                    # FL already exists!
                    self.commontools.new_message(
                        "Functional Location {0} already exists".format(
                            flrepr.functional_location_name
                        ))
                    fail += 1
                    continue

                # Doesn't appear to be an existing FL so create.
                flrepr = self._create_fl_from_row(
                    drow, fl_corefields, fltype, attrs, def_attrs)
                if flrepr is None:
                    # Error creating FL
                    fail += 1
                    continue

                # update row with new information - ID, GUID, etc.
                updfields = [fl_corefields[f] for f in [
                    'functional_location_id', 'id'] if f in fl_corefields]
                rev = {v: k for k, v in six.iteritems(fl_corefields)}
                for f in updfields:
                    row[fields.index(f)] = (flrepr.__getattribute__(rev[f]))

                cursor.updateRow(row)
                success += 1

        message = "Finished {0} Functional Location Creation, {1} Functional" \
                  " Locations created".format(lyr.name, str(success))

        if fail > 0:
            message = "{0}, {1} Functional Locations not created. (Check " \
                      "logfile {2})".format(
                message, str(fail), self.logfilename)

        self.commontools.new_message(message, "Assetic Integration")

        return success, fail

    def update_funclocs_from_layer(self, lyr, query=None):
        # type: (Any, str) -> (int, int)
        """
        Iterates over the rows in a passed in layer (narrowed down by
        optional query) and updates functional locations defined in
        the data.

        Returns the number of successful and failed updates of functional
        locations.

        :param lyr: passed in arcgis layerfile
        :param query: query to select certain attributes
        :return: number created, number failed
        """
        if not self._is_valid_config:
            self.logger.error("Invalid or missing configuration file, "
                        "Functional Location update aborted.")
            return

        lyr_config, fields, idfield = self._get_fl_layer_config(lyr, "update")
        if lyr_config is None and fields is None:
            msg = "Unable to process functional location layer '{0}' due to " \
                  "missing configuration".format(lyr.name)
            self.commontools.new_message(msg)
            self.logger.error(msg)
            # return indication that nothing was processed
            return 0, 0

        fl_corefields = lyr_config['fl_corefields']
        fl_coredefaults = lyr_config['fl_coredefaults']

        has_lyr_fl_type = False
        if 'functional_location_type' in fl_corefields:
            has_lyr_fl_type = True
        elif 'functional_location_type' not in fl_coredefaults:
            # need to have functional location type
            msg = "Unable to process functional location layer '{0}' due to " \
                  "missing functional location type".format(lyr.name)
            self.commontools.new_message(msg)
            self.logger.error(msg)
            # return indication that nothing was processed
            return 0, 0

        attrs = lyr_config['fl_attributefields']
        def_attrs = lyr_config['fl_attributedefaults']
        all_attr_fields = list(attrs.keys()) + list(def_attrs.keys())

        success = 0
        fail = 0
        with arcpy.da.SearchCursor(lyr, fields, query) as cursor:
            for row in cursor:

                if has_lyr_fl_type:
                    # many fltypes in a single layer
                    fltype = row[fields.index(
                        fl_corefields['functional_location_type'])]
                else:
                    # single fltype per layer defined in defaults
                    fltype = fl_coredefaults['functional_location_type']

                drow = dict(zip(fields, row))

                flid = drow[fl_corefields['functional_location_id']]

                fl_guid = None
                if "id" in fl_corefields and fl_corefields['id'] in drow:
                    fl_guid = drow[fl_corefields['id']]

                if flid in ['', None] and fl_guid in ['', None]:
                    # no FL ID defined. attempt to retrieve by name and type
                    flrepr = self.fltools.get_functional_location_by_name_and_type(
                        drow[fl_corefields['functional_location_name']]
                        , fltype, all_attr_fields)
                else:
                    # FL ID defined. attempt to retrieve by ID
                    if fl_guid:
                        flrepr = self.fltools.get_functional_location_by_id(
                            fl_guid, all_attr_fields)
                    else:
                        flrepr = self.fltools.get_functional_location_by_id(
                            flid, all_attr_fields)
                if flrepr is None:
                    # No FL found so move to next record
                    self.commontools.new_message(
                        "Unable to retrieve Functional Location {0} for "
                        "update".format(
                            drow[fl_corefields['functional_location_name']]
                        ))
                    fail += 1
                    continue

                # FL exists, check if the attributes are different
                # and then post if they are
                row_attrs = self._retrieve_fl_attrs_from_row(drow, attrs,
                                                             def_attrs)

                if row_attrs != flrepr.attributes or \
                        flrepr.functional_location_name != drow[
                    fl_corefields['functional_location_name']]:
                    # e.g. something has changed so update attributes with GIS
                    # attributes, and name in case it changed (not allow
                    # change to FL type or id)
                    flrepr.attributes = row_attrs
                    flrepr.functional_location_name = drow[
                        fl_corefields['functional_location_name']]
                    flepr = self.fltools.update_functional_location(flrepr)
                    if flepr:
                        success += 1
                    else:
                        fail += 1
                else:
                    # indicate success, just don't attempt update
                    success += 1

        message = "Finished {0} Functional Location Update, {1} Functional " \
                  "Locations updated".format(lyr.name, str(success))

        if fail > 0:
            message = "{0}, {1} Functional Locations not updated. (Check " \
                      "logfile {2})".format(
                message, str(fail), self.logfilename)

        self.commontools.new_message(message, "Assetic Integration")

        return success, fail
