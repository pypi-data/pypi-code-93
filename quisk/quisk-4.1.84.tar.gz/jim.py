from soapypkg.quisk_hardware import Hardware as BaseHardware
class Hardware(BaseHardware):
  def __init__(self, app, conf):
    BaseHardware.__init__(self, app, conf)
