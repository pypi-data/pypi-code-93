import cv2
import argparse
import time

def get_args():
    parser = argparse.ArgumentParser(description="Args for VideoRecorder.")

    parser.add_argument('source', type=str, default="/dev/video0", help='camera port for VideoCapture')
    parser.add_argument('--fb', type=str, default="1280x720", help='<width>x<height>')
    parser.add_argument('--fourcc', type=str, default="MJPG", help='fourcc for VideoCapture')
    parser.add_argument('--fps', type=float, default=20.0, help='fps for VideoCapture')
    parser.add_argument('--exposure', type=int, default=0, help='exposure for VideoCapture')
    parser.add_argument('--show', type=bool, default=0, help='display window for showing image')
    parser.add_argument('--duration', type=float, default=3600, help="duration for recording video")

    args = parser.parse_args()
    return args

class VideoRecorder:
    def __init__(self, source, width, height, fourcc, fps, show, exposure, duration):
        self.source = source
        self.width = width
        self.height = height
        self.fourcc = fourcc
        self.show = show
        self.duration = duration

        self.cap = cv2.VideoCapture()
        self.cap.open(source)
        if not self.cap.isOpened():
            raise Exception("failed to open camera")
        self.cap.set(3, width)
        self.cap.set(4, height)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc(*fourcc))
        if exposure:
            self.cap.set(cv2.CAP_PROP_EXPOSURE, exposure)

        self.writer = cv2.VideoWriter()
        timestamp = time.time()
        filename = str(int(timestamp)) + ".avi"
        #  via pip install opencv-python then there's no encoding support for x264
        writer_fourcc = cv2.VideoWriter.fourcc(*"H264")
        self.writer.open(filename, writer_fourcc, fps, (width, height))
        if not self.writer.isOpened():
            writer_fourcc = cv2.VideoWriter.fourcc(*"MJPG")
            self.writer.open(filename, writer_fourcc, fps, (width, height))

    def capture(self):
        t_start = time.time()
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            if self.show:
                cv2.imshow("frame", frame)
                key = cv2.waitKey(1)
                if key == ord('q'):
                    break
            self.writer.write(frame)
            if time.time() - t_start > self.duration:
                break
        cv2.destroyAllWindows()
        self.cap.release()

if __name__ == '__main__':
    args = get_args()
    width, height = args.fb.split('x')
    recorder = VideoRecorder(args.source, int(width), int(height), args.fourcc, args.fps,
                             args.show, args.exposure, args.duration)
    recorder.capture()
