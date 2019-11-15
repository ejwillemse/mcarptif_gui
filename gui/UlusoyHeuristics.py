# Optimally partition an existin route using Ulusoy's heuristic.
# Elias Willemse, CSIR Pretoria, Created 14 October 2009. 
#
#
# Derived from the articles:
# Belenguer, J., Benavent, E., Lacomme, P., Prins, C. (2006). Lower and uper 
# bounds for the mixed capacitated arc routing problem. Computers and Operations
# Research. 33(12) 
# p. 3363-3383.
# Specifically pages 3371-3372.
#
# Ghiani, G., Guerriero, F. Laporte, G., Musmanno, R. (2004). Tabu search 
# heuristics for the Arc Routing Problem with Intermediate Facilities under
# Capacity and Length Restrictions. Journal of Mathematical Modelling and 
# Algorithms. 3()
# p 209-223
# Specifically pages 211-213 
#
# Ghiani, G. Improta, G., Laporte, G. (2001). The Capacitated Arc Routing 
# Problem with Intermediate Facilities. Networks. 37(3)
# p 134-143
# Specifically pages 137-138

import EPSsolutions_IFs as EPSsolutions
import SPmodules2 as SPmodules
import copy
from copy import deepcopy
import reduceNumberTrips_IF
import transformSolution

huge = 1e30000 
    
def insDepot(solutionSequence, depotArc):
    ''' 
    Add a depotArc visit to the beginning and end of route
    '''
    solutionSequence.append(depotArc)
    solutionSequence.insert(0, depotArc)
    return(solutionSequence)


def spAuxGraph(G, route, source):
    '''
    Determines the shortest path and predecessor dict on the auxiliray
    graph.
    '''
    (spDistance, spPath) = SPmodules.DagSP(G, route, source)
    return(spDistance, spPath)

def spSolution(spDistance, spPath, source, destination):
    '''
    Determines the actual shortest path sequence and distance between
    a start and end point.
    '''
    Path = SPmodules.sp1SourceList(spPath, source, destination)
    return(spDistance[destination], Path)

def spAuxToSolution(finalDistance, Path, originalRoute):
    '''
    Converts the shortest path on the auxiliray graph to the actual
    partitioning of the original route.
    '''
    solution = {}
    nVehicles = len(Path) - 1

    for i in range(nVehicles):
        solution[i + 1] = {}
        sequence = originalRoute[Path[i]:Path[i + 1]]
        solution[i + 1]['Solution'] = sequence
    return(solution)

def genSpIFDictionary(info):
    '''
    Determines the best intermediate facility to insert between any two required
    arcs, including the depot arc.
    '''
    requiredArcs = info.reqArcList
    IFs = info.IFarcs
    depot = info.depotArc
    requiredArcs.insert(0, depot)
    spD = info.spDistanceD
    bestIF = {}
    bestIFdistD = {}
    for i in requiredArcs:
        bestIF[i] = {}
        bestIFdistD[i] = {}
        for j in requiredArcs:
            bestIFdistTemp = huge
            for q in IFs:
                dist = spD[i][q] + spD[q][j]
                if dist < bestIFdistTemp:
                    bestIFdistTemp = dist
                    bestIFdistD[i][j] = dist
                    bestIF[i][j] = q
    return(bestIF, bestIFdistD)

#===============================================================================
# Use EPSsolutions module to construct a giant initial route
#===============================================================================
class giantRoute(object):
    
    huge = 1e30000 

    def __init__(self, info):
        self.info = info       
        self.EPS = EPSsolutions.EPSinitialSolution(info)
        self.RouteBig = {}
        
    def genRoute(self, rule=False):
        '''
        Generate route using EPSsolutions by ignoring vehicle capacity.
        '''
        origMaxTrip = deepcopy(self.EPS.info.capacity)
        self.EPS.info.capacity = huge # ignore capacity
        self.RouteBig = self.EPS.genInitialSolution(rule)
        self.EPS.info.capacity = origMaxTrip
        self.info = origMaxTrip

#===============================================================================
# Optimally partition a giant route by including trips back to the depot.
# Only works if there is no maximum vehilce trip lenght and when there are
# no interdemiate facilities, and there is only one depot. Can be converted
# to cater for multiple depots.
#===============================================================================        
class Ulusoys(object):
    
    huge = 1e30000 
    
    def __init__(self, info):
        self.info = info
        self.partRoutes = {}
        self.partCost = {}
        self.partLoad = {}
        self.partTotalCost = 0
        self.completePartitionedSolution = {}
        self.printOutput = True
        self.outputLines = []
        self.depot = self.info.depotArc
        
    def genAuxGraphSP(self, routeOrig, depot=None):
        '''
        Generates the auxiliry graph and determines the shortest path through
        the graph - the optimal partition. Original route should not contain the 
        depot visits.
        '''
        if depot == None:
            depot = self.info.depotArc
        capacity = self.info.capacity
        spD = self.info.spDistanceD
        route = routeOrig[:]
        
        if self.info.dumpCost: dumpCost = self.info.dumpCost
        else: dumpCost = 0
        
        if route[0] == depot:
            del route[0]
        if route[ - 1] == depot:
            del route[ - 1]
        
        spRoute = [0]
        for i in range(1, len(route)): 
        # Determines the shortest path length between two arcs connected 
        # in original route.
            spRoute.append(spD[route[i - 1]][route[i]])
                
        sRoute = route[:]
        huge = 1e30000# Infinity
        dEst = {}
        piEst = {}
        L = {}
        G = {}
        
        auxNodes = range(len(sRoute) + 1)
        for i in auxNodes:
            dEst[i] = huge
            piEst[i] = None
        dEst[0] = 0
        
        for i in range(len(sRoute)):
            L[i] = {}
            G[i] = {}
            load = 0
            serviceC = 0
            spCosts = 0
            for j in range(i + 1, len(sRoute) + 1):
                load = load + self.info.demandD[sRoute[j - 1]]
                if load > capacity: break
                else:
                    if (j - i) > 1:
                        spCosts = spCosts + spD[sRoute[j - 2]][sRoute[j - 1]]
                    serviceC = serviceC + self.info.serveCostD[sRoute[j - 1]]
                    dDedge = spD[depot][sRoute[i]] + serviceC + spCosts + \
                             spD[sRoute[j - 1]][depot] + dumpCost 
                    L[i][j] = load
                    G[i][j] = dDedge
                    if dEst[j] > dEst[i] + dDedge:
                        dEst[j] = dEst[i] + dDedge
                        piEst[j] = i
        
        Path = SPmodules.sp1SourceList(piEst, auxNodes[0], auxNodes[ - 1])
        return(dEst[auxNodes[ - 1]], Path, G, L)
    
    def genPartitionClean(self, bigRoute):
        (finalDistance, Path, G, L) = self.genAuxGraphSP(bigRoute)
        depotArcs = self.info.depotArc
        nVehicles = len(Path) - 1
        partitionRoutes = {}
        partitionDistances = {}
        partitionLoads = {}
        for i in range(nVehicles):
            routeNoDepo = bigRoute[Path[i]:Path[i + 1]]
            partitionRoutes[i] = insDepot(routeNoDepo, depotArcs)
            partitionDistances[i] = G[Path[i]][Path[i+1]]
            partitionLoads[i] = L[Path[i]][Path[i + 1]]
        self.partRoutes = partitionRoutes
        self.partCost = partitionDistances
        self.partLoad = partitionLoads
        self.partTotalCost = finalDistance
    
    def genSolution(self, bigRoute, depo=None):
        '''
        Generate a partioned solution
        '''
        if depo == None:
            depo = self.info.depotArc
                
        (finalDistance, Path, G, L) = self.genAuxGraphSP(bigRoute)
        solutionIncomplete = spAuxToSolution(finalDistance, Path, bigRoute)
        
        iVehicles = solutionIncomplete.keys()
        nVehiclesCalc = len(Path) - 1
        if len(iVehicles) != nVehiclesCalc: 
            print('WTF')
   
        Tcost = 0
        
        for i in range(nVehiclesCalc):
            solutionIncomplete[iVehicles[i]]['Solution'] = insDepot(solutionIncomplete[iVehicles[i]]['Solution'], 
                                                                    depo)
            solutionIncomplete[iVehicles[i]]['Load'] = L[Path[i]][Path[i + 1]]
            solutionIncomplete[iVehicles[i]]['Cost'] = G[Path[i]][Path[i + 1]]
            Tcost = Tcost + G[Path[i]][Path[i + 1]]
        
        solutionIncomplete['Total cost'] = Tcost
        self.completePartitionedSolution = copy.deepcopy(solutionIncomplete)
        return(solutionIncomplete, nVehiclesCalc)
    
    def genInitialSolution(self, rule='MaxDepo'):
        init = giantRoute(self.info)
        init.genRoute(rule)
        (solution, nRoutes) = self.genSolution(init.RouteBig[1]['Solution'][1: - 1])
        return(solution, nRoutes)
    
    def genCompleteSolution(self):
        format = '%*d%*s%*d%*s%*d'
        bestSolutionCost = 1e300000
        bestSolutionNvehicles = 0
        minVehiclesBestSolutionCost = 1e300000
        minVehicles = 1e300000
        if self.printOutput:
            line = ' Ulusoy '
            print(line)
            self.outputLines.append(line)
            line = '------------------------------------------------------'
            print(line)
            self.outputLines.append(line)
            line = ' '
            print(line)
            self.outputLines.append(line)
        i = 0
        rules = ['MaxDepo','MinDepo','MaxYield','MinYield']
        for rule in rules:
            i += 1
            (solutionDict, nRoutes) = self.genInitialSolution(rule)
            if self.printOutput:
                line = format %(5,i+1,8,'Cost :', 7, solutionDict['Total cost'], 15, '# Trips :', 4, nRoutes)
                print(line)
                self.outputLines.append(line)
            if solutionDict['Total cost'] < bestSolutionCost:
                bestSolutionCost = solutionDict['Total cost']
                bestSolution = deepcopy(solutionDict)
                bestSolutionNvehicles = nRoutes
            if (nRoutes <= minVehicles) & (solutionDict['Total cost'] < minVehiclesBestSolutionCost):
                minVehiclesBestSolutionCost = solutionDict['Total cost']
                minVehiclesBestSolution = deepcopy(solutionDict)
                bestSolutionNvehicles = nRoutes
        line = ' '
        print(line)
        self.outputLines.append(line)
        line = '       Best solution : %d' %bestSolutionCost
        print(line)
        self.outputLines.append(line)
        line = '             # Trips : %d' %bestSolutionNvehicles
        print(line)
        self.outputLines.append(line)
        line = ' '
        print(line)
        self.outputLines.append(line)
        line = '  Min trips solution : %d' %minVehiclesBestSolutionCost
        print(line)
        self.outputLines.append(line)
        line = '             # Trips : %d' %bestSolutionNvehicles
        print(line)
        self.outputLines.append(line)
        return((bestSolution,bestSolutionNvehicles),(minVehiclesBestSolution,bestSolutionNvehicles))
    
    def genRandomSolution(self, nSolutions = 20, rule = 'RandomRule'):
        format = '%*d%*s%*d%*s%*d'
        bestSolutionCost = 1e300000
        bestSolutionNvehicles = 0
        minVehiclesBestSolutionCost = 1e300000
        minVehicles = 1e300000
        if self.printOutput:
            line = ' Ulusoy %s - Iterations %d' %(rule, nSolutions)
            print(line)
            self.outputLines.append(line)
            line = '------------------------------------------------------'
            print(line)
            self.outputLines.append(line)
            line = ' '
            print(line)
            self.outputLines.append(line)
        for i in range(nSolutions):
            (solutionDict, nRoutes) = self.genInitialSolution(rule)
            if self.printOutput:
                line = format %(5,i+1,8,'Cost :', 7, solutionDict['Total cost'], 15, '# Trips :', 4, nRoutes)
                print(line)
                self.outputLines.append(line)
            if solutionDict['Total cost'] < bestSolutionCost:
                bestSolutionCost = solutionDict['Total cost']
                bestSolution = deepcopy(solutionDict)
                bestSolutionNvehicles = nRoutes
            if (nRoutes <= minVehicles) & (solutionDict['Total cost'] < minVehiclesBestSolutionCost):
                minVehiclesBestSolutionCost = solutionDict['Total cost']
                minVehiclesBestSolution = deepcopy(solutionDict)
                bestSolutionNvehicles = nRoutes
        line = ' '
        print(line)
        self.outputLines.append(line)
        line = '       Best solution : %d' %bestSolutionCost
        print(line)
        self.outputLines.append(line)
        line = '             # Trips : %d' %bestSolutionNvehicles
        print(line)
        self.outputLines.append(line)
        line = ' '
        print(line)
        self.outputLines.append(line)
        line = '  Min trips solution : %d' %minVehiclesBestSolutionCost
        print(line)
        self.outputLines.append(line)
        line = '             # Trips : %d' %bestSolutionNvehicles
        print(line)
        self.outputLines.append(line)
        return((bestSolution,bestSolutionNvehicles),(minVehiclesBestSolution,bestSolutionNvehicles))
     
        
#===============================================================================
# Optimally partition a giant route by including trips to intermediate 
# facilities. Only works if there is one vehicle 
# and when there is one depot. No interdemiate facilities but can be converted
# to cater for multiple depots.
#===============================================================================
class UlusoysIFs_1vehicle(object):
    
    huge = 1e30000
    
    def __init__(self, info):
        self.info = info
        self.depot = self.info.depotArc
        
    def insIFsDepot(self, solutionIncomplete, bestIFs, Path, depot, routeOrig):
        iVehicle = solutionIncomplete.keys()
        for i in range(len(Path) - 1):
            sol = solutionIncomplete[iVehicle[i]]['Solution']
            if i == 0:
                sol.insert(0, depot)
            if len(routeOrig) == 1:
                sol.append(bestIFs[routeOrig[Path[i]]][depot])
            if i == (len(Path) - 2):
                sol.append(bestIFs[routeOrig[Path[i]]][depot])
                sol.append(depot)
            else:
                sol.append(bestIFs[routeOrig[Path[i+1]]][routeOrig[Path[i+1] + 1]])
                sol2 = solutionIncomplete[iVehicle[i + 1]]['Solution']
                sol2.insert(0, bestIFs[routeOrig[Path[i+1]]][routeOrig[Path[i+1]+ 1]])
                solutionIncomplete[iVehicle[i + 1]]['Solution'] = sol2
            solutionIncomplete[iVehicle[i]]['Solution'] = sol
        return(solutionIncomplete)
    
    def chooseBestIf(self, arcFrom, arcTo):
        IFs = self.info.IFarcs
        spD = self.info.spDistanceD
        bestIFdist = huge
        for i in IFs:
            dist = spD[arcFrom][i] + spD[i][arcTo]
            if dist < bestIFdist:
                bestIFdist = dist
                bestIF = i
        return(bestIFdist, bestIF)
            
    def  genAuxGraphSP(self, routeOrig, bestIFdistD, depot=None):
        '''
        Generates the auxiliry graph and determines the shortest path through
        the graph - the optimal partition. Original route should not contain the 
        depot visits.
        '''
        if depot == None:
            depot = self.info.depotArc
        capacity = self.info.capacity
        spD = self.info.spDistanceD
        route = routeOrig[:]

        if self.info.dumpCost: dumpCost = self.info.dumpCost
        else: dumpCost = 0
        
        if route[0] == depot:
            del route[0]
        if route[ - 1] == depot:
            del route[ - 1]
        
        spRoute = [0]
        for i in range(1, len(route)): # Determines the shortest path length between two arcs connected in original route.
            spRoute.append(spD[route[i - 1]][route[i]])
                
        sRoute = route[:]
              
        huge = 1e30000# Infinity
        dEst = {}
        piEst = {}
        L = {}
        G = {}
        IFbest = {}
        
        auxNodes = range(len(sRoute) + 1)
        for i in auxNodes:
            dEst[i] = huge
            piEst[i] = None
        dEst[0] = 0
        
        for i in range(len(sRoute)):
            L[i] = {}
            G[i] = {}
            IFbest[i] = {}
            load = 0
            serviceC = 0
            for j in range(i + 1, len(sRoute) + 1):
                load = load + self.info.demandD[sRoute[j - 1]]
                if load > capacity: break
                else:
                    serviceC = serviceC + self.info.serveCostD[sRoute[j - 1]]
                    if j == len(sRoute): 
                        bestIFdist = bestIFdistD[sRoute[j - 1]][depot]
                    else:
                        bestIFdist = bestIFdistD[sRoute[j - 1]][sRoute[j]]
                    if i == 0:
                        dDedge = spD[depot][sRoute[i]] + bestIFdist + serviceC + sum(spRoute[i + 1:j]) + dumpCost
                    else:
                        dDedge = bestIFdist + serviceC + sum(spRoute[i + 1:j]) + dumpCost 
                    L[i][j] = load
                    G[i][j] = dDedge
                    if dEst[j] > dEst[i] + dDedge:
                        dEst[j] = dEst[i] + dDedge
                        piEst[j] = i 
        
        Path = SPmodules.sp1SourceList(piEst, auxNodes[0], auxNodes[ - 1])
        return(dEst[auxNodes[ - 1]], Path, G, L)
        
    def genPartitionClean(self, routeOrig, bestIFdist, bestIF):
        (finalDistance, Path, G, L) = self.genAuxGraphSP(routeOrig, bestIFdist)
        return(finalDistance, Path, G, L)

    def genSolution(self, routeOrig):
        '''
        Generate a partioned solution
        '''
        bestIFs = self.info.bestIFD
        bestIFdist = self.info.bestIFdistD
        depot = self.info.depotArc
        
        (finalDistance, Path, G, L) = self.genAuxGraphSP(routeOrig, bestIFdist) 
        solutionIncomplete = spAuxToSolution(finalDistance, Path, routeOrig)
    
        
        iVehicles = solutionIncomplete.keys()
        nVehiclesCalc = len(Path) - 1
        if len(iVehicles) != nVehiclesCalc: 
            print('WTF')
   
        Tcost = 0
        
        solutionList = []
        loadList = []
        for i in range(nVehiclesCalc):
            solutionIncomplete[iVehicles[i]]['Load'] = L[Path[i]][Path[i + 1]]
            loadList.append(solutionIncomplete[iVehicles[i]]['Load'])
            solutionIncomplete[iVehicles[i]]['Cost'] = G[Path[i]][Path[i + 1]]
            solutionList.append(solutionIncomplete[iVehicles[i]]['Solution'])
            Tcost = Tcost + G[Path[i]][Path[i + 1]]
        solutionIncomplete['Total cost'] = Tcost
        solutionIncomplete = self.insIFsDepot(solutionIncomplete, bestIFs, Path, depot, routeOrig)
        self.completePartitionedSolution = copy.deepcopy(solutionIncomplete)

    def genSolutionList(self, routeOrig):
        '''
        Generate a partioned solution
        '''
        bestIFs = self.info.bestIFD
        bestIFdist = self.info.bestIFdistD
        depot = self.info.depotArc
        
        (finalDistance, Path, G, L) = self.genAuxGraphSP(routeOrig, bestIFdist) 
        solutionIncomplete = spAuxToSolution(finalDistance, Path, routeOrig)
    
        
        iVehicles = solutionIncomplete.keys()
        nVehiclesCalc = len(Path) - 1
        if len(iVehicles) != nVehiclesCalc: 
            print('WTF')
   
        cost = 0
        
        solutionList = []
        loadList = []
        for i in range(nVehiclesCalc):
            solutionList.append(solutionIncomplete[iVehicles[i]]['Solution'])
        for i in range(nVehiclesCalc):
            loadList.append(L[Path[i]][Path[i + 1]])
            cost += G[Path[i]][Path[i + 1]]
            if i == 0:
                solutionList[0].insert(0,depot)
            if i == (nVehiclesCalc-1):
                solutionList[i].append(bestIFs[solutionList[i][-1]][depot])
                solutionList[i].append(depot)
            else:
                solutionList[i].append(bestIFs[solutionList[i][-1]][solutionList[i+1][0]])
                solutionList[i+1].insert(0,bestIFs[solutionList[i][-2]][solutionList[i+1][0]])
        return(solutionList, loadList, cost)
    
    def genSubSolution(self, routeOrig):
        (solutionList, loadList, cost) = self.genSolutionList(routeOrig)
        solution = {'Solution':deepcopy(solutionList), 'Load':deepcopy(loadList),'Cost':cost}
        return(solution)
        

#===============================================================================
# Optimally partition a giant route by including trips to intermediate 
# facilities and by partitioning trips for different vehicles. Only works 
# if there is a maximum vehicle trip length and when there is one 
# depot.
#===============================================================================
class UlusoysIFs(object):
    
    huge = 1e30000 
    
    def __init__(self, info):
        self.info = info
        self.bestIF = info.bestIFD
        self.bestIFdist = info.bestIFdistD
        self.completePartitionedSolution = {}
        self.minN = reduceNumberTrips_IF.ReduceNumberOfVehicleRoutes(self.info)
        self.trans = transformSolution.transformSolution(self.info)
        self.printOutput = True
        self.outputLines = []
      
      
    def genAuxGraph1_SP(self, routeOrig, bestIFdistD, depot=None, maxTripLengthUpperLimitMulti=1000):
                                                                # maxTripLengthUpperLimitMulti=1): Old default
        '''
        Generates the auxiliry graph and determines the shortest path through
        the graph - the optimal partition. Original route should not contain the 
        depot visits.
        '''
        print('Gen Aux graph 1')
        
        if depot == None:
            depot = self.info.depotArc
        maxTripLength = self.info.maxTrip
        capacity = self.info.capacity
        spD = self.info.spDistanceD
        route = routeOrig[:]

        if self.info.dumpCost: dumpCost = self.info.dumpCost
        else: dumpCost = 0
        
        if route[0] == depot:
            del route[0]
        if route[ - 1] == depot:
            del route[ - 1]
        
        spRoute = [0]
        serviceRoute = []
        loadRoute = []
        
        for i in range(1, len(route)): # Determines the shortest path length between two arcs connected in original route.
            spRoute.append(spD[route[i - 1]][route[i]])
            serviceRoute.append(self.info.serveCostD[route[i - 1]])
            loadRoute.append(self.info.demandD[route[i - 1]])
            
        serviceRoute.append(self.info.serveCostD[route[i]])
        loadRoute.append(self.info.demandD[route[i]])
                
        sRoute = route[:]     
               
        huge = 1e30000# Infinity
        dEst = {}
        piEst = {}
        
        nReqArcs = len(sRoute)
        auxNodes = range(nReqArcs + 1)
        
        print('Initialise 1')
        for s in auxNodes:
            dEst[s] = {}
            piEst[s] = {}
            for v in range(s, nReqArcs + 1):
                dEst[s][v] = huge
                piEst[s][v] = None
            dEst[s][s] = 0
        
        startQ = 0
        maxTripLengthUpperLimit = maxTripLengthUpperLimitMulti * maxTripLength
        print('gen 1')
        for i in range(nReqArcs):
            print('arc %d of %d' %(i,nReqArcs))
            load = 0
            serv = 0
            for j in range(i + 1, nReqArcs + 1):
                load = load + self.info.demandD[sRoute[j - 1]]
                serv = serv + self.info.serveCostD[sRoute[j - 1]]

                if load > capacity: break
                else:
                    dDedge = 0
                    if j == len(sRoute): 
                        bestIFdist = bestIFdistD[sRoute[j - 1]][depot]
                    else:
                        bestIFdist = bestIFdistD[sRoute[j - 1]][sRoute[j]]
                    for q in range(startQ, i + 1):
                        dDedge = bestIFdist + sum(serviceRoute[i:j]) + sum(spRoute[i + 1:j]) + dumpCost 
                        if dEst[q][j] > dEst[q][i] + dDedge:
                            dEst[q][j] = dEst[q][i] + dDedge
                            piEst[q][j] = i
#                        if dEst[q][j] > maxTripLengthUpperLimit:
#                            startQ = startQ + 1
#                            break
        print('Finished 1')
        return(dEst, piEst, loadRoute)
    
    def  genAuxGraph2_SP(self, dEstIFs, routeOrig, bestIFdistD, depot=None):
        '''
        Calculates the optimal vehicle partition using the optimal IF partition.
        '''
        print('Gen Aux graph 2')
        huge = 1e30000# Infinity

        if depot == None:
            depot = self.info.depotArc
        
        
        spD = self.info.spDistanceD
        maxTripLength = self.info.maxTrip
        route = routeOrig[:]
        
        
        if route[0] == depot:
            del route[0]
        if route[ - 1] == depot:
            del route[ - 1]
        
        dEst = {}
        piEst = {}
        G = {}
        sRoute = route[:]
        
        nReqArcs = len(sRoute)
        auxNodes = range(nReqArcs + 1)        
        print('Initialise 2')
        for i in auxNodes:
            dEst[i] = huge
            piEst[i] = None
            
        dEst[0] = 0
        print('gen 2')
        for i in range(len(sRoute)):
            G[i] = {}
            serviceC = 0
            for j in range(i + 1, len(sRoute) + 1):
                if j == len(sRoute):
                    Edge = spD[depot][sRoute[i]] + dEstIFs[i][j]
                else:
                    Edge = spD[depot][sRoute[i]] + dEstIFs[i][j] - bestIFdistD[sRoute[j - 1]][sRoute[j]] + bestIFdistD[sRoute[j - 1]][depot]
                
                serviceC = serviceC + Edge
                
                if Edge > maxTripLength: break
                else:
                    G[i][j] = Edge
                    if dEst[j] > dEst[i] + Edge:
                        dEst[j] = dEst[i] + Edge
                        piEst[j] = i
        Path = SPmodules.sp1SourceList(piEst, auxNodes[0], auxNodes[ - 1])
        print('finished 2')
        return(dEst[auxNodes[-1]], Path, G)
    
    def partition(self, routeOrig, Path, piEst, bestIF, loadRoute, depo=None):
        '''
        Partition original giant route using the SP through two auxilary graphs.
        Inserts depots and the intermediate facilities, and recors the vehicle
        load and route costs.
        '''
        if depo == None:
            depo = self.info.depotArc
        nVehicles = len(Path) - 1
        incompleteSolution = {}
        for i in range(nVehicles):
            loads = []
            incompleteSolution[i + 1] = {}
            vehicleRoute = []
            start = Path[i]
            stop = Path[i + 1]
            piEstTemp = piEst[Path[i]]
            IFPath = SPmodules.sp1SourceList(piEstTemp, start, stop)
            nIFs = len(IFPath) - 1
            for j in range(nIFs):
                startIF = IFPath[j]
                stopIF = IFPath[j + 1]
                routeIF = routeOrig[startIF:stopIF]
                loads.append(sum(loadRoute[startIF:stopIF]))
                if (j + 1) == nIFs:
                    insertIF = bestIF[routeOrig[IFPath[j + 1] - 1]][depo]
                    routeIF.append(insertIF)
                    routeIF.append(depo)
                else:
                    insertIF = bestIF[routeOrig[IFPath[j + 1] - 1]][routeOrig[IFPath[j + 1]]]
                    routeIF.append(insertIF)
                if j == 0:
                    routeIF.insert(0, depo)
                else:
                    insertIFStart = bestIF[routeOrig[IFPath[j] - 1]][routeOrig[IFPath[j]]]
                    routeIF.insert(0, insertIFStart)
                vehicleRoute.append(routeIF)
            incompleteSolution[i + 1]['Solution'] = vehicleRoute
            incompleteSolution[i + 1]['Load'] = loads
        return(incompleteSolution)
    
#    def genPartitionClean(self, routeOrig, bestIFdist, bestIF, depo=None):
#        (dEst, piEst, loadRoute) = self.genAuxGraph1_SP(routeOrig, bestIFdist)
#        (finalCost, Path, G) = self.genAuxGraph2_SP(dEst, routeOrig, bestIFdist)
#        return(finalCost, Path, G)
    
    def genSolution(self, routeOrig, bestIFdist, bestIF, depo=None):
        '''
        Generate a partioned solution using two auxilary graphs. One from all to 
        all optimal optimal IF partitions, and one from optimal vehcile route
        partition.
        '''
        if depo == None:
            depo = self.info.depotArc
                
        (dEst, piEst, loadRoute) = self.genAuxGraph1_SP(routeOrig, bestIFdist)
        (finalCost, Path, G) = self.genAuxGraph2_SP(dEst, routeOrig, bestIFdist)
        
        
        solutionIncomplete = self.partition(routeOrig, Path, piEst, bestIF, loadRoute)
        iVehicles = solutionIncomplete.keys()
        
        nVehiclesCalc = len(Path) - 1
        if len(iVehicles) != nVehiclesCalc: 
            print('WTF')
   
        Tcost = 0
        for i in range(nVehiclesCalc):
            solutionIncomplete[iVehicles[i]]['Cost'] = G[Path[i]][Path[i + 1]]
            Tcost = Tcost + G[Path[i]][Path[i + 1]]
        solutionIncomplete['Total cost'] = finalCost
        self.completePartitionedSolution = solutionIncomplete
        nTrips = nVehiclesCalc
        return(solutionIncomplete, nTrips)
        
    def genInitialSolution(self, rule='MaxDepo'):
        init = giantRoute(self.info)
        init.genRoute(rule)
        return(init.RouteBig[1]['Solution'][1: - 1])
    
    def genSolution_IFs(self, rule='MaxDepo'):
        bestIFdist, bestIF = self.info.bestIFdistD, self.info.bestIFD
        routeOrig = self.genInitialSolution(rule)
        (solutionIncomplete, nTrips) = self.genSolution(routeOrig, bestIFdist, bestIF)
        return(solutionIncomplete, nTrips)
    
    def genInitialIFSolutionFromGiantRoute(self, routeOrig):
        bestIFdist, bestIF = self.info.bestIFdistD, self.info.bestIFD
        (solutionDict, nTrips) = self.genSolution(routeOrig, bestIFdist, bestIF)
        solutionDict = self.trans.newRoute(solutionDict)
        return(solutionDict, nTrips)
    
    def genCompleteSolution(self):
        format = '%*d%*s%*d%*s%*d'
        bestSolutionCost = 1e300000
        bestSolutionNvehicles = 0
        minVehiclesBestSolutionCost = 1e300000
        minVehicles = 1e300000
        if self.printOutput:
            line = ' Ulusoy '
            print(line)
            self.outputLines.append(line)
            line = '------------------------------------------------------'
            print(line)
            self.outputLines.append(line)
            line = ' '
            print(line)
            self.outputLines.append(line)
        i = 0
        rules = ['MaxDepo','MinDepo','MaxYield','MinYield']
        for rule in rules:
            i += 1
            (solutionDict, nRoutes) = self.genSolution_IFs(rule)
            solutionDict = self.trans.newRoute(solutionDict)
            (solutionDict, reduced,  nRoutes) = self.minN.variableReduction(solutionDict)
            if self.printOutput:
                line = format %(5,i+1,8,'Cost :', 7, solutionDict['Total cost'], 15, '# Trips :', 4, nRoutes)
                print(line)
                self.outputLines.append(line)
            if solutionDict['Total cost'] < bestSolutionCost:
                bestSolutionCost = solutionDict['Total cost']
                bestSolution = deepcopy(solutionDict)
                bestSolutionNvehicles = nRoutes
            if (nRoutes <= minVehicles) & (solutionDict['Total cost'] < minVehiclesBestSolutionCost):
                minVehiclesBestSolutionCost = solutionDict['Total cost']
                minVehiclesBestSolution = deepcopy(solutionDict)
                bestSolutionNvehicles = nRoutes
        line = ' '
        print(line)
        self.outputLines.append(line)
        line = '       Best solution : %d' %bestSolutionCost
        print(line)
        self.outputLines.append(line)
        line = '             # Trips : %d' %bestSolutionNvehicles
        print(line)
        self.outputLines.append(line)
        line = ' '
        print(line)
        self.outputLines.append(line)
        line = '  Min trips solution : %d' %minVehiclesBestSolutionCost
        print(line)
        self.outputLines.append(line)
        line = '             # Trips : %d' %bestSolutionNvehicles
        print(line)
        self.outputLines.append(line)
        return((bestSolution,bestSolutionNvehicles),(minVehiclesBestSolution,bestSolutionNvehicles))

    def genRandomSolution(self, nSolutions = 20, rule = 'RandomRule'):
        format = '%*d%*s%*d%*s%*d'
        bestSolutionCost = 1e300000
        bestSolutionNvehicles = 0
        minVehiclesBestSolutionCost = 1e300000
        minVehicles = 1e300000
        if self.printOutput:
            line = ' Ulusoy %s - Iterations %d' %(rule, nSolutions)
            print(line)
            self.outputLines.append(line)
            line = '------------------------------------------------------'
            print(line)
            self.outputLines.append(line)
            line = ' '
            print(line)
            self.outputLines.append(line)
        for i in range(nSolutions):
            (solutionDict, nRoutes) = self.genSolution_IFs(rule)
            solutionDict = self.trans.newRoute(solutionDict)
            (solutionDict, reduced,  nRoutes) = self.minN.variableReduction(solutionDict)
            if self.printOutput:
                line = format %(5,i+1,8,'Cost :', 7, solutionDict['Total cost'], 15, '# Trips :', 4, nRoutes)
                print(line)
                self.outputLines.append(line)
            if solutionDict['Total cost'] < bestSolutionCost:
                bestSolutionCost = solutionDict['Total cost']
                bestSolution = deepcopy(solutionDict)
                bestSolutionNvehicles = nRoutes
            if (nRoutes <= minVehicles) & (solutionDict['Total cost'] < minVehiclesBestSolutionCost):
                minVehiclesBestSolutionCost = solutionDict['Total cost']
                minVehiclesBestSolution = deepcopy(solutionDict)
                bestSolutionNvehicles = nRoutes
        line = ' '
        print(line)
        self.outputLines.append(line)
        line = '       Best solution : %d' %bestSolutionCost
        print(line)
        self.outputLines.append(line)
        line = '             # Trips : %d' %bestSolutionNvehicles
        print(line)
        self.outputLines.append(line)
        line = ' '
        print(line)
        self.outputLines.append(line)
        line = '  Min trips solution : %d' %minVehiclesBestSolutionCost
        print(line)
        self.outputLines.append(line)
        line = '             # Trips : %d' %bestSolutionNvehicles
        print(line)
        self.outputLines.append(line)
        return((bestSolution,bestSolutionNvehicles),(minVehiclesBestSolution,bestSolutionNvehicles))

if __name__ == "__main__":

    file = 'TransformedInput/LPR_benchmarkProblems/Lpr-c-01_pickled.txt'
    file2 = 'TransformedInput/LPR_benchmarkProblems/Lpr-b-01_IFs_pickled.txt'

    

    

