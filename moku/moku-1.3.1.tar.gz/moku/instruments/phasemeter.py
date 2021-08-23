from moku import Moku
from moku import session
from moku.exceptions import MokuException
from moku.utilities import find_moku_by_serial
from moku.utilities import validate_range


class Phasemeter(Moku):
    """
    The Phasemeter instrument is used to measure the amplitude and change in
    phase of periodic input signals.

    Using the auto-acquire feature, it can automatically lock to input
    frequencies in the range of 2-200MHz and track phase with a
    bandwidth of 10kHz.

    """

    def __init__(self, ip=None, serial=None, force_connect=False):
        self.id = 3
        self.operation_group = "phasemeter"

        if not any([ip, serial]):
            raise MokuException("IP (or) Serial is required")
        if serial:
            ip = find_moku_by_serial(serial)

        self.session = session.RequestSession(ip)
        super().__init__(force_connect=force_connect, session=self.session)
        self.upload_bitstream(self.id)

        self.set_defaults()

    def summary(self):
        """
        summary.
        """
        operation = "summary"

        return self.session.get(self.operation_group, operation)

    def set_defaults(self):
        """
        set_defaults.
        """
        operation = "set_defaults"

        return self.session.post(self.operation_group, operation)

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

    def set_acquisition_speed(self, speed, strict=True):
        """
        set_acquisition_speed.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type speed: `string`, {'30Hz', '120Hz', '480Hz', '2kHz', '15kHz', '122kHz'}
        :param speed: Acquisition Speed

        """
        operation = "set_acquisition_speed"

        params = dict(strict=strict, speed=validate_range(speed, list(
            ['30Hz', '120Hz', '480Hz', '2kHz', '15kHz', '122kHz'])),)
        return self.session.post(self.operation_group, operation, params)

    def get_acquisition_speed(self):
        """
        get_acquisition_speed.
        """
        operation = "get_acquisition_speed"

        return self.session.get(self.operation_group, operation)

    def set_pm_loop(
            self,
            channel,
            auto_acquire=False,
            frequency=30000000,
            bandwidth="2k5Hz",
            strict=True):
        """
        set_pm_loop.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type auto_acquire: `boolean`
        :param auto_acquire: Auto acquire frequency

        :type frequency: `number`
        :param frequency: Initial locking frequency of the designated channel

        :type bandwidth: `string`, {'10kHz', '2k5Hz', '600Hz', '150Hz', '40Hz', '10Hz'} (defaults to 2k5Hz)
        :param bandwidth: Bandwidth

        """
        operation = "set_pm_loop"

        params = dict(strict=strict,
                      channel=channel,
                      auto_acquire=auto_acquire,
                      frequency=frequency,
                      bandwidth=validate_range(bandwidth,
                                               list(['10kHz',
                                                     '2k5Hz',
                                                     '600Hz',
                                                     '150Hz',
                                                     '40Hz',
                                                     '10Hz'])),
                      )
        return self.session.post(self.operation_group, operation, params)

    def get_auto_acquired_frequency(self, channel, strict=True):
        """
        get_auto_acquired_frequency.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_auto_acquired_frequency"

        params = dict(strict=strict, channel=channel,)
        return self.session.post(self.operation_group, operation, params)

    def generate_output(
            self,
            channel,
            amplitude,
            frequency,
            phase=0,
            phase_locked=False,
            signal="Sine",
            phase_scaling=0.001,
            strict=True):
        """
        generate_output.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type amplitude: `number`
        :param amplitude: Waveform peak-to-peak amplitude

        :type frequency: `number`
        :param frequency: Frequency of the wave

        :type phase: `number`
        :param phase: Phase offset of the wave

        :type phase_locked: `boolean`
        :param phase_locked: Locks the phase of the generated sinewave to the measured phase of the input signal

        :type signal: `string`, {'Sine', 'Phase'} (defaults to Sine)
        :param signal: Type of output signal

        :type phase_scaling: `number`
        :param phase_scaling: Phase scaling

        """
        operation = "generate_output"

        params = dict(strict=strict,
                      channel=channel,
                      amplitude=amplitude,
                      frequency=frequency,
                      phase=phase,
                      phase_locked=phase_locked,
                      signal=validate_range(signal,
                                            list(['Sine',
                                                  'Phase'])),
                      phase_scaling=phase_scaling,
                      )
        return self.session.post(self.operation_group, operation, params)

    def disable_output(self, channel, strict=True):
        """
        disable_output.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "disable_output"

        params = dict(strict=strict, channel=channel,)
        return self.session.post(self.operation_group, operation, params)

    def disable_freewheeling(self, disable=True, strict=True):
        """
        disable_freewheeling.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type disable: `boolean`
        :param disable: Disable free wheeling

        """
        operation = "disable_freewheeling"

        params = dict(strict=strict, disable=disable,)
        return self.session.post(self.operation_group, operation, params)

    def get_data(self, timeout=60, wait_reacquire=False):
        """
        get_data.

        :type timeout: `number`, Seconds (defaults to 60)
        :param timeout: Wait for n seconds to receive a data frame

        :type wait_reacquire: `boolean`
        :param wait_reacquire: Wait until new dataframe is reacquired


        .. important::
            Default timeout for reading the data is 10 seconds. It
            can be increased by setting the read_timeout property of
            session object.

            Example: ``i.session.read_timeout=100`` (in seconds)

        """
        operation = "get_data"

        params = dict(timeout=timeout, wait_reacquire=wait_reacquire,)
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
