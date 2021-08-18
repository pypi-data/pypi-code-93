import smbus  # pylint: disable=E0401
import time, math

SHT3x_I2C_ADDRESS = 0x44

def exception_catch(func):
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e)
            return None
    return func_wrapper

class uFire_SHT3x():
    tempC = 0
    tempF = 0
    vpd_kPa = 0
    dew_pointC = 0
    dew_pointF = 0
    RH = 0
    status = 0
    _address = 0
    _i2cPort = 0
    status_string = ["no error", "not connected", "crc error"]

    @exception_catch
    def begin(self, i2c_bus=1):
        self._address = SHT3x_I2C_ADDRESS
        self._i2cPort = smbus.SMBus(i2c_bus)

    @exception_catch
    def connected(self):
        try:
            self._i2cPort.write_quick(self._address)
            return True
        except IOError:
            return False

    @exception_catch
    def measure(self):
        if (self.connected == False):
            self.status = 1
            return

        self._i2cPort.write_i2c_block_data(SHT3x_I2C_ADDRESS, 0x30, [0xA2])         # reset
        time.sleep(1 / 1000)
        self._i2cPort.write_i2c_block_data(SHT3x_I2C_ADDRESS, 0x24, [0x00])         # high accuracy, no clock stretching
        time.sleep(15 / 1000.0)
        data = self._i2cPort.read_i2c_block_data(SHT3x_I2C_ADDRESS, 0, 6)

        if (data[2] == self._crc(bytearray([data[0], data[1]]))):
            self.tempC = ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
            self.tempF = (self.tempC * 1.8) + 32;
            self.status = 0
        else:
            self.tempC = 0
            self.tempF = 0
            self.vpd_kPa = 0
            self.dew_pointC = 0
            self.dew_pointF = 0
            self.RH = 0
            self.status = 3;
            return

        if (data[5] == self._crc(bytearray([data[3], data[4]]))):
            self.RH = 100 * (data[3] * 256 + data[4]) / 65535.0
            
            # vpd
            es = 0.61078 * math.exp(17.2694 * self.tempC / (self.tempC + 238.3));
            ae = self.RH / 100 * es;
            self.vpd_kPa = es - ae;

            #dp
            tem = -1.0 * self.tempC;
            esdp = 6.112 * math.exp(-1.0 * 17.67 * tem / (243.5 - tem));
            ed = self.RH / 100.0 * esdp;
            eln = math.log(ed / 6.112);
            self.dew_pointC = -243.5 * eln / (eln - 17.67);
            self.dew_pointF = (self.dew_pointC * 1.8) + 32;

            self.status = 0
        else:
            self.tempC = 0
            self.tempF = 0
            self.vpd_kPa = 0
            self.dew_pointC = 0
            self.dew_pointF = 0
            self.RH = 0
            self.status = 3;
            return

    @exception_catch
    def _crc(self, data):
            crc = 0xff
            for byte in data:
                crc ^= byte
                for _ in range(8):
                    if crc & 0x80:
                        crc <<= 1
                        crc ^= 0x131  
                    else:
                        crc <<= 1
            return crc