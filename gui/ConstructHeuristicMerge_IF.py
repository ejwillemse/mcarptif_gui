'''
Created on 10 Jun 2010

@author: EWillemse
'''
from numpy import *
from copy import deepcopy
import reduceNumberTrips_IF

class MergeHeuristic(object):

    def __init__(self, info):
        '''
        Returns a Merge initial solution
        '''
        self.info = info
        self.printOutput = True
        self.outPutLines = []
        self.SP = self.info.spDistanceD
        self.depot = self.info.depotArc
        self.demand = self.info.demandD
        self.serviceCost = self.info.serveCostD
        self.invArc = self.info.invArcD
        self.IF_arc = self.info.bestIFD
        self.IF_dist = self.info.bestIFdistD
        self.maxTrip = self.info.maxTrip
        self.dumpCost= self.info.dumpCost
        self.minN = reduceNumberTrips_IF.ReduceNumberOfVehicleRoutes(self.info)
    
    def transformSolutionDict(self, solution):
        newSolution = {}
        for i in solution:
            if i != 'Total cost':
                newSolution[i] = {}
                newSolution[i]['Load'] = []
                newSolution[i]['Subtrip cost'] = []
                newSolution[i]['Solution'] = []
                loads = solution[i]['Load']
                subtripcost = solution[i]['Subtrip cost']
                routes = solution[i]['Solution']
                for j in routes:
                    newList = []
                    for q in j:
                        newList.append(int(str(q)))
                    newSolution[i]['Solution'].append(newList[:])
                for j in loads:
                    newSolution[i]['Load'].append(int(str(j)))
                for j in subtripcost:
                    newSolution[i]['Subtrip cost'].append(int(str(j)))
                ge = int(str(solution[i]['Cost']))
                newSolution[i]['Cost'] = ge
            else:
                newSolution[i] = int(str(solution[i]))
        return(newSolution)
        
    def makeSolution(self, routes):
        solutionDict = {}
        r = 0
        tCost = 0
        beginArc = []
        beginArcD = {}
        for route in routes.itervalues():
                solutionDictTemp = {}
                solutionDictTemp['Load'] = route['Load']
                solutionDictTemp['Solution'] = [self.depot] + route['Route'] + [self.depot]
                solutionDictTemp['Cost'] = self.routeCost(solutionDictTemp['Solution']) + self.info.dumpCost
                endArc = route['Route'][-1]
                if self.invArc[endArc] not in beginArc:
                    beginArc.append(route['Route'][0])
                    beginArcD[route['Route'][0]] = {'Key':r,'Cost':solutionDictTemp['Cost']}
                    r += 1
                    solutionDict[r] = deepcopy(solutionDictTemp)
                    tCost += solutionDict[r]['Cost']
                elif solutionDictTemp['Cost'] < beginArcD[self.invArc[endArc]]['Cost']:
                    solutionDict[beginArcD[self.invArc[endArc]]['Key']] =  deepcopy(solutionDictTemp)
                    tCost += solutionDictTemp['Cost'] - beginArcD[self.invArc[endArc]]['Cost']
        solutionDict['Total cost'] = tCost
        return(solutionDict)

    def genArcListPure(self):
        arcListNP = array(self.info.reqArcList, dtype = int)        
        return(arcListNP)

    def blockSort(self, block, routeLoads):
        for i, merge in enumerate(block):
            arcI, arcJ = merge['iArc'], merge['jArc']
            block[i]['sortCriteria'] = -abs(routeLoads[arcI]-routeLoads[arcJ])
        block.sort(order = ['sortCriteria','loadKey'])
        return(block)
    
    def createMergedSolutionPhase1(self):
        '''
        '''
        requiredArcList = self.genArcListPure()
        newInverseList = deepcopy(self.invArc)
        nRequiredArcs = shape(requiredArcList)[0]
#        nEdges = len(self.info.reqEdges)

        nEdgesAct = 0
        for i in requiredArcList:
            if  self.invArc[i]: nEdgesAct += 1
        
        nEdges = nEdgesAct/2

        nMerges = nRequiredArcs*(nRequiredArcs-1)-2*nEdges
        mergeMap = ones((nRequiredArcs,nRequiredArcs), dtype=int)
        mergeMatrix = zeros((nRequiredArcs,nRequiredArcs), dtype=int)
        routePointer = array(range(nRequiredArcs), dtype=int)
        mergeDeltaList = zeros((nMerges),dtype = [('Delta',int), ('iArc',int), ('jArc',int), ('I',int), ('J',int), ('sortCriteria',int),('loadKey',int) ])
        loads = zeros((nRequiredArcs),dtype=int)
        savingsDictionary = {}
        inverseMapKey = {}
        
        routes = {}
        routeEndArc = {}
        routeIndex = {}
        
        i = -1
        
        loadKeyList = range(nMerges)
        for indexI, arcI in enumerate(requiredArcList):
            routes[indexI] = {}
            routes[indexI]['Load'] = self.info.demandD[arcI]
            loads[indexI] = self.info.demandD[arcI]
            routes[indexI]['Route'] = [arcI]
            routes[indexI]['ArcIndex'] = [indexI]
            routeEndArc[indexI] = indexI
            savingsArcI = self.SP[arcI][self.depot]
            if indexI == 0:routeIndex[arcI] = indexI
            inverseI = newInverseList[arcI]
            for indexJ, arcJ in enumerate(requiredArcList):
                if indexI == 0:routeIndex[arcJ] = indexJ 
                if (indexI != indexJ):# & (arcJ != inverseI):
                    if arcJ != inverseI:
                        i += 1
                        saveDelta = self.SP[arcI][arcJ] - savingsArcI - self.SP[self.depot][arcJ] - self.info.dumpCost
                        loadKey = 100000
                        if newInverseList[arcI]: # & (newInverseList[arcJ] != None):
                            if newInverseList[arcJ]:
                                if inverseMapKey.get((newInverseList[arcJ], newInverseList[arcI])):
                                    inverseIndexI, inverseIndexJ = routeIndex[newInverseList[arcI]], routeIndex[newInverseList[arcJ]]
                                    saveDelta = min(mergeMatrix[inverseIndexJ, inverseIndexI], saveDelta)
                                    loadKey = inverseMapKey[(newInverseList[arcJ], newInverseList[arcI])]
                                else:
                                    loadKey =  loadKeyList.pop()
                                    inverseMapKey[(arcI, arcJ)] = loadKey
                        if savingsDictionary.get(saveDelta):savingsDictionary[saveDelta] += [i]
                        else:savingsDictionary[saveDelta] = [i]
                        invSort = -abs(self.info.demandD[arcI]-self.info.demandD[arcJ])
                        mergeMatrix[indexI, indexJ] = saveDelta
                        mergeDeltaList[i] = (saveDelta, indexI, indexJ, arcI, arcJ, invSort, loadKey)

        mergeDeltaList.sort(order = ['Delta','sortCriteria','loadKey'])
        countMerge = 0
        for iMerge, merge in enumerate(mergeDeltaList):
            if len(savingsDictionary[merge['Delta']]) > 1:
                blockChange = mergeDeltaList[iMerge:len(savingsDictionary[merge['Delta']])+iMerge]
                blockChange = self.blockSort(blockChange, loads)
                mergeDeltaList[iMerge:len(savingsDictionary[merge['Delta']])+iMerge] = blockChange
                merge = mergeDeltaList[iMerge]
                savingsDictionary[merge['Delta']] = [0] 

            arcI, arcJ = merge['iArc'], merge['jArc']
            I, J = merge['I'], merge['J']
            if mergeMap[arcI,arcJ]:
                pointI, pointJ = routePointer[arcI], routePointer[arcJ]
                mergedLoad = routes[pointI]['Load'] + routes[pointJ]['Load']
                mergeCost = self.routeCost(routes[pointI]['Route'] + routes[pointJ]['Route'])
                if (mergedLoad <= self.info.capacity) & (mergeCost <= self.maxTrip):
                    routes[pointI]['ArcIndex'] += routes[pointJ]['ArcIndex']
                    routes[pointI]['Route'] += routes[pointJ]['Route']
                    routes[pointI]['Load'] = mergedLoad
                    loads[pointI] = mergedLoad
                    mergeMap[merge['iArc'],:] = 0
                    mergeMap[:,merge['jArc']] = 0
                    if (newInverseList[I] != None) & (newInverseList[J] != None):
                        invRouteI = routeIndex[newInverseList[I]]
                        invRouteJ = routeIndex[newInverseList[J]]
                        if mergeMatrix[invRouteJ, invRouteI] != mergeMatrix[arcI, arcJ]:
                            invRouteI = routeIndex[newInverseList[I]]
                            invPointI = routePointer[invRouteI]
                            Ibegin = routes[invPointI]['Route'][0]
                            Iend = routes[invPointI]['Route'][-1]
                            invRouteIbegin = routes[invPointI]['ArcIndex'][0]
                            invRouteIend = routes[invPointI]['ArcIndex'][-1]
                            mergeMap[invRouteIend,:]=0
                            mergeMap[:, invRouteIbegin]=0
                            del routes[invPointI]
                            newInverseList[newInverseList[Iend]] = None
                            newInverseList[newInverseList[Ibegin]] = None
                            invRouteJ = routeIndex[newInverseList[J]]
                            invPointJ = routePointer[invRouteJ]
                            Jbegin = routes[invPointJ]['Route'][0]
                            Jend = routes[invPointJ]['Route'][-1]
                            invRouteJbegin = routes[invPointJ]['ArcIndex'][0]
                            invRouteJend = routes[invPointJ]['ArcIndex'][-1]
                            mergeMap[invRouteJend,:]=0
                            mergeMap[:,invRouteJbegin]=0
                            del routes[invPointJ]
                            newInverseList[newInverseList[Jend]] = None
                            newInverseList[newInverseList[Jbegin]] = None                            
                    if (newInverseList[I] != None) & (newInverseList[J] == None):
                        invRouteI = routeIndex[newInverseList[I]]
                        invPointI = routePointer[invRouteI]
                        Ibegin = routes[invPointI]['Route'][0]
                        Iend = routes[invPointI]['Route'][-1]
                        invRouteIbegin = routes[invPointI]['ArcIndex'][0]
                        invRouteIend = routes[invPointI]['ArcIndex'][-1]
                        mergeMap[invRouteIend,:]=0
                        mergeMap[:, invRouteIbegin]=0
                        del routes[invPointI]
                        newInverseList[newInverseList[Iend]] = None
                        newInverseList[newInverseList[Ibegin]] = None
                    elif (newInverseList[I] == None) & (newInverseList[J] != None):
                        invRouteJ = routeIndex[newInverseList[J]]
                        invPointJ = routePointer[invRouteJ]
                        Jbegin = routes[invPointJ]['Route'][0]
                        Jend = routes[invPointJ]['Route'][-1]
                        invRouteJbegin = routes[invPointJ]['ArcIndex'][0]
                        invRouteJend = routes[invPointJ]['ArcIndex'][-1]
                        mergeMap[invRouteJend,:]=0
                        mergeMap[:,invRouteJbegin]=0
                        del routes[invPointJ]
                        newInverseList[newInverseList[Jend]] = None
                        newInverseList[newInverseList[Jbegin]] = None
                    mergeMap[routeEndArc[pointJ], pointI] = 0
                    routePointer[routes[pointJ]['ArcIndex']] = routePointer[arcI]
                    loads[routes[pointJ]['ArcIndex']] = mergedLoad
                    routeEndArc[pointI] = routeEndArc[pointJ]
                    del routeEndArc[pointJ]
                    del routes[arcJ]
                    countMerge += 1
                    print('{201} Merge phase 1: %d Routes left %d'%(countMerge,len(routes)))
        return(routes)
    
    def secondPhaseArcs(self, routes):
        k = 0
        routeBegin = {}
        routeEnd = {}
        arcBegin = {}
        invRoutes = {}
        routeInfo = {}
        routeCost = {}
        nEdges = 0
        print('{212}',len(routes))
        for route in routes.itervalues():
            k +=1
            routeInfo[k] = deepcopy(route)
            routeCost[k] = self.routeCost(route['Route'])
            routeBegin[k] = route['Route'][0]
            routeEnd[k] = route['Route'][-1]
            arcBegin[route['Route'][0]] = k
            invRoute = arcBegin.get(self.invArc[route['Route'][-1]])
            if invRoute:
                invRoutes[k]= invRoute
                invRoutes[invRoute] = k
                nEdges += 1
            else:
                invRoutes[k] = None
        print('{226}',invRoutes)
        return(routeInfo, routeCost, routeBegin, routeEnd, invRoutes, nEdges)
    
    def routeCost(self, route):
        cost = self.SP[self.depot][route[0]] + self.serviceCost[route[0]]
        for i, arc in enumerate(route[1:]):
            cost += self.serviceCost[arc] + self.SP[route[i]][arc]
        cost += self.IF_dist[route[-1]][self.depot] + self.dumpCost
        return(cost)
    
    def blockSort2(self, block, costs):
        for i, merge in enumerate(block):
            arcI, arcJ = merge['iArc'], merge['jArc']
            block[i]['sortCriteria'] = -abs(costs[arcI]-costs[arcJ])
        block.sort(order = ['sortCriteria','loadKey'])
        return(block)
    
    def createMergedSolutionPhase2(self, routeInfo, routeCost, routeBegin, routeEnd, invRoute, nEdges):
        '''
        '''
        requiredArcList = routeInfo.keys()
        nRequiredArcs = shape(requiredArcList)[0]
        newInverseList = deepcopy(invRoute)
        
        nMerges = nRequiredArcs*(nRequiredArcs-1)-2*nEdges
        mergeMap = ones((nRequiredArcs,nRequiredArcs), dtype=int)
        mergeMatrix = zeros((nRequiredArcs,nRequiredArcs), dtype=int)
        routePointer = array(range(nRequiredArcs), dtype=int)
        mergeDeltaList = zeros((nMerges),dtype = [('Delta',int), ('iArc',int), ('jArc',int), ('I',int), ('J',int), ('sortCriteria',int),('loadKey',int) ])
        costs = zeros((nRequiredArcs),dtype=int)
        savingsDictionary = {}
        inverseMapKey = {}
        
        routes = {}
        routeEndArc = {}
        routeIndex = {}
        
        i = -1
        costKeyList = range(nMerges)
        for indexI, arcI in enumerate(requiredArcList):
            routes[indexI] = {}
            routes[indexI]['Cost'] = routeCost[arcI]
            costs[indexI] = routeCost[arcI]
            routes[indexI]['Route'] = [arcI]
            routes[indexI]['ArcIndex'] = [indexI]
            routeEndArc[indexI] = indexI
            arcIActual = routeEnd[arcI]
            savingsArcI = self.IF_dist[arcIActual][self.depot]
            if indexI == 0:routeIndex[arcI] = indexI
            inverseI = newInverseList[arcI]
            for indexJ, arcJ in enumerate(requiredArcList):
                if indexI == 0:routeIndex[arcJ] = indexJ 
                if (indexI != indexJ):# & (arcJ != inverseI):
                    if arcJ != inverseI:
                        i += 1
                        arcJActual = routeBegin[arcJ]
                        saveDelta = self.IF_dist[arcIActual][arcJActual] - savingsArcI - self.SP[self.depot][arcJActual]
                        costKey = 100000
                        if newInverseList[arcI]: # & (newInverseList[arcJ] != None):
                            if newInverseList[arcJ]:
                                if inverseMapKey.get((newInverseList[arcJ], newInverseList[arcI])):
                                    inverseIndexI, inverseIndexJ = routeIndex[newInverseList[arcI]], routeIndex[newInverseList[arcJ]]
                                    saveDelta = min(mergeMatrix[inverseIndexJ, inverseIndexI], saveDelta)
                                    costKey = inverseMapKey[(newInverseList[arcJ], newInverseList[arcI])]
                                else:
                                    costKey =  costKeyList.pop()
                                    inverseMapKey[(arcI, arcJ)] = costKey
                        if savingsDictionary.get(saveDelta):savingsDictionary[saveDelta] += [i]
                        else:savingsDictionary[saveDelta] = [i]
                        invSort = -abs(routeCost[arcI]-routeCost[arcJ])
                        mergeMatrix[indexI, indexJ] = saveDelta
                        mergeDeltaList[i] = (saveDelta, indexI, indexJ, arcI, arcJ, invSort, costKey)

        mergeDeltaList.sort(order = ['Delta','sortCriteria','loadKey'])
        countMerge = 0
        for iMerge, merge in enumerate(mergeDeltaList):
            if len(savingsDictionary[merge['Delta']]) > 1:
                blockChange = mergeDeltaList[iMerge:len(savingsDictionary[merge['Delta']])+iMerge]
                blockChange = self.blockSort2(blockChange, costs)
                mergeDeltaList[iMerge:len(savingsDictionary[merge['Delta']])+iMerge] = blockChange
                merge = mergeDeltaList[iMerge]
                savingsDictionary[merge['Delta']] = [0] 

            arcI, arcJ = merge['iArc'], merge['jArc']
            I, J = merge['I'], merge['J']
            if mergeMap[arcI,arcJ]:
                pointI, pointJ = routePointer[arcI], routePointer[arcJ]
                mergedCost = costs[pointI] + costs[pointJ] + merge['Delta']
                if mergedCost <= self.maxTrip:
                    routes[pointI]['ArcIndex'] += routes[pointJ]['ArcIndex']
                    routes[pointI]['Route'] += routes[pointJ]['Route']
                    routes[pointI]['Cost'] = mergedCost
                    costs[pointI] = mergedCost
                    mergeMap[merge['iArc'],:] = 0
                    mergeMap[:,merge['jArc']] = 0
                    if (newInverseList[I] != None) & (newInverseList[J] != None):
                        invRouteI = routeIndex[newInverseList[I]]
                        invRouteJ = routeIndex[newInverseList[J]]
                        if mergeMatrix[invRouteJ, invRouteI] != mergeMatrix[arcI, arcJ]:
                            invRouteI = routeIndex[newInverseList[I]]
                            invPointI = routePointer[invRouteI]
                            Ibegin = routes[invPointI]['Route'][0]
                            Iend = routes[invPointI]['Route'][-1]
                            invRouteIbegin = routes[invPointI]['ArcIndex'][0]
                            invRouteIend = routes[invPointI]['ArcIndex'][-1]
                            mergeMap[invRouteIend,:]=0
                            mergeMap[:, invRouteIbegin]=0
                            del routes[invPointI]
                            newInverseList[newInverseList[Iend]] = None
                            newInverseList[newInverseList[Ibegin]] = None
                            invRouteJ = routeIndex[newInverseList[J]]
                            invPointJ = routePointer[invRouteJ]
                            Jbegin = routes[invPointJ]['Route'][0]
                            Jend = routes[invPointJ]['Route'][-1]
                            invRouteJbegin = routes[invPointJ]['ArcIndex'][0]
                            invRouteJend = routes[invPointJ]['ArcIndex'][-1]
                            mergeMap[invRouteJend,:]=0
                            mergeMap[:,invRouteJbegin]=0
                            del routes[invPointJ]
                            newInverseList[newInverseList[Jend]] = None
                            newInverseList[newInverseList[Jbegin]] = None                            
                    if (newInverseList[I] != None) & (newInverseList[J] == None):
                        invRouteI = routeIndex[newInverseList[I]]
                        invPointI = routePointer[invRouteI]
                        Ibegin = routes[invPointI]['Route'][0]
                        Iend = routes[invPointI]['Route'][-1]
                        invRouteIbegin = routes[invPointI]['ArcIndex'][0]
                        invRouteIend = routes[invPointI]['ArcIndex'][-1]
                        mergeMap[invRouteIend,:]=0
                        mergeMap[:, invRouteIbegin]=0
                        del routes[invPointI]
                        newInverseList[newInverseList[Iend]] = None
                        newInverseList[newInverseList[Ibegin]] = None
                    elif (newInverseList[I] == None) & (newInverseList[J] != None):
                        invRouteJ = routeIndex[newInverseList[J]]
                        invPointJ = routePointer[invRouteJ]
                        Jbegin = routes[invPointJ]['Route'][0]
                        Jend = routes[invPointJ]['Route'][-1]
                        invRouteJbegin = routes[invPointJ]['ArcIndex'][0]
                        invRouteJend = routes[invPointJ]['ArcIndex'][-1]
                        mergeMap[invRouteJend,:]=0
                        mergeMap[:,invRouteJbegin]=0
                        del routes[invPointJ]
                        newInverseList[newInverseList[Jend]] = None
                        newInverseList[newInverseList[Jbegin]] = None
                    mergeMap[routeEndArc[pointJ], pointI] = 0
                    routePointer[routes[pointJ]['ArcIndex']] = routePointer[arcI]
                    costs[routes[pointJ]['ArcIndex']] = mergedCost
                    routeEndArc[pointI] = routeEndArc[pointJ]
                    del routeEndArc[pointJ]
                    del routes[arcJ]
                    countMerge += 1
                    print('{380} Merge phase 2: %d Routes left %d'%(countMerge,len(routes)))
        return(routes)
    
    def routeCost2(self, route):
        cost = self.serviceCost[route[0]]
        for i, arc in enumerate(route[1:]):
            cost += self.serviceCost[arc] + self.SP[route[i]][arc]
        cost += self.dumpCost
        return(cost)
    
    def createFinalSolution(self, routes_phase1, routes_phase2, invRoute):
        solutionDict = {}
        k = 0
        routeBegin = {}
        TTcost = 0
        for i in routes_phase2:
            k += 1
            solutionDict[k] = {}
            Route = routes_phase2[i]['Route']
            routeBegin[Route[0]] = k     
            nSubTrips = len(Route)
            subRouteKey1 = Route[0]
            subRoute = [[self.depot]+routes_phase1[subRouteKey1]['Route']]
            subLoad =  [routes_phase1[subRouteKey1]['Load']]
            for j in range(1,nSubTrips):
                subRouteKeyJ = Route[j]
                R = routes_phase1[subRouteKeyJ]['Route']
                L = routes_phase1[subRouteKeyJ]['Load']
                IF = self.IF_arc[subRoute[j-1][-1]][R[0]]
                R = [IF] + R
                subRoute[j-1] = subRoute[j-1] + [IF]
                subRoute += [R]
                subLoad += [L]
            subRoute[-1] += [self.IF_arc[subRoute[-1][-1]][self.depot]] + [self.depot]
            costs = []
            tCost = 0
            for j in range(nSubTrips):
                costs.append(self.routeCost2(subRoute[j]))
                tCost += costs[-1]
            invSolution = routeBegin.get(invRoute[Route[-1]])
            if invSolution:
                if tCost < solutionDict[invSolution]['Cost']:
                    TTcost += tCost - solutionDict[invSolution]['Cost']
                    solutionDict[invSolution]['Solution'] = deepcopy(subRoute)
                    solutionDict[invSolution]['Cost'] = routes_phase2[i]['Cost']
                    solutionDict[invSolution]['Load'] = deepcopy(subLoad)
                    solutionDict[invSolution]['Subtrip cost'] = deepcopy(costs)
                del solutionDict[k]
                k += -1
            else: 
                TTcost += tCost
                solutionDict[k]['Solution'] = deepcopy(subRoute)
                solutionDict[k]['Cost'] = routes_phase2[i]['Cost']
                solutionDict[k]['Load'] = deepcopy(subLoad)
                solutionDict[k]['Subtrip cost'] = deepcopy(costs)
            solutionDict['Total cost'] = TTcost
            solutionNew = self.transformSolutionDict(solutionDict)
        return(solutionNew)
                
                
            
    def mergeHeuristicIFs(self):
        routes_phase1 = self.createMergedSolutionPhase1()
        (routeInfo, routeCost, routeBegin, routeEnd, invRoute, nEdges) = self.secondPhaseArcs(routes_phase1)
        routes_phase2 = self.createMergedSolutionPhase2(routeInfo, routeCost, routeBegin, routeEnd, invRoute, nEdges)
        solutionDict = self.createFinalSolution(routeInfo, routes_phase2, invRoute)
        (solutionDict, reduced,  nRoutes) = self.minN.variableReduction(solutionDict)
        nTrips = len(solutionDict.keys())-1
        return(solutionDict, nTrips)
        
if __name__=="__main__":
    import LancommeARPconversions3 as LARP
    import testSolutions
    from time import clock
#    import psyco
#    psyco.full()
    info = LARP.ReadProblemDataIFs('cen_IF_ProblemInfo/Centurion_a_pickled.dat')
    merge = MergeHeuristic(info)
    t = clock()
    solution = merge.mergeHeuristicIFs()[0]
    ed = clock() - t
    e = testSolutions.testSolution(info, solution)
    e.testReportSolutionIFs()
    print(ed)
