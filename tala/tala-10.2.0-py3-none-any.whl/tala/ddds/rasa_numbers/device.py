from tala.model.device import DddDevice, DeviceAction, DeviceWHQuery, Validity


class RasaNumbersDevice(DddDevice):
    class NumberOfApplesValidity(Validity):
        def is_valid(self, apples_individual):
            return (apples_individual < 31) and (apples_individual > 5)

    class BuyApples(DeviceAction):
        def perform(self, desired_number_apples):
            return True

    class allowed_number_apples(DeviceWHQuery):
        def perform(self):
            maximum_allowed_amount = 30
            return [maximum_allowed_amount]
