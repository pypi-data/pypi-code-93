def retornar_o_resto_da_divisao(valor1, valor2):
    resultado = valor1 % valor2
    return 'O Resto da Divisão:' \
           ' {valor1} % {valor2} = {resultado}' \
           ''.format(valor1=valor1,
                     valor2=valor2,
                     resultado=resultado)
