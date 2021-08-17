from typing import Union

class Calculator:
    """
    This calculator class performs the following basic mathematical operations:
    * Addition
    * Subtraction
    * Division
    * Multiplication
    * nth root of number
    * Reset
    Attributes
    ----------
    __value : (int or float)
        the calculator memory value
    Methods
    --------
    memory_value():
        returns the calculator memory value
    __input_validation(num):
        validates that the value entered is a number or float
    reset_memory():
        resets the calculator memory to 0
    add(new_value: int or float):
        adds the new value to the value in the calculator memory
    subtract(new_value: int or float):
        subtracts the new value from the value in the calculator memory
    multiply(new_value: int or float):
        multiplies the new value with the value in the calculator memory
    divide(new_value: int or float):
        divides the value in the calculator memory with the new value
    n_root(root: int or float):
        takes the (n) root of the value in the calculator memory
    exponent(exponent: int or float):
        raises the values in the calculator memory to the power of the inputted value
    
    """

    def __init__(self, value:int = 0)-> None:
        """
        initializes the memory value
        """
        self.__input_validation(value)
        self.__index = value


    @property
    def memory_value(self) -> Union[int, float]:
        """
        Accesses the memory which initially is set to 0
        """
        return self.__index

    @staticmethod
    def __input_validation(number: Union[int, float]) -> None:
        """
        Validates that the inputed number is an integer or float
        """
        if not isinstance (number, (int, float)):
            raise TypeError("Not a Number (input float or integer)")

    def reset_memory(self) -> Union[int, float]:
        """
            Resets memory to 0
        """
        self.__index = 0
        return self.__index
       
    def add(self, num: Union[int, float]) -> Union[int, float]:
        """
           Adds inputed number to value in the memory
        """
        self.__input_validation(num)
        self.__index += num
        return self.__index

    def subtract(self, num: Union[int, float]) -> Union[int, float]:
        """
          Subtracts inputed number from value in memory
        """
        self.__input_validation(num)
        self.__index -= num
        return self.__index

    def multiply(self, num: Union[int, float]) -> Union[int, float]:
        """
          Multiplies inputed number by value in memory
        """
        self.__input_validation(num)
        self.__index *= num
        return self.__index

    def divide(self, num: Union[int, float]) -> Union[int, float]:
        """
          Divides inputed number by value in memory
        """
        self.__input_validation(num)
        try:
            self.__index /= num
            return self.__index
        except ZeroDivisionError as err:
            print(f"number cannot be zero => {err}")

    def modulus(self, num: Union[int, float]):
        """
          Divides inputed number by value in memory and return the reminder
        """
        self.__input_validation(num)
        try:
            self.__index %= num
            return self.__index
        except ZeroDivisionError as err:
            print(f"number cannot be zero => {err}")

    def nth_root(self, num: Union[int, float]) -> Union[int, float]:
        """
          Finds the root of number in the calculator memory by the inputed value given that memory_value > 0 && inputed num > 0
        """
        self.__input_validation(num)
        if self.__index <= 0:
            raise ValueError(f"The calculator does not have the capacity to compute negative roots")
        elif num <= 0:
            raise ValueError("The calculator does not have the capacity to compute negative roots")
        else:
            self.__index = self.__index**(1/num)
            return self.__index
    
    def exponent(self, num: Union[int, float]) -> Union[int, float]:
        """
        Raises the values in the calculator memory to the power of the inputed value
        """
        self.__input_validation(num)
        self.__index = self.__index ** num
        return self.__index

   