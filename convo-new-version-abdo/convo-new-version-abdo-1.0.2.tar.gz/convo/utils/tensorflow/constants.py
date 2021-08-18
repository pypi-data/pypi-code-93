# constants for configuration parameters of our tensorflow models

STAGE = "label"
SIZES_OF_HIDDEN_LAYERS = "hidden_layers_sizes"
SHARED_HIDDEN_LAYERS = "share_hidden_layers"

TRANSFORMER_DIMENSION = "transformer_size"
NUMBER_TRANSFORMER_LAYERS = "number_of_transformer_layers"
NUMBER_HEADS = "number_of_attention_heads"
UNI_DIRECTIONAL_ENCODER = "unidirectional_encoder"
RELATIVE_ATTENTION_KEY = "use_key_relative_attention"
RELATIVE_ATTENTION_VAL = "use_value_relative_attention"
RELATIVE_POSITION_MAXIMUM = "max_relative_position"

BATCH_SIZE = "batch_size"
GROUP_STRATEGY = "batch_strategy"
EPOCHS = "epochs"
RAND_SEED = "random_seed"
RATE_OF_LEARNING = "learning_rate"

DIMENSION_DENSE = "dense_dimension"
CONCATENATE_DIMENSION = "concat_dimension"
EMBEDDING_CAPACITY = "embedding_dimension"
ENCODING_CAPACITY = "encoding_dimension"

SIMILARITY_TYPE_CATEGORY = "similarity_type"
LOSS_CATEGORY = "loss_type"
NUMBER_NEG = "number_of_negative_examples"
MAXIMUM_POSITIVE_SIMILARITY = "maximum_positive_similarity"
MAXIMUM_NEGATIVE_SIMILARITY = "maximum_negative_similarity"
USE_MAXIMUM_NEGATIVE_SIMILARITY = "use_maximum_negative_similarity"

LOSS_SCALE = "scale_loss"
REGULARIZATION_CONST = "regularization_constant"
NEG_MARGIN_SCALE = "negative_margin_scale"
DROP_PRICE = "drop_rate"
ATTENTION_DROP_RATE = "drop_rate_attention"
DROP_RATE_DIALOG = "drop_rate_dialogue"
LABEL_DROP_RATE = "drop_rate_label"

WEIGHT_SPARSE = "weight_sparsity"

EVALUATE_NUMBER_EPOCHS = "evaluate_every_number_of_epochs"
EVALUATE_NUM_EXAMPLES = "evaluate_on_number_of_examples"

INTENT_CLASSIFY = "intent_classification"
ENTITY_IDENTIFICATION = "entity_recognition"
COVERED_LM = "use_masked_language_model"

SPARSE_INP_DROP_OUT = "use_sparse_input_dropout"
DENSE_INP_DROP_OUT = "use_dense_input_dropout"

LENGTH_RANKING = "ranking_length"

FLAG_BILOU = "BILOU_flag"

RETRIEVAL_INTENT = "retrieval_intent"

USE_TEXT_AS_LABEL = "use_text_as_label"

SOFT_MAX = "softmax"
EDGE = "margin"
AUTOMATIC = "auto"
INTERIOR = "inner"
COSINE_VALUE = "cosine"

BALANCED_VALUE = "balanced"

SEQUENTIAL = "sequence"
SENTENCE = "sentence"

POOL = "pooling"
MAXIMUM_POOLING = "max"
MEAN_POOL = "mean"

TENSOR_BOARD_LOG_DIRECTORY = "tensorboard_log_directory"
TENSOR_BOARD_LOGGING_LEVEL = "tensorboard_log_level"

SEQUENTIAL_FEATURES = "sequence_features"
STATEMENT_FEATURES = "sentence_features"

FEATURES = "featurizers"
CHECK_POINT_MODEL = "checkpoint_model"
