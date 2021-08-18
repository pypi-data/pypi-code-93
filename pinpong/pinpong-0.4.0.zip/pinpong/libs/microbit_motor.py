from pinpong.board import gboard,I2C
import time

class Microbit_Motor:
  PCA9685_ADDRESS                                 = 0x40
  MODE1                                           = 0x00
  MODE2                                           = 0x01
  PRESCALE                                        = 0xFE
  LED0_ON_L                                       = 0x06
  LED0_ON_H                                       = 0x07
  LED0_OFF_L                                      = 0x08
  LED0_OFF_L                                      = 0x09

  M1                                              = 0x1
  M2                                              = 0x2
  M3                                              = 0x3
  M4                                              = 0x4
  ALL                                             = 0x5

  CW                                              = 1
  CCW                                             = -1

  S1                                              = 0x08
  S2                                              = 0x07
  S3                                              = 0x06
  S4                                              = 0x05
  S5                                              = 0x04
  S6                                              = 0x03
  S7                                              = 0x02
  S8                                              = 0x01

  STP_CHA_L                                       =2047
  STP_CHA_H                                       =4095
  
  STP_CHB_L                                       =1
  STP_CHB_H                                       =2047
  
  STP_CHC_L                                       =1023
  STP_CHC_H                                       =3071
  
  STP_CHD_L                                       =3071
  STP_CHD_H                                       =1023
  
  BYG_CHA_L                                       =3071
  BYG_CHA_H                                       =1023
  
  BYG_CHB_L                                       =1023
  BYG_CHB_H                                       =3071
  
  BYG_CHC_L                                       =4095
  BYG_CHC_H                                       =2047
  
  BYG_CHD_L                                       =2047
  BYG_CHD_H                                       =4095

  M1_M2                                           = 0x1
  M3_M4                                           = 0x2
  def __init__(self, board=None, i2c_addr=0x40,bus_num=0):
    if isinstance(board, int):
      i2c_addr = board
      board = gboard
    elif board is None:
      board = gboard
      
    self.board = board
    self.i2c_addr = i2c_addr
    self.i2c = I2C(bus_num)

    self.init_PCA9685()
  
  def stepper_degree(self, index, direction, degree):
    self.set_stepper(index, direction > 0)
    if degree == 0:
      return
    Degree = abs(degree)
    time.sleep(((50000 * Degree) // (360*50)+80) / 1000)
    if index == 1:
      self.motor_stop(self.M1)
      self.motor_stop(self.M2)
    else:
      self.motor_stop(self.M3)
      self.motor_stop(self.M4)

  def stepper_turn(self, index, direction, turn):
    self.stepper_degree(index, direction, turn * 360)

  def set_stepper(self, index, dir):
    if index == 1:
      if dir:
        self.set_pwm(7, self.BYG_CHA_L, self.BYG_CHA_H)
        self.set_pwm(6, self.BYG_CHB_L, self.BYG_CHB_H)
        self.set_pwm(5, self.BYG_CHC_L, self.BYG_CHC_H)
        self.set_pwm(4, self.BYG_CHD_L, self.BYG_CHD_H)
      else:
        self.set_pwm(7, self.BYG_CHC_L, self.BYG_CHC_H)
        self.set_pwm(6, self.BYG_CHD_L, self.BYG_CHD_H)
        self.set_pwm(5, self.BYG_CHA_L, self.BYG_CHA_H)
        self.set_pwm(4, self.BYG_CHB_L, self.BYG_CHB_H)
    else:
      if dir:
        self.set_pwm(3, self.BYG_CHA_L, self.BYG_CHA_H)
        self.set_pwm(2, self.BYG_CHB_L, self.BYG_CHB_H)
        self.set_pwm(1, self.BYG_CHC_L, self.BYG_CHC_H)
        self.set_pwm(0, self.BYG_CHD_L, self.BYG_CHD_H)
      else:
        self.set_pwm(3, self.BYG_CHC_L, self.BYG_CHC_H)
        self.set_pwm(2, self.BYG_CHD_L, self.BYG_CHD_H)
        self.set_pwm(1, self.BYG_CHA_L, self.BYG_CHA_H)
        self.set_pwm(0, self.BYG_CHB_L, self.BYG_CHB_H)

  def servo(self, index, degree):
    if degree >= 180:
      degree = 180
    if degree < 0:
      degree = 0
    v_us = degree * 10 + 600
    value = v_us * 4095 // (1000000 // 50)
    self.set_pwm(index + 7, 0, value)

  def motor_stop(self, index):
    for i in range(1 if index == 5 else index, (index -1 if index == 5 else index) + 1):
        self.set_pwm((4-i) * 2, 0, 0)
        self.set_pwm((4-i) * 2 + 1, 0, 0)
  
  def motor_run(self, index, direction, speed):
    speed = speed * 16 * direction
    if speed >= 4096:
        speed = 4096
    if speed <= -4096:
        speed = -4096
    if index > 5 or index <= 0:
        return 
    for i in range(1 if index == 5 else index, (index -1 if index == 5 else index) + 1):
        pn = (4 - i) * 2
        pp = (4 - i) * 2 + 1
        if speed >= 0:
            self.set_pwm(pp, 0, speed)
            self.set_pwm(pn, 0, 0)
        else:
            self.set_pwm(pp ,0, 0)
            self.set_pwm(pn, 0, -speed)
      
  def set_pwm(self, channel, on, off):
    if channel < 0 or channel > 15:
        return
    buf = [self.LED0_ON_L+4*channel, on & 0xff, (on >> 8)&0xff, off & 0xff, (off>>8) & 0xff]
    self.i2c_write_buf(self.PCA9685_ADDRESS, buf)

  def init_PCA9685(self):
    self.writeReg(self.PCA9685_ADDRESS, self.MODE1, 0x00)
    self.set_freq(50)

  def set_freq(self, freq):
    prescaleval = 25000000
    prescaleval //= 4096
    prescaleval //= freq
    prescaleval -= 1
    prescale = prescaleval
    oldmode = self.readReg(self.PCA9685_ADDRESS, self.MODE1, 1)
    if oldmode != []:
        newmode = (oldmode[0] & 0x7F) | 0x10
        self.writeReg(self.PCA9685_ADDRESS, self.MODE1, newmode)
        self.writeReg(self.PCA9685_ADDRESS, self.PRESCALE, 0x84)
        self.writeReg(self.PCA9685_ADDRESS, self.MODE1, oldmode[0])
        time.sleep(0.005)
        self.writeReg(self.PCA9685_ADDRESS, self.MODE1, oldmode[0] | 0xa1)

  def readReg(self, address, reg, size):
    time.sleep(0.02)
    if reg == 0x1E:
      data = [0, 0x06]
      self.i2c.writeto_mem(address, reg, data)
      result = self.i2c.readfrom(address,size)
    else:
      result = self.i2c.readfrom_mem(address, reg, size)
    return result

  def i2c_write_buf(self, addr, p):
    self.i2c.writeto(addr, p)

  def writeReg(self, address, reg, val):
    if not isinstance(val, list):
        data = [val]
    self.i2c.writeto_mem(address, reg, data)