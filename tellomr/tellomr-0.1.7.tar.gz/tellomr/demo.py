import time
from tellomr import tello


drone = tello.Tello()

drone.key_control()

# 打开视频流
drone.streamon()
time.sleep(1)

# 开启视频流附加功能
# drone.stream_service_on()

# 起飞
drone.takeoff()

# 前进100cm
drone.forward(100)

# 旋转90°
drone.cw(90)

# 识别当前视频流中是否包含动物
# drone.identify_animal()

# 左翻滚
# drone.flip('l')

input()

# 降落
drone.land()

# 关闭视频流
drone.streamoff()
