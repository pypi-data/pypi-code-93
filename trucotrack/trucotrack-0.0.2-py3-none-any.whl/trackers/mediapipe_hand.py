import mediapipe as mp
from google.protobuf.json_format import MessageToDict
# from trucotrack.processors import csv_writer
from trucotrack.processors import csv_gzip_writer as csv_writer

class MediapipeHand:
    BONES = [
        'wrist', 'thumb_cmc', 'thumb_mcp', 'thumb_ip', 'thumb_tip',
        'index_finger_mcp', 'index_finger_pip', 'index_finger_dip', 'index_finger_tip',
        'middle_finger_mcp', 'middle_finger_pip', 'middle_finger_dip', 'middle_finger_tip',
        'ring_finger_mcp', 'ring_finger_pip', 'ring_finger_dip', 'ring_finger_tip',
        'pinky_mcp', 'pinky_pip', 'pinky_dip', 'pinky_tip']

    def __init__(self, args):
        self.args = args

        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=args.mp_hands_static == 'yes',
            max_num_hands=args.mp_hands_max)

        if self.args.mp_hands_csv != None:
            self.writer = csv_writer.CsvGzipWriter(self.args.mp_hands_csv, self.args)

        print('MediaPipe hand tracker will now start running with this arguments', self.args)

    def process(self, dispatched_frame):
        frame = dispatched_frame['frame']
        frame_rgb = dispatched_frame['frame_rgb']
        frame_number = dispatched_frame['frame_number']

        results = self.hands.process(frame_rgb)
        if not results.multi_hand_landmarks:
            return []

        records = []
        for hand_id, hand in enumerate(results.multi_handedness):
            hand = MessageToDict(hand)['classification'][0]
            hand_landmarks_message = results.multi_hand_landmarks[hand_id]

            if self.args.mp_hands_draw == 'yes':
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks_message,
                    self.mp_hands.HAND_CONNECTIONS)

            hand_landmarks = MessageToDict(hand_landmarks_message)['landmark']
            record = self.organize(hand, hand_landmarks, frame, frame_number)
            records.append(record)

        if hasattr(self, 'writer'):
            for record in records:
                self.writer.write(record)

        return records

    def organize(self, hand, hand_landmarks, frame, frame_number):
        height, width, _ = frame.shape

        record = {
            'frame_number': str(frame_number),
            'hand_index': str(hand['index']),
            'hand_score': '{:-f}'.format(hand['score']),
            'hand_handness': hand['label']
        }

        for bone_id, bone in enumerate(self.BONES):
            bone_landmarks = hand_landmarks[bone_id]
            bone_name = self.BONES[bone_id]

            for axe in bone_landmarks:
                if axe == 'x':
                    scale = width
                else:
                    scale = height

                bone_landmark = bone_landmarks[axe] * scale
                record[bone_name + '_' + axe] = '{:-f}'.format(bone_landmark)

        return record

    def close_writer(self):
        if hasattr(self, 'writer'):
            self.writer.close()
