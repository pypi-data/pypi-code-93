from .app_settings import PBF_FILE_SIZE_ESTIMATION_CSV_FILE_PATH
from .estimate_size import estimate_size_of_extent
from rest_framework import serializers

csv_source_file = PBF_FILE_SIZE_ESTIMATION_CSV_FILE_PATH


class FileEstimationSerializer(serializers.Serializer):
    west = serializers.FloatField()
    south = serializers.FloatField()
    east = serializers.FloatField()
    north = serializers.FloatField()

    def validate(self, data):
        data.update({
            'estimated_file_size_in_bytes': estimate_size_of_extent(
                csv_source_file,
                west=data['west'],
                south=data['south'],
                east=data['east'],
                north=data['north'],
            )
        })
        return data

    def to_representation(self, instance):
        return instance
