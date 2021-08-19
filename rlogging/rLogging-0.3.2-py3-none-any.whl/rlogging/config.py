import os

# Объект логгера, который будет использоваться при логировании
RLOGGING_LOGGER = os.environ.get('RLOGGING_LOGGER', 'rlogging.entities.loggers.Logger')

# Объект лога, который будет использоваться при логировании
RLOGGING_RECORD = os.environ.get('RLOGGING_RECORD', 'rlogging.entities.records.Record')

# Предоставленое для применения настроек время.
# Если до создания новых настроке в хранилище логов поступит много логов
# То до их полной обработки понадобится большее время
RLOGGING_WAIT_APPLY_SETTINGS = os.environ.get('RLOGGING_WAIT_APPLY_SETTINGS', 10)
