"""
Created on Tue Jun 22 21:01:59 2021
@author: Lucas Valentim lucasbcamara@gmail.com
Synopsis: Código baseado na planilha Ezalt do Nakka, disponível em:
    <https://www.nakka-rocketry.net/softw.html#ezalt>
Obetivo de transformar a planilha do excel em uma ferramenta em python.
"""
def Ezalt():
    import math
    import matplotlib.pyplot
    from datetime import datetime

#Abertura do programa
    print(" ")
    print("--Ezalt--")
    
#input do programa
    title=str(input(("Insira o nome do foguete: ")))
    F=float(input(("Insira o Impulso do motor (N): ")))
    It=float(input(("Insira o Impulso Total do motor (N-sec): ")))
    Mp=float(input(("Insira a Massa do propelente do motor (kg): ")))
    Mr=float(input(("Insira a Massa morta do foguete (kg): "))) #massa do foguete sem o motor
    D=float(input(("Insira o diâmetro do foguete (cm): ")))
    Cd=float(input(("Insira o coeficiente de arrasto (tipicamente entre 0,3 a 0,6): ")))

    print(" ")
#cálculos e outputs do programa
    print("------------------------")
    print(" ")
#tempo de impulso do motor
    t=It/F if F!=0 else 0
    print("Tempo de impulso do motor: t= ",'{:.3f}'.format(t)," s")
    
    if It>=1.3 and It<2.5:
        Classe="A"
    elif It>=2.5 and It<5:
        Classe="B"
    elif It>=5 and It<10:
        Classe="C"
    elif It>=10 and It<20:
        Classe="D"
    elif It>=20 and It<40:
        Classe="E"
    elif It>=40 and It<80:
        Classe="F"
    elif It>=80 and It<160:
        Classe="G"
    elif It>=160 and It<320:
        Classe="H"
    elif It>=320 and It<640:
        Classe="I"
    elif It>=640 and It<1280:
        Classe="J"
    else:
        Classe="K"
    print("Classificação do motor: ", Classe)

    Mra=Mr+Mp/2
    print("Massa média de voo do foguete: Mra= ",'{:.3f}'.format(Mra)," Kg")

    a=F/Mra-9.808
    print("Aceleração: a= ",'{:.3f}'.format(a)," m/s²")

    print(" ")
    print("Ideal -  Sem resistência de arrasto")
    print(" ")

    z1=1/2*(F/Mra-9.808)*t**2
    print("Altitude de burnout: ",'{:.3f}'.format(z1)," m")

    z2=F*z1/Mra/9.808
    print("Altitude de pico: ",'{:.3f}'.format(z2)," m")


    t2=t+math.sqrt(2*(z2-z1)/9.808)
    print("Tempo para atingir altitude de pico: ",'{:.3f}'.format(t2)," s")
    
    v1=math.sqrt((2*z1)/Mra*(F-Mra*9.808))
    print("Velocidade máxima: ",'{:.3f}'.format(v1)," m/s")
    
    print("------------------------")
    print("Fatores de redução de arrasto")
    print(" ")

    N=Cd*D**2*v1**2/Mr/1000
    print("Número de influência de arrasto: ",'{:.3f}'.format(N))

    if N>900:
        print("(Fora do alcance válido!)")
        print(" ")
#f1: fator de redução de altitude de pico. Altitude máxima é reduzida devido ao arrasto aerodinâmico
    if 1/(1.049909+0.001719*(N**1.0042225))>1 :
        f1=1
    else:
        f1=1/(1.049909+0.001719*(N**1.0042225))
    print("Fator de redução de altitude de pico: ",'{:.3f}'.format(f1), " m")

#f2: fator de redução de tempo de altitude. Tempo para atingir o pico é reduzido pelo arrasto aerodinâmico
    if 1/(1.048224+0.001093*(N**0.97255))>1 :
        f2=1
    else:
        f2=1/(1.048224+0.001093*(N**0.97255))
    print("Fator de redução de tempo de altitude: ",'{:.3f}'.format(f2)," s")

#f3: fator de redução da velocidade máxima. A velocidade máxima é reduzida devidoao arrasto aerodinâmico
    if (0.99769-0.000075691*N)>1 :
        f3=1
    else:
        f3=(0.99769-0.000075691*N)
    print("Fator de redução de velocidade máxima: ",'{:.3f}'.format(f3)," m/s")
   
#f4: fator de redução de altitude de burnout. A altitude do burnout é reduzido devido ao arrasto aerodinâmico
    if (0.99973-0.000043807*N)>1 :
        f4=1
    else:
        f4=(0.99973-0.000043807*N)
    print("Fator de redução de altitude de burnout: ",'{:.3f}'.format(f4)," m")

    print("------------------------")
    print("Predito com arrasto")
    print(" ")

    Zpico=f1*z2
    print("Altitude de pico: Zpico= ",'{:.3f}'.format(Zpico)," m")

    tpico=f2*t2
    print("Tempo para Altitude de pico: tpico= ",'{:.3f}'.format(tpico)," s")

    Vmax=f3*v1
    print("Velocidade máxima: vmax= ",'{:.3f}'.format(Vmax)," m/s")

    Zbo=f4*z1
    print("Altitude de burnout: Zbo= ",'{:.3f}'.format(Zbo)," m")

    if v1>331 :
        print(" ")
        print("AVISO: Foguete Supersônico. Resultados podem ser inválidos")
    
    print("------------------------")
    print("Melhor massa")

    Mmin=float(input("Insira a massa mínima (kg): "))
    
    while Mmin<=0 :
        print("O valor deve ser maior que zero")
        Mmin=float(input("Insira a massa mínima (kg): "))

    Mmax=float(input("Insira a massa máxima (kg): "))

    i=(Mmax-Mmin)/23
    #print("Intervalo: ",'{:.2f}'.format(i), ' Kg'))

    Mmassa=(i*5)+Mmin

    print("Melhor massa: ",'{:.2f}'.format(Mmassa), ' Kg')
#construção do gráfico    
    m=Mmin

    matplotlib.pyplot.title('Altitude por massa')
    matplotlib.pyplot.xlabel('Massa (Kg)')
    matplotlib.pyplot.ylabel('Altitude (m)')
    matplotlib.pyplot.grid(True)

    matplotlib.pyplot.plot([m, m+i,m+2*i,m+3*i,m+4*i,m+5*i,m+6*i,m+7*i,m+8*i,m+9*i,m+10*i,m+11*i,m+12*i,m+13*i,m+14*i,m+15*i,m+16*i,m+17*i,m+18*i,m+19*i,m+20*i,m+21*i,m+22*i
    ,m+23*i], [282, 445, 588, 698, 767, 796, 790, 758, 711, 656, 600, 545, 493, 446, 404, 366, 333, 303, 276, 253, 232, 214, 197, 182], color='g',marker='o')
    matplotlib.pyplot.annotate('Altitude Máx.', xy=(m+5*i, 796), xytext=(3.5, 600), arrowprops=dict(facecolor='black', shrink=0.1))

    matplotlib.pyplot.show()

#construção do arquivo em txt com os valores
    data=datetime.now()
    datatxt=data.strftime('%d/%m/%Y %H:%M')

    arquivo = open('ezalt_results.txt', 'a')
    arquivo.write('\n')
    arquivo.write(datatxt)
    arquivo.write('\n')
    arquivo.write('\n')
    arquivo.write('Título: ')
    arquivo.write(title)
    arquivo.write('\n')
    arquivo.write('Impulso do motor: F= ')
    arquivo.write('{}'.format(F))
    arquivo.write(' N')
    arquivo.write('\n')
    arquivo.write('Impulso total: It= ')
    arquivo.write('{}'.format(It))
    arquivo.write(' N-sec')
    arquivo.write('\n')
    arquivo.write('Massa do propelente: Mp= ')
    arquivo.write('{}'.format(Mp))
    arquivo.write(' Kg')
    arquivo.write('\n')
    arquivo.write('Massa morta: Mr= ')
    arquivo.write('{}'.format(Mr))
    arquivo.write(' Kg')
    arquivo.write('\n')
    arquivo.write('Diâmetro do foguete: D= ',)
    arquivo.write('{}'.format(D))
    arquivo.write(' cm')
    arquivo.write('\n')
    arquivo.write('Coeficiente de Arrasto: Cd= ')
    arquivo.write('{}'.format(Cd))
    arquivo.write('\n')
    arquivo.write('Tempo de impulso do motor: t= ')
    arquivo.write('{}'.format(t))
    arquivo.write(' s')
    arquivo.write('\n')
    arquivo.write('Classificação do motor: ')
    arquivo.write(Classe)
    arquivo.write('\n')
    arquivo.write('Massa média de voo: Mra= ')
    arquivo.write('{}'.format(Mra))
    arquivo.write(' Kg')
    arquivo.write('\n')
    arquivo.write('Aceleração: a= ')
    arquivo.write('{}'.format(a))
    arquivo.write(' m/s²')
    arquivo.write('\n')
    arquivo.write('-----------------------------------')
    arquivo.write('\n')
    arquivo.write('\n')
    arquivo.write('Ideal - Sem resistência de arrasto')
    arquivo.write('\n')
    arquivo.write('\n')
    arquivo.write('Altitude de Burnout: z1= ')
    arquivo.write('{}'.format(z1))
    arquivo.write(' m')
    arquivo.write('\n')
    arquivo.write('Altitude de pico: z2= ')
    arquivo.write('{}'.format(z2))
    arquivo.write(' m')
    arquivo.write('\n')
    arquivo.write('Tempo para altitude de pico: t2= ')
    arquivo.write('{}'.format(t2))
    arquivo.write(' s')
    arquivo.write('\n')
    arquivo.write('Velocidade máxima: v1= ')
    arquivo.write('{}'.format(v1))
    arquivo.write(' m/s')
    arquivo.write('\n')
    arquivo.write('----------------------------------')
    arquivo.write('\n')
    arquivo.write('\n')
    arquivo.write('Fatores de redução de arrasto')
    arquivo.write('\n')
    arquivo.write('\n')
    arquivo.write('Número de influência de arrasto: N= ')
    arquivo.write('{}'.format(N))
    arquivo.write('\n')
    arquivo.write('Fator de redução de altitude de pico: f1= ')
    arquivo.write('{}'.format(f1))
    arquivo.write(' m')
    arquivo.write('\n')
    arquivo.write('Fator de redução de tempo de altitude: f2= ')
    arquivo.write('{}'.format(f2))
    arquivo.write(' s')
    arquivo.write('\n')
    arquivo.write('Fator de redução de velocidade máxima: f3= ')
    arquivo.write('{}'.format(f3))
    arquivo.write(' m/s')
    arquivo.write('\n')
    arquivo.write('Fator de redução de altitude de burnout: f4= ')
    arquivo.write('{}'.format(f4))
    arquivo.write(' m')
    arquivo.write('\n')
    arquivo.write('----------------------------------')
    arquivo.write('\n')
    arquivo.write('\n')
    arquivo.write('Predito com arrasto')
    arquivo.write('\n')
    arquivo.write('\n')
    arquivo.write('Altitude de pico: Zpico= ')
    arquivo.write('{}'.format(Zpico))
    arquivo.write(' m')
    arquivo.write('\n')
    arquivo.write('Tempo para altitude de pico: tpico= ')
    arquivo.write('{}'.format(tpico))
    arquivo.write(' s')
    arquivo.write('\n')
    arquivo.write('Velocidade máxima: Vmax= ')
    arquivo.write('{}'.format(Vmax))
    arquivo.write(' m/s')
    arquivo.write('\n')
    arquivo.write('Altitude de burnout: Zbo= ')
    arquivo.write('{}'.format(Zbo))
    arquivo.write(' m')
    arquivo.write('\n')
    if v1==331:
        arquivo.write('AVISO: Foguete Supersônico. Resultados podem ser inválidos')
        arquivo.write('\n')
    arquivo.write('----------------------------------')
    arquivo.write('\n')
    arquivo.write('\n')
    arquivo.write('Melhor Massa')
    arquivo.write('\n')
    arquivo.write('\n')
    arquivo.write('Melhor massa: Mm= ')
    arquivo.write('{}'.format(Mmassa))
    arquivo.write(' Kg')
    arquivo.write('\n')
    arquivo.write('==================================')
    arquivo.close()

Ezalt()    