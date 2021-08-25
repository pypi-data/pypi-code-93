import mediapipe as mp
from google.protobuf.json_format import MessageToDict
from trucotrack.processors import csv_gzip_writer as csv_writer

class MediapipeFace:
    def __init__(self, args):
        self.args = args

        self.mp_faces = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.faces = self.mp_faces.FaceMesh(
            static_image_mode=args.mp_faces_static == 'no',
            max_num_faces=args.mp_faces_max)

        if self.args.mp_faces_csv != None:
            self.writer = csv_writer.CsvGzipWriter(self.args.mp_faces_csv, self.args)

    def process(self, dispatched_frame):
        frame = dispatched_frame['frame']
        frame_rgb = dispatched_frame['frame_rgb']
        frame_number = dispatched_frame['frame_number']

        results = self.faces.process(frame_rgb)
        if not results.multi_face_landmarks:
            return []

        records = []
        for face_index, face_landmark_message in enumerate(results.multi_face_landmarks):
            if self.args.mp_faces_draw == 'yes':
                  self.mp_drawing.draw_landmarks(
                      image=frame,
                      landmark_list=face_landmark_message)
                  self.mp_drawing.draw_landmarks(
                      image=frame,
                      landmark_list=face_landmark_message)

            face_landmarks = MessageToDict(face_landmark_message)['landmark']
            record = self.organize(face_index, face_landmarks, frame, frame_number)
            records.append(record)

        if hasattr(self, 'writer'):
            for record in records:
                self.writer.write(record)

        return records

    def organize(self, face_index, face_landmarks, frame, frame_number):
        height, width, _ = frame.shape

        record = {
            'face_index': str(face_index),
            'frame_number': str(frame_number),
        }

        bone_id = 0
        for face_landmark in face_landmarks:
            bone_id += 1

            for axe in face_landmark:
                if axe == 'x':
                    scale = width
                else:
                    scale = height

                coordinate_name = 'face_' + str(bone_id) + '_' + axe
                record[coordinate_name] = '{:-f}'.format(face_landmark[axe] * scale)

        return record

    def close_writer(self):
        if hasattr(self, 'writer'):
            self.writer.close()
