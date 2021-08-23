from moku import Moku
from moku import session
from moku.exceptions import MokuException
from moku.utilities import find_moku_by_serial
from moku.utilities import validate_range


class SpectrumAnalyzer(Moku):
    """
    Spectrum Analyzer instrument object.

    Instantiating this class will return a new Spectrum Analyzer
    instrument with the default state. This may raise a
    :any:`moku.exceptions.InvalidRequestException` if there is an
    active connection to the Moku.

    .. caution::
            Passing force_connect as True will forcefully takeover
            the control of Moku overwriting any existing session.

    """

    def __init__(self, ip=None, serial=None, force_connect=False):
        self.id = 2
        self.operation_group = "spectrumanalyzer"

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

    def sa_output(self, channel, amplitude, frequency, strict=True):
        """
        sa_output.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type amplitude: `number`
        :param amplitude: Waveform peak-to-peak amplitude

        :type frequency: `number`, [0Hz, 30e6Hz]
        :param frequency: Frequency of the wave

        """
        operation = "sa_output"

        params = dict(
            strict=strict,
            channel=channel,
            amplitude=amplitude,
            frequency=frequency,
        )
        return self.session.post(self.operation_group, operation, params)

    def get_rbw(self):
        """
        get_rbw.
        """
        operation = "get_rbw"

        return self.session.get(self.operation_group, operation)

    def set_rbw(self, mode, rbw_value=5000, strict=True):
        """
        set_rbw.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type mode: `string`, {'Auto', 'Manual', 'Minimum'}
        :param mode: Desired resolution bandwidth (Hz)

        :type rbw_value: `number`
        :param rbw_value: RBW value (only in manual mode)

        """
        operation = "set_rbw"

        params = dict(strict=strict, mode=validate_range(
            mode, list(['Auto', 'Manual', 'Minimum'])), rbw_value=rbw_value,)
        return self.session.post(self.operation_group, operation, params)

    def set_span(self, frequency1, frequency2, strict=True):
        """
        set_span.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type frequency1: `number`, [0Hz, 30e6Hz]
        :param frequency1: Left-most frequency

        :type frequency2: `number`, [0Hz, 30e6Hz]
        :param frequency2: Right-most frequency

        """
        operation = "set_span"

        params = dict(
            strict=strict,
            frequency1=frequency1,
            frequency2=frequency2,
        )
        return self.session.post(self.operation_group, operation, params)

    def sa_measurement(
            self,
            channel,
            frequency1,
            frequency2,
            rbw="Auto",
            rbw_value=5000,
            window="BlackmanHarris",
            strict=True):
        """
        sa_measurement.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type frequency1: `number`, [0Hz, 30e6Hz]
        :param frequency1: Left-most frequency

        :type frequency2: `number`, [0Hz, 30e6Hz]
        :param frequency2: Right-most frequency

        :type rbw: `string`, {'Auto', 'Manual', 'Minimum'} (defaults to Auto)
        :param rbw: Desired resolution bandwidth (Hz)

        :type rbw_value: `number`
        :param rbw_value: RBW value (only in manual mode)

        :type window: `string`, {'BlackmanHarris', 'FlatTop', 'Hanning', 'Rectangular'} (defaults to BlackmanHarris)
        :param window: Window Function

        """
        operation = "sa_measurement"

        params = dict(strict=strict,
                      channel=channel,
                      frequency1=frequency1,
                      frequency2=frequency2,
                      rbw=validate_range(rbw,
                                         list(['Auto',
                                               'Manual',
                                               'Minimum'])),
                      rbw_value=rbw_value,
                      window=validate_range(window,
                                            list(['BlackmanHarris',
                                                  'FlatTop',
                                                  'Hanning',
                                                  'Rectangular'])),
                      )
        return self.session.post(self.operation_group, operation, params)

    def set_window(self, window, strict=True):
        """
        set_window.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type window: `string`, {'BlackmanHarris', 'FlatTop', 'Hanning', 'Rectangular'}
        :param window: Window Function

        """
        operation = "set_window"

        params = dict(strict=strict, window=validate_range(window, list(
            ['BlackmanHarris', 'FlatTop', 'Hanning', 'Rectangular'])),)
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

    def get_data(
            self,
            timeout=60,
            wait_reacquire=False,
            units="dBm",
            psdUnits=False,
            strict=True):
        """
        get_data.

        :type timeout: `number`, Seconds (defaults to 60)
        :param timeout: Wait for n seconds to receive a data frame

        :type wait_reacquire: `boolean`
        :param wait_reacquire: Wait until new dataframe is reacquired

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type units: `string`, {'dBm', 'Vrms', 'Vpp', 'dBV'} (defaults to dBm)
        :param units: Units

        :type psdUnits: `boolean`
        :param psdUnits: PSD Units


        .. important::
            Default timeout for reading the data is 10 seconds. It
            can be increased by setting the read_timeout property of
            session object.

            Example: ``i.session.read_timeout=100`` (in seconds)

        """
        operation = "get_data"

        params = dict(timeout=timeout,
                      wait_reacquire=wait_reacquire,
                      strict=strict,
                      units=validate_range(units,
                                           list(['dBm',
                                                 'Vrms',
                                                 'Vpp',
                                                 'dBV'])),
                      psdUnits=psdUnits,
                      )
        return self.session.post(self.operation_group, operation, params)
