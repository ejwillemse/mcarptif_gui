#===============================================================================
# Floyd-Warshall algorithm adapted for Turn Penalties
# Elias Willemse, CSIR Pretoria, Created 10 Augus 2009. Edited 11 August 2009.

# Derived from the book:
# Cormen, T., Leiserson, C., Rivest, R. (1990). Introduction to algorithms 
# Chapter 26 pages 558-562.
#===============================================================================
def FloydWarshallTP(cDict, sucDict, penDict=None):
    '''
    Addaptation of the Floyd Warshall algorithm for computing arc to 
    arc shortest paths, instead of node to node.
    
    Required input are cost of each arc, the predecesors of an arc, 
    and the turn penalty from moving from one arc to another. Output 
    are the distance matrix D between all arcs, and the predecesor 
    matrix.
    
    Note that the graph has to be complete and connected, ie. all arcs should
    have at least one predecesor arc and one succesor arc.
    
    Output is an m x m dictionary - representing a matrix -  of distances
    and predecesors. For the predecesor matrix, a predecesor of zero means
    that the edge is the origen node.
    
    Algorithm runs in O(m^3) and uses O(m^2) space.
    '''
    huge = 1e30000# Infinity
    
    print('Starting SP shortes path calculations')
    
    arcs = cDict.keys()# Get arcs indexes
    nArcs = len(arcs)
    d = [huge]*nArcs# Initiate distance matrix
    pre = [0]*nArcs# Initiate predecessor matrix
    
    for i in arcs:
        d[i] = [huge]*nArcs
        pre[i] = [0]*nArcs
        print('Pre calc',i,nArcs)
        for j in arcs:
            if i == j:
                d[i][j] = 0# Distance from an arc to itself is zeros
                #d[i][j] = 0
            elif j in sucDict[i]:
                #if penDict:
                    #temp[j] = penDict[i].get(j)# Penalty for moving from arc i to j, and j is a successor of i
                #else:
                d[i][j] = 0
                pre[i][j] = i# Predecesor is obviously i
            #else:
                #d[i][j] = huge# If it is not a predecessor, the distance is infinity
        #d[i] = temp# Assign dictionary to d[i] - we have just computed the complete row i
        #pre[i] = temp2# Same as above but with the prdecessor matrix
        
    for k in arcs:
        print('SP calc',k,nArcs)
        for i in arcs:
            for j in arcs:
                if d[i][k] + d[k][j] + cDict[k] < d[i][j]:#If moving from arc i to arc j via arc k is shorter than moving directly from arc i to j:
                    #Note that we have to add the cost of traversing arc k
                    d[i][j] = d[i][k] + d[k][j] + cDict[k]#Update distance from arc i to j 
                    pre[i][j] = pre[k][j]#Update distance from arc i to j 

    return(d, pre)


#===============================================================================
# DAG-Shortest-paths
# Elias Willemse, CSIR Pretoria, Created 13 September 2009..

# From the book:
# Cormen, T., Leiserson, C., Rivest, R. (1990). Introduction to algorithms 
# Chapter 25 pages 536.
#===============================================================================
def DagSP(G, verticeS, source):
    '''
    Computes the single source shortest path in a directed acyclic graph.
    G must be in started succesor vertex format,i.e., G = {arc : {succesor arc : arc weight}}
    verticeS refers to a typologically sorted list of the verices.
    '''
    huge = 1e30000# Infinity
    dEst = {}.fromkeys(verticeS)
    piEst = {}.fromkeys(verticeS)
    
    for v in verticeS:
        dEst[v] = huge
        piEst[v] = None
        
    dEst[source] = 0
    
    for u in verticeS:
        for v in G[u].keys():
            if dEst[v] > dEst[u] + G[u][v]:
                dEst[v] = dEst[u] + G[u][v]
                piEst[v] = u
                
    return(dEst, piEst)


def DagAll2AllSP(G, verticeS):
    '''
    Computes the all source shortest paths in a directed acyclic graph.
    G must be in started succesor vertex format,i.e., G = {arc : {succesor arc : arc weight}}
    verticeS refers to a typologically sorted list of the verices.
    '''
    huge = 1e30000# Infinity
    dEst = {}.fromkeys(verticeS)
    piEst = {}.fromkeys(verticeS)
    
    nVertices = len(verticeS)
    for s in range(nVertices):
        dEst[s] = {}
        piEst[s] = {}
        for v in range(s,nVertices): 
            dEst[s][v] = huge
            piEst[s][v] = None
        dEst[s][s] = 0
    
    i = 0
    for u in verticeS:
        i = i + 1
        suc_u = G[u].keys()
        for v in suc_u:
            G_temp = G[u][v]
            for q in range(i): 
                if dEst[verticeS[q]][v] > dEst[verticeS[q]][u] + G_temp:
                    dEst[verticeS[q]][v] = dEst[verticeS[q]][u] + G_temp
                    piEst[verticeS[q]][v] = u
                
    return(dEst, piEst)

def sp1SourceList(piEst, origin, destination):
    '''
    Generate shortest path visitation list based on presidence dictionary, and 
    an origin and destination. 
    '''
    pathList = [destination]
    a = destination
    while True:
        a = piEst[a]
        pathList.append(a)
        if a == origin:break
    pathList.reverse()
    return(pathList)

def spSource1Listv2(piEst, origin, destination):
    '''
    Generate shortest path visitation list based on presidence dictionary, and 
    an origin and destination. 
    '''
    piEst = piEst[origin]
    pathList = [destination]
    a = destination
    while True:
        a = piEst[a]
        pathList.append(a)
        if a == origin:break
    pathList.reverse()
    return(pathList[1:-1])
    
if __name__=="__main__":
    verticeS = [0,1,2,3,4,5] 
    G = {0:{1:37,2:51},
         1:{2:27,3:56,4:80},
         2:{3:40,4:64},
         3:{4:32,5:50},
         4:{5:33},
         5:{}}
    
    (dEst, piEst) = DagAll2AllSP(G, verticeS)
    print(dEst[0][5])
    
    
    
    
    
    