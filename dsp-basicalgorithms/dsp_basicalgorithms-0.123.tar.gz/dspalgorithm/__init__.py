import numpy as np
from math import pi,cos,sin,tan,atan,ceil
import operator as op
from cmath import exp
def linear_conv(x,h):
              
              N=len(x)+len(h)-1
              x1=np.zeros((N))
              h1=np.zeros((N))
              m=len(x)
              n=len(h)
              y=np.zeros((N))
              for i in range(m):
                            x1[i]=x[i]
              for i in range(n):
                            h1[i]=h[i]
              for i in range(N):
                            for j in range(i+1):
                                          y[i]=y[i]+ x1[j]*h1[i-j]
              return y
    
def circular_conv(x,h):   
              N=max(len(x),len(h))
              y=np.zeros((N))
              x1=np.zeros((N))
              h1=np.zeros((N))
              for i in range(len(x)):
                            x1[i]=x[i]
              for i in range(len(h)):
                            h1[i]=h[i]
              for i in range(N):
                            for j in range(N):
                                          y[i]=y[i]+x1[j]*h1[op.mod((i-j),N)]

              return y

def sampling_theorem():
              Rt=float(input('Enter the resolution of analog signal'))
              Ns= int(1/Rt)
              t=[Rt*t1 for t1 in range(Ns)]
              fm=int(input('enter the fundamental frequency'))
              xt=[cos(2*pi*fm*Rt*t1) for t1 in range(Ns)]
              fs=int(input('enter the sampling frequency'))
              Ts=(1/fs)
              N=fs
              n=[n1 for n1 in range(N)]
              xn=[cos(2*pi*fm*n1*Ts) for n1 in range(N)]
              xr=np.zeros((len(xt)))
              tr=0
              for t1 in range(Ns):
                            for n2 in range(N):
                                          if((pi*(tr-n2*Ts)/Ts)==0):
                                                        xr[t1]=xr[t1]+xn[n2]
                                          else:
                                                        xr[t1]=xr[t1]+xn[n2]*(sin(pi*(tr-n2*Ts)/Ts))/((pi*(tr-n2*Ts))/Ts)
                            tr=tr+Rt
              return t,xt,n,xn,xr
def fft(x):
        N=len(x)
        X=np.zeros((N),'complex')
        for k in range(N):
            for n in range(N):
                X[k]=X[k] + x[n]*exp(-1j*2*pi*k*n/N)
        return X
    
def auto_correlation(x):
        x1=x[::-1]
        N=len(x)+len(x1)-1
        x11=np.zeros((N))
        h1=np.zeros((N))
        m=len(x)
        n=len(x1)
        y=[0]*N
        for i in range(m):
            x11[i]=x[i]    
        for i in range(n):
            h1[i]=x1[i]   
        for i in range(N):
            for j in range(i+1):
                y[i]=y[i]+ x11[j]*h1[i-j]   
        return y

def cross_correlation(x,h):
        h1=h[::-1]
        N=len(x)+len(h)-1
        x11=np.zeros((N))
        h11=np.zeros((N))
        m=len(x)
        n=len(h)
        y=np.zeros((N))
        for i in range(m):
            x11[i]=x[i]    
        for i in range(n):
            h11[i]=h1[i]   
        for i in range(N):
            for j in range(i+1):
                y[i]=y[i]+ x11[j]*h11[i-j]   
        return y

def filter(b,a,x):
              N=len(x)
              b1=np.zeros((N))
              a1=np.zeros((N))
              nr=np.zeros((N))
              dr=np.zeros((N))
              y=np.zeros((N))
              if(np.size(a)==1):
                            for i in range(len(b)):
                                          b1[i]=b[i]
                            for i in range(N):
                                          for j in range(i+1):
                                                        y[i]=y[i]+b1[j]*x[i-j]
              else:
                                          
                            for i in range(len(b)):
                                          b1[i]=b[i]
                            for i in range(len(a)):
                                          a1[i]=a[i]
                            for i in range(N):
                                          for j in range(i+1):
                                                        nr[i]=nr[i]+b1[j]*x[i-j]
                                          for j in range(i+1):
                                                        dr[i]=dr[i]-a1[j]*y[i-j]
                                          y[i]=nr[i]+dr[i]
              return y

def fir_lpf(N,wc,win,freq_resolution):
              w=np.zeros((N))
              if win=='hamm':            
                            for n in range(N):
                                          w[n]=0.54-0.46*cos((2*pi*n)/(N-1))
              elif win=='hann':
                            for n in range(N):
                                          w[n]=0.5-0.5*cos((2*pi*n)/(N-1))
              else:
                            for n in range(N):
                                          w[n]= 1
         
              hd=np.zeros((N))
              h=np.zeros((N))
              alp=(N-1)/2
              for n in range(N):
                            if n==alp:
                                          hd[n]=wc/pi
                            else:
                                          hd[n]=sin(wc*(n-alp))/(pi*(n-alp))
              for n in range(N):
                            h[n]=hd[n]*w[n]
              N1=np.ceil((2*pi)/(freq_resolution))+1
              H=np.zeros(int(N1),'complex')
              w2=-pi
              t1=np.zeros(int(N1))
              i=0
              for w1 in range(int(N1)):
                            for n in range(N):
                                          H[w1]=H[w1]+h[n]*exp(-1j*w2*n)
                            t1[i]=w2
                            w2=w2+freq_resolution
                            i=i+1
              return h,t1,H
def fir_hpf(N,wc,win,freq_resolution):
              w=np.zeros((N))
              if win=='hamm':            
                            for n in range(N):
                                          w[n]=0.54-0.46*cos((2*pi*n)/(N-1))
              elif win=='hann':
                            for n in range(N):
                                          w[n]=0.5-0.5*cos((2*pi*n)/(N-1))
              else:
                            for n in range(N):
                                          w[n]= 1
         
              hd=np.zeros((N))
              h=np.zeros((N))
              alp=(N-1)/2
              for n in range(N):
                            if n==alp:
                                          hd[n]=(pi-wc)/pi
                            else:
                                          hd[n]= -sin(wc*(n-alp))/(pi*(n-alp))
              for n in range(N):
                            h[n]=hd[n]*w[n]
              N1=np.ceil((2*pi)/(freq_resolution))+1
              H=np.zeros(int(N1),'complex')
              w2=-pi
              t1=np.zeros(int(N1))
              i=0
              for w1 in range(int(N1)):
                            for n in range(N):
                                          H[w1]=H[w1]+h[n]*exp(-1j*w2*n)
                            t1[i]=w2
                            w2=w2+freq_resolution
                            i=i+1
              return h,t1,H
def buttord(fp,fs,ap1,as1,F):
              T=1/F
              wp=2*pi*fp/F
              ws=2*pi*fs/F
              Wp=2*F*tan(wp/2)
              Ws=2*F*tan(ws/2)
              nr= 10**(ap1/10)-1
              dr=  10**(as1/10)-1
              N= np.log10((nr/dr))/(2*np.log10(Wp/Ws))
              N=ceil(N)
              if(ap1>10):
                            Wc= (Ws)/((10**(as1/10)-1)**(1/(2*N)))
              else:
                            Wc= (Wp)/((10**(ap1/10)-1)**(1/(2*N)))
              wc= 2*atan((Wc*T)/2)
              return N,wc/pi

