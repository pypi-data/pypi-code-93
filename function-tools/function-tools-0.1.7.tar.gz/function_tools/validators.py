class BaseValidator:
    """
    Базовый класс для создания валидатора
    """
    def validate(self, runnable):
        """
        Точка входа работы валидатора.

        Результат валидации должен быть записан в runnable.result
        """
