# -*- coding: utf-8 -*-

import plotly.graph_objects as go
from plotly.offline import plot as plt
import numpy as np
from sympy import *
import random 
import math
import re as rep

t = Symbol("t")

def conv(elemento):
    if elemento == '' or elemento == '+' or elemento == '  ' or elemento == ' + 'or elemento == ' ':
        numero = 1
    elif elemento == '-' or elemento == ' - ':
        numero = -1
    else:
        numero = float(S(elemento))
    return numero


def convierte(cadena):

    if "*" in cadena:
        elemento = cadena[:-1]
        if elemento == '' or elemento == '+' or elemento == '  ' or elemento == ' ':
            numero = 1
        elif elemento == '-' or elemento == ' - ':
            numero = -1
        else:
            numero = float(S(elemento))
        return numero

    if "*" not in cadena:
        elemento = cadena
        return conv(elemento)

def conver(elemento):
    if elemento == '' or elemento == '+':
        numero = 1
    elif elemento == '-':
        numero = -1
    else:
        numero = float(S(elemento))
    return numero


def extra(cadena):
    if "t" in cadena:
        if cadena[-1] != "t":
            primero = rep.split("t",cadena)
            lista = [conver(primero[0]),conver(primero[1])]
        else: 
            primero = rep.split("t",cadena)
            lista = [conver(primero[0]),0]
    else:
        lista = [0,conver(cadena[0])]
    return lista


  
def extraer(cadena):

    if cadena[-3] != "x" and cadena[-3] != "y" and cadena[-3] != "z" :
        
        if "x" not in cadena and "y" in cadena and "z" in cadena :
            segundo = rep.split("y",cadena) 
            tercero = rep.split("z",segundo[1])
            cuarto =  rep.split("=",tercero[1])
            return [0,conv(segundo[0]),conv(tercero[0]),conv(cuarto[0])]
            
        if "x" in cadena and "y" not in cadena and "z" in cadena :
            primero = rep.split("x",cadena)
            tercero = rep.split("z",primero[1])
            cuarto =  rep.split("=",tercero[1])
            return [conv(primero[0]),0,conv(tercero[0]),conv(cuarto[0])]
            
        if "x" in cadena and "y" in cadena and "z" not in cadena :
            primero = rep.split("x",cadena)
            segundo = rep.split("y",primero[1]) 
            cuarto =  rep.split("=",segundo[1])
            return [conv(primero[0]),conv(segundo[0]),0,conv(cuarto[0])]

        if "x" not in cadena and "y" not in cadena and "z" in cadena :
            tercero = rep.split("z",cadena)
            cuarto =  rep.split("=",tercero[1])
            return [0,0,conv(tercero[0]),conv(cuarto[0])]

        if "x" in cadena and "y" not in cadena and "z" not in cadena :
            primero = rep.split("x",cadena)
            cuarto =  rep.split("=",primero[1])
            return [conv(primero[0]),0,0,conv(cuarto[0])]

        if "x" not in cadena and "y" in cadena and "z" not in cadena :
            segundo = rep.split("y",cadena)
            cuarto =  rep.split("=",segundo[1])
            return [0,conv(segundo[0]),0,conv(cuarto[0])]

        if "x" in cadena and "y" in cadena and "z" in cadena :
            primero = rep.split("x",cadena)
            segundo = rep.split("y",primero[1]) 
            tercero = rep.split("z",segundo[1])
            cuarto =  rep.split("=",tercero[1])
            return [conv(primero[0]),conv(segundo[0]),conv(tercero[0]),conv(cuarto[0])]
    else:

        if "x" not in cadena and "y" in cadena and "z" in cadena :
            segundo = rep.split("y",cadena) 
            tercero = rep.split("z",segundo[1])
            return [0,conv(segundo[0]),conv(tercero[0]),0]
            
        if "x" in cadena and "y" not in cadena and "z" in cadena :
            primero = rep.split("x",cadena)
            tercero = rep.split("z",primero[1])
            return [conv(primero[0]),0,conv(tercero[0]),0]
            
        if "x" in cadena and "y" in cadena and "z" not in cadena :
            primero = rep.split("x",cadena)
            segundo = rep.split("y",primero[1]) 
            return [conv(primero[0]),conv(segundo[0]),0,0]

        if "x" not in cadena and "y" not in cadena and "z" in cadena :
            tercero = rep.split("z",cadena)
            return [0,0,conv(tercero[0]),0]

        if "x" in cadena and "y" not in cadena and "z" not in cadena :
            primero = rep.split("x",cadena)
            return [conv(primero[0]),0,0,0]

        if "x" not in cadena and "y" in cadena and "z" not in cadena :
            segundo = rep.split("y",cadena)
            return [0,conv(segundo[0]),0,0]

        if "x" in cadena and "y" in cadena and "z" in cadena :
            primero = rep.split("x",cadena)
            segundo = rep.split("y",primero[1]) 
            tercero = rep.split("z",segundo[1])
            return [conv(primero[0]),conv(segundo[0]),conv(tercero[0]),0]

def ecualist(ecua):

    ecuacion = Eq(1*x+2*y+5*z,3)


    if type(ecua)==type(ecuacion):

        ecu1 = str(ecua)[3:-1]
        cadena1 = rep.split(",",ecu1)[0]
        cadena2 = rep.split(",",ecu1)[1]

        ecua_sim = str(simplify(ecua))[3:-1]
        cadena3 = rep.split(",",ecua_sim)[0]
        cadena4 = rep.split(",",ecua_sim)[1]


        if "x" not in cadena1 and "y" in cadena1 and "z" in cadena1 :

            if conv(cadena2) != 0:
                segundo = rep.split("y",cadena3) 
                tercero = rep.split("z",segundo[1])
                return [0,convierte(segundo[0]),convierte(tercero[0]),conv(cadena4)]

            if conv(cadena2) == 0:
                segundo = rep.split("y",cadena3)
                tercero = rep.split("z",cadena4)
                return [0,convierte(segundo[0]),-1*convierte(tercero[0]),0] 

        
        if "x" in cadena1 and "y" not in cadena1 and "z" in cadena1 :
            if conv(cadena2) != 0:
                primero = rep.split("x",cadena3)
                tercero = rep.split("z",primero[1])
                return [convierte(primero[0]),0,convierte(tercero[0]),conv(cadena4)]
            if conv(cadena2) == 0:
                primero = rep.split("x",cadena3)
                tercero = rep.split("z",cadena4)
                return  [convierte(primero[0]),0,-1*convierte(tercero[0]),0]


        if "x" in cadena1 and "y" in cadena1 and "z" not in cadena1 :

            if conv(cadena2) != 0:
                primero = rep.split("x",cadena3)
                segundo = rep.split("y",primero[1])
                return [convierte(primero[0]),convierte(segundo[0]),0,conv(cadena4)]
            if conv(cadena2) == 0:
                primero = rep.split("x",cadena3)
                segundo = rep.split("y",cadena4)
                return  [convierte(primero[0]),-1*convierte(segundo[0]),0,0]

        if "x" not in cadena1 and "y" not in cadena1 and "z" in cadena1 :

            if conv(cadena2) != 0:
                tercero = rep.split("z",cadena3)
                return [0,0,convierte(tercero[0]),conv(cadena4)]
            if conv(cadena2) == 0:
                tercero = rep.split("z",cadena3)
                return [0,0,convierte(tercero[0]),0]

        if "x" in cadena1 and "y" not in cadena1 and "z" not in cadena1 :

            if conv(cadena2) != 0:
                primero = rep.split("x",cadena3)
                return [convierte(primero[0]),0,0,conv(cadena4)]
            if conv(cadena2) == 0:
                primero = rep.split("x",cadena3)
                return [convierte(primero[0]),0,0,0]

        if "x" not in cadena1 and "y" in cadena1 and "z" not in cadena1 :

            if conv(cadena2) != 0:
                segundo = rep.split("y",cadena3)
                return [0,convierte(segundo[0]),0,conv(cadena4)]
            if conv(cadena2) == 0:
                segundo = rep.split("y",cadena3)
                return [0,convierte(segundo[0]),0,0]

        if "x" in cadena1 and "y" in cadena1 and "z" in cadena1 :
            
            if conv(cadena2) != 0:
                primero = rep.split('x',cadena3)
                segundo = rep.split('y',primero[1])
                tercero = rep.split('z',segundo[1])
                return [convierte(primero[0]),convierte(segundo[0]),convierte(tercero[0]),conv(cadena4)]
            if conv(cadena2) == 0:
                primero = rep.split('x',cadena3)
                segundo = rep.split('y',cadena4)
                tercero = rep.split('z',segundo[1])
                return [convierte(primero[0]),-1*convierte(segundo[0]),-1*convierte(tercero[0]),0]

def sust(elemen,sub):
    elemenstring = str(elemen)
    if "t" in   elemenstring:
        return float(elemen.subs(t,sub))
    if "t" not in elemenstring:
        return float(elemen)

def listaplanos(lista):
    planos = []
    ecuacion = Eq(1*x+2*y+5*z,3)

    for elemen in lista:
        if type(elemen) == str or type(elemen)==type(ecuacion):
            planos.append(elemen)
    return planos


def listarectas(lista):
    rectas = []
    for elemen in lista:
        if type(elemen) == dict and ("t" in (str(elemen[x])+str(elemen[y])+ str(elemen[z]))):
            rectas.append(elemen)
        if type(elemen) == list and type(elemen[0])== str:
            rectas.append(elemen)
    return rectas

def listapuntos(lista):
    puntos = []
    for elemen in lista:
        if type(elemen) == tuple:
            puntos.append(elemen)
        if type(elemen) == dict and (type(elemen[x] + elemen[y] + elemen[z]) == int or type(elemen[x] + elemen[y]+ elemen[z]) == float):
            puntos.append(elemen)
    return puntos


def extraepun(coordenada):
    coorstring = str(coordenada)
    if "t" in coorstring:
        return float(coordenada.subs(t,0))
    if "t" not in coorstring:
        return float(coordenada)

def extraevec(coordenada):
    coorstring = str(coordenada)
    if "t" in coorstring:
        return float(coordenada.subs(t,1)-coordenada.subs(t,0))

    if "t" not in coorstring:
        return 0

def randomRgbaColor():
    r = random.randrange(0, 255)
    g = random.randrange(0, 255)  
    b =random.randrange(0, 255)
    return "rgb"+ "(" + str(r) + "," + str(g) + ","+ str(b) + ")"


def matrixtolist(A):
    a =  np.array(A).astype(np.float64)[0][0]
    b =  np.array(A).astype(np.float64)[1][0]
    c =  np.array(A).astype(np.float64)[2][0]
    return [a,b,c]


def nom(ecua):
    cadena  = str(ecua)[3:-1]
    cadena1 = cadena.replace(",", " =")
    cadena2 = cadena1.replace("*", "")
    return cadena2


def plot3D(*args):

    """Función elaborada  con la  librería Plotly y NumPy, compatible con la librería Sympy  para visualizar
    puntos, rectas, vectores y planos en el espacio."""

    
                        
    data = []
    xe = [0]
    ye = [0]
    ze = [0.3,-0.3]
    Ma = Matrix([1,2,3])
    ecuacion = Eq(1*x+2*y+5*z,3)
    l = []


    for V in args:

        if type(V) == type(Ma) and len(V)==3:
            
            v = matrixtolist(V)

            a = v[0]
            b = v[1]
            c = v[2]

            xe.append(a)
            ye.append(b)
            ze.append(c)
            l.append(V)
        
        if type(V) == type(ecuacion):

            P = ecualist(V)

            d = P[3]
            xe.append(d/(P[0]+0.1))
            ye.append(d/(P[1]+0.1))
            ze.append(d/(P[2]+0.1))

            xe.append(P[0])
            ye.append(P[1])
            ze.append(P[2])

            ze.append(d)   

            l.append(V) 

        if type(V) == tuple:

            xe.append(V[0])
            ye.append(V[1])
            ze.append(V[2])

            l.append(V)        



        if type(V) == list:

            if  type(V[0]) == str:
                
                if len(V) == 3:
                    lista_x = extra(V[0])
                    lista_y = extra(V[1])
                    lista_z = extra(V[2])

                    xe.append(lista_x[1])
                    ye.append(lista_y[1])
                    ze.append(lista_z[1])

                    xe.append(lista_x[1]+lista_x[0])
                    ye.append(lista_y[1]+lista_y[0])
                    ze.append(lista_z[1]+lista_z[0])


                    l.append(V)

                    escala = (max(xe)+max(ye)+max(ze))/10

                    tiempo = abs(escala)

                if len(V) == 4:

                    tiempo = abs(V[3])

                    lista_x = extra(V[0])
                    lista_y = extra(V[1])
                    lista_z = extra(V[2])

                    xe.append(lista_x[1])
                    ye.append(lista_y[1])
                    ze.append(lista_z[1])

                    xe.append(lista_x[1]+lista_x[0])
                    ye.append(lista_y[1]+lista_y[0])
                    ze.append(lista_z[1]+lista_z[0])

                    xe.append(lista_x[1]+lista_x[0]*(-1*tiempo))
                    ye.append(lista_y[1]+lista_y[0]*(-1*tiempo))
                    ze.append(lista_z[1]+lista_z[0]*(-1*tiempo))

                    xe.append(lista_x[1]+lista_x[0]*tiempo)
                    ye.append(lista_y[1]+lista_y[0]*tiempo)
                    ze.append(lista_z[1]+lista_z[0]*tiempo)

                    l.append(V)

            
            elif type(V[0]) == int or type(V[0]) == float :
                
                if type(V[1]) == int or type(V[1]) == float :
                    
                    xe.append(V[0])
                    ye.append(V[1])
                    ze.append(V[2])
                    l.append(V)

                if type(V[1]) == list :
                    
                    magni = V[0]

                    dir_x = V[1][0]
                    dir_y = V[1][1]
                    dir_z = V[1][2]

                    v = [magni *dir_x,magni*dir_y,magni*dir_z]

                    xe.append(v[0])
                    ye.append(v[1])
                    ze.append(v[2])
                    l.append(V)
            
                if type(V[1]) != list and type(V[1]) != int and type(V[1]) != float :

                    magni = V[0]

                    dir_x = np.array(V[1]).astype(np.float64)[0][0]
                    dir_y = np.array(V[1]).astype(np.float64)[1][0]
                    dir_z = np.array(V[1]).astype(np.float64)[2][0]

                    v = [magni *dir_x,magni*dir_y,magni*dir_z]

                    xe.append(v[0])
                    ye.append(v[1])
                    ze.append(v[2])
                    l.append(V)


            elif  type(V[0]) == tuple:


                if len(V)==2:

                    if type(V[1]) == tuple:
                    
                        xe.append(V[0][0])
                        xe.append(V[1][0])

                        ye.append(V[0][1])
                        ye.append(V[1][1])

                        ze.append(V[0][2])
                        ze.append(V[1][2])
                        l.append(V)

                    if type(V[1]) == list:

                        xe.append(V[0][0])
                        xe.append(V[0][0]+V[1][0])

                        ye.append(V[0][1])
                        ye.append(V[0][1]+V[1][1])

                        ze.append(V[0][2])
                        ze.append(V[0][2]+V[1][2])
                        l.append(V)

                    if  type(V[1]) != list and type(V[1]) != tuple:

                        a = np.array(V[1]).astype(np.float64).tolist()[0][0]
                        b = np.array(V[1]).astype(np.float64).tolist()[1][0]
                        c = np.array(V[1]).astype(np.float64).tolist()[2][0]

                        xe.append(V[0][0])
                        xe.append(V[0][0]+a)

                        ye.append(V[0][1])
                        ye.append(V[0][1]+b)

                        ze.append(V[0][2])
                        ze.append(V[0][2]+c)
                        l.append(V)

                else:

                    if  type(V[2]) == list:
                    
                        p_x = V[0][0]
                        p_y = V[0][1]
                        p_z = V[0][2]


                        magni = V[1]

                        dir_x = V[2][0]
                        dir_y = V[2][1]
                        dir_z = V[2][2]

                        v = [magni *dir_x+p_x ,magni*dir_y+p_y,magni*dir_z+p_z]

                        xe.append(p_x)
                        ye.append(p_y)
                        ze.append(p_z)


                        xe.append(v[0])
                        ye.append(v[1])
                        ze.append(v[2])
                        l.append(V)

                    if  type(V[2]) != list and  type(V[2]) != tuple:

                        p_x = V[0][0]
                        p_y = V[0][1]
                        p_z = V[0][2]


                        magni = V[1]

                        dir_x = np.array(V[2]).astype(np.float64)[0][0]
                        dir_y = np.array(V[2]).astype(np.float64)[1][0]
                        dir_z = np.array(V[2]).astype(np.float64)[2][0]

                        v = [magni *dir_x+p_x ,magni*dir_y+p_y,magni*dir_z+p_z]

                        xe.append(p_x)
                        ye.append(p_y)
                        ze.append(p_z)


                        xe.append(v[0])
                        ye.append(v[1])
                        ze.append(v[2])
                        l.append(V)
        
        if type(V) == str:
            
            P = extraer(V)

            d = -1*P[3]
            xe.append(d/(P[0]+0.1))
            ye.append(d/(P[1]+0.1))
            ze.append(d/(P[2]+0.1))

            xe.append(P[0])
            ye.append(P[1])
            ze.append(P[2])

            ze.append(d)
            l.append(V)

        if type(V) == dict:

            l.append(V)

            if "t" in (str(V[x]) + str(V[y]) + str(V[z])):
                
                if len(V) == 3:
                    
                    xi = extraepun(V[x])
                    yi = extraepun(V[y])
                    zi = extraepun(V[z])

                    a = extraevec(V[x])
                    b = extraevec(V[y])
                    c = extraevec(V[z])
                    
                    xe.append(xi)
                    ye.append(yi)
                    ze.append(zi)

                    xe.append(xi + a)
                    xe.append(yi + b)
                    xe.append(zi + c)

                    l.append(V)

                    escala = (max(xe)+max(ye)+max(ze))/10

                    tiempo = abs(escala)

                    xe.append(sust(V[x],tiempo))
                    ye.append(sust(V[y],tiempo))
                    ze.append(sust(V[z],tiempo))

                    xe.append(sust(V[x],-1*tiempo))
                    ye.append(sust(V[y],-1*tiempo))
                    ze.append(sust(V[x],-1*tiempo))

                if len(V) == 4:
                    
                    tiempo = abs(float(V[t]))

                    xi = extraepun(V[x])
                    yi = extraepun(V[y])
                    zi = extraepun(V[z])

                    a = extraevec(V[x])
                    b = extraevec(V[y])
                    c = extraevec(V[z])

                    l.append(V)
                    
                    xe.append(xi)
                    ye.append(yi)
                    ze.append(zi)

                    xe.append(xi + a)
                    ye.append(yi + b)
                    ze.append(zi + c)

                    xe.append(sust(V[x],tiempo))
                    ye.append(sust(V[y],tiempo))
                    ze.append(sust(V[z],tiempo))

                    xe.append(sust(V[x],-1*tiempo))
                    ye.append(sust(V[y],-1*tiempo))
                    ze.append(sust(V[z],-1*tiempo))

            if (V[x] + V[y] + V[z]) == int or (V[x] + V[y] + V[z]) == float:
                
                xe.append(V[x])
                ye.append(V[y])
                ze.append(V[z])

                l.append(V)

    escala = (max(xe)+max(ye)+max(ze))/30

    lp   = listaplanos(l)
    lr   = listarectas(l)
    lpun = listapuntos(l)

    
    for V in args:
        
        if type(V)==type(Ma) and len(V) == 3:
            
            v = matrixtolist(V)

            a = v[0]
            b = v[1]
            c = v[2]

            color = randomRgbaColor()
            vector = go.Scatter3d( 
            x = [0,a],
            y = [0,b],
            z = [0,c],
            marker = dict( size = 1,color= color),
            line = dict( color= color, width = 7),name="vector "+ str(args.index(V)+1))
            
            paleta = [[0, color],[1, color]]

            cono = go.Cone(x=[a], y=[b], z=[c], u=[a], v=[b], w=[c],sizemode="absolute",sizeref=escala,anchor="cm",
            showscale=False,
            colorscale=paleta,
            colorbar=dict(thickness=20, ticklen=4),
            name="vector "+ str(args.index(V)+1))
            
            data += [vector,cono]
            layout = go.Layout(margin = dict( l = 0,r = 0,b = 0,t = 0))

        if type(V) == type(ecuacion): 

            P = ecualist(V)


            if P[2] != 0:

                
                X = np.linspace(min(xe)-0.5,max(xe)+0.5,20)
                Y = np.linspace(min(ye)-0.5,max(ye)+0.5,20)
                x_p,y_p = np.meshgrid(X,Y)
                d = P[3]
                z_p = (-P[0]/P[2])*x_p+(-P[1]/P[2])*y_p + d/P[2]

                color = randomRgbaColor()
                paleta = [[0, color],[1, color]]
                nombre =  nom(V)
                
                
                plane = go.Surface(x=x_p, y=y_p, z=z_p, showscale=False,
                colorscale=paleta,
                opacity = 0.7,
                #surfacecolor = color,
                hoverinfo = "name + text",
                hovertext = nombre,
                colorbar=dict(thickness=20, ticklen=4),
                name= 'plano ' + str(lp.index(V)+1))
                
                
                data += [plane]
                layout = go.Layout(margin = dict( l = 0,r = 0,b = 0,t = 0))

            if  P[2]== 0 and P[1] != 0:

                X = np.linspace(min(xe)-0.5,max(xe)+0.5,20)
                Z = np.linspace(min(ze)-0.5,max(ze)+0.5,20)
                x_p,z_p = np.meshgrid(X,Z)
                d = P[3]
                y_p = (-P[0]/P[1])*x_p+ + d/P[1]

                color = randomRgbaColor()
                paleta = [[0, color],[1, color]]
                nombre =  nom(V)
                
                
                plane = go.Surface(x=x_p, y=y_p, z=z_p, showscale=False,
                colorscale=paleta,
                opacity = 0.7,
                #surfacecolor = color,
                hoverinfo = "name + text",
                hovertext = nombre,
                colorbar=dict(thickness=20, ticklen=4),
                name="plano "+ str(lp.index(V)+1))
                
                data += [plane]
                layout = go.Layout(margin = dict( l = 0,r = 0,b = 0,t = 0))
            
            if  P[2]== 0 and P[1] == 0:

                Y = np.linspace(min(xe)-0.5,max(xe)+0.5,20)
                Z = np.linspace(min(ze)-0.5,max(ze)+0.5,20)
                y_p,z_p = np.meshgrid(Y,Z)
                d = P[3]
                x_p = (-P[0]/P[0])*y_p+ + d/P[0]

                color = randomRgbaColor()
                paleta = [[0, color],[1, color]]
                nombre = nom(V)
                
                
                plane = go.Surface(x=x_p, y=y_p, z=z_p, showscale=False,
                colorscale=paleta,
                opacity = 0.7,
                #surfacecolor = color,
                hoverinfo = "name + text",
                hovertext = nombre,
                colorbar=dict(thickness=20, ticklen=4),
                name="plano "+ str(lp.index(V)+1) )
                
                data += [plane]
                layout = go.Layout(margin = dict( l = 0,r = 0,b = 0,t = 0))
        
        if type(V) == tuple:

            a = V[0]
            b = V[1]
            c = V[2]

            color = randomRgbaColor()
        
            point = go.Scatter3d( x = [a],y = [b],z = [c], mode='markers',marker=dict(color= color,size=5),showlegend=True,name= "punto"+ str(lpun.index(V)+1))
            data += [point]
            layout = go.Layout(margin = dict( l = 0,r = 0,b = 0,t = 0))
    
        if type(V) == list:

            if type(V[0]) == str:

                lista_x = extra(V[0])
                lista_y = extra(V[1])
                lista_z = extra(V[2])

                color = randomRgbaColor()
                nombre = "x = " + V[0]+ ", " + "y = " + V[1] +  ", " + "z = " + V[2]

                P = [lista_x[0]*(-1*tiempo)+lista_x[1],lista_y[0]*(-1*tiempo)+lista_y[1],lista_z[0]*(-1*tiempo)+lista_z[1]]
                Q = [lista_x[0]*tiempo+lista_x[1],lista_y[0]*tiempo+lista_y[1],lista_z[0]*tiempo+lista_z[1]]

                linea = go.Scatter3d(x = [P[0],Q[0]],
                    y =  [P[1],Q[1]],
                    z =  [P[2],Q[2]],
                    hoverinfo = "name + text",
                    hovertext = nombre,
                    marker = dict( size = 1,color= color ),
                    line = dict( color= color , width = 4),name="recta "+ str(lr.index(V)+1))
                
                data += [linea]
                
                layout = go.Layout(margin = dict( l = 0,r = 0,b = 0,t = 0))
            
            elif type(V[0]) == int or type(V[0]) == float :
                
                if type(V[1]) == int or type(V[1]) == float:
                    
                    xe.append(V[0])
                    ye.append(V[1])
                    ze.append(V[2])
                    color = randomRgbaColor()
                    vector = go.Scatter3d( 
                    x = [0,V[0]],
                    y = [0,V[1]],
                    z = [0,V[2]],
                    marker = dict( size = 1,color= color),
                    line = dict( color= color, width = 7),name="vector "+ str(args.index(V)+1))
                
                    paleta = [[0, color],[1, color]]

                    cono = go.Cone(x=[V[0]], y=[V[1]], z=[V[2]], u=[V[0]], v=[V[1]], w=[V[2]],sizemode="absolute",sizeref=escala,anchor="cm",
                    showscale=False,
                    colorscale=paleta,
                    colorbar=dict(thickness=20, ticklen=4),
                    name="vector "+ str(args.index(V)+1))
                
                    data += [vector,cono]
                    layout = go.Layout(margin = dict( l = 0,r = 0,b = 0,t = 0))

                if type(V[1]) == list :

                    magni = V[0]

                    dir_x = V[1][0]
                    dir_y = V[1][1]
                    dir_z = V[1][2]

                    v = [magni *dir_x,magni*dir_y,magni*dir_z]

                    color = randomRgbaColor()
                    vector = go.Scatter3d( 
                    x = [0,v[0]],
                    y = [0,v[1]],
                    z = [0,v[2]],
                    marker = dict( size = 1,color= color),
                    line = dict( color= color, width = 7),name="vector "+ str(args.index(V)+1))
                    
                    paleta = [[0, color],[1, color]]

                    cono = go.Cone(x=[v[0]], y=[v[1]], z=[v[2]], u=[v[0]], v=[v[1]], w=[v[2]],sizemode="absolute",sizeref= escala,anchor="cm",
                        showscale=False,
                        colorscale=paleta,
                        colorbar=dict(thickness=20, ticklen=4),
                        name="vector "+ str(args.index(V)+1))
                    
                    data += [vector,cono]
                    layout = go.Layout(margin = dict( l = 0,r = 0,b = 0,t = 0))
                
                if type(V[1]) != list and type(V[1]) != int and type(V[1]) != float :

                    magni = V[0]

                    dir_x = np.array(V[1]).astype(np.float64)[0][0]
                    dir_y = np.array(V[1]).astype(np.float64)[1][0]
                    dir_z = np.array(V[1]).astype(np.float64)[2][0]

                    v = [magni *dir_x,magni*dir_y,magni*dir_z]

                    color = randomRgbaColor()
                    vector = go.Scatter3d( 
                    x = [0,v[0]],
                    y = [0,v[1]],
                    z = [0,v[2]],
                    marker = dict( size = 1,color= color),
                    line = dict( color= color, width = 7),name="vector "+ str(args.index(V)+1))
                    
                    paleta = [[0, color],[1, color]]

                    cono = go.Cone(x=[v[0]], y=[v[1]], z=[v[2]], u=[v[0]], v=[v[1]], w=[v[2]],sizemode="absolute",sizeref= escala,anchor="cm",
                        showscale=False,
                        colorscale=paleta,
                        colorbar=dict(thickness=20, ticklen=4),
                        name="vector "+ str(args.index(V)+1))
                    
                    data += [vector,cono]
                    layout = go.Layout(margin = dict( l = 0,r = 0,b = 0,t = 0))

                    
            elif  type(V[0]) == tuple:

                if  len(V)==2:

                    if  type(V[1]) == tuple:
                        
                        xe.append(V[0][0])
                        xe.append(V[1][0])

                        ye.append(V[0][1])
                        ye.append(V[1][1])

                        ze.append(V[0][2])
                        ze.append(V[1][2])

                        nombre = "Tail"+ "=" + "(" + str(V[0][0])  + "," + str(V[0][1]) +"," +str(V[0][2]) + ")" + "\n" + "Head"+ "=" + "(" + str(V[1][0])  + "," + str(V[1][1]) +"," +str(V[1][2]) + ")"

                        color = randomRgbaColor()
                        vector = go.Scatter3d( 
                        x = [V[0][0],V[1][0]],
                        y = [V[0][1],V[1][1]],
                        z = [V[0][2],V[1][2]],
                        hoverinfo = "name + text",
                        hovertext = nombre,
                        marker = dict( size = 1,color= color),
                        line = dict( color= color, width = 7),name="vector "+ str(args.index(V)+1))
                    
                        paleta = [[0, color],[1, color]]

                        cono = go.Cone(x=[V[1][0]-0.0063*(V[1][0]-V[0][0])], y=[V[1][1]-0.0063*(V[1][1]-V[0][1])], z=[V[1][2]-0.0063*(V[1][2]-V[0][2])], u=[0.5*(V[1][0]-V[0][0])], v=[0.5*(V[1][1]-V[0][1])], w=[0.5*(V[1][2]-V[0][2])],sizemode="absolute",sizeref=escala,anchor="cm",
                        showscale=False,
                        colorscale=paleta,
                        hoverinfo = "skip",
                        colorbar=dict(thickness=20, ticklen=4),
                        name="vector "+ str(args.index(V)+1))
                    
                        data += [vector,cono]
                        layout = go.Layout(margin = dict( l = 0,r = 0,b = 0,t = 0))


                    if  type(V[1]) == list:

                        xe.append(V[0][0])
                        xe.append(V[0][0]+V[1][0])

                        ye.append(V[0][1])
                        ye.append(V[0][1]+V[1][1])

                        ze.append(V[0][2])
                        ze.append(V[0][2]+V[1][2])

                        nombre = "Tail"+ "=" + "(" + str(V[0][0])  + "," + str(V[0][1]) +"," +str(V[0][2]) + ")" + "\n" + "Head"+ "=" + "(" + str(V[0][0]+V[1][0])  + "," + str(V[0][1]+V[1][1]) +"," +str(V[0][2]+V[1][2]) + ")"

                        color = randomRgbaColor()
                        vector = go.Scatter3d( 
                        x = [V[0][0],V[0][0]+V[1][0]],
                        y = [V[0][1],V[0][1]+V[1][1]],
                        z = [V[0][2],V[0][2]+V[1][2]],
                        hoverinfo = "name + text",
                        hovertext = nombre,
                        marker = dict( size = 1,color= color),
                        line = dict( color= color, width = 7),name="vector "+ str(args.index(V)+1))
                    
                        paleta = [[0, color],[1, color]]

                        cono = go.Cone(x=[(V[0][0]+V[1][0])-0.063*((V[0][0]+V[1][0])-V[0][0])], y=[(V[0][1]+V[1][1])-0.063*((V[0][1]+V[1][1])-V[0][1])], z=[(V[0][2]+V[1][2])-0.063*((V[0][2]+V[1][2])-V[0][2])], u=[0.5*((V[0][0]+V[1][0])-V[0][0])], v=[0.5*((V[0][1]+V[1][1])-V[0][1])], w=[0.5*((V[0][2]+V[1][2])-V[0][2])],sizemode="absolute",sizeref=escala,anchor="cm",
                        showscale=False,
                        colorscale=paleta,
                        hoverinfo = "skip",
                        colorbar=dict(thickness=20, ticklen=4),
                        name="vector "+ str(args.index(V)+1))
                    
                        data += [vector,cono]
                        layout = go.Layout(margin = dict( l = 0,r = 0,b = 0,t = 0))
                    
                    if  type(V[1]) != list and type(V[1]) != tuple:
                        
                        a = np.array(V[1]).astype(np.float64).tolist()[0][0]
                        b = np.array(V[1]).astype(np.float64).tolist()[1][0]
                        c = np.array(V[1]).astype(np.float64).tolist()[2][0]

                        xe.append(V[0][0])
                        xe.append(V[0][0]+a)

                        ye.append(V[0][1])
                        ye.append(V[0][1]+b)

                        ze.append(V[0][2])
                        ze.append(V[0][2]+c)

                        nombre = "Tail"+ "=" + "(" + str(V[0][0])  + "," + str(V[0][1]) +"," +str(V[0][2]) + ")" + "\n" + "Head"+ "=" + "(" + str(V[0][0]+a)  + "," + str(V[0][1]+b) +"," +str(V[0][2]+c) + ")"

                        color = randomRgbaColor()
                        vector = go.Scatter3d( 
                        x = [V[0][0],V[0][0]+a],
                        y = [V[0][1],V[0][1]+b],
                        z = [V[0][2],V[0][2]+c],
                        hoverinfo = "name + text",
                        hovertext = nombre,
                        marker = dict( size = 1,color= color),
                        line = dict( color= color, width = 7),name="vector "+ str(args.index(V)+1))
                    
                        paleta = [[0, color],[1, color]]

                        cono = go.Cone(x=[(V[0][0]+a)-0.063*((V[0][0]+a)-V[0][0])], y=[(V[0][1]+b)-0.063*((V[0][1]+b)-V[0][1])], z=[(V[0][2]+c)-0.063*((V[0][2]+c)-V[0][2])], u=[0.5*((V[0][0]+a)-V[0][0])], v=[0.5*((V[0][1]+b)-V[0][1])], w=[0.5*((V[0][2]+c)-V[0][2])],sizemode="absolute",sizeref=escala,anchor="cm",
                        showscale=False,
                        colorscale=paleta,
                        hoverinfo = "skip",
                        colorbar=dict(thickness=20, ticklen=4),
                        name="vector "+ str(args.index(V)+1))
                
                        data += [vector,cono]
                        layout = go.Layout(margin = dict( l = 0,r = 0,b = 0,t = 0))

                else:
                    
                    if  type(V[2]) == list:
                        
                        p_x = V[0][0]
                        p_y = V[0][1]
                        p_z = V[0][2]


                        magni = V[1]

                        dir_x = V[2][0]
                        dir_y = V[2][1]
                        dir_z = V[2][2]

                        v = [magni *dir_x+p_x ,magni*dir_y+p_y,magni*dir_z+p_z]

                        xe.append(p_x)
                        ye.append(p_y)
                        ze.append(p_z)


                        xe.append(v[0])
                        ye.append(v[1])
                        ze.append(v[2])

                        nombre = "Tail"+ "=" + "(" + str(V[0][0])  + "," + str(V[0][1]) +"," +str(V[0][2]) + ")" + "\n" + "Head"+ "=" + "(" + str(v[0])  + "," + str(v[1]) +"," +str(v[2]) + ")"

                        color = randomRgbaColor()
                        vector = go.Scatter3d( 
                        x = [p_x,v[0]],
                        y = [p_y,v[1]],
                        z = [p_z,v[2]],
                        hoverinfo = "name + text",
                        hovertext = nombre,
                        marker = dict( size = 1,color= color),
                        line = dict( color= color, width = 7),name="vector "+ str(args.index(V)+1))
                        
                        paleta = [[0, color],[1, color]]

                        cono = go.Cone(x=[v[0]-0.063*(v[0]-p_x)], y=[v[1]-0.063*(v[1]-p_y)], z=[v[2]-0.063*(v[2]-p_z)], u=[0.5*(v[0]-p_x)], v=[0.5*(v[1]-p_y)], w=[0.5*(v[2]-p_z)],sizemode="absolute",sizeref=escala,anchor="cm",
                            showscale=False,
                            colorscale=paleta,
                            hoverinfo = "skip",
                            colorbar=dict(thickness=20, ticklen=4),
                            name="vector "+ str(args.index(V)+1))
                        
                        data += [vector,cono]
                        layout = go.Layout(margin = dict( l = 0,r = 0,b = 0,t = 0))

                    if  type(V[2]) != list and  type(V[2]) != tuple:
                        
                        p_x = V[0][0]
                        p_y = V[0][1]
                        p_z = V[0][2]


                        magni = V[1]

                        dir_x = np.array(V[2]).astype(np.float64)[0][0]
                        dir_y = np.array(V[2]).astype(np.float64)[1][0]
                        dir_z = np.array(V[2]).astype(np.float64)[2][0]

                        v = [magni *dir_x+p_x ,magni*dir_y+p_y,magni*dir_z+p_z]

                        xe.append(p_x)
                        ye.append(p_y)
                        ze.append(p_z)


                        xe.append(v[0])
                        ye.append(v[1])
                        ze.append(v[2])

                        nombre = "Tail"+ "=" + "(" + str(V[0][0])  + "," + str(V[0][1]) +"," +str(V[0][2]) + ")" + "\n" + "Head"+ "=" + "(" + str(v[0])  + "," + str(v[1]) +"," +str(v[2]) + ")"

                        color = randomRgbaColor()
                        vector = go.Scatter3d( 
                        x = [p_x,v[0]],
                        y = [p_y,v[1]],
                        z = [p_z,v[2]],
                        hoverinfo = "name + text",
                        hovertext = nombre,
                        marker = dict( size = 1,color= color),
                        line = dict( color= color, width = 7),name="vector "+ str(args.index(V)+1))
                        
                        paleta = [[0, color],[1, color]]

                        cono = go.Cone(x=[v[0]-0.063*(v[0]-p_x)], y=[v[1]-0.063*(v[1]-p_y)], z=[v[2]-0.063*(v[2]-p_z)], u=[0.5*(v[0]-p_x)], v=[0.5*(v[1]-p_y)], w=[0.5*(v[2]-p_z)],sizemode="absolute",sizeref=escala,anchor="cm",
                            showscale=False,
                            colorscale=paleta,
                            hoverinfo = "skip",
                            colorbar=dict(thickness=20, ticklen=4),
                            name="vector "+ str(args.index(V)+1))
                        
                        data += [vector,cono]
                        layout = go.Layout(margin = dict( l = 0,r = 0,b = 0,t = 0))

        if type(V) == str:

            P = extraer(V)

            if P[2] != 0:
                X_m = np.linspace(min(xe)-0.5,max(xe)+0.5,20)
                Y_m = np.linspace(min(ye)-0.5,max(ye)+0.5,20)
                x_p,y_p = np.meshgrid(X_m,Y_m)
                d = -1*P[3]
                z_p = (-P[0]/P[2])*x_p+(-P[1]/P[2])*y_p + d/P[2]

                color = randomRgbaColor()
                paleta = [[0, color],[1, color]]
                nombre = V
                    
                    
                plane = go.Surface(x=x_p, y=y_p, z=z_p, showscale=False,
                colorscale=paleta,
                opacity = 0.7,
                #surfacecolor = color,
                hoverinfo = "name + text",
                hovertext = nombre,
                colorbar=dict(thickness=20, ticklen=4),name="plano "+ str(lp.index(V)+1))

                data += [plane]
                layout = go.Layout(margin = dict( l = 0,r = 0,b = 0,t = 0))
                
            if  P[2]== 0 and P[1] != 0:

                X_m = np.linspace(min(xe)-0.5,max(xe)+0.5,20)
                Z_m = np.linspace(min(ze)-0.5,max(ze)+0.5,20)
                x_p,z_p = np.meshgrid(X_m,Z_m)
                d = -1*P[3]
                y_p = (-P[0]/P[1])*x_p+ + d/P[1]

                color = randomRgbaColor()
                paleta = [[0, color],[1, color]]
                nombre = V
                    
                    
                plane = go.Surface(x=x_p, y=y_p, z=z_p, showscale=False,
                colorscale=paleta,
                opacity = 0.7,
                #surfacecolor = color,
                hoverinfo = "name + text",
                hovertext = nombre,
                colorbar=dict(thickness=20, ticklen=4),
                name="plano "+ str(lp.index(V)+1))
                    
                data += [plane]
                layout = go.Layout(margin = dict( l = 0,r = 0,b = 0,t = 0))
                
            if  P[2]== 0 and P[1] == 0:

                Y_m = np.linspace(min(xe)-0.5,max(xe)+0.5,20)
                Z_m = np.linspace(min(ze)-0.5,max(ze)+0.5,20)
                y_p,z_p = np.meshgrid(Y_m,Z_m)
                d = -1*P[3]
                x_p = (-P[0]/P[0])*y_p+ + d/P[0]

                color = randomRgbaColor()
                paleta = [[0, color],[1, color]]
                nombre = V
                    
                    
                plane = go.Surface(x=x_p, y=y_p, z=z_p, showscale=False,
                colorscale=paleta,
                opacity = 0.7,
                #surfacecolor = color,
                hoverinfo = "name + text",
                hovertext = nombre,
                colorbar=dict(thickness=20, ticklen=4),
                name="plano "+ str(lp.index(V)+1))
                    
                data += [plane]
                layout = go.Layout(margin = dict( l = 0,r = 0,b = 0,t = 0))

        if type(V)== dict:

            if "t" in (str(V[x]) + str(V[y]) + str(V[z])):
                
                color = randomRgbaColor()
                nombre = "x = " + str(V[x]).replace("*","")+ ", " + "y = " + str(V[y]).replace("*","")+", " + "z = " + str(V[z]).replace("*","")

                P = [sust(V[x],tiempo),sust(V[y],tiempo),sust(V[z],tiempo)]
                Q = [sust(V[x],-1*tiempo),sust(V[y],-1*tiempo),sust(V[z],-1*tiempo)]
                linea = go.Scatter3d(x = [P[0],Q[0]],
                    y =  [P[1],Q[1]],
                    z =  [P[2],Q[2]],
                    hoverinfo = "name + text",
                    hovertext = nombre,
                    marker = dict( size = 1,color= color ),
                    line = dict( color= color , width = 4),name="recta"+ str(lr.index(V)+1))
                
                data += [linea]
                
                layout = go.Layout(margin = dict( l = 0,r = 0,b = 0,t = 0))
            
            if type(V[x] + V[y] + V[z]) == int or type(V[x] + V[y] + V[z]) == float:
                
                
                a = V[x]
                b = V[y]
                c = V[z]

                color = randomRgbaColor()
                point = go.Scatter3d( x = [a],y = [b],z = [c], mode='markers',marker=dict(color= color,size=5),showlegend=True,name= "punto"+ str(lpun.index(V)+1))
                
                data += [point]
                layout = go.Layout(margin = dict( l = 0,r = 0,b = 0,t = 0))



    paleta2 = [[0, "#2a3f5f"],[1, "#2a3f5f"]]
    point = go.Scatter3d( x = [0],y = [0],z = [0], mode='markers',marker=dict(color= "#2a3f5f",size=5),showlegend=True,name="origen")
    
    axex = go.Scatter3d( 
        x = [min(xe)-escala, max(xe)+escala],
        y = [0,0],
        z = [0,0],
        hoverinfo = "skip",
        marker = dict( size = 1,color= "#2a3f5f"),
        line = dict( color= "#2a3f5f", width = 3), showlegend=False,name="")
    
    
    conox = go.Cone(x=[max(xe)+escala], y=[0], z=[0], u=[max(xe)+escala], v=[0], w=[0],sizemode="absolute",sizeref= escala*0.6,anchor="cm",
               showscale=False,
               colorscale=paleta2,
               hoverinfo = "name",
               colorbar=dict(thickness=20, ticklen=4),name="Eje x-positivo")
    
    axey = go.Scatter3d( 
        x = [0,0],
        y = [min(ye)-escala,max(ye)+escala],
        z = [0,0],
        hoverinfo = "skip",
        marker = dict( size = 1,color="#2a3f5f"),
        line = dict( color= "#2a3f5f", width = 3), showlegend=False,name="")
    
    conoy = go.Cone(x=[0], y=[max(ye)+escala], z=[0], u=[0], v=[max(ye)+escala], w=[0],sizemode="absolute",sizeref=escala*0.6,anchor="cm",
               showscale=False,
               colorscale=paleta2,
               hoverinfo = "name",
               colorbar=dict(thickness=20, ticklen=4),
               name="Eje y-positivo ")
    
    axez = go.Scatter3d( 
        x = [0,0],
        y = [0,0],
        z = [min(ze)-escala,max(ze)+escala],
        hoverinfo = "skip",
        marker = dict( size = 1,color= "#2a3f5f"),
        line = dict( color= "#2a3f5f", width = 3), showlegend=False,name="eje z-positivo")
    
    conoz = go.Cone(x=[0], y=[0], z=[max(ze)+escala], u=[0], v=[0], w=[max(ze)+escala],sizemode="absolute",sizeref=escala*0.6,anchor="cm",
               showscale=False,
               colorscale=paleta2,
               hoverinfo= "name",
               colorbar=dict(thickness=20, ticklen=4),
               name="Eje z-positivo")
    

    fig = go.Figure(data= data + [point, axex, conox, axey, conoy, axez, conoz],layout=layout)

    fig.update_traces(showlegend=True, selector=dict(type='surface'))


    fig.update_layout(legend=dict(orientation="h",y=1.3,x=0.03),title_font=dict(size=50, color='rgb(1,21,51)'),showlegend=True,width=480, height=480)

    plt(fig,image_height=800,image_width=800)
    fig.show()
