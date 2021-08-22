def odd_generator(min: int, max: int):
    try:
        for number in range(min, max):
            if number % 2 != 0:
                yield number
    except:
        return "Error, please check your args"

def even_generator(min: int, max: int):
    try:
        for i in range(min, max):
            if i % 2 == 0:
                yield i
    except:
        return "Error, please check your args"





def custom_generator(min : int, max :int, divisable_by : int):
    try:
        for i in range(min, max):
            if i % divisable_by == 0:
                yield i
    except ZeroDivisionError:
        return "divisable_by cannot be 0"
    except:
        return "Error, please check your args"