#####################################################
#           Imports                                 #
#####################################################

# # Base Imports
import os
import json
import logging
from time import time
# import sys
# from random import shuffle


# # Local Imports
from hoodat_utils import s3
from hoodat_utils import models as m
from hoodat_utils.hoodat_sqlalchemy import HoodatSqlalchemy

# # Library Imports
import pickle
import pandas as pd
from PIL import Image
from matplotlib import pyplot
from keras.models import load_model
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from numpy import asarray, uint8, savez_compressed, expand_dims
# from sklearn.svm import SVC
# from sklearn.metrics import accuracy_score
from sklearn.preprocessing import Normalizer
# from sklearn.preprocessing import LabelEncoder
# from numpy import asarray, load, uint8, savez_compressed, expand_dims

#####################################################
#           Functions                               #
#####################################################


class facenet_embeddings():

    def __init__(self,
                env,
                series_name,
                run_name,
                video,
                folder,
                save_dir,
                sqlalchemy_database_uri,
                use_complete_tables=False):
        self.env = env
        self.series_name = series_name
        self.run_name = run_name
        self.video = video
        self.folder = folder
        self.sqlalchemy_database_uri = sqlalchemy_database_uri
        self.save_dir = save_dir
        self.engine = create_engine(self.sqlalchemy_database_uri)
        self.hoodat_sql = HoodatSqlalchemy(self.sqlalchemy_database_uri)
        self.use_complete_tables = use_complete_tables
        if self.use_complete_tables:
            self.s3_haar_key = f"static/frames/{self.folder}/{self.video}/haar_complete/"
        else:
            self.s3_haar_key = f"static/frames/{self.folder}/{self.video}/haar/"

    def make_embeddings(self):
        # 0. Make local save directory
        self.make_local_dir()
        # 1. Create faces query for sql
        # video_faces = self.query_video_faces()
        # 2. Download faces from S3
        self.download_images()
        self.X = asarray(self.load_faces(f"{self.save_dir}/images/"))
        # 3. Download model from S3
        self.download_file(
            s3_loc="static/data/dags/retrain_facenet/keras-facenet/model/facenet_keras.h5",
            save_loc=f"{self.save_dir}/facenet_keras.h5")
        self.load_facenet()
        # 4. Make Embeddings
        self.make_embeddings_dataset()
        # 5. Save to S3
        self.upload_embeddings_to_s3(
            s3_save_dir=f"static/data/dags/haar_facenet_embeddings_complete/video={self.video}/model={self.run_name}")

    def make_local_dir(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    # def query_video_faces(self):
    #     query = self.session.query(
    #         # m.Series.series_id,
    #         m.Video.video_id, m.Video.video_type, m.Video.save_name,
    #         m.Frame.frame_id, m.Frame.frame_number, m.Object.object_id, m.Object.object_x,
    #         m.Object.object_y, m.Object.object_w, m.Object.object_h,
    #         m.Object.object_cascade
    #     ).filter(
    #         m.Video.save_name == self.video
    #     ).join(m.Frame).join(m.Object)
    #     result = query.all()
    #     logging.info("Number of records: {0}".format(
    #         str(len(result))))
    #     return result

    def download_images(self):
        logging.info("Creating s3 connection")
        s3_conn = s3.s3_data(
            access_key=self.env.AWS_ACCESS_KEY_ID,
            secret_key=self.env.AWS_SECRET_ACCESS_KEY)
        logging.info("Starting file downloads")
        s3_conn.download_dir(
            region=self.env.AWS_DEFAULT_REGION,
            bucket=self.env.BUCKET,
            s3_loc=self.s3_haar_key,
            save_loc=f"{self.save_dir}/images/")
        logging.info("Files downloaded")

    def download_file(self, s3_loc, save_loc):
        logging.info("Creating s3 connection")
        s3_conn = s3.s3_data(
            access_key=self.env.AWS_ACCESS_KEY_ID,
            secret_key=self.env.AWS_SECRET_ACCESS_KEY)
        s3_conn.download_file(
            bucket=self.env.BUCKET,
            s3_loc=s3_loc,
            save_loc=save_loc)

    def load_facenet(self):
        logging.info("Loading facenet model")
        self.model = load_model(f"{self.save_dir}/facenet_keras.h5")
        logging.info("Facenet model loaded")

    def read_face(self, filename, required_size=(160, 160)):
        pixels = pyplot.imread(filename)
        image = Image.fromarray((pixels * 255).astype(uint8))
        image = image.resize(required_size)
        face_array = asarray(image)
        return face_array

    # load images and extract faces for all images in a directory
    def load_faces(self, directory):
        faces = list()
        self.faces_files = os.listdir(directory)
        # enumerate files
        for filename in self.faces_files:
            # path
            path = directory + filename
            # get face
            face = self.read_face(path)
            # store
            faces.append(face)
        return faces

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
        logging.info("Making embeddings dataset")
        # Convert each face in the data set to an embedding
        self.newX = list()
        for face_pixels in self.X:
            embedding = self.get_embedding(self.model, face_pixels)
            self.newX.append(embedding)
        self.newX = asarray(self.newX)
        logging.info(self.X.shape)
        self.X = self.newX
        logging.info("Saving embeddings")
        # Save arrays to one file in compressed format
        savez_compressed(f'{self.save_dir}/embeddings.npz', self.X)
        logging.info("Embeddings saved")

    def upload_embeddings_to_s3(self, s3_save_dir):
        logging.info("Creating s3 connection")
        s3_conn = s3.s3_data(
            access_key=self.env.AWS_ACCESS_KEY_ID,
            secret_key=self.env.AWS_SECRET_ACCESS_KEY)
        logging.info(f"Uploading embeddings file to {s3_save_dir}")
        s3_conn.upload_file(
            bucket=self.env.BUCKET,
            s3_loc=f"{s3_save_dir}/embeddings.npz",
            local_loc=f"{self.save_dir}/embeddings.npz")
        logging.info("Embeddings uploaded to s3")

    def predict_embeddings(self):
        # if video is not None:
        #     self.video = video
        # if model is not None:
        #     self.model = model
        # if self.X is None:
        #     self.X = self.download_file(
        #         s3_loc=f"static/data/dags/haar_facenet_embeddings/video={self.video}/model={self.run_name}/embeddings.npz",
        #         save_loc=f"{self.save_dir}/embeddings.npz")
        # svc_s3_loc = f"static/data/dags/retrain_facenet/retrained_models/{self.run_name}/facenet_svc_model.sav"
        # svc_save_loc = f"{self.save_dir}/facenet_svc_model.sav"
        # logging.info(f"Downloading {svc_s3_loc}")
        # self.download_file(
        #     s3_loc=svc_s3_loc,
        #     save_loc=svc_save_loc)
        # self.svc_model = pickle.load(open(svc_save_loc, "rb"))
        self.load_svc_model()
        # def predict_model(self):
        # Label encode targets
        # out_encoder = LabelEncoder()
        # out_encoder.fit(self.trainy)
        # self.transformedTrainy = out_encoder.transform(self.trainy)
        # Normalize input vectors
        in_encoder = Normalizer(norm='l2')
        self.transformedX = in_encoder.transform(self.X)
        # Predict
        yhat_X = self.svc_model.predict(self.transformedX)
        # Read encoder
        self.label_encoder = self.load_label_encoder()
        # self.faces_files
        return yhat_X

    def load_svc_model(self):
        svc_s3_loc = f"static/data/dags/retrain_facenet/retrained_models/{self.run_name}/facenet_svc_model.sav"
        svc_save_loc = f"{self.save_dir}/facenet_svc_model.sav"
        logging.info(f"Downloading {svc_s3_loc}")
        self.download_file(
            s3_loc=svc_s3_loc,
            save_loc=svc_save_loc)
        self.svc_model = pickle.load(open(svc_save_loc, "rb"))

    def load_label_encoder(self):
        label_encoder_s3_loc = f"static/data/dags/retrain_facenet/retrained_models/{self.run_name}/label_encoding.json"
        label_encoder_save_loc = f"{self.save_dir}/label_encoding.json"
        logging.info(f"Downloading {label_encoder_s3_loc}")
        self.download_file(
            s3_loc=label_encoder_s3_loc,
            save_loc=label_encoder_save_loc)
        with open(f"{self.save_dir}/label_encoding.json") as f:
            self.label_encoding = json.load(f)

    def make_predictions_df(self, predictions):
        self.predictions_df = pd.DataFrame(list(
            zip(
                self.faces_files,
                [self.label_encoding[str(x)] for x in predictions]
            )
        ))
        self.predictions_df.columns = ["face_file", "prediction"]
        self.predictions_df["video_name"] = self.video
        self.predictions_df["facenet_haar_model_name"] = self.run_name

    def query_ids(self):
        self.ids_df = pd.read_sql(f"""
            SELECT v.video_id, o.object_id, f.frame_number, o.object_cascade, o.object_x, o.object_y, o.object_w, o.object_h
            FROM videos v
            JOIN objects o
            ON v.video_id=o.video_id
            JOIN frames f
            ON o.frame_id=f.frame_id
            JOIN faces
            ON o.object_id=faces.object_id
            WHERE v.save_name = '{self.video}'
        """, con=self.engine)
        self.ids_df["face_file"] = self.ids_df.apply(
            lambda x: self.make_file_names(x), axis=1)

    def query_characters(self):
        self.characters_df = pd.read_sql(f"""
            SELECT v.series_id, c.character_id, REPLACE(c.character_name,' ', '_') AS character_name
            FROM videos v
            JOIN characters c
            ON v.series_id=c.series_id
            WHERE v.save_name = '{self.video}'
        """, con=self.engine)

    def make_file_names(self, d):
        result = f"f{d['frame_number']}c{d['object_cascade']}x{d['object_x']}y{d['object_y']}w{d['object_w']}h{d['object_h']}.jpg"
        return result

    def make_haar_facenet_predictions(self):
        self.haar_facenet_predictions = self.predictions_df.merge(
            self.ids_df
        ).merge(
            self.characters_df,
            left_on="prediction",
            right_on="character_name"
        )
        self.haar_facenet_predictions = self.haar_facenet_predictions[[
            "object_id", "video_id", "character_id", "facenet_haar_model_name"]]

    def as_int(self, value):
        if value is None:
            return None
        else:
            return int(value)

    def create_record(self, row):
        if self.use_complete_tables:
            result = m.Facenet_Haar_Prediction_Complete(
                object_id=self.as_int(row["object_id"]),
                video_id=self.as_int(row["video_id"]),
                character_id=self.as_int(row["character_id"]),
                facenet_haar_model_name=row["facenet_haar_model_name"],
                timestamp_added=time()
            )
        else:
            result = m.Facenet_Haar_Prediction(
                object_id=self.as_int(row["object_id"]),
                video_id=self.as_int(row["video_id"]),
                character_id=self.as_int(row["character_id"]),
                facenet_haar_model_name=row["facenet_haar_model_name"],
                timestamp_added=time()
            )
        return result

    def predictions_to_sql(self, predictions):
        self.make_predictions_df(predictions)
        self.query_ids()
        self.query_characters()
        self.make_haar_facenet_predictions()
        # commit to pandas
        if self.use_complete_tables:
            self.hoodat_sql.commit_pandas_df(
                df=self.haar_facenet_predictions,
                table="haar_facenet_predictions_complete",
                record_func=self.create_record
            )
        else:
            self.hoodat_sql.commit_pandas_df(
                df=self.haar_facenet_predictions,
                table="haar_facenet_predictions",
                record_func=self.create_record
            )


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
