from . import model


def test_gen_trip_vector():
    schema_text = """version: 0.1
features:
  start_time:
    hour: [
        [0, 1, 2, 3, 4, 5],
        [6, 7, 8, 9, 10, 11],
        [12, 13, 14, 15, 16, 17],
        [18, 19, 20, 21, 22, 23],
      ] # hour segments: 0-6, 6-12, 12-18, 18-24
    weekday: [[1, 2, 3, 4, 5], [6, 7]] # weekday segments: Mon-Friday, Sat-Sun
  latlng: 3 # Lat/Lng precision: 3 digits after decimal point
  ETA: 60 # round(ETA / 60)
  EDA: 1000 # round(ETA / 1000)
  straight_dist: 1000 # round(straight_dist / 1000)
"""
    import datetime

    schema = model.parse_feature_schema(schema_text)
    vector = schema.gen_trip_vector(model.RawInput(
        start_time=datetime.datetime.fromisoformat(
            "2020-04-29 16:00:00+00:00").timestamp(),
        pickup_lat=1.033333,
        pickup_lng=103.111111,
        dropoff_lat=1.044444,
        dropoff_lng=103.222222,
        eda=10000,
        eta=2000,
        straight_dist=6880,
    ))

    assert vector.start_hour_class == 2
    assert vector.start_weekday_class == 0
    assert vector.pickup_lat_trunc == 1.033
    assert vector.eda_scaled == 10
    assert vector.eta_scaled == 33
    assert vector.straight_dist_scaled == 7
