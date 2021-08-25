import numpy as np

def meshODE(t,sol):

     """
     Given a 2D meshgrid array input and an OdeSolution
     object, output the ODE solution held in OdeSolution
     as a meshgrid compatible with the input.

     Parameters
     ----------
     t : 2D np.array
         Form of the array should be like either XX or YY in
         XX,YY = np.meshgrid(xs,ys) for arbitrary xs and ys.
     sol : scipy.integrate.OdeSolution
         Continous ODE solution that you would like to extend
         to a second dimension.

     Returns
     -------
     out : 2D np.array
         The equivalent of calling sol(t) for the 2D input
         array, if that were an allowed operation.


     Example
     -------

     from scipy.integrate import solve_ivp
     import matplotlib.pyplot as plt

     def fun(t,y):

         return [y[1],-6*y[1]-8*y[0]]

     def exact(t,y0):

         A = - (y0[1]+ 2*y0[0])/2.0
         B = (y0[1]+4*y0[0])/2.0

         return [A*np.exp(-4*t) + B*np.exp(-2*t),
                 -4*A*np.exp(-4*t) - 2*B*np.exp(-2*t)]


     t_span = (0,1)
     y0 = (3.0,-4.0)

     sol = solve_ivp(fun,t_span,y0,dense_output=True).sol

     ts = np.linspace(t_span[0],t_span[1],num=101,endpoint=True)

     TT,QQ = np.meshgrid(ts,ts)

     plt.plot(QQ[:,0],meshODE(QQ,sol)[0][:,0],'ro')

     plt.plot(TT[0,:],meshODE(TT,sol)[0][0,:],'bo')
     plt.plot(ts,exact(ts,y0)[0],'k--')

     plt.show()



     """

     rows = len(t[:,0])
     cols = len(t[0,:])

     if np.abs(t[1,0]-t[0,0])>1e-15:

          dum = sol(t[:,0])
          outputdimensions = dum.ndim
          if outputdimensions == 1:
               dum_y = np.repeat(dum, repeats=cols)
               out_y = dum_y.reshape(rows,cols)
          else:
               dum_y = np.repeat(dum[0], repeats=cols)
               dum_yp = np.repeat(dum[1], repeats=cols)
               out_y = dum_y.reshape(rows,cols)
               out_yp = dum_yp.reshape(rows,cols)


     elif np.abs(t[0,1]-t[0,0])>1e-15:

          dum = sol(t[0,:])
          outputdimensions = dum.ndim
          if outputdimensions == 1:
               dum_y = np.repeat(dum, repeats=rows)
               out_y = dum_y.reshape(cols,rows).T
          else:
               dum_y = np.repeat(dum[0], repeats=rows)
               dum_yp = np.repeat(dum[1], repeats=rows)
               out_y = dum_y.reshape(cols,rows).T
               out_yp = dum_yp.reshape(cols,rows).T

     else:
          raise ValueError('Array input does not have the form '
                           'XX or YY from XX,YY = np.meshgrid(...).')

     if outputdimensions == 1:
          return out_y
     else:
          return out_y,out_yp


if __name__ == "__main__":

     from scipy.integrate import solve_ivp
     import matplotlib.pyplot as plt

     def fun(t,y):

         return [y[1],-6*y[1]-8*y[0]]

     def exact(t,y0):

         A = - (y0[1]+ 2*y0[0])/2.0
         B = (y0[1]+4*y0[0])/2.0

         return [A*np.exp(-4*t) + B*np.exp(-2*t),
                 -4*A*np.exp(-4*t) - 2*B*np.exp(-2*t)]


     t_span = (0,1)
     y0 = (3.0,-4.0)

     sol = solve_ivp(fun,t_span,y0,dense_output=True).sol

     ts = np.linspace(t_span[0],t_span[1],num=101,endpoint=True)

     TT,QQ = np.meshgrid(ts,ts)

     plt.plot(QQ[:,0],meshODE(QQ,sol)[0][:,0],'ro')

     plt.plot(TT[0,:],meshODE(TT,sol)[0][0,:],'bo')
     plt.plot(ts,exact(ts,y0)[0],'k--')

     plt.show()
