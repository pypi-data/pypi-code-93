import numpy as np
from easydict import EasyDict as edict
from pymodaq.daq_utils.daq_utils import (
    ThreadCommand,
    getLineInfo,
    DataFromPlugins,
    Axis,
)
from pymodaq.daq_viewer.utility_classes import DAQ_Viewer_base, comon_parameters
from PyQt5 import QtWidgets
import usb
from ...hardware import stellarnet as sn
from scipy.ndimage.filters import uniform_filter1d
import os, glob

class DAQ_1DViewer_Stellarnet(DAQ_Viewer_base):
    """
    """

    params = comon_parameters + [
        {
            "title": "Spectrometer Model:",
            "name": "spectrometer_model",
            "type": "list",
            "value": [],
            "readonly": True,
        },
        {
            "title": "Spectrometer ID:",
            "name": "spectrometer_id",
            "type": "int",
            "value": 0,
            "readonly": True,
        },
        {
            "title": "Calibration file:",
            "name": "cal_path",
            "type": "browsepath",
            "value": "",
            "readonly": False,
        },
        {
            "title": "Irradiance or counts (T/F):",
            "name": "irradiance_on",
            "type": "bool",
            "value": False,
        },
        {
            "title": "Take snapshot:",
            "name": "take_snap",
            "type": "bool",
            "value": False,
        },
        {
            "title": "Integration time (ms):",
            "name": "int_time",
            "type": "int",
            "value": 100,
            "default": 100,
            "min": 2,
            "max": 65535,
        },
        {
            "title": "X Timing Rate:",
            "name": "x_timing",
            "type": "int",
            "value": 3,
            "default": 3,
            "min": 1,
            "max": 3,
        },
        {
            "title": "Moving average window size:",
            "name": "x_smooth",
            "type": "int",
            "value": 0,
            "min": 0,
        },
        {
            "title": "Number of spectra to average:",
            "name": "scans_to_avg",
            "type": "int",
            "value": 1,
            "default": 1,
            "min": 1,
        },
    ]

    hardware_averaging = False

    def __init__(self, parent=None, params_state=None):

        super().__init__(parent, params_state)
        self.x_axis = None
        self.calibration = None
        self.controller = None
        self.calib_file_ok = None
        self.calib_on = False
        self.snapshot = None

        if self.settings.child("cal_path").value() == "":
            sn_path = os.path.dirname(sn.__file__)
            cal_path = glob.glob(sn_path+"\\*.CAL")[0]
            self.settings.child("cal_path").setValue(cal_path)

    def commit_settings(self, param):
        """
        """
        if param.name() == "int_time":
            self.controller.set_config(int_time=param.value())
        elif param.name() == "x_timing":
            self.controller.set_config(x_timing=param.value())
        elif param.name() == "x_smooth":
            self.controller.window_width = param.value()
        elif param.name() == "scans_to_avg":
            self.controller.set_config(scans_to_avg=param.value())
        elif param.name() == "irradiance_on":
            if param.value():  # calibrated
                self.calib_on = True
            else:
                self.calib_on = False

        elif param.name() == "cal_path":
            self.do_irradiance_calibration()

        elif param.name() == "take_snap":
            try:
                self.snapshot = np.asarray(self.moving_average(self.controller.read_spectrum()))
                self.settings.child("take_snap").setValue(False)

            except Exception as e:
                self.emit_status(
                    ThreadCommand("Update_Status", [getLineInfo() + str(e), "log"])
                )
                self.status.info = getLineInfo() + str(e)

    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object) custom object of a PyMoDAQ plugin (Slave case). None if only one detector by controller (Master case)

        Returns
        -------
        self.status (edict): with initialization status: three fields:
            * info (str)
            * controller (object) initialized controller
            *initialized: (bool): False if initialization failed otherwise True
        """

        try:
            print(os.getcwd())
            self.status.update(
                edict(
                    initialized=False,
                    info="",
                    x_axis=None,
                    y_axis=None,
                    controller=None,
                )
            )
            if self.settings.child("controller_status").value() == "Slave":
                if controller is None:
                    raise Exception(
                        "no controller has been defined externally while this detector is a slave one"
                    )
                else:
                    self.controller = controller
            else:
                devices = usb.core.find(
                    find_all=True,
                    idVendor=sn.StellarNet._STELLARNET_VENDOR_ID,
                    idProduct=sn.StellarNet._STELLARNET_PRODUCT_ID,
                )
                devices_count = len(list(devices))
                if devices_count > 1:
                    print(
                        "Warning, several Stellarnet devices found. I'll load the first one only."
                    )

                self.controller = sn.StellarNet(
                    devices[0]
                )  # Instance of StellarNet class
                self.settings.child("spectrometer_model").setValue(
                    self.controller._config["model"]
                )
                self.settings.child("spectrometer_id").setValue(
                    self.controller._config["device_id"]
                )
                setattr(
                    self.controller,
                    "window_width",
                    self.settings.child("x_smooth").value(),
                )

            # get the x_axis (you may want to to this also in the commit settings if x_axis may have changed
            data_x_axis = self.get_wl_axis()
            self.x_axis = [Axis(data=data_x_axis, label="Wavelength", units="m")]
            self.emit_x_axis()

            # initialize viewers pannel with the future type of data
            name = usb.util.get_string(
                self.controller._device, 100, self.controller._device.iProduct
            )
            data_init = [
                (
                    DataFromPlugins(
                        name=name,
                        dim="Data1D",
                        data=[np.asarray(self.controller.read_spectrum())],
                        x_axis=Axis(data=data_x_axis, label="Wavelength", units="m"),
                    )
                )
            ]
            QtWidgets.QApplication.processEvents()
            self.data_grabed_signal_temp.emit(data_init)
            self.data_grabed_signal_temp.emit(
                data_init
            )  # works the second time for some reason

            try:
                self.do_irradiance_calibration()
            except Exception as e:
                self.emit_status(
                    ThreadCommand("Update_Status", [getLineInfo() + str(e), "log"])
                )

            self.status.info = "Log test"
            self.status.initialized = True
            self.status.controller = self.controller
            return self.status

        except Exception as e:
            self.emit_status(
                ThreadCommand("Update_Status", [getLineInfo() + str(e), "log"])
            )
            self.status.info = getLineInfo() + str(e)
            self.status.initialized = False
            return self.status

    def close(self):
        """
            Not implemented.
        """
        return

    def do_irradiance_calibration(self):
        calibration = []
        try:
            with open(self.settings.child("cal_path").value(), "r") as file:
                for line in file:
                    if line[0].isdigit():
                        calibration.append(np.fromstring(line, sep=" "))
            calibration = np.asarray(calibration)

            idx_nonzero = np.nonzero(calibration[:, 1])[0]
            lowE_avg = np.mean(calibration[idx_nonzero[:10], 1])
            calibration[calibration[:, 1] == 0, 1] = lowE_avg

            self.calib_file_ok = True

            self.calibration = np.interp(
                self.x_axis[0]["data"]*1e9, calibration[:, 0], calibration[:, 1]
            )

        except:
            self.calib_file_ok = False
            self.calibration = None

    def moving_average(self, spectrum):
        N = self.controller.window_width
        if N == 0:
            return spectrum
        else:
            return uniform_filter1d(spectrum, size=N)

    def get_wl_axis(self):  # in meters
        pixels = np.arange(
            sn.StellarNet._PIXEL_MAP[self.controller._config["det_type"]]
        )

        if "coeffs" not in self.controller._config:
            raise Exception("Device has no stored coefficients")

        coeffs = self.controller._config["coeffs"]
        return 1e-9 * (
            (pixels ** 3) * coeffs[3] / 8.0
            + (pixels ** 2) * coeffs[1] / 4.0
            + pixels * coeffs[0] / 2.0
            + coeffs[2]
        )

    def grab_data(self, Naverage=1, **kwargs):
        """

        Parameters
        ----------
        kwargs: (dict) of others optionals arguments
        """
        ##synchrone version (blocking function)
        if self.calib_on and self.calib_file_ok:
            try:
                data_tot = [
                    self.calibration
                    * np.asarray(self.moving_average(self.controller.read_spectrum()))
                ]
            except:
                data_tot = [
                    np.asarray(self.moving_average(self.controller.read_spectrum()))
                ]
            label = "Irradiance (W/m2)"

        else:
            data_tot = [
                np.asarray(self.moving_average(self.controller.read_spectrum()))
            ]
            label = ["Signal (counts)"]

        if self.snapshot is not None:
            data_tot.append(self.snapshot)
            label.append("Snapshot")

        self.data_grabed_signal.emit(
            [
                DataFromPlugins(
                    name="StellarNet", data=data_tot, dim="Data1D", labels=label, x_axis=self.x_axis[0]
                )
            ]
        )

    # def callback(self):
    #     """optional asynchrone method called when the detector has finished its acquisition of data"""
    #     data_tot = self.controller.your_method_to_get_data_from_buffer()
    #     self.data_grabed_signal.emit([DataFromPlugins(name='Mock1', data=data_tot,
    #                                               dim='Data1D', labels=['dat0', 'data1'])])

    def stop(self):
        """
            Not implemented.
        """
        return
