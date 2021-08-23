
# HOW TO:
# This script is supposed to be run from the command line with two
# arguments:
# The name of the series for which you wanna run this process.
# The folder to save the images and annotations files to.
#
# Example:
# python web/make_facenet_retraining_data.py "Seinfeld" "sample_data/seinfeld_facenet_1"

#####################################################
#           Imports                                 #
#####################################################

# Base Imports
import os
import sys
import json
import logging
from random import shuffle


# Local Imports
from hoodat_utils import s3
from hoodat_utils import models as m

# Library Imports
import pickle
from PIL import Image
from matplotlib import pyplot
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from keras.models import load_model
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import Normalizer
from sklearn.preprocessing import LabelEncoder
from numpy import asarray, load, uint8, savez_compressed, expand_dims

#####################################################
#           Functions                               #
#####################################################


class retrain_facenet():

    def __init__(self, env, series_name, save_dir, sqlalchemy_database_uri):
        self.env = env
        self.save_dir = save_dir
        self.series_name = series_name
        self.sqlalchemy_database_uri = sqlalchemy_database_uri
        self.engine = create_engine(self.sqlalchemy_database_uri)

    def execute(self, train_split=1, predict=False, upload_to_s3=False, s3_save_dir=None):
        self.make_local_dir()
        logging.info("Downloading model")
        self.download_model()
        logging.info("Model downloaded")
        self.session = Session(self.engine)
        series_character_labels = self.query_series_character_labels()
        # logging.info(f"series_character_labels head: {series_character_labels[:3]}")
        if train_split != 1:
            shuffle(series_character_labels)
            split_index = round(train_split * len(series_character_labels))
            series_characters_train = series_character_labels[:split_index]
            series_characters_test = series_character_labels[split_index:]
        else:
            series_characters_train = series_character_labels
            series_characters_test = []
        # series_character_labels = self.query_series_character_labels()
        # logging.info(f"series_characters_train head: {series_characters_train[:3]}")
        character_list = self.unique_characters(series_character_labels)
        logging.info("character_list: ")
        logging.info(character_list)
        for character in character_list:
            character_folder_train = f"{self.save_dir}/train/{character}"
            character_folder_test = f"{self.save_dir}/test/{character}"
            if not os.path.isdir(character_folder_train):
                # logging.info(f"Creating {character_folder_train}")
                os.makedirs(character_folder_train)
            if not os.path.isdir(character_folder_test):
                # logging.info(f"Creating {character_folder_test}")
                os.makedirs(character_folder_test)
        files_train = self.make_file_names(series_characters_train)
        files_test = self.make_file_names(series_characters_test)
        file_list_train = self.make_file_list(
            series_characters_train, files_train, "train")
        file_list_test = self.make_file_list(
            series_characters_test, files_test, "test")
        self.download_images(file_list_train)
        self.download_images(file_list_test)
        logging.info("Making compressed datasets")
        self.make_compressed_datasets()
        logging.info("Made compressed datasets")
        logging.info("Loading model")
        self.load_facenet()
        logging.info("Loaded model")
        logging.info("Making embeddings")
        self.make_embeddings_dataset()
        logging.info("Made embeddings")
        logging.info("Fitting model")
        self.fit_model()
        logging.info("Model Fitted")
        if predict is True:
            logging.info("Scoring train and test sets")
            self.predict_model()
        if upload_to_s3 is True:
            logging.info("Saving model")
            self.save_retrained_model()
            logging.info("Saved model")
            self.upload_model_to_s3(s3_save_dir)
            logging.info("Uploaded model to S3")
            logging.info("Saving label_encoder")
            self.save_label_encoder()
            logging.info("Saved label_encoder")
            self.upload_label_encoder_to_s3(s3_save_dir)
            logging.info("Uploaded label_encoder to S3")

    def make_local_dir(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def query_series_character_labels(self):
        query = self.session.query(
            m.Series.series_id, m.Video.video_id, m.Video.video_type, m.Video.save_name, m.Frame.frame_id,
            m.Frame.frame_number, m.Object.object_id,
            m.Character_Label.character_label_id, m.Object.object_x,
            m.Object.object_y, m.Object.object_w, m.Object.object_h,
            m.Object.object_cascade, m.Character.character_name
        ).filter(
            m.Series.series_name == self.series_name
        ).join(m.Episode).join(m.Video).join(m.Frame).join(m.Object).join(m.Character_Label).join(m.Character)
        series_character_labels = query.all()
        logging.info("Number of labels: {0}".format(
            str(len(series_character_labels))))
        return series_character_labels

    def unique_characters(self, series_character_labels):
        character_list = list(
            set([x.character_name.replace(" ", "_") for x in series_character_labels]))
        return character_list

    def make_file_names(self, series_character_labels):
        result = [
            f"f{x[5]}c{x[12]}x{x[8]}y{x[9]}w{x[10]}h{x[11]}.jpg" for x in series_character_labels]
        return result

    def make_file_download_from_list(self, series_character_labels, file_names):
        files = []
        for i, x in enumerate(series_character_labels):
            files.append(
                f"static/frames/{x[2].lower().replace(' ', '_')}/{x[3]}/haar/{file_names[i]}")
        # logging.info(f"Head of files: {files[:3]}")
        return files

    def make_file_download_to_list(self, series_character_labels, file_names, train_or_test="train"):
        files = []
        for i, x in enumerate(series_character_labels):
            files.append(
                f"{self.save_dir}/{train_or_test}/{x[-1].replace(' ', '_')}/{file_names[i]}")
        # files = [f"{self.save_dir}/{x[-1].replace(' ', '_')}/" for x in series_character_labels]
        # logging.info(f"Head of characters: {files[:3]}")
        return files

    def make_file_list(self, series_character_labels, file_names, train_or_test="train"):
        from_list = self.make_file_download_from_list(
            series_character_labels, file_names)
        to_list = self.make_file_download_to_list(
            series_character_labels, file_names, train_or_test)
        file_list = list(zip(from_list, to_list))
        return file_list

    def download_images(self, file_list):
        logging.info("Creating s3 connection")
        s3_conn = s3.s3_data(
            access_key=self.env.AWS_ACCESS_KEY_ID,
            secret_key=self.env.AWS_SECRET_ACCESS_KEY)
        logging.info("Starting file downloads")
        for file_from_and_to in file_list:
            s3_conn.download_file(
                bucket=self.env.BUCKET,
                s3_loc=file_from_and_to[0],
                save_loc=file_from_and_to[1])
        logging.info("Files downloaded")

    def download_model(self):
        logging.info("Creating s3 connection")
        s3_conn = s3.s3_data(
            access_key=self.env.AWS_ACCESS_KEY_ID,
            secret_key=self.env.AWS_SECRET_ACCESS_KEY)
        s3_conn.download_file(
            bucket=self.env.BUCKET,
            s3_loc="static/data/dags/retrain_facenet/keras-facenet/model/facenet_keras.h5",
            save_loc=f"{self.save_dir}/facenet_keras.h5")

    def load_facenet(self):
        self.model = load_model(f"{self.save_dir}/facenet_keras.h5")

    def read_face(self, filename, required_size=(160, 160)):
        pixels = pyplot.imread(filename)
        image = Image.fromarray((pixels * 255).astype(uint8))
        image = image.resize(required_size)
        face_array = asarray(image)
        return face_array

    # load images and extract faces for all images in a directory
    def load_faces(self, directory):
        faces = list()
        # enumerate files
        for filename in os.listdir(directory):
            # path
            path = directory + filename
            # get face
            face = self.read_face(path)
            # store
            faces.append(face)
        return faces

    # load a dataset that contains one subdir for each class that in turn contains images
    def load_dataset(self, directory):
        X, y = list(), list()
        # enumerate folders, on per class
        for subdir in os.listdir(directory):
            # path
            path = directory + subdir + '/'
            # skip any files that might be in the dir
            if not os.path.isdir(path):
                continue
            # load all faces in the subdirectory
            faces = self.load_faces(path)
            # create labels
            labels = [subdir for _ in range(len(faces))]
            # summarize progress
            logging.info('>loaded %d examples for class: %s' % (len(faces), subdir))
            # store
            X.extend(faces)
            y.extend(labels)
        return asarray(X), asarray(y)

    def make_compressed_datasets(self):
        # load train dataset
        self.trainX, self.trainy = self.load_dataset(f'{self.save_dir}/train/')
        logging.info(self.trainX.shape, self.trainy.shape)
        # load test dataset
        self.testX, self.testy = self.load_dataset(f'{self.save_dir}/test/')
        # save arrays to one file in compressed format
        savez_compressed(f'{self.save_dir}/dataset.npz', self.trainX, self.trainy, self.testX, self.testy)

    def get_embedding(self, model, face_pixels):
        # scale pixel values
        face_pixels = face_pixels.astype('float32')
        # standardize pixel values across channels (global)
        mean, std = face_pixels.mean(), face_pixels.std()
        face_pixels = (face_pixels - mean) / std
        # transform face into one sample
        samples = expand_dims(face_pixels, axis=0)
        # make prediction to get embedding
        yhat = model.predict(samples)
        return yhat[0]

    def make_embeddings_dataset(self):
        # Convert each face in the train set to an embedding
        self.newTrainX = list()
        for face_pixels in self.trainX:
            embedding = self.get_embedding(self.model, face_pixels)
            self.newTrainX.append(embedding)
        self.newTrainX = asarray(self.newTrainX)
        logging.info(self.newTrainX.shape)
        # Convert each face in the test set to an embedding
        self.newTestX = list()
        for face_pixels in self.testX:
            embedding = self.get_embedding(self.model, face_pixels)
            self.newTestX.append(embedding)
        self.newTestX = asarray(self.newTestX)
        logging.info(self.newTestX.shape)
        # Save arrays to one file in compressed format
        savez_compressed(f'{self.save_dir}/embeddings.npz',
                         self.newTrainX, self.trainy, self.newTestX, self.testy)

    def fit_model(self):
        # Normalize input vectors
        in_encoder = Normalizer(norm='l2')
        self.transformedTrainX = in_encoder.transform(self.newTrainX)
        self.transformedTestX = in_encoder.transform(self.newTestX)
        # Label encode targets
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(self.trainy)
        self.transformedTrainy = self.label_encoder.transform(self.trainy)
        self.transformedTesty = self.label_encoder.transform(self.testy)
        # Fit model
        self.svc_model = SVC(kernel='linear', probability=True)
        self.svc_model.fit(self.transformedTrainX, self.transformedTrainy)

    def predict_model(self):
        # Predict
        yhat_train = self.svc_model.predict(self.transformedTrainX)
        yhat_test = self.svc_model.predict(self.transformedTestX)
        # Score
        score_train = accuracy_score(self.transformedTrainy, yhat_train)
        score_test = accuracy_score(self.transformedTesty, yhat_test)
        # Summarize
        logging.info('Accuracy: train=%.3f, test=%.3f' % (score_train*100, score_test*100))

    def save_retrained_model(self):
        model_file = f"{self.save_dir}/facenet_svc_model.sav"
        pickle.dump(self.svc_model, open(model_file, "wb"))

    def save_label_encoder(self):
        file_path = f"{self.save_dir}/label_encoding.json"
        self.label_mapping = dict(
            zip(
                [str(x) for x in self.label_encoder.transform(
                    self.label_encoder.classes_)],
                self.label_encoder.classes_
            )
        )
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.label_mapping, f, ensure_ascii=False, indent=4)

    def upload_model_to_s3(self, s3_save_dir):
        logging.info("Creating s3 connection")
        s3_conn = s3.s3_data(
            access_key=self.env.AWS_ACCESS_KEY_ID,
            secret_key=self.env.AWS_SECRET_ACCESS_KEY)
        s3_conn.upload_file(
            bucket=self.env.BUCKET,
            s3_loc=f"{s3_save_dir}/facenet_svc_model.sav",
            local_loc=f"{self.save_dir}/facenet_svc_model.sav")
        logging.info("Model uploaded to s3")

    def upload_label_encoder_to_s3(self, s3_save_dir):
        logging.info("Creating s3 connection")
        s3_conn = s3.s3_data(
            access_key=self.env.AWS_ACCESS_KEY_ID,
            secret_key=self.env.AWS_SECRET_ACCESS_KEY)
        s3_conn.upload_file(
            bucket=self.env.BUCKET,
            s3_loc=f"{s3_save_dir}/label_encoding.json",
            local_loc=f"{self.save_dir}/label_encoding.json")
        logging.info("Label encoder uploaded to s3")



# if __name__ == "__main__":
#     SERIES_NAME = sys.argv[1]
#     SAVE_DIR = sys.argv[2]
#     SQLALCHEMY_DATABASE_URI = "mysql://{0}:{1}@{2}/{3}".format(
#         env.DB_USER_RDS, env.DB_PASS_RDS, env.DB_SERVICE_RDS, env.DB_NAME_RDS
#     )
#     fnd = facenet_data(
#         series_name=SERIES_NAME,
#         save_dir=SAVE_DIR,
#         sqlalchemy_database_uri=SQLALCHEMY_DATABASE_URI)
#     fnd.execute()
#     logging.info("Script complete")
