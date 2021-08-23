from boxx import *

with inpkg():
    from .hik_camera import *
    from . import hik_camera


class HikCamera(hik_camera.HikCamera):
    def setting(self):
        self.set_exposure(25000)  # 1999733

        self.pixel_format = "RGB8Packed"
        self.setitem("PixelFormat", self.pixel_format)
        self.set_raw()

        self.setitem("GevSCPD", 43200)  # 包延时 ns


if __name__ == "__main__":
    """
    sshpass -p '1qaz!QAZ' scp -P 3336 -r /home/dl/ai_asrs/hik_camera/hik_camera Administrator@47.103.201.240:hik_camera/; sshpass -p '1qaz!QAZ' ssh -p 3336 Administrator@47.103.201.240 python hik_camera/hik_camera/tmp_windows_debug.py
    """

    ips = HikCamera.get_all_ips()
    print(ips)
    ip = list(ips)[0]
    if 1:
        pass
    for ip in ips[::]:
        cam = HikCamera(ip)
        print(ip)
        with cam:
            print(cam["DeviceModelName"])
            # print(cam["ExposureTime"])
            # print("GevSCPSPacketSize:", cam["GevSCPSPacketSize"])
            # cam["Gain"] = 0  # 19.8
            # print(cam["Gain"])
            # print(cam["PixelSize"])
            # print(cam["PixelFormat"])
            for i in range(1):
                with boxx.timeit("cam.get_frame"):
                    img = tree / cam.get_frame()
                    # print("cam.get_exposure", cam["ExposureTime"])
            # print(cam["PixelFormat"])

            path = "D:/ai_asrs/tmp/windows_debug" if sysi.win else tmpboxx()
            boxx.makedirs(path)
            tmp_filename = pathjoin(path, localTimeStr(True))
            if p / cam.is_raw:
                cam.save_raw(img, tmp_filename + ".dng", compress=False)
                rgbs = [
                    # cam.raw_to_uint8_rgb(img, poww=0.3),
                ]
                rgb = cam.raw_to_uint8_rgb(img, poww=0.3)
                img = rgb
            boxx.imsave(pred / tmp_filename + ".jpg", img)
        sleep(1)



if 0:
    cams = HikCamera.get_all_cams()
    with cams:
        with boxx.timeit("cams.get_frame"):
            imgs = cams.get_frame()
        print("imgs = cams.get_frame()")
        boxx.tree(imgs)
