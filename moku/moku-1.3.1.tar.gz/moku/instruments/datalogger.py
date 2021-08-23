from moku import Moku
from moku import session
from moku.exceptions import MokuException
from moku.utilities import find_moku_by_serial
from moku.utilities import validate_range


class Datalogger(Moku):
    """
    Datalogger instrument object.

    Instantiating this class will return a new Datalogger
    instrument with the default state. This may raise a
    :any:`moku.exceptions.InvalidRequestException` if there is an
    active connection to the Moku.

    .. caution::
            Passing force_connect as True will forcefully takeover
            the control of Moku overwriting any existing session.

    """

    def __init__(self, ip=None, serial=None, force_connect=False):
        self.id = 7
        self.operation_group = "datalogger"

        if not any([ip, serial]):
            raise MokuException("IP (or) Serial is required")
        if serial:
            ip = find_moku_by_serial(serial)

        self.session = session.RequestSession(ip)
        super().__init__(force_connect=force_connect, session=self.session)
        self.upload_bitstream(self.id)

    def set_frontend(self, channel, impedance, coupling, range, strict=True):
        """
        set_frontend.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type impedance: `string`, {'1MOhm', '50Ohm'}
        :param impedance: Impedance

        :type coupling: `string`, {'AC', 'DC'}
        :param coupling: Input Coupling

        :type range: `string`, {'Default', '400mVpp', '1Vpp', '4Vpp', '10Vpp', '40Vpp', '50Vpp'}
        :param range: Input Range

        """
        operation = "set_frontend"

        params = dict(strict=strict,
                      channel=channel,
                      impedance=validate_range(impedance,
                                               list(['1MOhm',
                                                     '50Ohm'])),
                      coupling=validate_range(coupling,
                                              list(['AC',
                                                    'DC'])),
                      range=validate_range(range,
                                           list(['Default',
                                                 '400mVpp',
                                                 '1Vpp',
                                                 '4Vpp',
                                                 '10Vpp',
                                                 '40Vpp',
                                                 '50Vpp'])),
                      )
        return self.session.post(self.operation_group, operation, params)

    def set_acquisition_mode(self, mode="Normal", strict=True):
        """
        set_acquisition_mode.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type mode: `string`, {'Normal', 'Precision', 'PeakDetect'} (defaults to Normal)
        :param mode: Acquisition Mode

        """
        operation = "set_acquisition_mode"

        params = dict(strict=strict, mode=validate_range(
            mode, list(['Normal', 'Precision', 'PeakDetect'])),)
        return self.session.post(self.operation_group, operation, params)

    def set_samplerate(self, sample_rate, strict=True):
        """
        set_samplerate.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type sample_rate: `number`, [10, 1e6]
        :param sample_rate: Target samples per second

        """
        operation = "set_samplerate"

        params = dict(strict=strict, sample_rate=sample_rate,)
        return self.session.post(self.operation_group, operation, params)

    def disable_channel(self, channel, disable=True, strict=True):
        """
        disable_channel.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type disable: `boolean`
        :param disable: Boolean value to enable/disable

        """
        operation = "disable_channel"

        params = dict(strict=strict, channel=channel, disable=disable,)
        return self.session.post(self.operation_group, operation, params)

    def summary(self):
        """
        summary.
        """
        operation = "summary"

        return self.session.get(self.operation_group, operation)

    def generate_waveform(
            self,
            channel,
            type,
            amplitude=1,
            frequency=10000,
            offset=0,
            phase=0,
            duty=50,
            symmetry=50,
            dc_level=0,
            edge_time=0,
            pulse_width=0,
            strict=True):
        """
        generate_waveform.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type type: `string`, {'Off', 'Sine', 'Square', 'Ramp', 'Pulse', 'DC'}
        :param type: Waveform type

        :type amplitude: `number`, [4e-3V, 10V]  (defaults to 1)
        :param amplitude: Waveform peak-to-peak amplitude

        :type frequency: `number`, [1e-3Hz, 20e6Hz]  (defaults to 10000)
        :param frequency: Waveform frequency

        :type offset: `number`, [-5V, 5V]  (defaults to 0)
        :param offset: DC offset applied to the waveform

        :type phase: `number`, [0Deg, 360Deg]  (defaults to 0)
        :param phase: Waveform phase offset

        :type duty: `number`, [0.0%, 100.0%]  (defaults to 50)
        :param duty: Duty cycle as percentage (Only for Square wave)

        :type symmetry: `number`, [0.0%, 100.0%]  (defaults to 50)
        :param symmetry: Fraction of the cycle rising

        :type dc_level: `number`
        :param dc_level: DC Level. (Only for DC waveform)

        :type edge_time: `number`, [16e-9, pulse width]  (defaults to 0)
        :param edge_time: Edge-time of the waveform (Only for Pulse wave)

        :type pulse_width: `number`
        :param pulse_width: Pulse width of the waveform (Only for Pulse wave)

        """
        operation = "generate_waveform"

        params = dict(strict=strict,
                      channel=channel,
                      type=validate_range(type,
                                          list(['Off',
                                                'Sine',
                                                'Square',
                                                'Ramp',
                                                'Pulse',
                                                'DC'])),
                      amplitude=amplitude,
                      frequency=frequency,
                      offset=offset,
                      phase=phase,
                      duty=duty,
                      symmetry=symmetry,
                      dc_level=dc_level,
                      edge_time=edge_time,
                      pulse_width=pulse_width,
                      )
        return self.session.post(self.operation_group, operation, params)

    def start_logging(
            self,
            duration=60,
            file_name_prefix="",
            comments="",
            stop_existing=False,
            strict=True):
        """
        start_logging.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type duration: `integer`, Sec (defaults to 60)
        :param duration: Duration to log for

        :type file_name_prefix: `string`
        :param file_name_prefix: Optional file name prefix

        :type comments: `string`
        :param comments: Optional comments to be included

        :type stop_existing: `boolean`
        :param stop_existing: Pass as true to stop any existing session and begin a new one


        .. important::
            It is recommended **not** to relinquish the ownership of the
            device until logging session is completed

        """
        operation = "start_logging"

        params = dict(
            strict=strict,
            duration=duration,
            file_name_prefix=file_name_prefix,
            comments=comments,
            stop_existing=stop_existing,
        )
        return self.session.post(self.operation_group, operation, params)

    def logging_progress(self):
        """
        logging_progress.
        """
        operation = "logging_progress"

        return self.session.get(self.operation_group, operation)

    def stop_logging(self):
        """
        stop_logging.
        """
        operation = "stop_logging"

        return self.session.get(self.operation_group, operation)
