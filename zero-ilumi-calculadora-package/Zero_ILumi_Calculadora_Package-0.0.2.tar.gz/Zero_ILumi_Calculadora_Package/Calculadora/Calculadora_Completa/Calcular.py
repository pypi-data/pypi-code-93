from Zero_ILumi_Calculadora_Package.Calculadora.Arithmetic_Operations.soma import somar
from Zero_ILumi_Calculadora_Package.Calculadora.Arithmetic_Operations.subtracao import subtrair
from Zero_ILumi_Calculadora_Package.Calculadora.Arithmetic_Operations.multiplicacao import multiplicar
from Zero_ILumi_Calculadora_Package.Calculadora.Arithmetic_Operations.divisao import dividir
from Zero_ILumi_Calculadora_Package.Calculadora.Arithmetic_Operations.resto_divisao import retornar_o_resto_da_divisao


def Calculadora():
    while True:
        try:
            primeiro_numero = int(input('Digite o primeiro valor\n'))
            segundo_numero = int(input('Digite o segundo valor\n'))
            resultado_soma = somar(primeiro_numero, segundo_numero)
            resultado_subtracao = subtrair(primeiro_numero, segundo_numero)
            resultado_multiplicacao = multiplicar(primeiro_numero, segundo_numero)
            resultado_divisao = dividir(primeiro_numero, segundo_numero)
            resultado_resto_divisao = retornar_o_resto_da_divisao(primeiro_numero, segundo_numero)
            print(resultado_soma)
            print(resultado_subtracao)
            print(resultado_multiplicacao)
            print(resultado_divisao)
            print(resultado_resto_divisao)
            continuar = int(input('Deseja Continuar Calculando?\n'
                                  '1:Sim\n'
                                  '2:Não\n'))
            if continuar == 1:
                pass
            elif continuar == 2:
                print('Obrigado por usar o pacote Zero_ILumi_Calculadora_Package')
                break
        except ValueError:
            print('Valor Invalido')

if __name__ == '__main__':
    pass