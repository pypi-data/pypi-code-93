#####################################################
#           Imports                                 #
#####################################################

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import backref

#####################################################
#           Script                                  #
#####################################################

db = SQLAlchemy()


class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    full_name = db.Column(db.String(64))
    display_name = db.Column(db.String(48))
    signup_timestamp = db.Column(db.String(10), nullable=False)
    videos = db.relationship("Video", backref="User", lazy="dynamic")

    def __repr__(self):
        return "<User %r>" % (self.display_name)


class Video(db.Model):

    __tablename__ = "videos"

    video_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    episode_id = db.Column(db.Integer, db.ForeignKey("episodes.episode_id"))
    video_name = db.Column(db.String(156), nullable=False, unique=True)
    save_name = db.Column(db.String(156), nullable=False, unique=True)
    video_type = db.Column(db.String(48), nullable=False)
    youtube_link = db.Column(db.String(128), unique=True)
    timestamp_add_video = db.Column(db.String(10), nullable=False)
    download_process_complete = db.Column(db.Boolean)
    series_id = db.Column(db.Integer, db.ForeignKey("series.series_id"))
    actor_group_id = db.Column(
        db.Integer, db.ForeignKey("actor_groups.actor_group_id"))
    frames = db.relationship("Frame", backref="Video", lazy="dynamic")
    frames_complete = db.relationship(
        "Frame_Complete", backref="Video", lazy="dynamic")
    objects = db.relationship("Object", backref="Video", lazy="dynamic")
    objects_complete = db.relationship(
        "Object_Complete", backref="Video", lazy="dynamic")
    triggers = db.relationship("Trigger", backref="Video", lazy="dynamic")
    faces = db.relationship("Face", backref="Video", lazy="dynamic")
    facenet_haar_predictions = db.relationship(
        "Facenet_Haar_Prediction", backref=backref("Video", uselist=False))

    __table_args__ = (db.UniqueConstraint("video_id", "episode_id", name="episode_video"),
                      )


class Frame(db.Model):

    __tablename__ = "frames"

    frame_id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("videos.video_id"))
    frame_number = db.Column(db.Integer, nullable=False)
    objects = db.relationship("Object", backref="Frame", lazy="dynamic")
    face = db.relationship(
        "Face", backref=backref("Frame", uselist=False), lazy="dynamic")

    __table_args__ = (db.UniqueConstraint(
        "video_id", "frame_number", name="video_frame"),
    )


class Frame_Complete(db.Model):

    __tablename__ = "frames_complete"

    frame_id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("videos.video_id"))
    frame_number = db.Column(db.Integer, nullable=False)
    objects_complete = db.relationship(
        "Object_Complete", backref="Frame_Complete", lazy="dynamic")
    faces_complete = db.relationship(
        "Face_Complete", backref=backref("Frame_Complete", uselist=False), lazy="dynamic")

    __table_args__ = (db.UniqueConstraint(
        "video_id", "frame_number", name="video_frame"),
    )


class Object(db.Model):

    __tablename__ = "objects"

    object_id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("videos.video_id"))
    frame_id = db.Column(db.Integer, db.ForeignKey("frames.frame_id"))
    episode_id = db.Column(db.Integer, db.ForeignKey("episodes.episode_id"))
    object_number = db.Column(db.Integer, nullable=False)
    object_cascade = db.Column(db.Integer, nullable=False)
    object_x = db.Column(db.Integer, nullable=False)
    object_y = db.Column(db.Integer, nullable=False)
    object_w = db.Column(db.Integer, nullable=False)
    object_h = db.Column(db.Integer, nullable=False)
    character_label = db.relationship(
        "Character_Label", backref=backref("Object", uselist=False))
    object_pca_features = db.relationship(
        "Object_PCA_Features", backref=backref("Object", uselist=False))
    object_umap_features = db.relationship(
        "Object_UMAP_Features", backref=backref("Object", uselist=False))
    face = db.relationship(
        "Face", backref=backref("Object", uselist=False))
    facenet_haar_predictions = db.relationship(
        "Facenet_Haar_Prediction", backref=backref("Object", uselist=False))

    __table_args__ = (db.UniqueConstraint(
        "video_id", "frame_id", "object_number", name="object"),
    )


class Object_Complete(db.Model):

    __tablename__ = "objects_complete"

    object_id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("videos.video_id"))
    frame_id = db.Column(db.Integer, db.ForeignKey("frames_complete.frame_id"))
    episode_id = db.Column(db.Integer, db.ForeignKey("episodes.episode_id"))
    object_number = db.Column(db.Integer, nullable=False)
    object_cascade = db.Column(db.Integer, nullable=False)
    object_x = db.Column(db.Integer, nullable=False)
    object_y = db.Column(db.Integer, nullable=False)
    object_w = db.Column(db.Integer, nullable=False)
    object_h = db.Column(db.Integer, nullable=False)
    faces_complete = db.relationship(
        "Face_Complete", backref=backref("Object_Complete", uselist=False), lazy="dynamic")
    facenet_haar_predictions = db.relationship(
        "Facenet_Haar_Prediction", backref=backref("Object_Complete", uselist=False))
    # character_label = db.relationship(
    #     "Character_Label", backref=backref("Object", uselist=False))
    # object_pca_features = db.relationship(
    #     "Object_PCA_Features", backref=backref("Object", uselist=False))
    # object_umap_features = db.relationship(
    #     "Object_UMAP_Features", backref=backref("Object", uselist=False))
    # face = db.relationship(
    #     "Face", backref=backref("Object", uselist=False))
    # facenet_haar_predictions = db.relationship(
    #     "Facenet_Haar_Prediction", backref=backref("Object", uselist=False))

    __table_args__ = (db.UniqueConstraint(
        "video_id", "frame_id", "object_number", name="object"),
    )


class Face(db.Model):

    __tablename__ = "faces"

    face_id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.Integer, db.ForeignKey("objects.object_id"))
    video_id = db.Column(db.Integer, db.ForeignKey("videos.video_id"))
    frame_id = db.Column(db.Integer, db.ForeignKey("frames.frame_id"))
    episode_id = db.Column(db.Integer, db.ForeignKey("episodes.episode_id"))
    object_number = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.UniqueConstraint(
        "video_id", "frame_id", "object_number", name="object"),
    )


class Face_Complete(db.Model):

    __tablename__ = "faces_complete"

    face_id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.Integer, db.ForeignKey(
        "objects_complete.object_id"))
    video_id = db.Column(db.Integer, db.ForeignKey("videos.video_id"))
    frame_id = db.Column(db.Integer, db.ForeignKey("frames_complete.frame_id"))
    episode_id = db.Column(db.Integer, db.ForeignKey("episodes.episode_id"))
    object_number = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.UniqueConstraint(
        "video_id", "frame_id", "object_number", name="object"),
    )


class Dlib_Face_Unaligned(db.Model):

    __tablename__ = "dlib_faces_unaligned"

    dlib_faces_unaligned_id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("videos.video_id"))
    frame_id = db.Column(db.Integer, db.ForeignKey("frames.frame_id"))
    episode_id = db.Column(db.Integer, db.ForeignKey("episodes.episode_id"))
    object_number = db.Column(db.Integer, nullable=False)
    object_x = db.Column(db.Integer, nullable=False)
    object_y = db.Column(db.Integer, nullable=False)
    object_w = db.Column(db.Integer, nullable=False)
    object_h = db.Column(db.Integer, nullable=False)
    # character_label = db.relationship("Character_Label", backref=backref("Dlib_Face_Unaligned", uselist=False))

    __table_args__ = (db.UniqueConstraint(
        "video_id", "frame_id", "object_number", name="dlib_face_unaligned"),
    )


class Dlib_Face_Aligned(db.Model):

    __tablename__ = "dlib_faces_aligned"

    dlib_faces_aligned_id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("videos.video_id"))
    frame_id = db.Column(db.Integer, db.ForeignKey("frames.frame_id"))
    episode_id = db.Column(db.Integer, db.ForeignKey("episodes.episode_id"))
    object_number = db.Column(db.Integer, nullable=False)
    object_x = db.Column(db.Integer, nullable=False)
    object_y = db.Column(db.Integer, nullable=False)
    object_w = db.Column(db.Integer, nullable=False)
    object_h = db.Column(db.Integer, nullable=False)
    # character_label = db.relationship("Character_Label", backref=backref("Dlib_Face_Aligned", uselist=False))

    __table_args__ = (db.UniqueConstraint(
        "video_id", "frame_id", "object_number", name="dlib_faces_aligned"),
    )


class Character_Label(db.Model):

    __tablename__ = "character_labels"

    character_label_id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.Integer, db.ForeignKey("objects.object_id"))
    character_id = db.Column(
        db.Integer, db.ForeignKey("characters.character_id"))
    timestamp_labelled = db.Column(db.String(10), nullable=False)

    __table_args__ = (db.UniqueConstraint(
        "object_id", "character_id", name="object_label"),
    )


class Series(db.Model):

    __tablename__ = "series"

    series_id = db.Column(db.Integer, primary_key=True)
    series_name = db.Column(db.String(128), nullable=False)
    series_release_year = db.Column(db.Integer)
    series_end_year = db.Column(db.Integer)
    timestamp_add_series = db.Column(db.String(10), nullable=False)
    videos = db.relationship("Video", backref="Series", lazy="dynamic")
    characters = db.relationship("Character", backref="Series", lazy="dynamic")
    seasons = db.relationship("Season", backref="Series", lazy="dynamic")
    episodes = db.relationship("Episode", backref="Series", lazy="dynamic")


class Season(db.Model):

    __tablename__ = "seasons"

    season_id = db.Column(db.Integer, primary_key=True)
    season_number = db.Column(db.Integer, nullable=False)
    season_year_start = db.Column(db.Integer, nullable=False)
    series_id = db.Column(db.Integer, db.ForeignKey("series.series_id"))
    timestamp_add_season = db.Column(db.String(10), nullable=False)

    __table_args__ = (db.UniqueConstraint("series_id", "season_number", name="series_season"),
                      )


class Episode(db.Model):

    __tablename__ = "episodes"

    episode_id = db.Column(db.Integer, primary_key=True)
    episode_name = db.Column(db.String(128))
    episode_number = db.Column(db.Integer, nullable=False)
    episode_date = db.Column(db.String(10))
    timestamp_add_episode = db.Column(db.String(10), nullable=False)
    series_id = db.Column(db.Integer, db.ForeignKey("series.series_id"))
    season_id = db.Column(db.Integer, db.ForeignKey("seasons.season_id"))
    video = db.relationship("Video", backref="Episode", uselist=False)
    face = db.relationship(
        "Face", backref=backref("Episode", uselist=False), lazy="dynamic")

    __table_args__ = (db.UniqueConstraint("episode_number", "season_id", name="season_episode"),
                      )


class Actor(db.Model):

    __tablename__ = "actors"

    actor_id = db.Column(db.Integer, primary_key=True)
    actor_name = db.Column(db.String(128), nullable=False)
    timestamp_add_actor = db.Column(db.String(10), nullable=False)
    characters = db.relationship("Character", backref="Actor", lazy="dynamic")
    actor_group_lookups = db.relationship(
        "Actor_Group_Lookup", backref="Actor", lazy="dynamic")


class Actor_Group(db.Model):

    __tablename__ = "actor_groups"

    actor_group_id = db.Column(db.Integer, primary_key=True)
    actor_group_name = db.Column(db.String(64), nullable=False)
    timestamp_add_actor_group = db.Column(db.String(10), nullable=False)
    actor_group_lookups = db.relationship(
        "Actor_Group_Lookup", backref="Actor_Group", lazy="dynamic")
    videos = db.relationship("Video", backref="Actor_Group", lazy="dynamic")


class Actor_Group_Lookup(db.Model):

    __tablename__ = "actor_group_lookup"

    actor_group_lookup_id = db.Column(db.Integer, primary_key=True)
    actor_group_id = db.Column(db.Integer, db.ForeignKey(
        "actor_groups.actor_group_id"), nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey(
        "actors.actor_id"), nullable=False)
    timestamp_add_actor_group_lookup = db.Column(db.String(10), nullable=False)


class Character(db.Model):

    __tablename__ = "characters"

    character_id = db.Column(db.Integer, primary_key=True)
    series_id = db.Column(db.Integer, db.ForeignKey(
        "series.series_id"), nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey(
        "actors.actor_id"), nullable=False)
    character_name = db.Column(db.String(128), nullable=False)
    timestamp_add_character = db.Column(db.String(10), nullable=False)
    facenet_haar_predictions = db.relationship(
        "Facenet_Haar_Prediction", backref=backref("Character", uselist=False))

    __table_args__ = (db.UniqueConstraint("series_id", "character_name", name="series_character"),
                      )


class Process(db.Model):

    __tablename__ = "processes"

    process_id = db.Column(db.Integer, primary_key=True)
    process_name = db.Column(db.String(32), nullable=False)
    airflow_dag_id = db.Column(db.String(32), nullable=False)
    timestamp_add_process = db.Column(db.String(10), nullable=False)
    triggers = db.relationship("Trigger", backref="Process", lazy="dynamic")


class Trigger(db.Model):

    __tablename__ = "triggers"

    trigger_id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey(
        "videos.video_id"), nullable=False)
    process_id = db.Column(db.Integer, db.ForeignKey(
        "processes.process_id"), nullable=False)
    timestamp_add_trigger = db.Column(db.String(10), nullable=False)
    status_complete = db.Column(db.Boolean, nullable=False)

    __table_args__ = (db.UniqueConstraint(
        "video_id", "process_id", name="video_process"), )


class Session_Info(db.Model):

    __tablename__ = "session_info"

    session_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ip_timestamp = db.Column(db.String(50), nullable=False)
    ip = db.Column(db.String(16), nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
    route_rule = db.Column(db.String(100), nullable=False)


class Haar_Cascade(db.Model):

    __tablename__ = "haar_cascades"

    haar_cascade_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    haar_cascade_name = db.Column(db.String(32), primary_key=True)
    file = db.Column(db.String(48), primary_key=True)


class Object_PCA_Features(db.Model):

    __tablename__ = "object_pca_features"

    object_pca_features_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    object_id = db.Column(db.Integer, db.ForeignKey("objects.object_id"))
    feature_1 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_2 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_3 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_4 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_5 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_6 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_7 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_8 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_9 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_10 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_11 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_12 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_13 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_14 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_15 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_16 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_17 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_18 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_19 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_20 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_21 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_22 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_23 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_24 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_25 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_26 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_27 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_28 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_29 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_30 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_31 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_32 = db.Column(db.Numeric(7, 6), nullable=False)
    timestamp_added = db.Column(db.String(10), nullable=False)


class Object_UMAP_Features(db.Model):

    __tablename__ = "object_umap_features"

    object_umap_features_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    object_id = db.Column(db.Integer, db.ForeignKey("objects.object_id"))
    feature_1 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_2 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_3 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_4 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_5 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_6 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_7 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_8 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_9 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_10 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_11 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_12 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_13 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_14 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_15 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_16 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_17 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_18 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_19 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_20 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_21 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_22 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_23 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_24 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_25 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_26 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_27 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_28 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_29 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_30 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_31 = db.Column(db.Numeric(7, 6), nullable=False)
    feature_32 = db.Column(db.Numeric(7, 6), nullable=False)
    timestamp_added = db.Column(db.String(10), nullable=False)


class Facenet_Haar_Model(db.Model):

    __tablename__ = "facenet_haar_models"

    facenet_haar_model_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    model_name = db.Column(db.String(24), unique=True, nullable=False)
    series_id = db.Column(db.Integer, db.ForeignKey("series.series_id"))
    timestamp_added = db.Column(db.String(10), nullable=False)
    model_input_data = db.relationship(
        "Facenet_Haar_Model_Input_Data", backref="Facenet_Haar_Model", lazy="dynamic")
    model_predictions = db.relationship(
        "Facenet_Haar_Prediction", backref="Facenet_Haar_Model", lazy="dynamic")


class Facenet_Haar_Model_Input_Data(db.Model):

    __tablename__ = "facenet_haar_model_input_data"

    facenet_haar_model_input_data_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    object_id = db.Column(db.Integer, db.ForeignKey(
        "objects.object_id"), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey(
        "characters.character_id"), nullable=False)
    model_name = db.Column(db.String(24), db.ForeignKey(
        "facenet_haar_models.model_name"), nullable=False)
    timestamp_added = db.Column(db.String(10), nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            "model_name", "object_id", name="facenet_haar_model_input_model_object"),
    )


class Facenet_Haar_Prediction(db.Model):

    __tablename__ = "facenet_haar_predictions"

    facenet_haar_prediction_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    object_id = db.Column(db.Integer, db.ForeignKey(
        "objects.object_id"), nullable=False)
    object_complete_id = db.Column(db.Integer, db.ForeignKey(
        "objects_complete.object_id"), nullable=True)
    video_id = db.Column(db.Integer, db.ForeignKey(
        "videos.video_id"), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey(
        "characters.character_id"), nullable=False)
    facenet_haar_model_name = db.Column(db.String(24), db.ForeignKey(
        "facenet_haar_models.model_name"), nullable=False)
    timestamp_added = db.Column(db.String(10), nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            "object_id", "video_id", "facenet_haar_model_name", name="facenet_haar_prediction_and_model"),
        db.UniqueConstraint(
            "facenet_haar_model_name", "object_id", name="facenet_haar_prediction_model_object"),
    )


class Facenet_Haar_Prediction_Complete(db.Model):

    __tablename__ = "facenet_haar_predictions_complete"

    facenet_haar_prediction_complete_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    object_id = db.Column(db.Integer, db.ForeignKey(
        "objects_complete.object_id"), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey(
        "videos.video_id"), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey(
        "characters.character_id"), nullable=False)
    facenet_haar_model_name = db.Column(db.String(24), nullable=False)
    timestamp_added = db.Column(db.String(10), nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            "object_id", "video_id", name="facenet_haar_prediction_complete"),
        db.UniqueConstraint(
            "facenet_haar_model_name", "object_id", name="facenet_haar_prediction_complete_model"),
    )
