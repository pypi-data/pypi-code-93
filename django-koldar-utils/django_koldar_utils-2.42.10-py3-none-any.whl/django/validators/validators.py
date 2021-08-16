import abc

from django.core.exceptions import ValidationError


def validate_image_min_width(value_to_check, min_width: int = 32):
    if not (value_to_check.width > min_width):
        raise ValidationError(f"image has width {value_to_check.width}, which is less than the minimum one {min_width}!")