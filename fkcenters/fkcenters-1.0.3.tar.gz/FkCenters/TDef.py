import os
import os.path
import sys
folder='RESULT'
fname=''
data=''
measure=''
test_type=None
n_iter = 100
n_init = 5
repeat = 4
n=4096
d=8
k=-1
num=-1
o="out"
verbose=0
n_group=2
init_type ='best'
alpha = 1.1
beta=1.9
is_auto_save = True
is_skip_eval = False
m='kModes'
seed = -1
def InitParameters(args):
    global n_iter,n_init,num,n,d,k,test_type,data,measure,folder,verbose,n_group,init_type,fname,alpha,repeat,m,beta,is_skip_eval,seed
    index = 1
    while index < len(args):
        if args[index]== '-n_init': n_init = int(args[index+1]); index+=2; continue;
        if args[index]== '-n_iter': n_iter = int(args[index+1]); index+=2; continue;
        if args[index]== '-n': n = int(args[index+1]); index+=2; continue;
        if args[index]== '-d': d = int(args[index+1]); index+=2; continue;
        if args[index]== '-k': k = int(args[index+1]); index+=2; continue;
        if args[index]== '-num': num = int(args[index+1]); index+=2; continue;
        if args[index]== '-o': o = args[index+1]; index+=2; continue;
        if args[index]== '-test_type': test_type = args[index+1]; index+=2; continue;
        if args[index]== '-data': data = args[index+1]; index+=2; continue;
        if args[index]== '-measure': measure = args[index+1]; index+=2; continue;
        if args[index]== '-folder': folder = args[index+1]; index+=2; continue;
        if args[index]== '-m': m = args[index+1]; index+=2; continue;
        if args[index]== '-fname': fname = args[index+1]; index+=2; continue;
        if args[index]== '-verbose': verbose = int(args[index+1]); index+=2; continue;
        if args[index]== '-n_group': n_group = int(args[index+1]); index+=2; continue;
        if args[index]== '-seed': seed = int(args[index+1]); index+=2; continue;
        if args[index]== '-init_type': init_type = args[index+1]; index+=2; continue;
        if args[index]== '-alpha': alpha = float(args[index+1]); index+=2; continue;
        if args[index]== '-beta': beta = float(args[index+1]); index+=2; continue;
        if args[index]== '-repeat': repeat = int(args[index+1]); index+=2; continue;
        if args[index]== '-is_skip_eval': is_skip_eval = True; index+=1; continue;
        print('ERROR: Cannot understand ',args[index] ) 
        index+= 1 
if __name__ == "__main__":
    print(sys.argv)
    InitParameters(sys.argv)
