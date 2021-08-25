import asyncio

from OpenHub.homekit_accessories.homkit_sensor_interface import HomeKitSensorInterface
import logging
from OpenHub.globals import driver
from pyhap.const import CATEGORY_CAMERA
from pyhap.camera import Camera as PyHapCamera
from pyhap.camera import VIDEO_CODEC_PARAM_PROFILE_ID_TYPES, VIDEO_CODEC_PARAM_LEVEL_TYPES

logger = logging.getLogger(__name__)


class Camera(PyHapCamera):
    run_debug_message = "Camera State: "
    FFMPEG_CMD = (
        """raspivid -o - -t 0 -rot 180 -w {width} -h {height} -fps {fps} -b 2000000 | cvlc -vvv stream:///dev/stdin --sout '#rtp{{sdp=rtsp://{address}:{v_port}}}' :demux=h264""")

    category = CATEGORY_CAMERA

    def __init__(self, serial_no=None, display_name=None, *args, **kwargs):
        self.category = CATEGORY_CAMERA
        self.FFMPEG_CMD = (
            """raspivid -o - -t 0 -rot 180 -w {width} -h {height} -fps {fps} -b 2000000 | cvlc -vvv stream:///dev/stdin --sout '#rtp{{sdp=rtsp://{address}:{v_port}}}' :demux=h264""")

        options = {"video": {
            "codec": {
                "profiles": [
                    VIDEO_CODEC_PARAM_PROFILE_ID_TYPES["BASELINE"],
                ],
                "levels": [
                    VIDEO_CODEC_PARAM_LEVEL_TYPES['TYPE3_1'],
                ],
            },
            "resolutions": [
                [1280, 720, 30],
            ],
        }, "audio": {
            "codecs": []
        }, "address": "192.168.1.136",
            'start_stream_cmd': "raspivid -o - -t 0 -rot 180 -w {width} -h {height} -fps {fps} -b 2000000 | cvlc -vvv stream:///dev/stdin --sout '#rtp{{sdp=rtsp://{address}:{v_port}}}' :demux=h264",
            'srtp': False}
        self.display_name = self.set_display_name(display_name)
        self.serial_no = serial_no

        super().__init__(options, driver=driver, display_name=self.display_name, *args, **kwargs)
        # super(HomeKitSensorInterface, self).__init__(serial_no=serial_no, display_name=display_name, *args,
        #                                              **kwargs)

    def set_display_name(self, display_name):
        if display_name is None:
            return "Camera"
        else:
            return display_name

    # def add_functional_service(self):
    #     return self.add_preload_service('C')
    #
    # def add_functional_service_characteristic(self):
    #     # return self.service.configure_char(
    #     #     'On', setter_callback=self.set_relay)
    #     pass
    #     # ### For client extensions ###

    # def get_snapshot(self, image_size):  # pylint: disable=unused-argument, no-self-use
    #     """Return a jpeg of a snapshot from the camera.
    #     Overwrite to implement getting snapshots from your camera.
    #     :param image_size: ``dict`` describing the requested image size. Contains the
    #         keys "image-width" and "image-height"
    #     """
    #     with open(os.path.join(RESOURCE_DIR, 'snapshot.jpg'), 'rb') as fp:
    #         return fp.read()
