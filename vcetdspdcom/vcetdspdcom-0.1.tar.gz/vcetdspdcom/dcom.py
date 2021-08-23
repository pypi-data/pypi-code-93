import random
import math as mt
import numpy as np
def ask_modulation(fs,fc,tb,sim_t):
    sb=tb*fs
    x=[random.randint(0,1) for i in range(int(sim_t/tb))]
    m=[]
    for i in range(len(x)):
        if x[i]==0:
            m.append(([0]*int(sb)))
        else:
            m.append(([1]*int(sb)))
    t=[i for i in np.arange(0,sim_t,1/fs)]
    c=[np.cos(2*np.pi*fc*i) for i in np.arange(0,sim_t,1/fs)]
    m=np.array(m)
    m=m.reshape(-1,)
    c=np.array(c)
    y=m*c 
    y_output=y
    m_message=m
    c_carrier=c
    t_time=t
    return y_output,m_message,c_carrier,t_time
def psk_modulation(fs,fc,tb,sim_t):
    sb=tb*fs
    x=[random.randint(0,1) for i in range(int(sim_t/tb))]
    m=[]
    for i in range(len(x)):
        if x[i]==0:
            m.append(([-1]*int(sb)))
        else:
            m.append(([1]*int(sb)))
    t=[i for i in np.arange(0,sim_t,1/fs)]
    c=[np.cos(2*np.pi*fc*i) for i in np.arange(0,sim_t,1/fs)]
    m=np.array(m)
    m=m.reshape(-1,)
    c=np.array(c)
    y=m*c
    y_output=y
    m_message=m
    c_carrier=c
    t_time=t
    return y_output,m_message,c_carrier,t_time
def fsk_modulation(fs,fc1,fc2,tb,sim_t):
    sb=tb*fs
    x=[random.randint(0,1) for i in range(int(sim_t/tb))]
    m1=[]
    m2=[]
    for i in range(len(x)):
        if x[i]==0:
            m1.append(([0]*int(sb)))
            m2.append(([1]*int(sb)))
        else:
            m1.append(([1]*int(sb)))
            m2.append(([0]*int(sb)))
    t=[i for i in np.arange(0,sim_t,1/fs)]
    c1=[np.cos(2*np.pi*fc1*i) for i in np.arange(0,sim_t,1/fs)]
    c2=[np.cos(2*np.pi*fc2*i) for i in np.arange(0,sim_t,1/fs)]
    m1=np.array(m1)
    m2=np.array(m2)
    m1=m1.reshape(-1,)
    m2=m2.reshape(-1,)
    c1=np.array(c1)
    c2=np.array(c2)
    y=m1*c1+m2*c2
    y_output=y
    m_message=m1
    c_carrier1=c1
    c_carrier2=c2
    t_time=t
    return y_output,m_message,c_carrier1,c_carrier2,t_time
def dpsk_modulation(fs,fc,tb,sim_t,init_bit):
    sb=tb*fs
    d=init_bit
    b=[random.randint(0,1) for i in range(int(sim_t/tb))]
    print(b)
    x=[]
    #b=np.array([1,0,1,1,0])
    m1=[]
    for i in range(len(b)):
        if b[i]==0:
            m1.append(([-1]*int(sb)))
        else:
            m1.append(([1]*int(sb)))
    m1=np.array(m1)
    m1=m1.reshape(-1,)

    for i in range(len(b)):
        re= b[i]^d
        re= not re
        x.append(int(re))
        d=re
    m=[]
    for i in range(len(x)):
        if x[i]==0:
            m.append(([-1]*int(sb)))
        else:
            m.append(([1]*int(sb)))
    t=[i for i in np.arange(0,sim_t,1/fs)]
    c=[np.cos(2*np.pi*fc*i) for i in np.arange(0,sim_t,1/fs)]
    m=np.array(m)
    m=m.reshape(-1,)
    c=np.array(c)
    y=m*c
    y_output=y
    m_message=m1
    enc_message=m
    c_carrier=c
    t_time=t
    return y_output,m_message,enc_message,c_carrier,t_time
def qpsk_modulation(fs,fc,tb,sim_t):
    sb=2*tb*fs
    x=[random.randint(0,1) for i in range(int(sim_t/tb))]
    t=[i for i in np.arange(0,sim_t,1/fs)]
    c=[np.cos(2*np.pi*fc*i) for i in np.arange(0,sim_t,1/fs)]
    m=[]
    for i in range(len(x)):
        if x[i]==0:
            m.append(([-1]*int(sb/2)))
        else:
            m.append(([1]*int(sb/2)))
    m=np.array(m)
    m=m.reshape(-1,)
    t=[i for i in np.arange(0,sim_t,1/fs)]
    m1=[]
    for i in range(0,len(x)-1,2):
        if x[i]==0 and x[i+1]==0:
            c1=[np.cos((2*np.pi*fc*i)) for i in np.arange(0,((2*tb)/(sim_t)),1/fs)]
            m1.append(c1)
        elif x[i]==0 and x[i+1]==1:
            c2=[np.cos((2*np.pi*fc*i)+(pi/2)) for i in np.arange(0,((2*tb)/(sim_t)),1/fs)]
            m1.append(c2)
        elif x[i]==1 and x[i+1]==0:
            c3=[np.cos((2*np.pi*fc*i)+(pi)) for i in np.arange(0,((2*tb)/(sim_t)),1/fs)]
            m1.append(c3)
        else:
            c4=[np.cos((2*np.pi*fc*i)+((3*pi)/2)) for i in np.arange(0,((2*tb)/(sim_t)),1/fs)]
            m1.append(c4)
    m1=np.array(m1)
    m1=m1.reshape(-1,)
    y_output=m1
    m_message=m
    c_carrier=c
    t_time=t
    return y_output,m_message,c_carrier,t_time
def qam_modulation(fs,fc,tb,sim_t):
    sb=tb*fs
    x=[random.randint(0,1) for i in range(int(sim_t/tb))]
    nb=len(x)//4
    if len(x)%4 != 0:
        re=len(x)%4
        nb+=1
        for i in range(4-re):
            x.append(0)
        sim_t+=(4-re)*tb
    msg=[]
    for i in range(len(x)):
        if x[i]==0:
            msg.append(([-1]*int(sb)))
        else:
            msg.append(([1]*int(sb)))
    msg=np.array(msg)
    msg=msg.reshape(-1,)
    print(msg.shape)
    t1=[i for i in np.arange(0,sim_t,1/fs)]
    print(x)
    a=[]
    b=[]
    for i in range(0,len(x)-3,4):
        if x[i]==0 and x[i+1]==0:
            a.append(-0.22)
        elif x[i]==0 and x[i+1]==1:
            a.append(-0.82)
        elif x[i]==1 and x[i+1]==0:
            a.append(0.22)
        elif x[i]==1 and x[i+1]==1:
            a.append(0.82)
        if x[i+2]==0 and x[i+3]==0:
            b.append(-0.22)
        elif x[i+2]==0 and x[i+3]==1:
            b.append(-0.82)
        elif x[i+2]==1 and x[i+3]==0:
            b.append(0.22)
        elif x[i+2]==1 and x[i+3]==1:
            b.append(0.82)
    a=np.array(a)
    b=np.array(b)
    print(a,b)
    m1=list()
    st=0
    so=sim_t/len(a)
    carrier1=[np.sin((2*np.pi*fc*i)) for i in np.arange(0,sim_t,1/fs)]
    carrier2=[np.cos((2*np.pi*fc*i)) for i in np.arange(0,sim_t,1/fs)]
    for t in range(len(a)):
        c1=[a[t]*np.cos((2*np.pi*fc*i))+ b[t]*np.sin((2*np.pi*fc*i)) for i in np.arange(st,so,1/fs)]
        m1=m1+c1
        st=so
        so+=sim_t/len(a)
    if (len(m1)!=len(t1)):
        tr=min(len(m1),len(t1))
        if len(m1)>len(t1):
            m1=m1[:tr]
        else:
            t1=t1[:tr]
            carrier1=carrier1[:tr]
            carrier2=carrier2[:tr]
    m1=np.array(m1)
    m1=m1.reshape(-1,)
    y_output=m1
    m_message=msg
    c_carrier1=carrier1
    c_carrier2=carrier2
    t_time=t1
    return y_output,m_message,c_carrier1,c_carrier2,t_time
