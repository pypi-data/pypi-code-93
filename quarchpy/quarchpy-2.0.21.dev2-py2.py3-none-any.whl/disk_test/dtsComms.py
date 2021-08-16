import platform
import time
import logging
import socket
import threading
from datetime import datetime
import traceback
from xml.etree.ElementTree import Element, SubElement, Comment, tostring

import xml.etree.ElementTree as cElementTree

from quarchpy.disk_test.Drive_wrapper import DriveWrapper
from quarchpy.disk_test.testLine import testLine
from quarchpy.disk_test.dtsGlobals import dtsGlobals


class DTSCommms:

    def __init__(self):
        # declaring variables used in sending messages at different sections of class
        self.versionNumber = "1.02"
        self.request_tag = "Request"
        self.response_tag = "Response"
        self.request_id_counter = 0

        self.time_since_last_send = None
        self.response = None

    def comms_send(self, toSend, timeToWait=5):
        if dtsGlobals.send_to_gui:
            #print(toSend)
            self.sendMsgToGUI(toSend, timeToWait)
        else:
            print(toSend)

    """
    Function for any item being sent to GUI 
    Default is to wait 3 seconds, but can be set for longer / infinite
    """

    def sendMsgToGUIwithResponse(self, to_send, timeToWait=5):
        if not to_send:
            logging.warning("Passed a None item to send ")
            return
        # Opening socket using ip of connected device.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((dtsGlobals.GUI_TCP_IP, 9921))

        # sending message
        self.send_item_to_java(s, to_send)

        # basically infinite wait
        if timeToWait is None:
            timeToWait = 999999

        self.response = None

        # function for response + timeout
        start = time.time()
        while time.time() - start <= (timeToWait * 1000):
            if self.response is None:
                time.sleep(.1)  # Just to avoid hogging the CPU
                self.getReturnPacket(s)
            else:
                # All the processes are done, break now.
                break

        # Close socket on way out
        s.close()

        # print(self.response)

        return self.response

    def sendMsgToGUI(self, to_send, timeToWait=5):

        if not to_send:
            logging.warning("Passed a None item to send ")
            return

        # Opening socket using ip of connected device.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((dtsGlobals.GUI_TCP_IP, 9921))

        # printText("Item Sent across : " + toSend)
        # to_send = str.encode(to_send)

        self.send_item_to_java(s, to_send)

        # basically infinite wait
        if timeToWait is None:
            timeToWait = 999999

        # if response_required:
        self.processTimeoutAndResult(s, timeToWait, to_send)

        # Close socket on way out
        s.close()

    def send_item_to_java(self, s, to_send):
        if self.time_since_last_send:
            time_dif = time.time() - self.time_since_last_send

        #print(to_send)

        if len(to_send) > 8000:
            n = 8000
            items_to_send = [to_send[i:i + n] for i in range(0, len(to_send), n)]
            for split_msg in items_to_send:
                # split_msg = str.encode(str(len(split_msg))) + b">" + split_msg
                s.sendall(split_msg + b"\n")
        else:
            # sending message
            # s.sendall(str.encode(str(len(to_send))) + b">" + to_send + b"\n")
            s.sendall(to_send + b"\n")

        self.time_since_last_send = time.time()

    """
    Starts a subprocess to attempt to receive a return packet from java
    if timeout of 3 seconds is exceeded, break
    """

    def processTimeoutAndResult(self, socket, timeToWait, message_sent=""):

        process_object = threading.Thread(target=self.getReturnPacket(socket, message_sent))
        process_object.start()
        # timeout of 5 seconds
        start = time.time()
        while time.time() - start <= (timeToWait*1000):
            if process_object.is_alive():
                time.sleep(.1)  # Just to avoid hogging the CPU
            else:
                # All the processes are done, break now.
                break
        else:
            # We only enter this if we didn't 'break' above.
            logging.error("timed out whilst getting response")
            process_object.terminate()
            process_object.join()



    """
    reads data from socket passed
    """

    def getReturnPacket(self, socket, message_sent=""):

        buffer_size = 4096
        data = ""
        have_response = False
        expected_responses = ["<Response>","</Response>"]
        while True:

            # if not received start and end of expected
            if not have_response:
                temp_data = socket.recv(buffer_size)
                if not temp_data:
                    continue
                data += temp_data.decode("utf-8")
                found = True
                for r_string in expected_responses:
                    if not r_string in data:
                        found = False
                        if data:
                            logging.debug("current response = " + str(data))
                if found:
                    have_response = True

            else:
                # print(data)
                try:
                    data = data[data.index("<Response>"):]
                    if data.count("</Response>") > 1:
                        data = data.split("</Response>")
                        for response in data:
                            response = response[: response.index('</Response>') + len("</Response>")]
                            xml_tree = cElementTree.fromstring(response)
                            if not self.parse_response(xml_tree, response):
                                logging.warning("Unknown response")
                    else:
                        data = data[: data.index('</Response>') + len("</Response>")]
                        xml_tree = cElementTree.fromstring(data.replace("\n",""))
                        if not self.parse_response(xml_tree, data):
                            logging.warning("Unknown response")
                    break
                except cElementTree.ParseError as err:
                    logging.error("Error parsing Java response")
                except Exception as i:
                    traceback.print_exc()
                    logging.warning("Unknown exception caught reading response : " + str(i))
                    logging.debug("Recv buffer : " + str(data))
                    logging.debug("Sent cmd : " + str(message_sent))
        return

    def create_response(self, function_complete=False, function_type=None):
        response = testLine()
        response.function_complete = function_complete
        root_tag = Element(self.response_tag)
        response_function_complete_tag = SubElement(root_tag, 'function_complete')
        response_function_complete_tag.text = str(response.function_complete)
        if function_type:
            response_function_type_tag = SubElement(root_tag, 'function_type')
            response_function_type_tag.text = str(function_type)

        return tostring(root_tag)

    def create_request_root(self, root_tag, request_type, response_required=True):
        request_type_tag = SubElement(root_tag, 'RequestType')
        request_type_tag.text = str(request_type)

        request_id_tag = SubElement(root_tag, 'RequestID')
        self.request_id_counter += 1
        request_id_tag.text = str(self.request_id_counter)

        response_required_tag = SubElement(root_tag, 'ResponseRequired')
        response_required_tag.text = str(response_required)

    def create_request_poll(self, poll_type=None):

        root_tag = Element(self.request_tag)

        self.create_request_root(root_tag, request_type="Poll", response_required=False)

        poll_child = SubElement(root_tag, 'poll')

        if poll_type:
            child_tag = SubElement(poll_child, 'poll_type')
            child_tag.text = str(poll_type)

        return tostring(root_tag)

    def create_request_function(self, function_call, function_value=None, requires_response=True):

        root_tag = Element(self.request_tag)

        self.create_request_root(root_tag, request_type="Function", response_required=requires_response)

        function_child = SubElement(root_tag, 'function')

        child = SubElement(function_child, 'function_call')
        child.text = str(function_call)

        # Additional info, Like a directory or version number
        if function_value:
            child = SubElement(function_child, 'function_value')
            child.text = str(function_value)

        return tostring(root_tag)

    def create_request_gui(self, title, description, window_type, window_mode="PY", dict_of_modules=None,
                           dict_of_drives=None, report_dict=None):

        root_tag = Element(self.request_tag)

        self.create_request_root(root_tag, request_type="GUI")

        gui_tag = SubElement(root_tag, 'gui')

        title_tag = SubElement(gui_tag, 'title')
        title_tag.text = str(title)

        description_tag = SubElement(gui_tag, 'description')
        description_tag.text = str(description)

        window_type_tag = SubElement(gui_tag, 'windowType')
        window_type_tag.text = str(window_type)

        if window_mode:
            window_mode_tag = SubElement(gui_tag, 'windowMode')
            window_mode_tag.text = str(window_mode)

        if dict_of_modules:
            for conn_string, qtl_num in dict_of_modules.items():
                self.add_xml_quarch_module(conn_string, qtl_num, gui_tag)

        if dict_of_drives:
            for device in dict_of_drives:
                self.add_xml_drive(device, gui_tag)

        if report_dict:
            self.add_report_item(report_dict, gui_tag)

        return tostring(root_tag)

    def create_request_log(self, logTime, messageType, messageText, messageSource, messageData=None, test_result=None,
                           uId="", group=None, sub_group=None):

        root_tag = Element(self.request_tag)

        self.create_request_root(root_tag, request_type="log", response_required=False)

        self.notifyTestLogEventXml(root_tag, uId, logTime, messageType, messageText, messageSource, test_result,
                                   messageData, group, sub_group)

        return tostring(root_tag)

    def create_request_status(self, number_of_test_points=None, add_test_points=None, completion_value=None):

        root_tag = Element(self.request_tag)

        self.create_request_root(root_tag, request_type="Status")

        status_child = SubElement(root_tag, 'status')

        if completion_value:
            child_tag = SubElement(status_child, 'completionValue')
            child_tag.text = str(completion_value)

        if number_of_test_points:
            child_tag = SubElement(status_child, 'num_of_test_points')
            child_tag.text = str(number_of_test_points)

        if add_test_points:
            child_tag = SubElement(status_child, 'add_test_points')
            child_tag.text = str(add_test_points)

        return tostring(root_tag)

    def create_request_variable(self, custom_variable_list, root_tag=None):

        # Id variables are being sent along
        if root_tag is None:
            root_tag = Element(self.request_tag)

            self.create_request_root(root_tag, request_type="variable")

        for custom_variable in custom_variable_list:
            top = SubElement(root_tag, "customVariables")

            child = SubElement(top, 'name')
            child.text = str(custom_variable.custom_name)
            child = SubElement(top, 'defaultVal')
            child.text = str(custom_variable.default_value)
            child = SubElement(top, 'customVal')
            child.text = str(custom_variable.custom_value)

            child = SubElement(top, 'variableDesc')
            child.text = str(custom_variable.description)

            # if there is a choice of specific value, list them to user instead
            if custom_variable.acceptedVals:
                child = SubElement(top, 'acceptedVals')
                child.text = str(custom_variable.acceptedVals)

            if custom_variable.numerical_max:
                child = SubElement(top, 'numerical_max')
                child.text = str(custom_variable.numerical_max)

            if custom_variable.type:
                child = SubElement(top, 'type')
                child.text = str(custom_variable.type)


        return tostring(root_tag)

    def add_xml_drive(self, device, tree_tag):

        top = SubElement(tree_tag, "found_drives")

        if isinstance(device, DriveWrapper):
            child = SubElement(top, 'Name')
            child.text = str(device.description)

            child = SubElement(top, 'Standard')
            child.text = str(device.identifier_str)

            child = SubElement(top, 'ConnType')
            child.text = str(device.drive_type)

            child = SubElement(top, 'Drive_Path')
            child.text = str(device.drive_path)

            child = SubElement(top, 'Sys_Cmd')
            child.text = str(device.system_cmd)

            child = SubElement(top, 'itemType')
            child.text = str("Drive")

            child = SubElement(top, 'XmlVersion')
            child.text = str(self.versionNumber)

    def add_xml_quarch_module(self, dict_key, dict_value, tree_tag, output_mode=None):

        top = SubElement(tree_tag, "quarch_modules")

        indexOfColon = dict_key.find(":")
        conType = str(dict_key[:indexOfColon])
        IpAddress = str(dict_key[indexOfColon + 1:])

        child = SubElement(top, 'ConnType')
        child.text = str(conType)

        child = SubElement(top, 'QtlNum')
        child.text = str(dict_value)

        child = SubElement(top, 'itemType')
        child.text = str("Module")

        if output_mode is not None:
            child = SubElement(top, "OutputMode")
            child.text = str(output_mode)

        child = SubElement(top, 'IpAddress')
        child.text = str(IpAddress)

    def add_report_item(self, dictionary, tree_tag, output_mode=None):

        top = SubElement(tree_tag, "report_items")

        for key, val in dictionary.items():
            child = SubElement(top, key)
            child.text = str(dictionary[key])

            if "custom_variables" in key:
                self.create_request_variable(custom_variable_list=val, root_tag=top)

            if "cpu" in key:
                child = SubElement(top, 'cpu')
                child.text = str(dictionary['cpu'])
            if "operating_system" in key:
                child = SubElement(top, 'operating_system')
                child.text = str(dictionary['operating_system'])
            if "host_platform" in key:
                child = SubElement(top, 'host_platform')
                child.text = str(dictionary['host_platform'])
            if "drive" in key:
                child = SubElement(top, 'drive')
                child.text = str(dictionary['drive'])
            if "quarch_module" in key:
                child = SubElement(top, 'quarch_module')
                child.text = str(dictionary['quarch_module'])

    def notifyTestLogEventXml(self, tree_tag, unique_id, timeStamp, logType, logText, logSource, test_result=None,
                              log_details=None, group=None, sub_group=None):
        if unique_id == "" or unique_id is None:
            # quick check in place just to ensure the unique id of an object is not sent incorrectly
            unique_id = " "

        # Build main XML structure
        xml_object = cElementTree.SubElement(tree_tag, "log_object")
        cElementTree.SubElement(xml_object, "uniqueID").text = unique_id
        cElementTree.SubElement(xml_object, "timestamp").text = datetime.utcfromtimestamp(timeStamp).strftime(
            '%Y-%m-%d %H:%M:%S')
        cElementTree.SubElement(xml_object, "logType").text = logType
        cElementTree.SubElement(xml_object, "text").text = logText
        cElementTree.SubElement(xml_object, "messageSource").text = logSource
        if test_result is not None:
            cElementTree.SubElement(xml_object, "test_result").text = test_result
        if group:
            cElementTree.SubElement(xml_object, "group").text = group
        if sub_group:
            cElementTree.SubElement(xml_object, "sub_group").text = sub_group

        # Add details dictionary if present
        if log_details is not None:
            xml_details = cElementTree.SubElement(xml_object, "logDetails")
            for k, v in log_details.items():
                xml_entry = cElementTree.SubElement(xml_details, "entry")
                cElementTree.SubElement(xml_entry, "key").text = str(k)
                cElementTree.SubElement(xml_entry, "value").text = str(v)

    def send_stop_test(self, reason=""):
        self.sendMsgToGUI(self.create_request_function(function_call="stop_test", function_value=reason,
                                                       requires_response=False))

    def send_start_timeout(self):
        self.sendMsgToGUI(self.create_request_function(function_call="start_timeout", requires_response=False))

    def send_stop_timeout(self):
        self.sendMsgToGUI(self.create_request_function(function_call="stop_timeout", requires_response=False))

    def isVersionCompat(self, version_number):
        # If the min version is current version, it is fine
        if version_number == dtsGlobals.minQCSVersion:
            return True
        version_numbers = version_number.split(".")
        min_version_numbers = dtsGlobals.minQCSVersion.split(".")
        # Iterate through each number to ensure compat
        for i, number in enumerate(version_numbers):
            # If same item is > it is a pass
            if version_numbers[i] > min_version_numbers[i]:
                return True
            # If same item is < it is a fail
            if version_numbers[i] < min_version_numbers[i]:
                return False

            # Should be redundant as we'll already know if they're the same
            # If last item of list
            if i == len(version_numbers) - 1:
                if version_numbers[i] == min_version_numbers[i]:
                    return True
        return True

    def parse_response(self, xml_tree, original_data):

        new_response = testLine()

        if str(xml_tree.tag).lower() == "response":
            new_response.parse_response(xml_tree, original_data)

        if new_response.qcs_version:
            dtsGlobals.QCSVersionValid = self.isVersionCompat(new_response.qcs_version)
            return True

        if new_response.user_choice:
            dtsGlobals.choiceResponse = new_response.user_choice
            return True

        if str(new_response.request_stop).lower() == "true":
            dtsGlobals.continueTest = False
            return True

        if new_response.qpy_version_valid and bool(new_response.qpy_version_valid) is False:
            dtsGlobals.validVersion = False
            return True

        if new_response.is_c_var_response:
            self.response = new_response.custom_variable_dict
            if not self.response:
                self.response = {}
            return True

        if new_response.function_complete:
            return True

        return False



