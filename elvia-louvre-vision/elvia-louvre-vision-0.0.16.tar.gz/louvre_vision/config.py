class Config():
    """Configuration values."""

    custom_vision_max_training_file_size = int(6e6)
    default_delimiter: str = ';'
    default_image_variant: str = "standard"
    hash_length: int = 10
    image_longer_side: int = 2000
    predictions_rounding_decimal_places: int = 3
