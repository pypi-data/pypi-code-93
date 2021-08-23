from moku import Moku
from moku import session
from moku.exceptions import MokuException
from moku.utilities import find_moku_by_serial
from moku.utilities import validate_range


class FrequencyResponseAnalyzer(Moku):
    """
    Frequency Response Analyzer instrument object.

    Instantiating this class will return a new Frequency Response Analyzer
    instrument with the default state. This may raise a
    :any:`moku.exceptions.InvalidRequestException` if there is an
    active connection to the Moku.

    .. caution::
            Passing force_connect as True will forcefully takeover
            the control of Moku overwriting any existing session.

    """

    def __init__(self, ip=None, serial=None, force_connect=False):
        self.id = 9
        self.operation_group = "fra"

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

    def fra_measurement(
            self,
            channel,
            input_only=False,
            start_frequency=0,
            stop_frequency=0,
            averaging_duration=0,
            averaging_cycles=0,
            output_amplitude=0,
            strict=True):
        """
        fra_measurement.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type input_only: `boolean`
        :param input_only: If enabled, measures input signal alone. Defaults to false, which is In/Out mode

        :type start_frequency: `number`, [1e-3Hz, 20e6Hz]  (defaults to 0)
        :param start_frequency: Sweep start frequency

        :type stop_frequency: `number`, [1e-3Hz, 20e6Hz]  (defaults to 0)
        :param stop_frequency: Sweep end frequency

        :type averaging_duration: `number`, [1e-6Sec, 10Sec]  (defaults to 0)
        :param averaging_duration: Minimum averaging time per sweep point.

        :type averaging_cycles: `integer`, [1, 1048576]  (defaults to 0)
        :param averaging_cycles: Minimum averaging cycles per sweep point.

        :type output_amplitude: `number`, [2e-3Vpp, 10Vpp]  (defaults to 0)
        :param output_amplitude: Output amplitude

        """
        operation = "fra_measurement"

        params = dict(
            strict=strict,
            channel=channel,
            input_only=input_only,
            start_frequency=start_frequency,
            stop_frequency=stop_frequency,
            averaging_duration=averaging_duration,
            averaging_cycles=averaging_cycles,
            output_amplitude=output_amplitude,
        )
        return self.session.post(self.operation_group, operation, params)

    def measurement_mode(self, input_only=False, strict=True):
        """
        measurement_mode.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type input_only: `boolean`
        :param input_only: Set the measurement mode. If enabled, measures input signal alone. Defaults to false, which is In/Out mode

        """
        operation = "measurement_mode"

        params = dict(strict=strict, input_only=input_only,)
        return self.session.post(self.operation_group, operation, params)

    def set_sweep(
            self,
            start_frequency=0,
            stop_frequency=0,
            num_points=512,
            averaging_time=0,
            averaging_cycles=0,
            settling_time=0,
            settling_cycles=0,
            linear_scale=False,
            strict=True):
        """
        set_sweep.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type start_frequency: `number`, [1e-3Hz, 20e6Hz]  (defaults to 0)
        :param start_frequency: Sweep start frequency

        :type stop_frequency: `number`, [1e-3Hz, 20e6Hz]  (defaults to 0)
        :param stop_frequency: Sweep stop frequency

        :type num_points: `integer`
        :param num_points: Number of points in the sweep (rounded to nearest power of 2)

        :type averaging_time: `number`, [1e-6Sec, 10Sec]  (defaults to 0)
        :param averaging_time: Minimum averaging time per sweep point.

        :type averaging_cycles: `integer`, [1, 1048576]  (defaults to 0)
        :param averaging_cycles: Minimum averaging cycles per sweep point.

        :type settling_time: `number`, [1e-6Sec, 10Sec]  (defaults to 0)
        :param settling_time: Minimum settling time per sweep point.

        :type settling_cycles: `integer`, [1, 1048576]  (defaults to 0)
        :param settling_cycles: Minimum settling cycles per sweep point.

        :type linear_scale: `boolean`
        :param linear_scale: Enables linear scale. If set to false scale is set to logarithmic. Defaults to false

        """
        operation = "set_sweep"

        params = dict(
            strict=strict,
            start_frequency=start_frequency,
            stop_frequency=stop_frequency,
            num_points=num_points,
            averaging_time=averaging_time,
            averaging_cycles=averaging_cycles,
            settling_time=settling_time,
            settling_cycles=settling_cycles,
            linear_scale=linear_scale,
        )
        return self.session.post(self.operation_group, operation, params)

    def start_sweep(self):
        """
        start_sweep.
        """
        operation = "start_sweep"

        return self.session.post(self.operation_group, operation)

    def stop_sweep(self):
        """
        stop_sweep.
        """
        operation = "stop_sweep"

        return self.session.post(self.operation_group, operation)

    def set_output(self, channel, amplitude, offset=0, strict=True):
        """
        set_output.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type amplitude: `number`, [-5V, 5V]
        :param amplitude: Waveform peak-to-peak amplitude

        :type offset: `number`, [-5V, 5V]  (defaults to 0)
        :param offset: DC offset applied to the waveform

        """
        operation = "set_output"

        params = dict(
            strict=strict,
            channel=channel,
            amplitude=amplitude,
            offset=offset,
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

    def set_harmonic_multiplier(self, multiplier=1, strict=True):
        """
        set_harmonic_multiplier.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type multiplier: `integer`, [1, 15]  (defaults to 1)
        :param multiplier: Multiplier applied to the fundamental frequency

        """
        operation = "set_harmonic_multiplier"

        params = dict(strict=strict, multiplier=multiplier,)
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
