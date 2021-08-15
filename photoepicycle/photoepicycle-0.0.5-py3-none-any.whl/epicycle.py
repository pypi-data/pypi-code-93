import matplotlib.pyplot as plt
import numpy as np
from skimage import io
import cv2
from skimage import feature 
import copy
import networkx as nx
from sklearn.neighbors import NearestNeighbors
from skimage.transform import resize
from collections import OrderedDict

def removeDuplicates(lst):
    b = []
    for i in lst:
        # Add to the new list
        # only if not present
        if i not in b:
            b.append(i)
    return b

def pyth(p1,p2): #defined as tubles
    return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def comparison(CurrentNode,ChosenNode, zeros_list,original_dist):
    #Now it is time for some comparison 
    comparison = []
    dis = [i for i in original_dist[ChosenNode]]#Get the distance from ori list
    dis_interest = [dis[i] for i in zeros_list] #nclude the zeros only
    dis_sum = sum(dis) #Sum current configuration
    comparison.append(dis_sum)
    cur_node = original_dist[ChosenNode][CurrentNode] #Call the distance
    sum_1 = cur_node + dis_interest[0] #Do sum with first edge
    sum_2 = cur_node + dis_interest[1] #Do some with second edge
    comparison.append(sum_1)
    comparison.append(sum_2)
    min_com = (np.array(comparison)).argmin()
    return min_com, dis_interest[0], dis_interest[1]



def linefollowing(points,dist_m,original_dist):
       
    #random
    '''
    start_point = random.randint(0,len(points)-1)
    x_sorted.append(points[start_point][0])
    y_sorted.append(points[start_point][1])
    '''
    #predefined 
    start_point = 5 #Or  random
    prev_nodes = []
    prev_nodes.append(start_point)
    
    ite = 100 + len(points)
    #Assigning initial order
    for a in range(ite): #Probably for an undefined time
    
        #Storing value temprorary
        temp = original_dist[start_point][prev_nodes[-1]]
        print("temp: ", temp)
        #Setting recently visited node to zero
        original_dist[start_point][prev_nodes[-1]] = 0
        #Getting the interesting row
        min_dis = np.array(original_dist[start_point])
        #Masking zeros
        valid_idx = np.where(np.array(min_dis) > 0)[0]
        #Get the index
        ind = valid_idx[min_dis[valid_idx].argmin()]
        #Store the original value
        original_dist[start_point][prev_nodes[-1]] = temp
        #Find the connections in the chosen node
        con_node = dist_m[ind]
        zer = np.where(np.array(con_node)==0)[0] #Should always containt elements
        #if len(zer)>2:
          # print("Zer is too large")
          # print("iteration: ", a)
        if len(zer) == 2:
            min_com, dis1, dis2 = comparison(start_point,ind,zer,original_dist)
            b=1 #An iterative timer
            print("node of interest is: ", ind, "and its distance row is: ")
            print(con_node)
            print(" ")
            print("I am coming from node ", start_point, ", and my distance row is:  ")
            print(dist_m[start_point])
            if min_com == 0: #Keep the suggested node as it is and look for the second smallest
                print("min_com==0")
                for n in range(original_dist[ind]):
                    b_small = np.argpartition(original_dist[ind],b)
                    b_small = b_small[b]
                    #Call the list of possible connections
                    L= dist_m[b_small]
                    zer_1 = np.where(np.array(L)==0)[0]
                    if len(zer_1)<2: #No connections made on that node yet
                        #Choose that node
                        ind = b_small
                        break
                    
                    b += b_small
                
            else:
                #choose this edge and remove previous configuration
                if min_com == 1:
                    #Modify the chosen node's dist matrix
                    print("min_com==1")
                    dist_m[ind][zer[0]] = dis1
                    dist_m[zer[0]][ind] = dis1
                if min_com == 2:
                    #Modify the chosen node's dist matrix
                    print("min_com==2")
                    dist_m[ind][zer[1]] = dis2
                    dist_m[zer[1]][ind] = dis2
    
                
    
        #Set it to zero in the dist matrix
        dist_m[start_point][ind] = 0
        dist_m[ind][start_point] = 0 
        
        #Start point re-assigning
        prev_nodes.append(start_point)
        start_point = ind
    
    
        
    
    #create x and y from dist_m's zeros
    x_sorted = []
    y_sorted = []
    start_point = 5
    x_sorted.append(points[start_point][0])
    y_sorted.append(points[start_point][1])
    ind_l = []
    for _ in range(len(dist_m)-2):
        sp = dist_m[start_point]
        z=np.where(np.array(sp)==0)
        fz = z[0][0] #index of first zero
        ind_l.append(fz)
        dist_m[fz][start_point] = np.NINF
        dist_m[start_point][fz] = np.NINF    
        x_sorted.append(points[fz][0])
        y_sorted.append(points[fz][1])
        start_point = fz 
    
    x_sorted.append(x_sorted[0])
    y_sorted.append(y_sorted[0])
    
    
    print("sorted")
    print("x_sorted: ", x_sorted)
    print("y_sorted: ", y_sorted)
    
    return x_sorted, y_sorted


def img_init(path, scale=20, s=1):
    img = io.imread(path)
       
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    #percent by which the image is resized
    scale_percent = scale
    
    #calculate the 50 percent of original dimensions
    width = int(gray.shape[1] * scale_percent / 100)
    height = int(gray.shape[0] * scale_percent / 100)
    
    # dsize
    dsize = (width, height)
    
    # resize image
    gray = cv2.resize(gray, dsize)
    
    #edge detection 
    edges = feature.canny(gray,sigma=s)
    #edges = cv2.Canny(gray,100,200)
    unity = np.ones((edges.shape[0], edges.shape[1]))
    bi_e = unity * edges
    
    x = []
    y = []
    for i in range(bi_e.shape[0]):
        for j in range(bi_e.shape[1]):
            if bi_e[i][j] == 1:
                x.append(j)
                y.append(i)
    y = [abs(i-bi_e.shape[0]) for i in y]
    
    return np.array(x), np.array(y), gray, edges
    
    
def Neighbour_Sorting(x,y, nn=2): #nn refers to the number of points connected together, has to be two
    
    #Explore NearestNeighbors algorithm
    points = np.c_[x,y]
    clf = NearestNeighbors(n_neighbors=nn).fit(points)
    G = clf.kneighbors_graph() #Adjacency matrix
    #G = clf.radius_neighbors_graph()
    count_p = 0
    count_n = 0
    G_arr = G.toarray()
    '''
    for i in range(len(G_arr)):
        a = np.where(G_arr[:,i] == 1)
        if len(a[0]) > 2:
            count_p += 1
            print('Found', count_p, 'larger than two elements')
        if len(a[0]) < 2:
            count_n += 1
            print('Found', count_n, 'smaller than two elements')
     '''       
    #Now we can do the connections based on the adjacency matrix
    
    T = nx.from_scipy_sparse_matrix(G)
    order = list(nx.dfs_preorder_nodes(T, 0)) ################ What does this do???
    x_o = x[order]
    y_o = y[order]
    

    #Choosing an appropriate starting point
    paths = [list(nx.dfs_preorder_nodes(T, i)) for i in range(len(points))]
    
    mindist = np.inf
    minidx = 0
    
    for i in range(len(points)):
        p = paths[i]           # order of nodes
        ordered = points[p]    # ordered nodes
        # find cost of that order by the sum of euclidean distances between points (i) and (i+1)
        cost = (((ordered[:-1] - ordered[1:])**2).sum(1)).sum()
        if cost < mindist:
            mindist = cost
            minidx = i
    
    opt_order = paths[minidx]
    x_o = x[opt_order]
    y_o = y[opt_order]
    points_o = points[opt_order]
   
    return x_o, y_o, G, clf, G_arr, points_o 
