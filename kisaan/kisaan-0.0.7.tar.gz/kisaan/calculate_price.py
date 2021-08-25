def calculate_price(unit,unit_price,weight):
    unit=str(unit)
    unit_price=str(unit_price)
    weight=str(weight)

    if(len(unit.split(" "))==2):
        custom_unit_value,unit=unit.split(" ")
    else:
        custom_unit_value="1"

    weight_value,weight_unit=weight.split(" ")
    weight_unit_standard={"kg":1,"gm":1000,"liter":1,"ml":1000,"dozen":1,"piece":12}
    if(weight_unit_standard[unit]<weight_unit_standard[weight_unit]):
        price=eval(weight_value)*eval(unit_price)/(weight_unit_standard[unit]/eval(custom_unit_value))
        return price
    elif(weight_unit_standard[unit]==weight_unit_standard[weight_unit]):
        price=eval(weight_value)*eval(unit_price)/eval(custom_unit_value)
        return price
    elif(weight_unit_standard[unit]>weight_unit_standard[weight_unit]):
        return eval(weight_value)*eval(unit_price)*(weight_unit_standard[unit]/eval(custom_unit_value))