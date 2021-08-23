from moku import Moku
from moku import session
from moku.exceptions import MokuException
from moku.utilities import find_moku_by_serial
from moku.utilities import validate_range


class WaveformGenerator(Moku):
    """
    Waveform Generator instrument object.

    Instantiating this class will return a new  Waveform Generator
    instrument with the default state. This may raise a
    :any:`moku.exceptions.InvalidRequestException` if there is an
    active connection to the Moku.

    .. caution::
            Passing force_connect as True will forcefully takeover
            the control of Moku overwriting any existing session.

    """

    def __init__(self, ip=None, serial=None, force_connect=False):
        self.id = 4
        self.operation_group = "waveformgenerator"

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

    def set_defaults(self):
        """
        set_defaults.
        """
        operation = "set_defaults"

        return self.session.post(self.operation_group, operation)

    def output_load(self, channel, load, strict=True):
        """
        output_load.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type load: `string`, {'1MOhm', '50Ohm'}
        :param load: Output load

        """
        operation = "output_load"

        params = dict(strict=strict, channel=channel,
                      load=validate_range(load, list(['1MOhm', '50Ohm'])),)
        return self.session.post(self.operation_group, operation, params)

    def sync_phase(self):
        """
        sync_phase.
        """
        operation = "sync_phase"

        return self.session.get(self.operation_group, operation)

    def set_modulation(
            self,
            channel,
            type,
            source,
            depth=0,
            frequency=10000000,
            strict=True):
        """
        set_modulation.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type type: `string`, {'Amplitude', 'Frequency', 'Phase'}
        :param type: Modulation type

        :type source: `string`, {'Input1', 'Input2', 'Input3', 'Input4', 'Output1', 'Output2', 'Output3', 'Output4', 'Internal'}
        :param source: Modulation source

        :type depth: `number`,  (defaults to 0)
        :param depth: Modulation depth (depends on modulation type): Percentage modulation depth, Frequency Deviation/Volt or +/- phase shift/Volt

        :type frequency: `number`, [0Hz, 50e6Hz]  (defaults to 10000000)
        :param frequency: Frequency of internally-generated sine wave modulation. This parameter is ignored if the source is set to ADC or DAC.

        """
        operation = "set_modulation"

        params = dict(strict=strict,
                      channel=channel,
                      type=validate_range(type,
                                          list(['Amplitude',
                                                'Frequency',
                                                'Phase'])),
                      source=validate_range(source,
                                            list(['Input1',
                                                  'Input2',
                                                  'Input3',
                                                  'Input4',
                                                  'Output1',
                                                  'Output2',
                                                  'Output3',
                                                  'Output4',
                                                  'Internal'])),
                      depth=depth,
                      frequency=frequency,
                      )
        return self.session.post(self.operation_group, operation, params)

    def disable_modulation(self, channel, strict=True):
        """
        disable_modulation.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "disable_modulation"

        params = dict(strict=strict, channel=channel,)
        return self.session.post(self.operation_group, operation, params)

    def set_burst_mode(
            self,
            channel,
            source,
            mode,
            trigger_level=0,
            burst_cycles=3,
            burst_duration=0.1,
            burst_period=1,
            strict=True):
        """
        set_burst_mode.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type source: `string`, {'Input1', 'Input2', 'Input3', 'Input4', 'Output1', 'Output2', 'Output3', 'Output4', 'Internal', 'External'}
        :param source: Trigger source

        :type mode: `string`, {'Gated', 'Start', 'NCycle'}
        :param mode: Burst mode

        :type trigger_level: `number`, [-5V, 5V]  (defaults to 0)
        :param trigger_level: Trigger threshold level

        :type burst_cycles: `number`, [1, 1e6]  (defaults to 3)
        :param burst_cycles: The integer number of signal repetitions to generate once triggered (NCycle mode only)

        :type burst_duration: `number`, [1 cycle periodSec, 1e3Sec]  (defaults to 0.1)
        :param burst_duration: Burst duration

        :type burst_period: `number`
        :param burst_period: Burst Period

        """
        operation = "set_burst_mode"

        params = dict(strict=strict,
                      channel=channel,
                      source=validate_range(source,
                                            list(['Input1',
                                                  'Input2',
                                                  'Input3',
                                                  'Input4',
                                                  'Output1',
                                                  'Output2',
                                                  'Output3',
                                                  'Output4',
                                                  'Internal',
                                                  'External'])),
                      mode=validate_range(mode,
                                          list(['Gated',
                                                'Start',
                                                'NCycle'])),
                      trigger_level=trigger_level,
                      burst_cycles=burst_cycles,
                      burst_duration=burst_duration,
                      burst_period=burst_period,
                      )
        return self.session.post(self.operation_group, operation, params)

    def set_sweep_mode(
            self,
            channel,
            source,
            stop_frequency=30000000,
            sweep_time=1,
            trigger_level=0,
            strict=True):
        """
        set_sweep_mode.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type source: `string`, {'Input1', 'Input2', 'Input3', 'Input4', 'Output1', 'Output2', 'Output3', 'Output4', 'Internal', 'External'}
        :param source: Trigger source

        :type stop_frequency: `number`, [100Hz, 20e6Hz]  (defaults to 30000000)
        :param stop_frequency: Sweep stop Frequency

        :type sweep_time: `number`, [1 cycle periodSec, 1e3Sec]  (defaults to 1)
        :param sweep_time: Duration of sweep

        :type trigger_level: `number`, [-5V, 5V]  (defaults to 0)
        :param trigger_level: Trigger threshold level

        """
        operation = "set_sweep_mode"

        params = dict(strict=strict,
                      channel=channel,
                      source=validate_range(source,
                                            list(['Input1',
                                                  'Input2',
                                                  'Input3',
                                                  'Input4',
                                                  'Output1',
                                                  'Output2',
                                                  'Output3',
                                                  'Output4',
                                                  'Internal',
                                                  'External'])),
                      stop_frequency=stop_frequency,
                      sweep_time=sweep_time,
                      trigger_level=trigger_level,
                      )
        return self.session.post(self.operation_group, operation, params)
