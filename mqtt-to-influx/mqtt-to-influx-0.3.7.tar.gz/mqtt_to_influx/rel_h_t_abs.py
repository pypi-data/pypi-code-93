# pylint 
# vim: tw=100 foldmethod=indent
# pylint: disable=bad-continuation, invalid-name, superfluous-parens
# pylint: disable=bad-whitespace, mixed-indentation
# pylint: disable=redefined-outer-name
# pylint: disable=missing-docstring, trailing-whitespace, trailing-newlines, too-few-public-methods
# pylint: disable=unused-argument

def interpolation (x, x1, x2, r1, r2):
    if x1 == x2:
        # print (F"I have problems: \n  x: {x}\n  x1:{x1}\n  x2:{x2}")
        a = 1    
    else:
        a = (r1 - r2) / (x1 - x2)
    b = r1 - a * x1
    return a * x + b

def rel_hum_to_abs_hum (temperature, humidity):
    temperature_table = [50, 45, 40, 35, 30, 25, 20, 15, 10, 5, 0, -5, -10, -15, -20, -25]
    humidity_table = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    i=0
    # float hmd1, hmd2

    conversion_table = \
               [[8.3,	16.6,	24.9,	33.2,	41.5,	49.8,	58.1,	66.4,	74.7,	83.0],
                [6.5,	13.1,	19.6,	26.2,	32.7,	39.3,	45.8,	52.4,	58.9,	65.4],
                [5.1,	10.2,	15.3,	20.5,	25.6,	30.7,	35.8,	40.9,	46.0,	51.1],
                [4.0,	7.9 ,   11.9,	15.8,	19.8,	23.8,	27.7,	31.7,	35.6,	39.6],
                [3.0,	6.1 ,   9.1 ,   12.1,	15.2,	18.2,	21.3,	24.3,	27.3,	30.4],
                [2.3,	4.6 ,   6.9 ,   9.2 ,   11.5,	13.8,	16.1,	18.4,	20.7,	23.0],
                [1.7,	3.5 ,   5.2 ,   6.9 ,   8.7 ,   10.4,	12.1,	13.8,	15.6,	17.3],
                [1.3,	2.6 ,   3.9 ,   5.1 ,   6.4 ,   7.7 ,   9.0 ,   10.3,	11.5,	12.8],
                [0.9,	1.9 ,   2.8 ,   3.8 ,   4.7 ,   5.6 ,   6.6 ,   7.5 ,   8.5 ,   9.4 ],
                [0.7,	1.4 ,   2.0 ,   2.7 ,   3.4 ,   4.1 ,   4.8 ,   5.4 ,   6.1 ,   6.8 ],
                [0.5,	1.0 ,   1.5 ,   1.9 ,   2.4 ,   2.9 ,   3.4 ,   3.9 ,   4.4 ,   4.8 ],
                [0.3,	0.7 ,   1.0 ,   1.4 ,   1.7 ,   2.1 ,   2.4 ,   2.7 ,   3.1 ,   3.4 ],
                [0.2,	0.5 ,   0.7 ,   0.9 ,   1.2 ,   1.4 ,   1.6 ,   1.9 ,   2.1 ,   2.3 ],
                [0.2,	0.3 ,   0.5 ,   0.6 ,   0.8 ,   1.0 ,   1.1 ,   1.3 ,   1.5 ,   1.6 ],
                [0.1,	0.2 ,   0.3 ,   0.4 ,   0.4 ,   0.5 ,   0.6 ,   0.7 ,   0.8 ,   0.9 ],
                [0.1,	0.1 ,   0.2 ,   0.2 ,   0.3 ,   0.3 ,   0.4 ,   0.4 ,   0.5 ,   0.6 ]]
    # search temperature index
    temperature_idx = 0
    for t in temperature_table:
        if temperature >= t:
            break
        temperature_idx += 1

    temp_idx1 = temperature_idx
    if temp_idx1 > len(temperature_table):
        temp_idx1 = len(temperature_table)
    temp_idx2 = temperature_idx-1
    if temp_idx1 < 0:
        temp_idx1 = 0
    # print (F"t_idx1: {temp_idx1} - t_idx2: {temp_idx2}")
    temp1     = temperature_table[temp_idx1]
    temp2     = temperature_table[temp_idx2]
    
    # search humidity index
    humidity_idx = 0
    for i in range(0,10):
        if (humidity <= humidity_table[i]):
            break
        humidity_idx += 1

    hum_idx1 = humidity_idx-1
    if hum_idx1 < 0:
        hum_idx1 = 0
    hum_idx2 = humidity_idx
    if hum_idx2 > len(humidity_table):
        hum_idx2 = len(humidity_table)
    hum1     = humidity_table[hum_idx1]
    hum2     = humidity_table[hum_idx2]

    hmd1 = interpolation (temperature, temp1, temp2, \
        conversion_table[temp_idx1][hum_idx1],
        conversion_table[temp_idx2][hum_idx1])
    hmd2 = interpolation (temperature, temp1, temp2, \
        conversion_table[temp_idx1][hum_idx2],
        conversion_table[temp_idx2][hum_idx2])

    absolute_humidity = interpolation (humidity, hum1, hum2, hmd1, hmd2)

    return absolute_humidity; 

if (__name__ == "main"):
    print (F"rel: {rel_hum_to_abs_hum(-25,100)}")
    print (F"rel: {rel_hum_to_abs_hum(50,10)}")
    print (F"rel: {rel_hum_to_abs_hum(50,100)}")
    print (F"rel: {rel_hum_to_abs_hum(-25,10)}")

    print (F"rel: {rel_hum_to_abs_hum(45,90)}")
    print (F"rel: {rel_hum_to_abs_hum(45,95)}")
    print (F"rel: {rel_hum_to_abs_hum(15.8, 98)}")
