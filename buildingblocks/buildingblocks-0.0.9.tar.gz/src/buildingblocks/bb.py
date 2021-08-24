# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 21:10:56 2021

@author: npkn
"""
 
def interpolate(Xdata,Ydata,Xnew):
    def datamodel(Xdata,Ydata):    
        import numpy as np
        from numpy.linalg import inv         
        Xdata=np.array(Xdata)
        Ydata=np.array(Ydata)
    
        LenX=len(Xdata)
        LenY=len(Ydata) 
        A=[]
        minErr=np.sum((np.max(Ydata)-min(Ydata))*(np.max(Ydata)-min(Ydata)))
        minErrK=minErr
        minErrM=minErr
        Predicted_y=[]
        
        def Calculations(LenX,deg,k,m,Xdata,Ydata,minErr,minErrK,minErrM):
            noPara = round((0.69+0.01*m)*LenX)
            xMod = (Xdata/deg)*k
            Xmat=np.zeros((LenX,noPara))
            Xmat[:,0]=np.ones(LenX)
            i=0
            j=0
            while i<noPara-1:
                i=i+1
                j=j+1
                Xmat[:,i]=np.cos(np.array(j*xMod*np.pi))
                if i<noPara-1:
                    i=i+1
                    Xmat[:,i]=np.sin(np.array(j*xMod*np.pi))
            Mat1=np.matmul(Xmat.transpose(), Xmat)
            Mat2=inv(Mat1)     
            xINV= np.matmul(Mat2,Xmat.transpose())
            A= np.matmul(xINV,Ydata)
            Predicted_y=np.matmul(Xmat,A)
            SqErr=np.sum((Predicted_y-Ydata)*(Predicted_y-Ydata))
            error=np.sqrt(SqErr)
        
            if error < minErr:
                minErr = error
                minErrK=k
                minErrM=m
            return [minErrK, minErrM,A,Predicted_y,minErr]
 
        if LenX==LenY:
            if round(np.max(Xdata)) >= round(np.min(Xdata)):
                deg=np.max(Xdata)
            else:
                deg=np.min(Xdata)
            maxK=5
            maxM=30
            for m in range(1,maxM+1):
                for k in range(1,maxK+1):
                    print("calculating iteration {} out of {} iterations".format((m-1)*maxK+k,maxK*maxM))
                    [minErrK, minErrM,A,Predicted_y,minErr]=Calculations(LenX,deg,k,m,Xdata, Ydata,minErr,minErrK,minErrM)
    
            m=minErrM
            k=minErrK
            [minErrK, minErrM,A,Predicted_y,minErr]=Calculations(LenX,deg,k,m,Xdata, Ydata,minErr,minErrK,minErrM)
            ParaSet=[LenX,deg,k,m]
            ParaSet.append(list(A))
        else:
          print("X and Y are not of same size")
        return ParaSet


    def usemodel(Xnew,ParaSet):
        import numpy as np
        [LenX,deg,k,m]=ParaSet[0:4]
        # print(k,m)
        noPara = round((0.69+0.01*30)*LenX)
        A=np.zeros(noPara)   
        LenParaSet=len(ParaSet[4])
        A[0:LenParaSet]=ParaSet[4]
        xMod = (Xnew/deg)*k
        LenX=len(Xnew)
        Xmat=np.zeros((LenX,noPara))
        Xmat[:,0]=np.ones(LenX)
        i=0
        j=0
        while i<noPara-1:
            i=i+1
            j=j+1
            Xmat[:,i]=np.cos(np.array(j*xMod*np.pi))
            if i<noPara-1:
                i=i+1
                Xmat[:,i]=np.sin(np.array(j*xMod*np.pi))
        Predicted_y=np.matmul(Xmat,A)
        return Predicted_y


    ParaSet=datamodel(Xdata,Ydata)
    Ynew=usemodel(Xnew,ParaSet)
    return Ynew











