import plotly.graph_objects as go
from plotly.offline import plot
import numpy as np
from sympy import Matrix
import random 
import math


def randomRgbaColor(): 
   r = random.randrange(0, 255) 
   g = random.randrange(0, 255)  
   b =random.randrange(0, 255)
   return "rgb"+ "(" + str(r) + "," + str(g) + ","+ str(b) + ")"

import plotly.graph_objects as go
import numpy as np
import math
from sympy import Matrix


def plotvectors2D(*args):
    
    '''Función elaborada en el módulo Plotly y NumPy para visualizar multiples vectores en el plano cartesiano, que pueden tener 
    un punto inicial y un punto final dado, estar anclados en el origen del plano, o vectores equipolentes a otro que inicie en 
    un punto dado (traslación de vectores), y vectores en forma polar anclados en el origen o con un punto inicial dado, 
    acepta como argumentos vectores unidimensionales o bidimensionales definidos como matriz columna en la librería SymPy'''
    
    fig = go.Figure()
    x = [0]
    y = [0]
    for V in args:

        nombre = "vector "+ str(args.index(V)+1)

        # plotvector2D([x])
        if type(V)== list and len(V) == 1:

            color = randomRgbaColor()
            x.append(V[0])
            y.append(0)
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
        
        else:

             
            if (type(V[0]) == int or type(V[0]) == float):

                # plotvector2D([x1,y1])
                if  (type(V[1]) == int or type(V[1]) == float):

                    color = randomRgbaColor()
                    x.append(V[0])
                    y.append(V[1])
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

                else:

                    # plotvector2D([a,"b"])
                    r = V[0]
                    theta_str = V[1]
                    theta = math.radians(float(theta_str[:]))

                    coor1 = round(r*math.cos(theta),3)
                    coor2 = round(r*math.sin(theta),3)

                    color = randomRgbaColor()
                    x.append(coor1)
                    y.append(coor2)
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

                if  (type(V[1]) == int or type(V[1]) == float):
                    
                    p_x = V[0][0]
                    p_y = V[0][1]

                    r = V[1]
                    theta_str = V[2]
                    theta = math.radians(float(theta_str[:]))

                    coor1 = round(r*math.cos(theta),3)
                    coor2 = round(r*math.sin(theta),3)

                    color = randomRgbaColor()
                    x.append(coor1 + p_x)
                    x.append(p_x)
                    y.append(coor2 + p_y)
                    y.append(p_y)
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
                        
                        color = randomRgbaColor()
                        x.append(V[0][0])
                        x.append(V[1][0]+V[0][0])
                        y.append(V[1][0])
                        y.append(0+V[0][1])
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
                        color = randomRgbaColor()
                        x.append(V[0][0])
                        x.append(V[1][0]+V[0][0])
                        y.append(V[1][0])
                        y.append(V[1][1]+V[0][1])
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
                    
                    color = randomRgbaColor()
                    x.append(V[0][0])
                    x.append(V[1][0])
                    y.append(V[0][1])
                    y.append(V[1][1])
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
                        
                        color = randomRgbaColor()
                        a = np.array(V[1]).astype(np.float64).tolist()[0][0]
                        b = 0
                        x.append(V[0][0])
                        x.append(a+V[0][0])
                        y.append(V[0][1])
                        y.append(b+V[0][1])
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
                        color = randomRgbaColor()
                        a = np.array(V[1]).astype(np.float64).tolist()[0][0]
                        b = np.array(V[1]).astype(np.float64).tolist()[1][0]
                        x.append(V[0][0])
                        x.append(a+V[0][0])
                        y.append(V[0][1])
                        y.append(b+V[0][1])
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

        
        if type(V) != list:
            
            # plotvector2D(A) A = Matrix([x])
            if len(V) == 1:
                color = randomRgbaColor()
                a = np.array(V).astype(np.float64).tolist()[0][0]
                b = 0
                x.append(a)
                y.append(b)
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
                color = randomRgbaColor()
                a = np.array(V).astype(np.float64).tolist()[0][0]
                b = np.array(V).astype(np.float64).tolist()[1][0]
                x.append(a)
                y.append(b)
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
 

    fig.add_trace(go.Scatter(x=[0],y=[0],mode='markers',marker=dict(color="#2a3f5f",size=9),showlegend=True,opacity=1,name="origen"))

    fig.add_annotation(ax = min(x)-0.54, axref = 'x', ay = 0, ayref = 'y',x = max(x)+0.5, xref = 'x', y = 0, yref = 'y',arrowwidth = 1.5, arrowhead = 2,arrowcolor = "#2a3f5f")
    fig.add_annotation(ax = 0, axref = 'x', ay = min(y)-0.54, ayref = 'y',x = 0, xref = 'x', y = max(y)+0.5, yref = 'y',arrowwidth = 1.5, arrowhead = 2,arrowcolor = "#2a3f5f")
    fig.add_annotation(text="$x$", x=max(x)+0.5, y=-0.2, arrowhead=1, showarrow=False)
    fig.add_annotation(text="$y$", x=-0.2, y=max(y)+0.5, arrowhead=1, showarrow=False)

    fig.update_xaxes(title = "$\large{x}$", title_font=dict(size=30, family='latex', color='rgb(1,21,51)'),range = [min(x)-0.5, max(x)+0.5],showgrid = True) #,zerolinecolor="black" ,autorange = True
    fig.update_yaxes(title = "$\large{y}$", title_font=dict(size=30, family='latex', color='rgb(1,21,51)'),range = [min(y)-0.5, max(y)+0.5],showgrid = True) #, zerolinecolor= "black" ,autorange = True
    fig.update_layout(font=dict(family="latex",size=20,color="black")) #y=1.2,x=0.03
    #fig.update_layout(title= "",title_font=dict(size=5, family='latex', color='rgb(1,21,51)'),title_x=0.5)
    fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1, itemdoubleclick ="toggle"),title_font=dict(size=30, color='rgb(1,21,51)'),showlegend=True,width=500, height=480)
    fig.show()

def plotvectors3D(*args):
    
    '''Función elaborada con el módulo Plotly y Numpy, permite visualizar multiples vectores en el espacio tridimensional, que pueden tener
     un punto inicial y un punto final dado, estar anclados en el origen del espacio, o vectores equipolentes a otro que inicie en un 
     punto dado (traslación de vectores), y vectores desde una magnitud y un vector director unitario dado, acepta como argumentos 
     vectores columna tridimensionales definidos en la librería SymPy.'''
   
    data = []
    x = [0]
    y = [0]
    z = [0.3,-0.3]


    for V in args:

        if type(V[0]) == int or type(V[0]) == float :

            if type(V[1]) == int or type(V[1]) == float :

                x.append(V[0])
                y.append(V[1])
                z.append(V[2])

            if type(V[1]) == list :
                
                magni = V[0]

                dir_x = V[1][0]
                dir_y = V[1][1]
                dir_z = V[1][2]

                v = [magni *dir_x,magni*dir_y,magni*dir_z]

                x.append(v[0])
                y.append(v[1])
                z.append(v[2])
            
            if type(V[1]) != list and type(V[1]) != int and type(V[1]) != float :

                magni = V[0]

                dir_x = np.array(V[1]).astype(np.float64)[0][0]
                dir_y = np.array(V[1]).astype(np.float64)[1][0]
                dir_z = np.array(V[1]).astype(np.float64)[2][0]

                v = [magni *dir_x,magni*dir_y,magni*dir_z]

                x.append(v[0])
                y.append(v[1])
                z.append(v[2])


        if  type(V[0]) == tuple:


            if len(V)==2:

                if type(V[1]) == tuple:
                    
                    x.append(V[0][0])
                    x.append(V[1][0])

                    y.append(V[0][1])
                    y.append(V[1][1])

                    z.append(V[0][2])
                    z.append(V[1][2])

                if type(V[1]) == list:

                    x.append(V[0][0])
                    x.append(V[0][0]+V[1][0])

                    y.append(V[0][1])
                    y.append(V[0][1]+V[1][1])

                    z.append(V[0][2])
                    z.append(V[0][2]+V[1][2])

                if  type(V[1]) != list and type(V[1]) != tuple:

                    a = np.array(V[1]).astype(np.float64).tolist()[0][0]
                    b = np.array(V[1]).astype(np.float64).tolist()[1][0]
                    c = np.array(V[1]).astype(np.float64).tolist()[2][0]

                    x.append(V[0][0])
                    x.append(V[0][0]+a)

                    y.append(V[0][1])
                    y.append(V[0][1]+b)

                    z.append(V[0][2])
                    z.append(V[0][2]+c)

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

                    x.append(p_x)
                    y.append(p_y)
                    z.append(p_z)


                    x.append(v[0])
                    y.append(v[1])
                    z.append(v[2])

                if  type(V[2]) != list and  type(V[2]) != tuple:

                    p_x = V[0][0]
                    p_y = V[0][1]
                    p_z = V[0][2]


                    magni = V[1]

                    dir_x = np.array(V[2]).astype(np.float64)[0][0]
                    dir_y = np.array(V[2]).astype(np.float64)[1][0]
                    dir_z = np.array(V[2]).astype(np.float64)[2][0]

                    v = [magni *dir_x+p_x ,magni*dir_y+p_y,magni*dir_z+p_z]

                    x.append(p_x)
                    y.append(p_y)
                    z.append(p_z)


                    x.append(v[0])
                    y.append(v[1])
                    z.append(v[2])

            
           
        if type(V) != list:

            a = np.array(V).astype(np.float64).tolist()[0][0]
            b = np.array(V).astype(np.float64).tolist()[1][0]
            c = np.array(V).astype(np.float64).tolist()[2][0]

            x.append(a)
            y.append(b)
            z.append(c)

                    
             
    escala = (max(x)+max(y)+max(z))/30

    
    for V in args:

        if type(V[0]) == int or type(V[0]) == float :

            if type(V[1]) == int or type(V[1]) == float:
                
                x.append(V[0])
                y.append(V[1])
                z.append(V[2])
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

                
        if  type(V[0]) == tuple:

            if  len(V)==2:

                if  type(V[1]) == tuple:
                    
                    x.append(V[0][0])
                    x.append(V[1][0])

                    y.append(V[0][1])
                    y.append(V[1][1])

                    z.append(V[0][2])
                    z.append(V[1][2])

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

                    x.append(V[0][0])
                    x.append(V[0][0]+V[1][0])

                    y.append(V[0][1])
                    y.append(V[0][1]+V[1][1])

                    z.append(V[0][2])
                    z.append(V[0][2]+V[1][2])

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

                    x.append(V[0][0])
                    x.append(V[0][0]+a)

                    y.append(V[0][1])
                    y.append(V[0][1]+b)

                    z.append(V[0][2])
                    z.append(V[0][2]+c)

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

                    x.append(p_x)
                    y.append(p_y)
                    z.append(p_z)


                    x.append(v[0])
                    y.append(v[1])
                    z.append(v[2])

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

                    x.append(p_x)
                    y.append(p_y)
                    z.append(p_z)


                    x.append(v[0])
                    y.append(v[1])
                    z.append(v[2])

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



        if type(V) != list:

            a = np.array(V).astype(np.float64).tolist()[0][0]
            b = np.array(V).astype(np.float64).tolist()[1][0]
            c = np.array(V).astype(np.float64).tolist()[2][0]

            x.append(a)
            y.append(b)
            z.append(c)

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




    paleta2 = [[0, "#2a3f5f"],[1, "#2a3f5f"]]
    point = go.Scatter3d( x = [0],y = [0],z = [0], mode='markers',marker=dict(color= "#2a3f5f",size=5),showlegend=True,name="origen")
    
    axex = go.Scatter3d( 
        x = [min(x)-escala, max(x)+escala],
        y = [0,0],
        z = [0,0],
        hoverinfo = "skip",
        marker = dict( size = 1,color= "#2a3f5f"),
        line = dict( color= "#2a3f5f", width = 3), showlegend=False,name="")
    
    
    conox = go.Cone(x=[max(x)+escala], y=[0], z=[0], u=[max(x)+escala], v=[0], w=[0],sizemode="absolute",sizeref= escala*0.6,anchor="cm",
               showscale=False,
               colorscale=paleta2,
               hoverinfo = "name",
               colorbar=dict(thickness=20, ticklen=4),name="Eje x-positivo")
    
    axey = go.Scatter3d( 
        x = [0,0],
        y = [min(y)-escala,max(y)+escala],
        z = [0,0],
        hoverinfo = "skip",
        marker = dict( size = 1,color="#2a3f5f"),
        line = dict( color= "#2a3f5f", width = 3), showlegend=False,name="")
    
    conoy = go.Cone(x=[0], y=[max(y)+escala], z=[0], u=[0], v=[max(y)+escala], w=[0],sizemode="absolute",sizeref=escala*0.6,anchor="cm",
               showscale=False,
               colorscale=paleta2,
               hoverinfo = "name",
               colorbar=dict(thickness=20, ticklen=4),
               name="Eje y-positivo ")
    
    axez = go.Scatter3d( 
        x = [0,0],
        y = [0,0],
        z = [min(z)-escala,max(z)+escala],
        hoverinfo = "skip",
        marker = dict( size = 1,color= "#2a3f5f"),
        line = dict( color= "#2a3f5f", width = 3), showlegend=False,name="eje z-positivo")
    
    conoz = go.Cone(x=[0], y=[0], z=[max(z)+escala], u=[0], v=[0], w=[max(z)+escala],sizemode="absolute",sizeref=escala*0.6,anchor="cm",
               showscale=False,
               colorscale=paleta2,
               hoverinfo= "name",
               colorbar=dict(thickness=20, ticklen=4),
               name="Eje z-positivo")
    
    
    #plano = go.Surface(x = np.linspace(min(x),max(x),500), y = np.linspace(min(y),max(y),500) ,z = np.zeros(500),showscale=False)

    fig = go.Figure(data= data + [point, axex, conox, axey, conoy, axez, conoz] ,layout=layout)


    fig.update_layout(legend=dict(orientation="h",y=1.3,x=0.03),title_font=dict(size=50, color='rgb(1,21,51)'),showlegend=True,width=480, height=480)


    plot(fig,image_height=800,image_width=800)
    fig.show()

