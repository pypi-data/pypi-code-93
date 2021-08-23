import cv2
import mediapipe as mp
from trucotrack.writers import csv_writer
from google.protobuf.json_format import MessageToDict

class MediapipeHand:
    BONES = [
        'wrist', 'thumb_cmc', 'thumb_mcp', 'thumb_ip', 'thumb_tip',
        'index_finger_mcp', 'index_finger_pip', 'index_finger_dip', 'index_finger_tip',
        'middle_finger_mcp', 'middle_finger_pip', 'middle_finger_dip', 'middle_finger_tip',
        'ring_finger_mcp', 'ring_finger_pip', 'ring_finger_dip', 'ring_finger_tip',
        'pinky_mcp', 'pinky_pip', 'pinky_dip', 'pinky_tip']

    def __init__(self, args):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands()
        self.frame_number = 0
        self.args = args
        self.writer = csv_writer.CSVWriter(self.args)

    def run(self):
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
            results = self.hands.process(frame_rgb)

            if self.args.first != None and 'camera' in self.args:
                if self.frame_number >= self.args.first:
                    self.process(results, frame)
            else:
                self.process(results, frame)

            cv2.imshow('Motion Tracker', frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        capture.release()
        cv2.destroyAllWindows()
        self.writer.close()

    def process(self, results, frame):
        if not results.multi_hand_landmarks:
            return []

        for hand_id, hand in enumerate(results.multi_handedness):
            hand = MessageToDict(hand)['classification'][0]
            hand_landmarks_message = results.multi_hand_landmarks[hand_id]

            if self.args.draw == 'yes':
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks_message,
                    self.mp_hands.HAND_CONNECTIONS)

            hand_landmarks = MessageToDict(hand_landmarks_message)['landmark']
            record = self.organize(hand, hand_landmarks, frame)
            self.writer.write(record)

    def organize(self, hand, hand_landmarks, frame):
        height, width, _ = frame.shape

        record = {
            'frame_number': self.frame_number,
            'hand_index': hand['index'],
            'hand_score': hand['score'],
            'hand_handness': hand['label']
        }

        for bone_id, bone in enumerate(self.BONES):
            bone_landmarks = hand_landmarks[bone_id]
            bone_name = self.BONES[bone_id]

            for axe in bone_landmarks:
                if axe == 'x':
                    record[bone_name + '_' + axe] = bone_landmarks[axe] * width
                else:
                    record[bone_name + '_' + axe] = bone_landmarks[axe] * height

        return record
