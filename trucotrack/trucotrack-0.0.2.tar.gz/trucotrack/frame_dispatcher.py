import cv2

class FrameDispatcher:
    def __init__(self, args):
        self.frame_number = 0
        self.args = args
        print('The frame dispatcher will now start running with this arguments', self.args)

    def get_frame(self):
        if self.args.video != None:
            capture = cv2.VideoCapture(self.args.video)
        else:
            capture = cv2.VideoCapture(self.args.camera)

        while True:
            result, frame = capture.read()
            if result == False:
                break

            self.frame_number += 1

            if self.args.first != None and 'camera' not in self.args:
                if self.frame_number < self.args.first:
                    continue

            if self.args.last != None:
                if self.frame_number > self.args.last:
                    break

            if self.args.flip == 'yes':
                frame = cv2.flip(frame, 1)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            frame_to_dispatch = {
                'args': self.args,
                'frame_number': self.frame_number,
                'frame': frame,
                'frame_rgb': frame_rgb
            }

            if self.args.first != None and 'camera' in self.args:
                if self.frame_number >= self.args.first:
                    yield frame_to_dispatch
            else:
                yield frame_to_dispatch

            if cv2.waitKey(1) & 0xFF == 27:
                break

        capture.release()
        cv2.destroyAllWindows()
