from typing import List, Union
from datetime import datetime
from pydantic import BaseModel
import yaml


class RawInput(BaseModel):
    start_time: float
    pickup_lat: float
    pickup_lng: float
    dropoff_lat: float
    dropoff_lng: float
    eda: float
    eta: float
    straight_dist: float


class FeatureVector(BaseModel):
    pickup_lat_trunc: float
    pickup_lng_trunc: float
    dropoff_lat_trunc: float
    dropoff_lng_trunc: float
    start_hour_class: int
    start_weekday_class: int
    eda_scaled: int
    eta_scaled: int
    straight_dist_scaled: int

    def to_list(self) -> List[Union[float, int]]:
        return [
            self.pickup_lat_trunc,
            self.pickup_lng_trunc,
            self.dropoff_lat_trunc,
            self.dropoff_lng_trunc,
            self.start_hour_class,
            self.start_weekday_class,
            self.eda_scaled,
            self.eta_scaled,
            self.straight_dist_scaled
        ]

    def field_names(self) -> List[str]:
        return [
            'pickup_lat_trunc',
            'pickup_lng_trunc',
            'dropoff_lat_trunc',
            'dropoff_lng_trunc',
            'start_hour_class',
            'start_weekday_class',
            'eda_scaled',
            'eta_scaled',
            'straight_dist_scaled'
        ]


class StartTimeEncoder:
    def __init__(self, hour_pieces=List[List[int]], weekday_pieces=List[List[int]]):
        self.hour_pieces = hour_pieces
        self.weekday_pieces = weekday_pieces

    def hour_class(self, ts: int):
        h = datetime.utcfromtimestamp(ts).hour
        # using piece index as label
        for i, p in enumerate(self.hour_pieces):
            for h2 in p:
                if h2 == h:
                    return i
        # treat all other hours not in self.hour_pieces as a label
        return len(self.hour_pieces)

    def weekday_class(self, ts: int):
        d = datetime.utcfromtimestamp(ts).isoweekday()
        # using piece index as label
        for i, p in enumerate(self.weekday_pieces):
            for d2 in p:
                if d2 == d:
                    return i
        # treat all other weekdays not in self.weekday_pieces as a label
        return len(self.hour_pieces)


class LatLngEncoder():
    def __init__(self, ndigits):
        self.ndigits = ndigits

    def truncate(self, f: float):
        return round(f, self.ndigits)


class ScaleEncoder():
    def __init__(self, unit: int):
        self.unit = unit

    def scale(self, f: float):
        return round(f / self.unit)


class FeatureSchema:
    def __init__(self, schema):
        self._check_version(schema)
        if "features" not in schema:
            raise Exception("schema.features missing")
        features = schema["features"]
        self.start_time_encoder = self._create_start_time_encoder(features)
        self.latlng_encoder = self._create_latlng_encoder(features)
        self.eta_encoder = self._create_eta_encoder(features)
        self.eda_encoder = self._create_eda_encoder(features)
        self.straight_dist_encoder = self._create_straight_dist_encoder(
            features)

    def gen_trip_vector(self, raw: RawInput) -> FeatureVector:
        return FeatureVector(
            pickup_lat_trunc=self.latlng_encoder.truncate(raw.pickup_lat),
            pickup_lng_trunc=self.latlng_encoder.truncate(raw.pickup_lng),
            dropoff_lat_trunc=self.latlng_encoder.truncate(raw.dropoff_lat),
            dropoff_lng_trunc=self.latlng_encoder.truncate(raw.dropoff_lng),
            start_hour_class=self.start_time_encoder.hour_class(
                raw.start_time),
            start_weekday_class=self.start_time_encoder.weekday_class(
                raw.start_time),
            eda_scaled=self.eda_encoder.scale(raw.eda),
            eta_scaled=self.eta_encoder.scale(raw.eta),
            straight_dist_scaled=self.straight_dist_encoder.scale(
                raw.straight_dist)
        )

    def _check_version(self, schema):
        if "version" not in schema:
            raise Exception("schema.version missing")
        # TODO: auto version number instead of hard-coded
        if str(schema["version"]) != "0.1":
            raise Exception(
                f"schema.version mismatch, expect: 0.1, got: {schema['version']}")

    def _create_start_time_encoder(self, features) -> StartTimeEncoder:
        if "start_time" not in features:
            raise Exception(
                "schema.features: start_time missing\n{}".format(features))
        if "hour" not in features["start_time"]:
            raise Exception(
                "schema.features: start_time.hour missing\n{}".format(features))
        if "weekday" not in features["start_time"]:
            raise Exception(
                "schema.features: start_time.weekday missing\n{}".format(features))
        return StartTimeEncoder(features["start_time"]["hour"], features["start_time"]["weekday"])

    def _create_latlng_encoder(self, features) -> LatLngEncoder:
        if "latlng" not in features:
            raise Exception(
                "schema.features: latlng missing\n{}".format(features))
        return LatLngEncoder(features["latlng"])

    def _create_eta_encoder(self, features) -> ScaleEncoder:
        if "ETA" not in features:
            raise Exception("feature schema: ETA missing\n{}".format(features))
        return ScaleEncoder(features["ETA"])

    def _create_eda_encoder(self, features) -> ScaleEncoder:
        if "EDA" not in features:
            raise Exception(
                "schema.features: EDA missing\n{}".format(features))
        return ScaleEncoder(features["EDA"])

    def _create_straight_dist_encoder(self, features) -> ScaleEncoder:
        if "straight_dist" not in features:
            raise Exception(
                "schema.features: straight_dist missing\n{}".format(features))
        return ScaleEncoder(features["straight_dist"])


def parse_feature_schema(text):
    schema = yaml.load(text, Loader=yaml.FullLoader)
    return FeatureSchema(schema)


if __name__ == "__main__":
    with open("./sample.feature-spec.yaml") as f:
        schema = parse_feature_schema(f.read())

    import time
    vector = schema.gen_trip_vector(RawInput(
        start_time=time.time(),
        pickup_lat=1.033333,
        pickup_lng=103.111111,
        dropoff_lat=1.044444,
        dropoff_lng=103.222222,
        eda=10000,
        eta=2000,
        straight_dist=6880,
    ))
    print(vector.field_names())
    print(vector.to_list())
