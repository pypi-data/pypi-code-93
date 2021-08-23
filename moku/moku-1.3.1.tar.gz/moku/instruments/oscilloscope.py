from moku import Moku
from moku import session
from moku.exceptions import MokuException
from moku.utilities import find_moku_by_serial
from moku.utilities import validate_range


class Oscilloscope(Moku):
    """
    Oscilloscope instrument object.

    Instantiating this class will return a new Oscilloscope
    instrument with the default state. This may raise a
    :any:`moku.exceptions.InvalidRequestException` if there is an
    active connection to the Moku.

    .. caution::
            Passing force_connect as True will forcefully takeover
            the control of Moku overwriting any existing session.

    """

    def __init__(self, ip=None, serial=None, force_connect=False):
        self.id = 1
        self.operation_group = "oscilloscope"

        if not any([ip, serial]):
            raise MokuException("IP (or) Serial is required")
        if serial:
            ip = find_moku_by_serial(serial)

        self.session = session.RequestSession(ip)
        super().__init__(force_connect=force_connect, session=self.session)
        self.upload_bitstream(self.id)

        self.set_defaults()

    def set_defaults(self):
        """
        set_defaults.
        """
        operation = "set_defaults"

        return self.session.post(self.operation_group, operation)

    def sync_output_phase(self):
        """
        sync_output_phase.
        """
        operation = "sync_output_phase"

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

    def set_source(self, channel, source, strict=True):
        """
        set_source.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type source: `string`, {'None', 'Input1', 'Input2', 'Input3', 'Input4', 'Output1', 'Output2', 'Output3', 'Output4'}
        :param source: Set channel data source

        """
        operation = "set_source"

        params = dict(strict=strict,
                      channel=channel,
                      source=validate_range(source,
                                            list(['None',
                                                  'Input1',
                                                  'Input2',
                                                  'Input3',
                                                  'Input4',
                                                  'Output1',
                                                  'Output2',
                                                  'Output3',
                                                  'Output4'])),
                      )
        return self.session.post(self.operation_group, operation, params)

    def osc_measurement(
            self,
            t1,
            t2,
            trigger_source,
            edge,
            level,
            strict=True):
        """
        osc_measurement.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type t1: `number`
        :param t1: Time from the trigger point to the left of screen

        :type t2: `number`
        :param t2: Time from the trigger point to the right of screen. (Must be a positive number, i.e. after the trigger event)

        :type trigger_source: `string`, {'ChannelA', 'ChannelB', 'ChannelC', 'ChannelD', 'Input1', 'Input2', 'Input3', 'Input4', 'Output1', 'Output2', 'Output3', 'Output4', 'ProbeA', 'ProbeB', 'ProbeC', 'ProbeD', 'External'}
        :param trigger_source: Trigger source

        :type edge: `string`, {'Rising', 'Falling', 'Both'}
        :param edge: Which edge to trigger on. Only edge trigger is used with this function, pulse trigger can be enabled using set_trigger()

        :type level: `number`, [-5V, 5V]
        :param level: Trigger level

        """
        operation = "osc_measurement"

        params = dict(strict=strict,
                      t1=t1,
                      t2=t2,
                      trigger_source=validate_range(trigger_source,
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
                      edge=validate_range(edge,
                                          list(['Rising',
                                                'Falling',
                                                'Both'])),
                      level=level,
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

    def summary(self):
        """
        summary.
        """
        operation = "summary"

        return self.session.get(self.operation_group, operation)

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
