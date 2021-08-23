from moku import Moku
from moku import session
from moku.exceptions import MokuException
from moku.utilities import find_moku_by_serial
from moku.utilities import validate_range


class PIDController(Moku):
    """
    PIDController instrument object.

    Instantiating this class will return a new PIDController
    instrument with the default state. This may raise a
    :any:`moku.exceptions.InvalidRequestException` if there is an
    active connection to the Moku.

    .. caution::
            Passing force_connect as True will forcefully takeover
            the control of Moku overwriting any existing session.

    """

    def __init__(self, ip=None, serial=None, force_connect=False):
        self.id = 5
        self.operation_group = "pidcontroller"

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

    def set_control_matrix(
            self,
            channel,
            input_gain1,
            input_gain2,
            strict=True):
        """
        set_control_matrix.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type input_gain1: `number`, [0dB, 20dB]
        :param input_gain1: ADC input gain for Channel 1

        :type input_gain2: `number`, [0dB, 20dB]
        :param input_gain2: ADC input gain for Channel 2

        """
        operation = "set_control_matrix"

        params = dict(
            strict=strict,
            channel=channel,
            input_gain1=input_gain1,
            input_gain2=input_gain2,
        )
        return self.session.post(self.operation_group, operation, params)

    def enable_output(
            self,
            channel,
            signal,
            output,
            enable_gain=False,
            strict=True):
        """
        enable_output.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type signal: `boolean`
        :param signal: Enable/Disable output signal

        :type output: `boolean`
        :param output: Enable/Disable output

        :type enable_gain: `boolean`
        :param enable_gain: If applicable, sets the output gain

        """
        operation = "enable_output"

        params = dict(
            strict=strict,
            channel=channel,
            signal=signal,
            output=output,
            enable_gain=enable_gain,
        )
        return self.session.post(self.operation_group, operation, params)

    def enable_input(self, channel, enabled, strict=True):
        """
        enable_input.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type enabled: `boolean`
        :param enabled: Enable/Disable input signal

        """
        operation = "enable_input"

        params = dict(strict=strict, channel=channel, enabled=enabled,)
        return self.session.post(self.operation_group, operation, params)

    def set_input_offset(self, channel, offset, strict=True):
        """
        set_input_offset.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type offset: `number`, [-5V, 5V]
        :param offset: Output DC offset

        """
        operation = "set_input_offset"

        params = dict(strict=strict, channel=channel, offset=offset,)
        return self.session.post(self.operation_group, operation, params)

    def set_output_offset(self, channel, offset, strict=True):
        """
        set_output_offset.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type offset: `number`, [-5V, 5V]
        :param offset: Output DC offset

        """
        operation = "set_output_offset"

        params = dict(strict=strict, channel=channel, offset=offset,)
        return self.session.post(self.operation_group, operation, params)

    def set_monitor(self, monitor_channel, source, strict=True):
        """
        set_monitor.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type monitor_channel: `integer`
        :param monitor_channel: Monitor channel

        :type source: `string`, {'None', 'Input1', 'Control1', 'Output1', 'Input2', 'Control2', 'Output2', 'Input3', 'Control3', 'Output3', 'Input4', 'Control4', 'Output4'}
        :param source: Monitor channel source. The source is one of: Input1 : Channel 1 ADC input, Control1 : PID Channel 1 input (after mixing, offset and scaling), Output1 : PID Channel 1 output, Input2 : Channel 2 ADC Input, Control2 : PID Channel 2 input (after mixing, offset and scaling), Output2 : PID Channel 2 output

        """
        operation = "set_monitor"

        params = dict(strict=strict,
                      monitor_channel=monitor_channel,
                      source=validate_range(source,
                                            list(['None',
                                                  'Input1',
                                                  'Control1',
                                                  'Output1',
                                                  'Input2',
                                                  'Control2',
                                                  'Output2',
                                                  'Input3',
                                                  'Control3',
                                                  'Output3',
                                                  'Input4',
                                                  'Control4',
                                                  'Output4'])),
                      )
        return self.session.post(self.operation_group, operation, params)

    def set_by_gain_and_section(
            self,
            channel,
            section,
            overall_gain=20,
            prop_gain=None,
            int_gain=None,
            diff_gain=None,
            int_corner=None,
            diff_corner=None,
            strict=True):
        """
        set_by_gain_and_section.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type section: `integer`
        :param section: Section to configure

        :type overall_gain: `number`
        :param overall_gain: Overall Gain

        :type prop_gain: `number`
        :param prop_gain: Proportional gain factor

        :type int_gain: `number`
        :param int_gain: Integrator gain factor

        :type diff_gain: `number`
        :param diff_gain: Differentiator gain factor

        :type int_corner: `number`
        :param int_corner: Integrator gain corner

        :type diff_corner: `number`
        :param diff_corner: Differentiator gain corner

        """
        operation = "set_by_gain_and_section"

        params = dict(
            strict=strict,
            channel=channel,
            section=section,
            overall_gain=overall_gain,
            prop_gain=prop_gain,
            int_gain=int_gain,
            diff_gain=diff_gain,
            int_corner=int_corner,
            diff_corner=diff_corner,
        )
        return self.session.post(self.operation_group, operation, params)

    def set_by_gain(
            self,
            channel,
            overall_gain=20,
            prop_gain=None,
            int_gain=None,
            diff_gain=None,
            int_corner=None,
            diff_corner=None,
            strict=True):
        """
        set_by_gain.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type overall_gain: `number`
        :param overall_gain: Overall Gain

        :type prop_gain: `number`
        :param prop_gain: Proportional gain factor

        :type int_gain: `number`
        :param int_gain: Integrator gain factor

        :type diff_gain: `number`
        :param diff_gain: Differentiator gain factor

        :type int_corner: `number`
        :param int_corner: Integrator gain corner

        :type diff_corner: `number`
        :param diff_corner: Differentiator gain corner

        """
        operation = "set_by_gain"

        params = dict(
            strict=strict,
            channel=channel,
            overall_gain=overall_gain,
            prop_gain=prop_gain,
            int_gain=int_gain,
            diff_gain=diff_gain,
            int_corner=int_corner,
            diff_corner=diff_corner,
        )
        return self.session.post(self.operation_group, operation, params)

    def set_by_frequency(
            self,
            channel,
            prop_gain=-10,
            int_crossover=None,
            diff_crossover=None,
            double_int_crossover=None,
            int_saturation=None,
            diff_saturation=None,
            strict=True):
        """
        set_by_frequency.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type prop_gain: `number`, [-60dB, 60dB]  (defaults to -10)
        :param prop_gain: Proportional gain factor

        :type int_crossover: `number`, [31.25e-3Hz, 312.5e3Hz]
        :param int_crossover: Integrator crossover frequency

        :type diff_crossover: `number`, [312.5e-3Hz, 3.125e6Hz]
        :param diff_crossover: Differentiator crossover frequency

        :type double_int_crossover: `number`, [31.25e-3Hz, 312.5e3Hz]
        :param double_int_crossover: Second integrator crossover frequency

        :type int_saturation: `number`, [-60dB, 60dB]
        :param int_saturation: Integrator gain saturation

        :type diff_saturation: `number`, [-60dB, 60dB]
        :param diff_saturation: Differentiator gain saturation

        """
        operation = "set_by_frequency"

        params = dict(
            strict=strict,
            channel=channel,
            prop_gain=prop_gain,
            int_crossover=int_crossover,
            diff_crossover=diff_crossover,
            double_int_crossover=double_int_crossover,
            int_saturation=int_saturation,
            diff_saturation=diff_saturation,
        )
        return self.session.post(self.operation_group, operation, params)

    def set_timebase(self, t1, t2, strict=True):
        """
        set_timebase.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type t1: `number`
        :param t1: Time from the trigger point to the left of screen. This may be negative (trigger on-screen) or positive (trigger off the left of screen).

        :type t2: `number`
        :param t2: Time from the trigger point to the right of screen. (Must be a positive number, i.e. after the trigger event)

        """
        operation = "set_timebase"

        params = dict(strict=strict, t1=t1, t2=t2,)
        return self.session.post(self.operation_group, operation, params)

    def set_trigger(
            self,
            type="Edge",
            source="Input1",
            level=0,
            mode="Auto",
            edge="Rising",
            polarity="Positive",
            width=0.0001,
            width_condition="LessThan",
            nth_event=1,
            holdoff=0,
            auto_sensitivity=True,
            noise_reject=False,
            hf_reject=False,
            strict=True):
        """
        set_trigger.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type type: `string`, {'Edge', 'Pulse'} (defaults to Edge)
        :param type: Trigger type

        :type source: `string`, {'ChannelA', 'ChannelB', 'ChannelC', 'ChannelD', 'Input1', 'Input2', 'Input3', 'Input4', 'Output1', 'Output2', 'Output3', 'Output4', 'ProbeA', 'ProbeB', 'ProbeC', 'ProbeD', 'External'} (defaults to Input1)
        :param source: Trigger Source

        :type level: `number`, [-5V, 5V]  (defaults to 0)
        :param level: Trigger level

        :type mode: `string`, {'Auto', 'Normal', 'Single'} (defaults to Auto)
        :param mode: Trigger mode

        :type edge: `string`, {'Rising', 'Falling', 'Both'} (defaults to Rising)
        :param edge: Which edge to trigger on. In Pulse Width modes this specifies whether the pulse is positive (rising) or negative (falling), with the 'both' option being invalid

        :type polarity: `string`, {'Positive', 'Negative'} (defaults to Positive)
        :param polarity: Trigger pulse polarity (Pulse mode only)

        :type width: `number`, [26e-3Sec, 10Sec]  (defaults to 0.0001)
        :param width: Width of the trigger pulse (Pulse mode only)

        :type width_condition: `string`, {'GreaterThan', 'LessThan'} (defaults to LessThan)
        :param width_condition: Trigger pulse width condition (pulse mode only)

        :type nth_event: `integer`, [0, 65535]  (defaults to 1)
        :param nth_event: The number of trigger events to wait for before triggering

        :type holdoff: `number`, [1e-9Sec, 10Sec]  (defaults to 0)
        :param holdoff: The duration to hold-off Oscilloscope trigger post trigger event

        :type auto_sensitivity: `boolean`
        :param auto_sensitivity: Configure auto or manual hysteresis for noise rejection.

        :type noise_reject: `boolean`
        :param noise_reject: Configure the Oscilloscope with a small amount of hysteresis to prevent repeated triggering due to noise

        :type hf_reject: `boolean`
        :param hf_reject: Configure the trigger signal to pass through a low pass filter to smooths out the noise

        """
        operation = "set_trigger"

        params = dict(strict=strict,
                      type=validate_range(type,
                                          list(['Edge',
                                                'Pulse'])),
                      source=validate_range(source,
                                            list(['ChannelA',
                                                  'ChannelB',
                                                  'ChannelC',
                                                  'ChannelD',
                                                  'Input1',
                                                  'Input2',
                                                  'Input3',
                                                  'Input4',
                                                  'Output1',
                                                  'Output2',
                                                  'Output3',
                                                  'Output4',
                                                  'ProbeA',
                                                  'ProbeB',
                                                  'ProbeC',
                                                  'ProbeD',
                                                  'External'])),
                      level=level,
                      mode=validate_range(mode,
                                          list(['Auto',
                                                'Normal',
                                                'Single'])),
                      edge=validate_range(edge,
                                          list(['Rising',
                                                'Falling',
                                                'Both'])),
                      polarity=validate_range(polarity,
                                              list(['Positive',
                                                    'Negative'])),
                      width=width,
                      width_condition=validate_range(width_condition,
                                                     list(['GreaterThan',
                                                           'LessThan'])),
                      nth_event=nth_event,
                      holdoff=holdoff,
                      auto_sensitivity=auto_sensitivity,
                      noise_reject=noise_reject,
                      hf_reject=hf_reject,
                      )
        return self.session.post(self.operation_group, operation, params)

    def set_hysteresis(self, hysteresis_mode, value=0, strict=True):
        """
        set_hysteresis.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type hysteresis_mode: `string`, {'Absolute', 'Relative'}
        :param hysteresis_mode: Trigger sensitivity hysteresis mode

        :type value: `number`
        :param value: Hysteresis around trigger

        """
        operation = "set_hysteresis"

        params = dict(strict=strict, hysteresis_mode=validate_range(
            hysteresis_mode, list(['Absolute', 'Relative'])), value=value,)
        return self.session.post(self.operation_group, operation, params)

    def enable_rollmode(self, roll=False, strict=True):
        """
        enable_rollmode.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type roll: `boolean`
        :param roll: Enable roll

        """
        operation = "enable_rollmode"

        params = dict(strict=strict, roll=roll,)
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
