from moku import Moku
from moku import session
from moku.exceptions import MokuException
from moku.utilities import find_moku_by_serial
from moku.utilities import validate_range


class LogicAnalyzer(Moku):
    """
    Logic Analyzer instrument object.

    Instantiating this class will return a new Logic Analyzer
    instrument with the default state. This may raise a
    :any:`moku.exceptions.InvalidRequestException` if there
    is an active connection to the Moku.

    Available states for a pin are:

    =====  ========================
    State  Description
    =====  ========================
    I      Input
    O      Output
    H      High, pin is set to 1
    L      Low, pin is set to 0
    X      Off, Pin is off
    =====  ========================

    .. caution::
            Passing force_connect as True will forcefully takeover
            the control of Moku overwriting any existing session.

    """

    def __init__(self, ip=None, serial=None, force_connect=False):
        self.id = 17
        self.operation_group = "logicanalyzer"

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

    def get_pins(self):
        """
        get_pins.
        """
        operation = "get_pins"

        return self.session.post(self.operation_group, operation)

    def set_pins(self, pin, state, strict=True):
        """
        set_pin.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type pin: `string`, {'Pin1', 'Pin2', 'Pin3', 'Pin4', 'Pin5', 'Pin6', 'Pin7', 'Pin8', 'Pin9', 'Pin10', 'Pin11', 'Pin12', 'Pin13', 'Pin14', 'Pin15', 'Pin16'}
        :param pin: Target pin to configure

        :type state: `string`, {'I', 'O', 'H', 'L', 'X'}
        :param state: State of the target pin.

        """
        operation = "set_pins"

        params = dict(strict=strict,
                      pin=validate_range(pin,
                                         list(['Pin1',
                                               'Pin2',
                                               'Pin3',
                                               'Pin4',
                                               'Pin5',
                                               'Pin6',
                                               'Pin7',
                                               'Pin8',
                                               'Pin9',
                                               'Pin10',
                                               'Pin11',
                                               'Pin12',
                                               'Pin13',
                                               'Pin14',
                                               'Pin15',
                                               'Pin16'])),
                      state=validate_range(state,
                                           list(['I',
                                                 'O',
                                                 'H',
                                                 'L',
                                                 'X'])),
                      )
        return self.session.post(self.operation_group, operation, params)

    def start_all(self):
        """
        start_all.
        """
        operation = "start_all"

        return self.session.post(self.operation_group, operation)

    def generate_pattern(
            self,
            pin,
            pattern,
            divider=1,
            repeat=True,
            iterations=1,
            strict=True):
        """
        generate_pattern.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type pin: `string`, {'Pin1', 'Pin2', 'Pin3', 'Pin4', 'Pin5', 'Pin6', 'Pin7', 'Pin8', 'Pin9', 'Pin10', 'Pin11', 'Pin12', 'Pin13', 'Pin14', 'Pin15', 'Pin16'}
        :param pin: Pin to generate pattern on

        :type pattern: `array`
        :param pattern: Pattern to generate, array filled with 0's and 1's. Maximum size is 1024

        :type divider: `integer`, [1, 1e6]  (defaults to 1)
        :param divider: Divider to scale down the base frequency of 125 MHz to the tick frequency. Fore example, a divider of 2 provides a 62.5 MHz tick frequency.

        :type repeat: `boolean`
        :param repeat: Repeat forever

        :type iterations: `integer`, [1, 8192]  (defaults to 1)
        :param iterations: Number of iterations, valid when repeat is set to false

        """
        operation = "generate_pattern"

        params = dict(strict=strict,
                      pin=validate_range(pin,
                                         list(['Pin1',
                                               'Pin2',
                                               'Pin3',
                                               'Pin4',
                                               'Pin5',
                                               'Pin6',
                                               'Pin7',
                                               'Pin8',
                                               'Pin9',
                                               'Pin10',
                                               'Pin11',
                                               'Pin12',
                                               'Pin13',
                                               'Pin14',
                                               'Pin15',
                                               'Pin16'])),
                      pattern=pattern,
                      divider=divider,
                      repeat=repeat,
                      iterations=iterations,
                      )
        return self.session.post(self.operation_group, operation, params)

    def set_trigger(
            self,
            source,
            type="Edge",
            mode="Auto",
            edge="Rising",
            polarity="Positive",
            width_condition="GreaterThan",
            width=0.0001,
            nth_event=1,
            holdoff=0,
            strict=True):
        """
        set_trigger.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type source: `string`, {'Pin1', 'Pin2', 'Pin3', 'Pin4', 'Pin5', 'Pin6', 'Pin7', 'Pin8', 'Pin9', 'Pin10', 'Pin11', 'Pin12', 'Pin13', 'Pin14', 'Pin15', 'Pin16'}
        :param source: Trigger Source

        :type type: `string`, {'Edge', 'Pulse'} (defaults to Edge)
        :param type: Trigger type

        :type mode: `string`, {'Auto', 'Normal', 'Single'} (defaults to Auto)
        :param mode: Trigger mode

        :type edge: `string`, {'Rising', 'Falling', 'Both'} (defaults to Rising)
        :param edge: Which edge to trigger on (edge mode only)

        :type polarity: `string`, {'Positive', 'Negative'} (defaults to Positive)
        :param polarity: Trigger pulse polarity

        :type width_condition: `string`, {'GreaterThan', 'LessThan'} (defaults to GreaterThan)
        :param width_condition: Trigger pulse width condition (pulse mode only)

        :type width: `number`, [26e-3Sec, 10Sec]  (defaults to 0.0001)
        :param width: Trigger width

        :type nth_event: `integer`, [0, 65535]  (defaults to 1)
        :param nth_event: The number of trigger events to wait for before triggering

        :type holdoff: `number`, [1e-9Sec, 10Sec]  (defaults to 0)
        :param holdoff: The duration to hold off Oscilloscope trigger post trigger event.

        """
        operation = "set_trigger"

        params = dict(strict=strict,
                      source=validate_range(source,
                                            list(['Pin1',
                                                  'Pin2',
                                                  'Pin3',
                                                  'Pin4',
                                                  'Pin5',
                                                  'Pin6',
                                                  'Pin7',
                                                  'Pin8',
                                                  'Pin9',
                                                  'Pin10',
                                                  'Pin11',
                                                  'Pin12',
                                                  'Pin13',
                                                  'Pin14',
                                                  'Pin15',
                                                  'Pin16'])),
                      type=validate_range(type,
                                          list(['Edge',
                                                'Pulse'])),
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
                      width_condition=validate_range(width_condition,
                                                     list(['GreaterThan',
                                                           'LessThan'])),
                      width=width,
                      nth_event=nth_event,
                      holdoff=holdoff,
                      )
        return self.session.post(self.operation_group, operation, params)

    def set_timebase(self, t1, t2, roll_mode, strict=True):
        """
        set_timebase.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type t1: `number`
        :param t1: Time from the trigger point to the left of screen.

        :type t2: `number`
        :param t2: Time from the trigger point to the right of screen. (Must be a positive number, i.e. post trigger event)

        :type roll_mode: `boolean`
        :param roll_mode: Toggle Roll Mode

        """
        operation = "set_timebase"

        params = dict(strict=strict, t1=t1, t2=t2, roll_mode=roll_mode,)
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
