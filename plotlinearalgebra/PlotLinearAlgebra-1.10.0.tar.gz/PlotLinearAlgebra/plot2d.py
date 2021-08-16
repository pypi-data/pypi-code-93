# -*- coding: utf-8 -*-

import plotly.graph_objects as go
from plotly.offline import plot
import numpy as np
from sympy import *
import random 
import re as rep
import math


x,y,w= symbols("x y w")



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


def extraerl(cadena):

    if cadena[-3] != "x" and cadena[-3] != "y" :
        
        if "x" not in cadena and "y" in cadena :
            segundo = rep.split("y",cadena) 
            tercero =  rep.split("=",segundo[1])
            return [0,conv(segundo[0]),conv(tercero[0])]
            
        if "x" in cadena and "y" not in cadena:
            primero = rep.split("x",cadena)
            tercero =  rep.split("=",primero[1])
            return [conv(primero[0]),0,conv(tercero[0])]
            
        if "x" in cadena and "y" in cadena :
            primero = rep.split("x",cadena)
            segundo = rep.split("y",primero[1]) 
            tercero =  rep.split("=",segundo[1])
            return [conv(primero[0]),conv(segundo[0]),conv(tercero[0])]

    else:

        if "x" not in cadena and "y" in cadena:
            segundo = rep.split("y",cadena) 
            return [0,conv(segundo[0]),0]
            
        if "x" in cadena and "y" not in cadena:
            primero = rep.split("x",cadena)
            return [conv(primero[0]),0,0]
            
        if "x" in cadena and "y" in cadena :
            primero = rep.split("x",cadena)
            segundo = rep.split("y",primero[1]) 
            return [conv(primero[0]),conv(segundo[0]),0]

def ecualistrec(ecua):

    ecuacion = Eq(1*w,3)


    if type(ecua)==type(ecuacion):

        ecu1 = str(ecua)[3:-1]
        cadena1 = rep.split(",",ecu1)[0]
        cadena2 = rep.split(",",ecu1)[1]

        ecua_sim = str(simplify(ecua))[3:-1]
        cadena3 = rep.split(",",ecua_sim)[0]
        cadena4 = rep.split(",",ecua_sim)[1]


        if "x" not in cadena1 and "y" in cadena1 :

            if conv(cadena2) != 0:
                segundo = rep.split("y",cadena3) 
                return [0,convierte(segundo[0]),conv(cadena4)]

            if conv(cadena2) == 0:
                segundo = rep.split("y",cadena3)
                return [0,convierte(segundo[0]),0] 

        
        if "x" in cadena1 and "y" not in cadena1:

            if conv(cadena2) != 0:
                primero = rep.split("x",cadena3)
                return [convierte(primero[0]),0,conv(cadena4)]

            if conv(cadena2) == 0:
                primero = rep.split("x",cadena3)
                return  [convierte(primero[0]),0,0]


        if "x" in cadena1 and "y" in cadena1 :

            if conv(cadena2) != 0:
                primero = rep.split("x",cadena3)
                segundo = rep.split("y",primero[1])
                return [convierte(primero[0]),convierte(segundo[0]),conv(cadena4)]

            if conv(cadena2) == 0:
                primero = rep.split("x",cadena3)
                segundo = rep.split("y",cadena4)
                return  [convierte(primero[0]),-1*convierte(segundo[0]),0]



def randomRgbaColor(): 
   r = random.randrange(0, 255) 
   g = random.randrange(0, 255)  
   b =random.randrange(0, 255)
   return "rgb"+ "(" + str(r) + "," + str(g) + ","+ str(b) + ")"


def listavectores(lista):
    vectores = []
    Ma = Matrix([2])
    for elemen in lista:
        if type(elemen) == list or type(elemen) == type(Ma):
            vectores.append(elemen)
    return vectores


def listarectas(lista):
    rectas = []
    ecuacion = Eq(1*w,3)
    for elemen in lista:
        if type(elemen) == str or type(elemen) == type(ecuacion): 
            rectas.append(elemen)
        if type(elemen) == dict and ("t" in (str(elemen[x])+str(elemen[y]))):
            rectas.append(elemen)
    return rectas

def listapuntos(lista):
    puntos = []
    for elemen in lista:
        if type(elemen) == tuple:
            puntos.append(elemen)
        if type(elemen) == dict and (type(elemen[x] + elemen[y]) == int or type(elemen[x] + elemen[y]) == float):
            puntos.append(elemen)
    return puntos


def nom(ecua):
    cadena  = str(ecua)[3:-1]
    cadena1 = cadena.replace(",", " =")
    cadena2 = cadena1.replace("*", "")
    return cadena2


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


def paralist(diccio):
    a = extraevec(diccio[x])
    b = extraepun(diccio[x])
    c = extraevec(diccio[y])
    d = extraepun(diccio[y])
    lista = [c,-1*a,d*a-b*c]
    return lista



def plot2D(*args):

    """Función elaborada  con la  librería Plotly y NumPy, compatible con la librería Sympy  para visualizar
    puntos,rectas y vectores en el plano"""

    ecuacion = Eq(1*w,3)
    Ma = Matrix([2])

    xe = [0.5,-0.5] 
    ye = [0.5,-0.5]

    l = []

    for V in args:

        # plotvector2D([x])

        if type(V) == list:
            
            if len(V) == 1:
                
                xe.append(V[0])
                ye.append(0)
                l.append(V)

            if type(V[0]) == int or type(V[0]) == float:

                # plotvector2D([x1,y1])
                if  type(V[1]) == int or type(V[1]) == float:

                    xe.append(V[0])
                    ye.append(V[1])
                    l.append(V)

                if  type(V[1]) == str:
                    
                    # plotvector2D([a,"b"])
                    r = V[0]
                    theta_str = V[1]
                    theta = math.radians(float(theta_str[:]))

                    coor1 = round(r*math.cos(theta),3)
                    coor2 = round(r*math.sin(theta),3)
                    xe.append(coor1)
                    ye.append(coor2)
                    l.append(V)                                               
                
            if  type(V[0]) == tuple:

                # plotvector2D([(x0,y0),a,"b"])

                if  type(V[1]) == int or type(V[1]) == float:
                    
                    p_x = V[0][0]
                    p_y = V[0][1]

                    r = V[1]
                    theta_str = V[2]
                    theta = math.radians(float(theta_str[:]))

                    coor1 = round(r*math.cos(theta),3)
                    coor2 = round(r*math.sin(theta),3)

                    xe.append(coor1 + p_x)
                    xe.append(p_x)
                    ye.append(coor2 + p_y)
                    ye.append(p_y)

                    l.append(V)

                if type(V[1]) == list:

                    # plotvector2D([(x0,y0),[x]])
                    if len(V[1])==1:
                        
                        color = randomRgbaColor()
                        xe.append(V[0][0])
                        xe.append(V[1][0]+V[0][0])
                        ye.append(V[1][0])
                        ye.append(0+V[0][1])

                        l.append(V)

                    else:
                        # plotvector2D([(x0,y0),[x,y]])
                        xe.append(V[0][0])
                        xe.append(V[1][0]+V[0][0])
                        ye.append(V[1][0])
                        ye.append(V[1][1]+V[0][1])

                        l.append(V)

                # plotvector2D([(x1,y1),(x2,y2)])
                if type(V[1]) == tuple:
                    
                    xe.append(V[0][0])
                    xe.append(V[1][0])
                    ye.append(V[0][1])
                    ye.append(V[1][1])

                    l.append(V)
                    
                    
                if type(V[1]) != list and type(V[1]) != tuple and type(V[1]) != int and type(V[1]) != float:

                    # plotvector2D([(x0,y0),A]) A = Matrix([x])
                    if len(V[1])== 1:
    
                        a = np.array(V[1]).astype(np.float64).tolist()[0][0]
                        b = 0
                        xe.append(V[0][0])
                        xe.append(a+V[0][0])
                        ye.append(V[0][1])
                        ye.append(b+V[0][1])
                        l.append(V)

                    else:

                        # plotvector2D([(x0,y0),A]) A = Matrix([x,y])
                        a = np.array(V[1]).astype(np.float64).tolist()[0][0]
                        b = np.array(V[1]).astype(np.float64).tolist()[1][0]
                        xe.append(V[0][0])
                        xe.append(a+V[0][0])
                        ye.append(V[0][1])
                        ye.append(b+V[0][1])
                        l.append(V)
     

        if type(V) == type(Ma):
            
            # plotvector2D(A) A = Matrix([x])
            if len(V) == 1:
                a = np.array(V).astype(np.float64).tolist()[0][0]
                b = 0
                xe.append(a)
                ye.append(b)
                l.append(V)

            else:

                # plotvector2D(A) A = Matrix([x,y])
                a = np.array(V).astype(np.float64).tolist()[0][0]
                b = np.array(V).astype(np.float64).tolist()[1][0]
                xe.append(a)
                ye.append(b)
                l.append(V)

        if type(V) == str:
            
            R = extraerl(V)

            if R[0] == 0:
                Cx = [2,0]
                Cy = [0,-R[2]/R[1]]

            if R[1] == 0:
                
                Cx = [-R[2]/R[0],0]
                Cy = [0,2]

            if R[0] != 0 and R[1] != 0:
                        
                Cx = [-R[2]/R[0],0]
                Cy = [0,-R[2]/R[1]] 
                
            xe.append(Cx[0])
            ye.append(Cy[1])
            l.append(V)

        if type(V) == type(ecuacion):
            
            R = ecualistrec(V)

            if R[0] == 0:
                
                Cx = [2,0]
                Cy = [0,R[2]/R[1]]

            if R[1] == 0:
                
                Cx = [R[2]/R[0],0]
                Cy = [0,2]

            if R[0] != 0 and R[1] != 0:
                        
                Cx = [R[2]/R[0],0]
                Cy = [0,R[2]/R[1]] 
                
            xe.append(Cx[0])
            ye.append(Cy[1])
            l.append(V)

        if type(V) == tuple:

            xe.append(V[0])
            ye.append(V[1])
            l.append(V)

        if type(V) == dict:
            
            R = paralist(V)

            if R[0] == 0 and R[1] != 0:
                Cx = [2,0]
                Cy = [0,-R[2]/R[1]]

                xe.append(Cx[0])
                ye.append(Cy[1])
                l.append(V)

            if R[1] == 0 and R[0] != 0:
                
                Cx = [-R[2]/R[0],0]
                Cy = [0,2]

                xe.append(Cx[0])
                ye.append(Cy[1])
                l.append(V)

            if R[0] != 0 and R[1] != 0:
                        
                Cx = [-R[2]/R[0],0]
                Cy = [0,-R[2]/R[1]]

                xe.append(Cx[0])
                ye.append(Cy[1])
                l.append(V)
            
            if R[0] == 0 and R[1] == 0:
                
                Pun = [float(V[x]),float(V[y])]
                xe.append(Pun[0])
                ye.append(Pun[1])
                l.append(V)



    minx = min(xe)-0.5
    maxx = max(xe)+0.5
    miny = min(ye)-0.5
    maxy = max(ye)+0.5


    lv   = listavectores(l)
    lr   = listarectas(l)
    lpun = listapuntos(l)
                
    fig = go.Figure()

    for V in args:

        #nombre = "vector " + str(args.index(V)+1)

        if type(V) == list:
            
            if len(V) == 1:

                # plotvector2D([x])
                
                nombre = "vector " + str(lv.index(V)+1)

                color = randomRgbaColor()
                #fig.add_trace(go.Scatter(x=[V[0]],y=[V[1]],mode='markers',marker=dict(color= color,size=3),showlegend=True,name=nombre))
                fig.add_trace(go.Scatter(x=[0,V[0]], y=[0,0],mode='lines',marker=dict(color= color,size=8),showlegend=True,name= nombre))
                fig.add_annotation(
                x=V[0],  # Coordenada en x cabeza
                y=0,  # Coordenada en y cabeza
                ax=0.0,  # Coordenada en x de la cola
                ay=0.0,  # Coordenada en x de la cola
                xref='x',
                yref='y',
                axref='x',
                ayref='y',
                showarrow=True,
                arrowhead=2,
                arrowsize=1.5,
                arrowwidth=2.3,
                arrowcolor = color)


            if type(V[0]) == int or type(V[0]) == float:

                # plotvector2D([x1,y1])
                
                if  type(V[1]) == int or type(V[1]) == float:
                    
                    nombre = "vector " + str(lv.index(V)+1)
                    color = randomRgbaColor()
                    #fig.add_trace(go.Scatter(x=[V[0]],y=[V[1]],mode='markers',marker=dict(color= color,size=3),showlegend=True,name=nombre))
                    fig.add_trace(go.Scatter(x=[0,V[0]], y=[0,V[1]],mode='lines',marker=dict(color= color,size=8),showlegend=True,name= nombre))
                    fig.add_annotation(
                    x=V[0],  # Coordenada en x cabeza
                    y=V[1],  # Coordenada en y cabeza
                    ax=0.0,  # Coordenada en x de la cola
                    ay=0.0,  # Coordenada en x de la cola
                    xref='x',
                    yref='y',
                    axref='x',
                    ayref='y',
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1.5,
                    arrowwidth=2.3,
                    name="Markers and Text",
                    arrowcolor = color)

                if  type(V[1]) == str:

                    # plotvector2D([a,"b"])
                    r = V[0]
                    theta_str = V[1]
                    theta = math.radians(float(theta_str[:]))

                    coor1 = round(r*math.cos(theta),3)
                    coor2 = round(r*math.sin(theta),3)

                    nombre = "vector " + str(lv.index(V)+1)
                    color = randomRgbaColor()
                    #fig.add_trace(go.Scatter(x=[V[0]],y=[V[1]],mode='markers',marker=dict(color= color,size=7),showlegend=True,name="vector "+ str(args.index(V)+1)))
                    fig.add_trace(go.Scatter(x=[0,coor1], y=[0,coor2],mode='lines',marker=dict(color= color,size=8),showlegend=True,name="vector "+ str(args.index(V)+1)))
                    fig.add_annotation(
                    x=coor1,  # Coordenada en x cabeza
                    y=coor2,  # Coordenada en y cabeza
                    ax=0.0,  # Coordenada en x de la cola
                    ay=0.0,  # Coordenada en x de la cola
                    xref='x',
                    yref='y',
                    axref='x',
                    ayref='y',
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1.5,
                    arrowwidth=2.3,
                    arrowcolor = color)                                                 
                    
            if  type(V[0]) == tuple:

                # plotvector2D([(x0,y0),a,"b"])

                if  type(V[1]) == int or type(V[1]) == float:
                    
                    p_x = V[0][0]
                    p_y = V[0][1]

                    r = V[1]
                    theta_str = V[2]
                    theta = math.radians(float(theta_str[:]))

                    coor1 = round(r*math.cos(theta),3)
                    coor2 = round(r*math.sin(theta),3)

                    nombre = "vector " + str(lv.index(V)+1)
                    color = randomRgbaColor()
                    #fig.add_trace(go.Scatter(x=[V[0]],y=[V[1]],mode='markers',marker=dict(color= color,size=7),showlegend=True,name="vector "+ str(args.index(V)+1)))
                    fig.add_trace(go.Scatter(x=[p_x,coor1+p_x], y=[p_y,coor2+p_y],mode='lines',marker=dict(color= color,size=8),showlegend=True,name="vector "+ str(args.index(V)+1)))
                    fig.add_annotation(
                    x=coor1 + p_x,  # Coordenada en x cabeza
                    y=coor2 + p_y,  # Coordenada en y cabeza
                    ax=p_x,  # Coordenada en x de la cola
                    ay=p_y,  # Coordenada en x de la cola
                    xref='x',
                    yref='y',
                    axref='x',
                    ayref='y',
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1.5,
                    arrowwidth=2.3,
                    arrowcolor = color)

                if type(V[1]) == list:

                    # plotvector2D([(x0,y0),[x]])
                    if len(V[1])==1:

                        nombre = "vector " + str(lv.index(V)+1)
                        color = randomRgbaColor()
                        #fig.add_trace(go.Scatter(x=[V[1][0]+V[0][0]],y=[V[1][1]+V[0][1]],mode='markers',marker=dict(color= color,size=3),showlegend=True,name=nombre))
                        fig.add_trace(go.Scatter(x=[V[0][0],V[0][0]+V[1][0]], y=[V[0][1],V[0][1]+0],mode='lines',marker=dict(color= color,size=8),showlegend=True,name= nombre))
                        fig.add_annotation(
                        x=V[0][0]+V[1][0],  # Coordenada en x cabeza 
                        y=V[0][1]+0,  # Coordenada en y cabeza
                        ax=V[0][0],  # Coordenada en x de la cola
                        ay=V[0][1],  # Coordenada en y de la cola
                        xref='x',
                        yref='y',
                        axref='x',
                        ayref='y',
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1.5,
                        arrowwidth=2.3,
                        arrowcolor = color)
                
                    else:

                        # plotvector2D([(x0,y0),[x,y]])
                        nombre = "vector " + str(lv.index(V)+1)
                        color = randomRgbaColor()
                        #fig.add_trace(go.Scatter(x=[V[1][0]+V[0][0]],y=[V[1][1]+V[0][1]],mode='markers',marker=dict(color= color,size=3),showlegend=True,name=nombre))
                        fig.add_trace(go.Scatter(x=[V[0][0],V[0][0]+V[1][0]], y=[V[0][1],V[0][1]+V[1][1]],mode='lines',marker=dict(color= color,size=8),showlegend=True,name= nombre))
                        fig.add_annotation(
                        x=V[0][0]+V[1][0],  # Coordenada en x cabeza 
                        y=V[0][1]+V[1][1],  # Coordenada en y cabeza
                        ax=V[0][0],  # Coordenada en x de la cola
                        ay=V[0][1],  # Coordenada en y de la cola
                        xref='x',
                        yref='y',
                        axref='x',
                        ayref='y',
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1.5,
                        arrowwidth=2.3,
                        arrowcolor = color)

                # plotvector2D([(x1,y1),(x2,y2)])
                if type(V[1]) == tuple:
                    
                    nombre = "vector " + str(lv.index(V)+1)
                    color = randomRgbaColor()
                    #fig.add_trace(go.Scatter(x=[V[1][0]],y=[V[1][1]],mode='markers',marker=dict(color= color,size=3),showlegend=True,name=nombre))
                    fig.add_trace(go.Scatter(x=[V[0][0],V[1][0]], y=[V[0][1],V[1][1]],mode='lines',marker=dict(color= color,size=8),showlegend=True,name= nombre))
                    fig.add_annotation(
                    x=V[1][0],  # Coordenada en x cabeza
                    y=V[1][1],  # Coordenada en y cabeza
                    ax=V[0][0],  # Coordenada en x de la cola
                    ay=V[0][1],  # Coordenada en y de la cola
                    xref='x',
                    yref='y',
                    axref='x',
                    ayref='y',
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1.5,
                    arrowwidth=2.3,
                    arrowcolor = color)
                    
                if type(V[1]) != list and type(V[1]) != tuple and type(V[1]) != int and type(V[1]) != float:

                    # plotvector2D([(x0,y0),A]) A = Matrix([x])
                    if len(V[1])== 1:
                        
                        nombre = "vector " + str(lv.index(V)+1)
                        color = randomRgbaColor()
                        a = np.array(V[1]).astype(np.float64).tolist()[0][0]
                        b = 0
                        #fig.add_trace(go.Scatter(x=[V[1][0]+V[0][0]],y=[V[1][1]+V[0][1]],mode='markers',marker=dict(color= color,size=3),showlegend=True,name=nombre))
                        fig.add_trace(go.Scatter(x=[V[0][0],V[0][0]+a], y=[V[0][1],V[0][1]+b],mode='lines',marker=dict(color= color,size=8),showlegend=True,name= nombre))
                        fig.add_annotation(
                        x=V[0][0]+a,  # Coordenada en x cabeza 
                        y=V[0][1]+b,  # Coordenada en y cabeza
                        ax=V[0][0],  # Coordenada en x de la cola
                        ay=V[0][1],  # Coordenada en y de la cola
                        xref='x',
                        yref='y',
                        axref='x',
                        ayref='y',
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1.5,
                        arrowwidth=2.3,
                        arrowcolor = color)

                    else:
                        # plotvector2D([(x0,y0),A]) A = Matrix([x,y])

                        nombre = "vector " + str(lv.index(V)+1)
                        color = randomRgbaColor()
                        a = np.array(V[1]).astype(np.float64).tolist()[0][0]
                        b = np.array(V[1]).astype(np.float64).tolist()[1][0]
                        #fig.add_trace(go.Scatter(x=[V[1][0]+V[0][0]],y=[V[1][1]+V[0][1]],mode='markers',marker=dict(color= color,size=3),showlegend=True,name=nombre))
                        fig.add_trace(go.Scatter(x=[V[0][0],V[0][0]+a], y=[V[0][1],V[0][1]+b],mode='lines',marker=dict(color= color,size=8),showlegend=True,name= nombre))
                        fig.add_annotation(
                        x=V[0][0]+a,  # Coordenada en x cabeza 
                        y=V[0][1]+b,  # Coordenada en y cabeza
                        ax=V[0][0],  # Coordenada en x de la cola
                        ay=V[0][1],  # Coordenada en y de la cola
                        xref='x',
                        yref='y',
                        axref='x',
                        ayref='y',
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1.5,
                        arrowwidth=2.3,
                        arrowcolor = color)

        
        if type(V) == type(Ma):
            
            # plotvector2D(A) A = Matrix([x])
            if len(V) == 1:

                nombre = "vector " + str(lv.index(V)+1)
                color = randomRgbaColor()
                a = np.array(V).astype(np.float64).tolist()[0][0]
                b = 0
                #fig.add_trace(go.Scatter(x=[a],y=[b],mode='markers',marker=dict(color= color,size=3),showlegend=True,name=nombre))
                fig.add_trace(go.Scatter(x=[0,a], y=[0,b],mode='lines',marker=dict(color= color,size=8),showlegend=True,name= nombre))
                fig.add_annotation(
                x=a,  # Coordenada en x cabeza
                y=b,  # Coordenada en y cabeza
                ax=0.0,  # Coordenada en x de la cola
                ay=0.0,  # Coordenada en x de la cola
                xref='x',
                yref='y',
                axref='x',
                ayref='y',
                showarrow=True,
                arrowhead=2,
                arrowsize=1.5,
                arrowwidth=2.3,
                arrowcolor = color)

            else:
                # plotvector2D(A) A = Matrix([x,y])

                nombre = "vector " + str(lv.index(V)+1)
                color = randomRgbaColor()
                a = np.array(V).astype(np.float64).tolist()[0][0]
                b = np.array(V).astype(np.float64).tolist()[1][0]
                #fig.add_trace(go.Scatter(x=[a],y=[b],mode='markers',marker=dict(color= color,size=3),showlegend=True,name=nombre))
                fig.add_trace(go.Scatter(x=[0,a], y=[0,b],mode='lines',marker=dict(color= color,size=8),showlegend=True,name= nombre))
                fig.add_annotation(
                x=a,  # Coordenada en x cabeza
                y=b,  # Coordenada en y cabeza
                ax=0.0,  # Coordenada en x de la cola
                ay=0.0,  # Coordenada en x de la cola
                xref='x',
                yref='y',
                axref='x',
                ayref='y',
                showarrow=True,
                arrowhead=2,
                arrowsize=1.5,
                arrowwidth=2.3,
                arrowcolor = color)

       
        #"2x+3y=5"

        if type(V) == str:

            R = extraerl(V)
            

            if R[1]!=0:

                nombre = "recta " + str(lr.index(V)+1)
                color = randomRgbaColor()
                P = [minx,((-1*R[0]*minx-1*R[2]))/R[1]]
                Q = [maxx,((-1*R[0]*maxx-1*R[2]))/R[1]]
                #fig.add_trace(go.Scatter(x=[V[0]],y=[V[1]],mode='markers',marker=dict(color= color,size=7),showlegend=True,name=nombre)
                fig.add_trace(go.Scatter(x=[P[0],Q[0]], y=[P[1],Q[1]],
                                         mode='lines',
                                         hoverinfo = "name + text",
                                         hovertext = V,
                                         marker=dict(color= color,size=9),
                                         showlegend=True,
                                         name= nombre ))

            if R[1]==0:

                nombre = "recta " + str(lr.index(V)+1)
                color = randomRgbaColor()
                P = [-R[2]/R[0],maxy]
                Q = [-R[2]/R[0],miny]
                #fig.add_trace(go.Scatter(x=[V[0]],y=[V[1]],mode='markers',marker=dict(color= color,size=7),showlegend=True,name="vector "+ str(args.index(V)+1)))
                fig.add_trace(go.Scatter(x=[P[0],Q[0]], y=[P[1],Q[1]],
                                         mode='lines',
                                         hoverinfo = "name + text",
                                         hovertext = V,
                                         marker=dict(color= color,size=9),
                                         showlegend=True,
                                         name= nombre))

        # Eq(2*x+3y,3)      
        if type(V) == type(ecuacion):
            
            R =  ecualistrec(V)
            

            if R[1]!=0:

                nombre = "recta " + str(lr.index(V)+1)
                color = randomRgbaColor()
                P = [minx,(-1*R[0]*minx + R[2])/R[1]]
                Q = [maxx,(-1*R[0]*maxx + R[2])/R[1]]
                #fig.add_trace(go.Scatter(x=[V[0]],y=[V[1]],mode='markers',marker=dict(color= color,size=7),showlegend=True,name="vector "+ str(args.index(V)+1)))
                fig.add_trace(go.Scatter(x=[P[0],Q[0]], y=[P[1],Q[1]],
                                         mode='lines',
                                         hoverinfo = "name + text",
                                         hovertext = str(nom(V)),
                                         marker=dict(color= color,size=9),
                                         showlegend=True,
                                         name=nombre))

            if R[1]==0:

                nombre = "recta " + str(lr.index(V)+1)
                color = randomRgbaColor()
                P = [R[2]/R[0],maxy]
                Q = [R[2]/R[0],miny]
                #fig.add_trace(go.Scatter(x=[V[0]],y=[V[1]],mode='markers',marker=dict(color= color,size=7),showlegend=True,name="vector "+ str(args.index(V)+1)))
                fig.add_trace(go.Scatter(x=[P[0],Q[0]], y=[P[1],Q[1]],
                                         mode='lines',
                                         hoverinfo = "name + text",
                                         hovertext = str(nom(V)),
                                         marker=dict(color= color,size=9),
                                         showlegend=True,
                                         name=nombre))
                
        # (2,3)      
        if type(V) == tuple:
 
            nombre = "punto " + str(lpun.index(V)+1)
            color = randomRgbaColor()
            #fig.add_trace(go.Scatter(x=[V[0]],y=[V[1]],mode='markers',marker=dict(color= color,size=7),showlegend=True,name="vector "+ str(args.index(V)+1)))
            fig.add_trace(go.Scatter(x=[V[0]], y=[V[1]],mode='markers',marker=dict(color= color,size=8),showlegend=True,name=nombre))


        if type(V) == dict:
            
            R = paralist(V)
            

            if R[1]!=0:

                nombre =  "x = " + str(V[x]).replace("*","")+ ", " + "y = " + str(V[y]).replace("*","")
                color = randomRgbaColor()
                P = [minx,((-1*R[0]*minx-1*R[2]))/R[1]]
                Q = [maxx,((-1*R[0]*maxx-1*R[2]))/R[1]]
                #fig.add_trace(go.Scatter(x=[V[0]],y=[V[1]],mode='markers',marker=dict(color= color,size=7),showlegend=True,name="vector "+ str(args.index(V)+1)))
                fig.add_trace(go.Scatter(x=[P[0],Q[0]], y=[P[1],Q[1]],
                                         mode='lines',
                                         hoverinfo = "name + text",
                                         hovertext = nombre,
                                         marker=dict(color= color,size=9),
                                         showlegend=True,
                                         name="recta "+ str(lr.index(V)+1)))

            if R[1]==0 and R[0]!=0:

                nombre =  "x = " + str(V[x]).replace("*","")+ ", " + "y = " + str(V[y]).replace("*","")
                color = randomRgbaColor()
                P = [-R[2]/R[0],maxy]
                Q = [-R[2]/R[0],miny]
                #fig.add_trace(go.Scatter(x=[V[0]],y=[V[1]],mode='markers',marker=dict(color= color,size=7),showlegend=True,name="vector "+ str(args.index(V)+1)))
                fig.add_trace(go.Scatter(x=[P[0],Q[0]], y=[P[1],Q[1]],
                                         mode='lines',
                                         hoverinfo = "name + text",
                                         hovertext = nombre,
                                         marker=dict(color= color,size=9),
                                         showlegend=True,
                                         name="recta "+ str(lr.index(V)+1)))
                
            if R[0] == 0 and R[1] == 0:

                P = [V[x],V[y]]
                nombre = "punto " + str(lpun.index(V)+1)
                color = randomRgbaColor()
                #fig.add_trace(go.Scatter(x=[V[0]],y=[V[1]],mode='markers',marker=dict(color= color,size=7),showlegend=True,name="vector "+ str(args.index(V)+1)))
                fig.add_trace(go.Scatter(x=[Pun[0]], y=[Pun[1]],mode='markers',marker=dict(color= color,size=8),showlegend=True,name=nombre))
            


    fig.add_trace(go.Scatter(x=[0],y=[0],mode='markers',marker=dict(color="#2a3f5f",size=9),showlegend=True,opacity=1,name="origen"))

    fig.add_annotation(ax = min(xe)-0.54, axref = 'x', ay = 0, ayref = 'y',x = max(xe)+0.5, xref = 'x', y = 0, yref = 'y',arrowwidth = 1.5, arrowhead = 2,arrowcolor = "#2a3f5f")
    fig.add_annotation(ax = 0, axref = 'x', ay = min(ye)-0.75, ayref = 'y',x = 0, xref = 'x', y = max(ye)+0.5, yref = 'y',arrowwidth = 1.5, arrowhead = 2,arrowcolor = "#2a3f5f")
    #fig.add_annotation(text=r'$x$', x=max(x)+0.5, y=-0.3, arrowhead=1, showarrow=False)
    #fig.add_annotation(text=r'$y$', x=-0.3, y=max(y)+0.5, arrowhead=1, showarrow=False)

    fig.update_xaxes(title = r'$\large{x}$', title_font=dict(size=30, family='latex', color='rgb(1,21,51)'),range = [min(xe)-0.5, max(xe)+0.5],showgrid = True) #,zerolinecolor="black" ,autorange = True
    fig.update_yaxes(title = r'$\large{y}$', title_font=dict(size=30, family='latex', color='rgb(1,21,51)'),range = [min(ye)-0.5, max(ye)+0.5],showgrid = True) #, zerolinecolor= "black" ,autorange = True
    fig.update_layout(font=dict(family="latex",size=20,color="black")) #y=1.2,x=0.03
    #fig.update_layout(title= "",title_font=dict(size=5, family='latex', color='rgb(1,21,51)'),title_x=0.5)
    fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1, itemdoubleclick ="toggle"),title_font=dict(size=30, color='rgb(1,21,51)'),showlegend=True,width=500, height=480)
    fig.show()