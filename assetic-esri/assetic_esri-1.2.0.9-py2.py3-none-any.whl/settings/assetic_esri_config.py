# coding: utf-8

"""
    assetic_esri.tools.LayerConfig  (assetic_esri_config.py)
    Config manager to assist with using arcgis integration with assetic
"""
from __future__ import absolute_import

import os
import pprint
import xml.dom.minidom

import six

from ..tools.esri_messager import EsriMessager

class LayerConfig(object):
    """
    Class to manage definition of field mapping between assetic and ESRI layers
    """

    def __init__(self, xmlfile=None):
        self._assetlayerconfig = None
        self._loglevel = None
        self._logfile = None
        self._buttonconfig = {}
        self._bulk_threshold = None
        self._calculations_plugin = None

        self.xmlwkos = None
        self.xmlassets = None
        self.xmlfcnlocation = None
        self._buttonconfig = None

        self._assetlayerconfig = None
        self._fcnlayerconfig = None

        # initialise messager so can use messaging method
        self.commontools = EsriMessager()

        ##initalise settings by reading file and getting config
        self.init_xml(xmlfile)

    @property
    def fcnlayerconfig(self):
        return self._fcnlayerconfig

    @property
    def assetconfig(self):
        return self._assetlayerconfig

    @property
    def buttonconfig(self):
        return self._buttonconfig

    @property
    def loglevel(self):
        return self._loglevel

    @property
    def logfile(self):
        return self._logfile

    @property
    def bulk_threshold(self):
        return self._bulk_threshold

    @property
    def calculations_plugin(self):
        return self._calculations_plugin

    def init_xml(self, xmlfile=None):
        """
        Read the XML configuration file into separate dom objects for assets and
        work orders
        """
        if xmlfile is None:
            xmlfile = os.path.abspath(os.environ.get("APPDATA") \
                                      + "\\Assetic\\arcmap_edit_config.xml")

        # Open XML config document using minidom parser
        DOMTree = xml.dom.minidom.parse(xmlfile)
        collection = DOMTree.documentElement

        # get logfile and debug info
        loglevel = collection.getElementsByTagName("loglevel")
        self._loglevel = None
        if len(loglevel) > 0 and len(loglevel[0].childNodes) > 0:
            self._loglevel = str(loglevel[0].childNodes[0].data)

        self._logfile = None
        logfile = collection.getElementsByTagName("logfile")
        if len(logfile) > 0 and len(logfile[0].childNodes) > 0:
            self._logfile = str(logfile[0].childNodes[0].data)
            if not os.path.isdir(os.path.dirname(self._logfile)):
                # folder for log file not correct
                self.commontools.new_message(
                    "log file directory not found for: {0}".format(
                        self._logfile))
                self._logfile = None

        self._bulk_threshold = None
        bulk_threshold = collection.getElementsByTagName("bulk_threshold")
        if len(bulk_threshold) > 0 and len(bulk_threshold[0].childNodes) > 0:
            xml_bulk_threshold = int(bulk_threshold[0].childNodes[0].data)
            try:
                self._bulk_threshold = int(xml_bulk_threshold)
            except ValueError:
                # needs to be an int
                self.commontools.new_message(
                    "bulk_threshold setting must be an integer: {0}".format(
                        xml_bulk_threshold))
                self._bulk_threshold = None

        # Get all the wko and asset elements in the collection
        operations = collection.getElementsByTagName("operation")
        for operation in operations:
            if operation.getAttribute("action") == "Create Work Order":
                self.xmlwkos = operation.getElementsByTagName("layer")
            elif operation.getAttribute("action") == "Asset":
                self.xmlassets = operation.getElementsByTagName("layer")
            elif operation.getAttribute("action") == "Functional Location":
                self.xmlfcnlocation = operation.getElementsByTagName(
                    "layer")
            elif operation.getAttribute("action") == "Buttons":
                self._buttonconfig = self.get_button_action_config(operation)

        # get custom calculations plugin if set
        self._calculations_plugin = None
        plugin = collection.getElementsByTagName("calculations_file")
        if len(plugin) > 0 and len(plugin[0].childNodes) > 0:
            if os.path.isfile(str(plugin[0].childNodes[0].data)):
                self._calculations_plugin = str(plugin[0].childNodes[0].data)
            else:
                self.commontools.new_message(
                    "Calculations plugin file {0} not found".format(
                        str(plugin[0].childNodes[0].data)))

        # convert xml to list of dictionaries
        self._assetlayerconfig = self.get_asset_config_for_layers()
        self._fcnlayerconfig = self.get_functional_location_config_for_layers()

    def get_asset_config_for_layers(self):
        """
        From the XML configuration get the field names in the layers and the
        corresponding assetic field names
        :return: a list of dictionaries of assetic category to field name
        """
        allconfig = list()

        if not self.xmlassets:
            return allconfig

        for xmlasset in self.xmlassets:
            if xmlasset.hasAttribute("name"):
                lyr_config = {}
                coredict = {}
                attrdict = {}
                coredefsdict = {}
                attsdefsdict = {}
                addrdict = {}
                addrdefaultsdict = {}
                componentlist = list()
                funclocdict = {}
                calculationslist = list()

                lyr_config["layer"] = xmlasset.getAttribute("name")
                if lyr_config["layer"] == None:
                    msg = "Expecting tag <layer> in XML configuration"
                    self.commontools.new_message(msg)
                    return None

                assetcat = str(xmlasset.getElementsByTagName("category")[0].childNodes[0].data)
                if assetcat == None:
                    msg = "Asset Category for layer {0} not configured.\n" \
                          "Expecting tag <category>".format(lyr_config["layer"])
                    self.commontools.new_message(msg)
                    return None
                lyr_config["asset_category"] = assetcat

                # get core field mappings with layer fields
                for core in xmlasset.getElementsByTagName("corefields"):
                    for corefields in core.childNodes:
                        if corefields.nodeType == 1:
                            coredict[str(corefields.nodeName)] = str(corefields.childNodes[0].data)
                # check that we have either 'id' or 'asset_id' as minimum
                if "id" not in coredict and "asset_id" not in coredict:
                    msg = "Asset GUID and Asset ID for layer {0} not " \
                          "configured.\n" \
                          "Expecting tag <id> or <asset_id>, or both".format(
                        lyr_config["layer"])
                    self.commontools.new_message(msg)
                    return None
                # get attribute field mappings with layer fields
                for atts in xmlasset.getElementsByTagName("attributefields"):
                    for attflds in atts.childNodes:
                        if attflds.nodeType == 1:
                            attrdict[str(attflds.nodeName)] = str(attflds.childNodes[0].data)
                # get core field default value (where no layer field)
                for core in xmlasset.getElementsByTagName("coredefaults"):
                    for coredefaults in core.childNodes:
                        if coredefaults.nodeType == 1:
                            coredefsdict[str(coredefaults.nodeName)] = str(coredefaults.childNodes[0].data)
                # get attribute field default value (where no layer field)
                for atts in xmlasset.getElementsByTagName("attributedefaults"):
                    for attdefaults in atts.childNodes:
                        if attdefaults.nodeType == 1:
                            attsdefsdict[str(attdefaults.nodeName)] = str(attdefaults.childNodes[0].data)

                # get functional location fields
                for atts in xmlasset.getElementsByTagName("functional_location"):
                    for att in atts.childNodes:
                        if att.nodeType == 1:
                            funclocdict[str(att.nodeName)] = str(att.childNodes[0].data)

                # get component fields
                for component in xmlasset.getElementsByTagName("component"):
                    componentdict = {
                        "attributes": dict()
                        , "defaults": dict()
                        , "dimensions": list()
                    }
                    # get fields that map to layer attributes
                    for comp in component.getElementsByTagName(
                            "componentfields"):
                        for compfld in comp.childNodes:
                            if compfld.nodeType == 1:
                                if len(compfld.childNodes) > 0:
                                    componentdict["attributes"][
                                        str(compfld.nodeName)] = str(
                                        compfld.childNodes[0].data)
                                else:
                                    self.commontools.new_message(
                                        "No value supplied for component "
                                        "{0} tag {1}".format(
                                            component.getAttribute("name")
                                            , str(compfld.nodeName))
                                    )
                    # get component default value (where no layer field)
                    for compdefs in component.getElementsByTagName(
                            "componentdefaults"):
                        for compdefault in compdefs.childNodes:
                            if compdefault.nodeType == 1:
                                if len(compdefault.childNodes) > 0:
                                    componentdict["defaults"][
                                        str(compdefault.nodeName)] = str(
                                        compdefault.childNodes[0].data)
                                else:
                                    self.commontools.new_message(
                                        "No value supplied for component "
                                        "{0} default value tag {1}".format(
                                            component.getAttribute("name")
                                            , str(compfld.nodeName))
                                    )
                    dimension_xml = component.getElementsByTagName("dimension")
                    if dimension_xml:
                        componentdict["dimensions"] = self.get_dimension_config(
                            dimension_xml)

                    # add component setting to list of components
                    if len(componentdict["defaults"]) > 0 or \
                            len(componentdict["attributes"]) > 0:
                        componentlist.append(componentdict)

                # get address fields
                for addr in xmlasset.getElementsByTagName("addressfields"):
                    for addrfld in addr.childNodes:
                        if addrfld.nodeType == 1:
                            addrdict[str(addrfld.nodeName)] = \
                                str(addrfld.childNodes[0].data)
                # get address default value (where no layer field)
                for addrdefs in \
                        xmlasset.getElementsByTagName("addressdefaults"):
                    for addrdefault in addrdefs.childNodes:
                        if addrdefault.nodeType == 1:
                            addrdefaultsdict[str(addrdefault.nodeName)] = \
                                str(addrdefault.childNodes[0].data)
                # upload spatial?
                spatial = None
                uploadtagchk = xmlasset.getElementsByTagName(
                    "upload_feature")
                if uploadtagchk and len(uploadtagchk) > 0:
                    spatial = xmlasset.getElementsByTagName(
                        "upload_feature")[0].childNodes[0].data.upper() == 'TRUE'

                if not spatial or not isinstance(spatial, bool):
                    spatial = False
                    # if len(addrdict) > 0 or len(addrdefaultsdict) > 0:
                    #     msg = """Tag <upload_feature> in XML configuration
                    #             must be set to 'True' if defining fields for the
                    #             tags <addressfields> or <addressdefaults>.
                    #             Will assume <upload_feature>=True and continue"""
                    #     self.commontools.new_message(msg)
                    #     spatial = True
                status_cfg = "Active"
                status_chk = xmlasset.getElementsByTagName("creation_status")
                if status_chk and len(status_chk) > 0:
                    try:
                        status_cfg = xmlasset.getElementsByTagName(
                            "creation_status")[0].childNodes[0].data
                    except:
                        pass
                if status_cfg in ["Active", "Proposed", "Notional Asset"]:
                    status = status_cfg
                else:
                    status = "Active"
                    self.commontools.new_message(
                        "Status to use on asset creation not set correctly in "
                        "tag <creation_status>.\nCurrent setting is '{0}', use"
                        "one of 'Active', 'Proposed', 'Notional Asset'."
                        "\nDefaulting to status 'Active'".format(status_cfg))

                # get configuration for custom calculations to apply
                for calculation in xmlasset.getElementsByTagName(
                        "calculation"):
                    calculationdict = {
                        "input_fields": list()
                        , "output_field": None
                        , "calculation_tool": None
                    }
                    # get input fields that map to layer attributes
                    for input_field in calculation.getElementsByTagName(
                            "input_fields"):
                        for input_fld in input_field.childNodes:
                            if input_fld.nodeType == 1:
                                if len(input_fld.childNodes) > 0:
                                    calculationdict["input_fields"].append(
                                        str(input_fld.childNodes[0].data))
                                else:
                                    self.commontools.new_message(
                                        "No value supplied for calculation "
                                        "{0} tag {1}".format(
                                            calculation.getAttribute("name")
                                            , str(input_fld.nodeName))
                                    )
                    # get output field name
                    # get core field default value (where no layer field)
                    for calc_cfg in calculation.childNodes:
                        if calc_cfg.nodeType == 1 and \
                                str(calc_cfg.nodeName) != "input_fields":
                            calculationdict[str(calc_cfg.nodeName)] = \
                                str(calc_cfg.childNodes[0].data)

                    if len(calculationdict["input_fields"]) > 0 and \
                            calculationdict["output_field"] and \
                            calculationdict["calculation_tool"]:
                        calculationslist.append(calculationdict)
                    else:
                        self.commontools.new_message(
                            "Configuration for {0} calculation fields "
                            "incomplete".format(lyr_config["layer"]))

                lyr_config["upload_feature"] = spatial
                lyr_config["creation_status"] = status

                lyr_config["corefields"] = coredict
                lyr_config["attributefields"] = attrdict
                lyr_config["coredefaults"] = coredefsdict
                lyr_config["attributedefaults"] = attsdefsdict
                lyr_config["addressfields"] = addrdict
                lyr_config["addressdefaults"] = addrdefaultsdict
                lyr_config["components"] = componentlist
                lyr_config['functionallocation'] = funclocdict
                lyr_config['calculations'] = calculationslist

                allconfig.append(lyr_config)

        # if coreitems !=None:
        #    for corefields in coreitems.childNodes:
        #        if corefields.nodeType == 1:
        #            fields.append(str(corefields.childNodes[0].data))
        #            fielddict[str(corefields.nodeName)] = str(corefields.childNodes[0].data)     
        return allconfig

    def get_dimension_config(self, dimension_xml):
        """
        From the XML configuration dimension node get the dimension defaults
        :param dimension_xml: the dimension xml node which is defined within
        a component.  There may be one of more dimension settings
        :return: list of dict with dimension attributes and defaults
        """
        dimension_list = list()
        for dimension in dimension_xml:
            dimension_dict = {
                "attributes": dict()
                , "defaults": dict()
            }
            # get dimension fields that map to layer attributes
            for dim in dimension.getElementsByTagName("dimensionfields"):
                for dim_fld in dim.childNodes:
                    if dim_fld.nodeType == 1:
                        if len(dim_fld.childNodes) > 0:
                            dimension_dict["attributes"][
                                str(dim_fld.nodeName)] = str(
                                dim_fld.childNodes[0].data)
                        else:
                            self.commontools.new_message(
                                "No value supplied for dimension "
                                "{0} tag {1}".format(
                                    dim.getAttribute("name")
                                    , str(dim_fld.nodeName))
                            )
            # get dimension default value (where no layer field)
            for dim in dimension.getElementsByTagName("dimensiondefaults"):
                for dim_def in dim.childNodes:
                    if dim_def.nodeType == 1:
                        if len(dim_def.childNodes) > 0:
                            dimension_dict["defaults"][
                                str(dim_def.nodeName)] = str(
                                dim_def.childNodes[0].data)
                        else:
                            self.commontools.new_message(
                                "No value supplied for dimension "
                                "{0} default value tag {1}".format(
                                    dim.getAttribute("name")
                                    , str(dim_def.nodeName))
                            )
            if dimension_dict["attributes"] or dimension_dict["defaults"]:
                dimension_list.append(dimension_dict)
        return dimension_list

    def get_functional_location_config_for_layers(self):
        """
        Configuration for Functional Location creation/update
        From the XML configuration get the field names in the layers and the
        corresponding assetic field names
        :return: a list of dictionaries of assetic category to field name
        """
        allconfig = list()

        if not self.xmlfcnlocation:
            return allconfig

        for xmlfcnloc in self.xmlfcnlocation:
            if xmlfcnloc.hasAttribute("name"):
                lyr_config = dict()

                lyr_config["layer"] = xmlfcnloc.getAttribute("name")

                lyr_config["fl_corefields"] = self.get_dict_for_tag(
                    xmlfcnloc, "fl_corefields")
                lyr_config["fl_coredefaults"] = self.get_dict_for_tag(
                    xmlfcnloc, "fl_coredefaults")
                lyr_config["fl_attributefields"] = self.get_dict_for_tag(
                    xmlfcnloc, "fl_attributefields")
                lyr_config["fl_attributedefaults"] = self.get_dict_for_tag(
                    xmlfcnloc, "fl_attributedefaults")

                # check that we have either 'id' or 'asset_id' as minimum
                valid_config = True
                if "id" not in lyr_config["fl_corefields"] and \
                        "functional_location_id" not in \
                        lyr_config["fl_corefields"]:
                    msg = "Functional Location GUID and Functional Location " \
                          "ID for layer {0} not configured.\nExpecting tag " \
                          "<id> or <functional_location_id>, or both".format(
                        lyr_config["layer"])
                    self.commontools.new_message(msg)
                    return None
                if "functional_location_type" not in \
                        lyr_config["fl_corefields"] and \
                        "functional_location_type" not in \
                        lyr_config["fl_coredefaults"]:
                    self.commontools.new_message(
                        "<functional_location_type> must be defined as a core "
                        "field or core default field for functional "
                        "location layer {0}".format(lyr_config["layer"]))

                if valid_config:
                    allconfig.append(lyr_config)

        return allconfig

    @staticmethod
    def get_dict_for_tag(element, tag):
        # type: (xml.dom.minidom.Element, str) -> dict
        """
        For a given element build a dict from the nodes in the element
        :param element: An XML element
        :param tag: the string value of the tag
        :returns: A dict with the mappings defined by the XML nodes in the
        element
        """
        mappings = dict()
        for nodes in element.getElementsByTagName(tag):
            for node in nodes.childNodes:
                if node.nodeType == 1 and len(node.childNodes) > 0:
                    mappings[str(node.nodeName)] = str(node.childNodes[0].data)
        return mappings

    def get_layer_wko_config(self, layername):
        """
        From the XML configuration get the work order defaults
        :param layername: work order layer name to get the config for
        :return: assetic_esri.WkoConfigRepresentation
        and a dictionary of assetic category to arcMap field name
        """
        config = WkoConfigRepresentation()
        for xmlwko in self.xmlwkos:
            if xmlwko.hasAttribute("name") and \
                    xmlwko.getAttribute("name") == layername:
                config.wkoguidfld = xmlwko.getElementsByTagName("guidfield")[0].childNodes[0].data
                config.wkoidfld = xmlwko.getElementsByTagName("friendlyfield")[0].childNodes[0].data
                config.assetidfld = xmlwko.getElementsByTagName("assetidfield")[0].childNodes[0].data
                config.failurecode = xmlwko.getElementsByTagName("failurecode")[0].childNodes[0].data
                config.remedycode = xmlwko.getElementsByTagName("remedycode")[0].childNodes[0].data
                config.causecode = xmlwko.getElementsByTagName("causecode")[0].childNodes[0].data
                # config.resourceid = xmlwko.getElementsByTagName("resourceid")[0].childNodes[0].data
                config.wkotype = xmlwko.getElementsByTagName("wkotypeid")[0].childNodes[0].data
        return config

    def get_button_action_config(self, xmlbuttons):
        button_config = {}
        button_config["but_create"] = False
        button_config["but_update"] = False
        button_config["but_delete"] = False
        button_config["but_show"] = False
        button_config["but_create"] = str(xmlbuttons.getElementsByTagName("create")[0].childNodes[0].data)
        button_config["but_update"] = str(xmlbuttons.getElementsByTagName("update")[0].childNodes[0].data)
        button_config["but_delete"] = str(xmlbuttons.getElementsByTagName("delete")[0].childNodes[0].data)
        button_config["but_show"] = str(xmlbuttons.getElementsByTagName("show")[0].childNodes[0].data)
        return button_config


# --wko config representation-----------------------------------------------
class WkoConfigRepresentation(object):
    """
    Use to hold user configurations for WKO
    """

    def __init__(self, wkoguidfld=None, wkoidfld=None, assetidfld=None
                 , remedycode=None, causecode=None, failurecode=None
                 , resourceid=None, wkotype=None):

        self.fieldtypes = {
            'wkoguidfld': 'str',
            'wkoidfld': 'str',
            'assetidfld': 'str',
            'remedycode': 'int',
            'causecode': 'int',
            'failurecode': 'int',
            'resourceid': 'str',
            'wkotype': 'int'
        }
        self._wkoguidfld = wkoguidfld
        self._wkoidfld = wkoidfld
        self._assetidfld = assetidfld
        self._remedycode = remedycode
        self._causecode = causecode
        self._failurecode = failurecode
        self._resourceid = resourceid
        self._wkotype = wkotype

    @property
    def wkoguidfld(self):
        return self._wkoguidfld

    @wkoguidfld.setter
    def wkoguidfld(self, wkoguidfld):
        self._wkoguidfld = wkoguidfld

    @property
    def wkoidfld(self):
        return self._wkoidfld

    @wkoidfld.setter
    def wkoidfld(self, wkoidfld):
        self._wkoidfld = wkoidfld

    @property
    def assetidfld(self):
        return self._assetidfld

    @assetidfld.setter
    def assetidfld(self, assetidfld):
        self._assetidfld = assetidfld

    @property
    def remedycode(self):
        return self._remedycode

    @remedycode.setter
    def remedycode(self, remedycode):
        self._remedycode = remedycode

    @property
    def causecode(self):
        return self._causecode

    @causecode.setter
    def causecode(self, causecode):
        self._causecode = causecode

    @property
    def failurecode(self):
        return self._failurecode

    @failurecode.setter
    def failurecode(self, failurecode):
        self._failurecode = failurecode

    @property
    def resourceid(self):
        return self._resourceid

    @resourceid.setter
    def resourceid(self, resourceid):
        self._resourceid = resourceid

    @property
    def wkotype(self):
        return self._wkotype

    @wkotype.setter
    def wkotype(self, wkotype):
        self._wkotype = wkotype

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in six.iteritems(self.fieldtypes):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
