'''
Created on 21 May 2010

@author: EWillemse
'''
from copy import deepcopy
import optDirectHeuristic as optD

class SinlgeRouteModifications(object):

    def __init__(self, info):
        self.info = info
        self.SP = self.info.spDistanceD
        self.IFD = self.info.bestIFdistD
        self.bestChange = 0
        self.bestNeighbour = None
        self.maxTrip = self.info.maxTrip

    def singleRemove1route(self, routeI, position):
        arcRemoved = routeI[position]
        costChange = self.SPdict[routeI[position-1]][routeI[position+1]] - self.SPdict[routeI[position-1]][routeI[position]] - self.SPdict[routeI[position]][routeI[position+1]]
        modifiedRoute = routeI[:]
        del modifiedRoute[position]
        return(modifiedRoute, arcRemoved, costChange)
    
    def singleInsert1Route(self, routeI, arcInsert, insertPosistion):
        i = insertPosistion
        costChange = self.SPdict[routeI[i-1]][arcInsert] + self.SPdict[arcInsert][routeI[i]] - self.SPdict[routeI[i-1]][routeI[i]]
        modifiedRoute = routeI[:]
        modifiedRoute[i:i] = [arcInsert]
        return(modifiedRoute, costChange)
    
    def findBestInversionArcInsert(self, routeI, arcRemoved, position):
        modifiedRoute1 = routeI[:]
        j = position
        (modifiedRoute2, costChange2) = self.singleInsert1Route(modifiedRoute1, arcRemoved, j)
        if self.arcInvDict[arcRemoved]:
            (modifiedRoute3, costChange3) = self.singleInsert1Route(modifiedRoute1, self.arcInvDict[arcRemoved], j)
            costChange3 += - self.arcCostDict[arcRemoved] + self.arcCostDict[self.arcInvDict[arcRemoved]]
            if costChange3 < costChange2: modifiedRoute2, costChange2 = modifiedRoute3[:], costChange3
        return(modifiedRoute2, costChange2)

    def removeInsertAllArcs(self, routeI, routeP = None):
        nArcs = len(routeI)
        removalInsertionNeighbourhood = []
        for i in range(1,nArcs-1):
            (modifiedRoute1, arcRemoved, costChange1) = self.singleRemove1route(routeI, i)
            insertPosition = range(1, nArcs-1)
            del insertPosition[i-1]
            for j in insertPosition:
                (modifiedRoute2, costChange2) = self.findBestInversionArcInsert(modifiedRoute1, arcRemoved, j)
                neighbour = {'routes':routeP,'pos':(i,j),'arc':arcRemoved,'costDelta':costChange1+costChange2,'modifiedRoutes':modifiedRoute2}
                #print('1 remove insert',costChange1+costChange2)
                if (costChange1+costChange2 < self.bestChange):
                    self.bestChange = costChange1+costChange2
                    self.bestNeighbour = (costChange1+costChange2,neighbour,'RemoveInsertAllArcs','oneRoute')
        return(removalInsertionNeighbourhood)
    
    def exchangeAllArcs(self, routeI, routeP = None):
        nArcs = len(routeI)
        removalInsertionNeighbourhood = []
        for i in range(1,nArcs-3):
            (modifiedRoute1, arcRemoved1, costChange1) = self.singleRemove1route(routeI, i)
            for j in range(i+2,nArcs-1):
                (modifiedRoute2, arcRemoved2, costChange2) = self.singleRemove1route(modifiedRoute1, j-1)
                (modifiedRoute2, costChange3) = self.findBestInversionArcInsert(modifiedRoute2, arcRemoved1, j-1)
                (modifiedRoute2, costChange4) = self.findBestInversionArcInsert(modifiedRoute2, arcRemoved2, i)
                neighbour = {'routes':routeP,'pos':(i,j),'arc':(arcRemoved1,arcRemoved2),'costDelta':costChange1+costChange2+costChange3+costChange4,'modifiedRoutes':modifiedRoute2}
                #print('1 exchange',costChange1+costChange2+costChange3+costChange4)
                if (costChange1+costChange2+costChange3+costChange4 < self.bestChange):
                    self.bestChange = costChange1+costChange2+costChange3+costChange4
                    self.bestNeighbour = (costChange1+costChange2+costChange3+costChange4,neighbour,'ExchangeAllArcs','oneRoute')
        return(removalInsertionNeighbourhood)
    
    def genAllsingeRouteNeighbours(self, solutionList):
        for p in range(len(solutionList)):
            self.removeInsertAllArcs(solutionList[p],p)
            self.exchangeAllArcs(solutionList[p],p)
            
            
    def singleArcExchangeDeltas(self,arcRemovedI,arcRemovedJ,costsChange):
        serviceCostI = self.arcCostDict[arcRemovedI]
        serviceCostJ = self.arcCostDict[arcRemovedJ]
        (costChangeI1, costChangeI2, costChangeJ1, costChangeJ2) = costsChange
        costIdelta = costChangeI1 + costChangeI2 + serviceCostJ - serviceCostI
        costJdelta = costChangeJ1 + costChangeJ2 + serviceCostI - serviceCostJ
        Deltas = (costIdelta, costJdelta)
        return(Deltas)
    
    def removeInsertAllArcsRouteAllRoutes(self, routes, costs):
        nRoutes = len(routes)
        removalInsertionNeighbourhood = []
        for routeIpos in range(nRoutes):
            routeI = routes[routeIpos]
            nRoutesJRange = range(nRoutes)
            del nRoutesJRange[routeIpos]
            nArcsI = len(routeI)
            for i in range(1,nArcsI-1):
                (modifiedRouteI, arcRemoved, costChangeI) = self.singleRemove1route(routeI, i)
                subCostArcRemove = self.arcCostDict[arcRemoved]
                costChangeI += -subCostArcRemove
                for routeJpos in nRoutesJRange:
                    jCost = costs[routeJpos]
                    routeJ = routes[routeJpos]
                    nArcsJ = len(routeJ)
                    for j in range(1, nArcsJ-1):
                        (modifiedRouteJ, costChangeJ) = self.findBestInversionArcInsert(routeJ, arcRemoved, j)
                        costChangeJ += subCostArcRemove 
                        neighbour = {'routes':(routeIpos,routeJpos),'pos':(i,j),'arc':arcRemoved,'costDelta':(costChangeI,costChangeJ),'modifiedRoutes':(modifiedRouteI,modifiedRouteJ)}
                        #print('m remove insert',costChangeI+costChangeJ)
                        if ((costChangeI+costChangeJ) < self.bestChange) & (jCost + costChangeJ <= self.maxTrip):
                            self.bestChange = costChangeI+costChangeJ
                            self.bestNeighbour = (costChangeI+costChangeJ,neighbour,'RemoveInsertAllArcsAllRoutes','twoRoutes')
        return(removalInsertionNeighbourhood)
    
    def exchangeAllArcsAllRoutes(self, routes, costs):
        nRoutes = len(routes)
        removalInsertionNeighbourhood = []
        for routeIpos in range(nRoutes-1):
            routeI = routes[routeIpos]
            nRoutesJRange = range(routeIpos+1,nRoutes)
            nArcsI = len(routeI)
            costI = costs[routeIpos]
            for i in range(1,nArcsI-1):
                (modifiedRouteIa, arcRemovedI, costChangeI1) = self.singleRemove1route(routeI, i)
                for routeJpos in nRoutesJRange:
                    costJ = costs[routeJpos]
                    routeJ = routes[routeJpos]
                    nArcsJ = len(routeJ)
                    for j in range(1, nArcsJ-1):
                        (modifiedRouteJ, arcRemovedJ, costChangeJ1) = self.singleRemove1route(routeJ, j)
                        (modifiedRouteI, costChangeI2) = self.findBestInversionArcInsert(modifiedRouteIa, arcRemovedJ, i)
                        (modifiedRouteJ, costChangeJ2) = self.findBestInversionArcInsert(modifiedRouteJ, arcRemovedI, j)
                        costsChange = (costChangeI1, costChangeI2, costChangeJ1, costChangeJ2)
                        Deltas = self.singleArcExchangeDeltas(arcRemovedI,arcRemovedJ,costsChange)
                        (costIdelta, costJdelta) = Deltas         
                        neighbour = {'routes':(routeIpos,routeJpos),'pos':(i,j),'arc':(arcRemovedI,arcRemovedJ),'costDelta':(costIdelta,costJdelta),'modifiedRoutes':(modifiedRouteI,modifiedRouteJ)}
                        #print('m exchange',costIdelta+costJdelta)
                        if (costIdelta+costJdelta < self.bestChange) & (costI + costIdelta <= self.maxTrip) & (costJ + costJdelta <= self.maxTrip):
                            self.bestChange = costIdelta+costJdelta
                            self.bestNeighbour = (costIdelta+costJdelta,neighbour,'ExchangeAllArcsAllRoutes','twoRoutes')
        return(removalInsertionNeighbourhood)

    def genAllMultiRouteNeighbours(self, solutionList, costList):
        self.removeInsertAllArcsRouteAllRoutes(solutionList, costList)
        self.exchangeAllArcsAllRoutes(solutionList, costList)

class refitIFs(SinlgeRouteModifications):
    
    def __init__(self,info):
        SinlgeRouteModifications.__init__(self, info)
        self.info = info
        self.depot = self.info.depotArc
        self.inverseBool = True
        self.invOptDir = True
        self.straightInv = False
        self.printOutput = True
        self.outputLines = []
    
    def makeSolution(self, oldSolutionList, oldCostList):
        solutionDict = {}
        totalCost = 0
        SP = self.info.spDistanceD
        solutionList = []
        costList = []
        for i in range(len(oldSolutionList)):
            if len(oldSolutionList[i]) > 2:
                solutionList.append(deepcopy(oldSolutionList[i]))
                costList.append(oldCostList[i])
        for i in range(len(solutionList)):
            solutionDict[i+1] = {}
            solutionDict[i+1]['Solution'] = []
            solutionDict[i+1]['Subtrip cost'] = []
            solutionDict[i+1]['Load'] = []
            for j in range(1,len(solutionList[i])-1):
                subTripJ = self.arcDict[solutionList[i][j]]
                tripCost = self.arcCostDict[solutionList[i][j]]
                if j == 1:
                    subTripJ.insert(0,self.depot)
                else:
                    subTripJ.insert(0,self.SPnodes[solutionList[i][j-1]][solutionList[i][j]])
                subTripJ.append(self.SPnodes[solutionList[i][j]][solutionList[i][j+1]])
                tripCost += SP[subTripJ[0]][subTripJ[1]] + SP[subTripJ[-2]][subTripJ[-1]] 
                solutionDict[i+1]['Solution'].append(deepcopy(subTripJ))
                solutionDict[i+1]['Load'].append(self.arcLoadDict[solutionList[i][j]])
                solutionDict[i+1]['Subtrip cost'].append(tripCost)
            solutionDict[i+1]['Solution'][-1].append(self.depot)
            solutionDict[i+1]['Subtrip cost'][-1] += SP[solutionDict[i+1]['Solution'][-1][-2]][solutionDict[i+1]['Solution'][-1][-1]]
            solutionDict[i+1]['Cost'] = costList[i]
            totalCost += costList[i]
        solutionDict['Total cost'] = totalCost
        return(solutionDict)
    
    def makeMove(self, solutionList, costList, neighbour):
        '''
        '''
        move = neighbour[1]
        if neighbour[-1] == 'oneRoute':
            position = move['routes']
            solutionList[position] = deepcopy(move['modifiedRoutes'])
            costList[position] += neighbour[0]
        if neighbour[-1] == 'twoRoutes':
            (positionI, positionJ) = move['routes']
            (solutionList[positionI], solutionList[positionJ]) = move['modifiedRoutes']
            (costDeltaI, costDeltaJ) = move['costDelta']
            costList[positionI] += costDeltaI
            costList[positionJ] +=  costDeltaJ
        return(solutionList, costList)
            
    
    def solutionCost2(self, solutionList):
        cost = 0
        for solI in solutionList:
            for j in range(len(solI)-1):
                cost += self.arcCostDict[solI[j]]
                cost += self.SPdict[solI[j]][solI[j+1]]
            cost += self.arcCostDict[solI[j+1]]
        return(cost)

    def inverseRoute(self, route):
        inv = self.info.invArcD
        serve = self.info.serveCostD
        SP = self.info.spDistanceD
        newRoute = route[:]
        newRoute.reverse()
        cost = 0
        for i in range(len(route)):
            if inv[newRoute[i]]:newRoute[i]=inv[newRoute[i]]
            cost += serve[newRoute[i]]
            if i > 0: cost += SP[newRoute[i-1]][newRoute[i]]
        cost += self.info.dumpCost
        return(newRoute,cost)
    
    def inverseRouteOpt(self, route):
        newRoute = route[:]
        newRoute.reverse()
        opt = optD.optArcDirect(newRoute,self.info)
        opt.optRoute()
        newRoute = opt.impRoute[:]
        cost = opt.cost + self.info.dumpCost
        return(newRoute,cost) 
    
    def dismantleSolution(self, solution):
        k = 0
        SP = self.info.spDistanceD
        arcDict = {}
        arcRepDict = {}
        arcCostDict = {}
        arcLoadDict = {}
        arcInvDict = {}
        arcDict[k] = [self.depot]
        arcRepDict[k] = (self.depot, self.depot)
        arcInvDict[k] = k
        arcCostDict[k] = 0
        arcLoadDict[k] = 0
        solutionList = []
        costList = []
        SPdict = {}
        SPnodes = {}
        nRoutes = len(solution.keys())-1
        
        for i in range(1,nRoutes+1):
            routeI = solution[i]['Solution']
            lList = [0]
            for subRouteI in range(len(routeI)):
                k += 1
                lList.append(k)
                if subRouteI == len(routeI)-1: 
                    arcDict[k] = routeI[subRouteI][1:-2]
                    arcCostDict[k] = solution[i]['Subtrip cost'][subRouteI] - SP[routeI[subRouteI][0]][routeI[subRouteI][1]] - SP[routeI[subRouteI][-3]][routeI[subRouteI][-2]] - SP[routeI[subRouteI][-2]][routeI[subRouteI][-1]]
                else: 
                    arcDict[k] = routeI[subRouteI][1:-1]
                    arcCostDict[k] = solution[i]['Subtrip cost'][subRouteI] - SP[routeI[subRouteI][0]][routeI[subRouteI][1]] - SP[routeI[subRouteI][-2]][routeI[subRouteI][-1]]
                arcLoadDict[k] = solution[i]['Load'][subRouteI]
                arcRepDict[k] = (arcDict[k][0], arcDict[k][-1])
                if self.inverseBool:
                    if self.straightInv: (arcDict[k+1],arcCostDict[k+1]) = self.inverseRoute(arcDict[k])
                    if self.invOptDir: 
                        if (len(arcDict[k]) > 1): (arcDict[k+1],arcCostDict[k+1]) = self.inverseRouteOpt(arcDict[k])
                        else: (arcDict[k+1],arcCostDict[k+1]) = self.inverseRoute(arcDict[k])
                    arcInvDict[k+1] = k
                    arcInvDict[k] = k+1
                    arcLoadDict[k+1] = arcLoadDict[k]
                    k += 1
                    arcRepDict[k] = (arcDict[k][0], arcDict[k][-1])
                else:
                    arcInvDict[k] = 0
            lList.append(0)
            costList.append(solution[i]['Cost'])
            solutionList.append(deepcopy(lList))
        
        IFD = self.info.bestIFdistD
        IFDnode = self.info.bestIFD
        k += 1
        for i in range(k):
            SPdict[i] = {}
            SPnodes[i] = {}
            jRange = range(k)
            beginArc = arcRepDict[i][-1]
            del jRange[i]
            SPdict[i][i] = 0
            SPnodes[i][i] = None
            for j in jRange:
                endArc = arcRepDict[j][0]
                if endArc != beginArc:
                    if i == 0:
                        SPdict[i][j] = SP[beginArc][endArc]
                        SPnodes[i][j] = None
                    else:
                        SPdict[i][j] = IFD[beginArc][endArc]
                        SPnodes[i][j] = IFDnode[beginArc][endArc]
                else:SPdict[i][j] = 1e300000
        self.arcDict = deepcopy(arcDict)
        self.arcRepDict = deepcopy(arcRepDict)
        self.arcCostDict = deepcopy(arcCostDict)
        self.arcLoadDict = deepcopy(arcLoadDict)
        self.arcInvDict = deepcopy(arcInvDict)
        self.SPdict = deepcopy(SPdict)
        self.SPnodes = deepcopy(SPnodes)
        return(solutionList, costList)
    
    def removeEmptySubTrips(self, solution):
        newSolution = {}
        SP = self.info.spDistanceD
        nRoutes = len(solution.keys())-1
        k = 0
        tCost = 0
        for i in range(1,nRoutes+1):
            k += 1
            newSolution[k] = {}
            routeI = solution[i]['Solution']
            loadI =  solution[i]['Load']
            costsI =  solution[i]['Subtrip cost']
            routes = []
            loads = []
            costs = []
            for subRouteI in range(len(routeI)):
                if (subRouteI == len(routeI)-1) & (len(routeI[subRouteI]) > 3):
                    routes.append(routeI[subRouteI])
                    loads.append(loadI[subRouteI])
                    costs.append(costsI[subRouteI])
                elif (subRouteI == len(routeI)-1) & (len(routeI[subRouteI]) <= 3) & (len(routeI) > 1):
                    routes[subRouteI-1].append(self.info.depotArc)
                    addChange = SP[routes[subRouteI-1][-2]][routes[subRouteI-1][-1]]
                    costs[subRouteI-1] += addChange
                elif (subRouteI < len(routeI)-1) & (len(routeI[subRouteI]) > 2):
                    routes.append(routeI[subRouteI])
                    loads.append(loadI[subRouteI])
                    costs.append(costsI[subRouteI])
            if not routes: k+=-1
            else:
                newSolution[k]['Solution'] = deepcopy(routes)
                newSolution[k]['Subtrip cost'] = deepcopy(costs)
                newSolution[k]['Load'] = deepcopy(loads)
                newSolution[k]['Cost'] = sum(costs)
                tCost += sum(costs)
        newSolution['Total cost'] = tCost
        return(newSolution)
                    
    
    def optIFinsert(self, solution):
        IFD = self.info.bestIFdistD
        IFDnode = self.info.bestIFD
        SP = self.info.spDistanceD
        nRoutes = len(solution.keys())-1
        for i in range(1,nRoutes+1):             
            routeI = solution[i]['Solution']
            for subRouteI in range(len(routeI)):
                if subRouteI == len(routeI)-1: 
                    bestEndIFcost = IFD[routeI[subRouteI][-3]][routeI[subRouteI][-1]]
                    bestEndIF = IFDnode[routeI[subRouteI][-3]][routeI[subRouteI][-1]]
                    previousCost = SP[routeI[subRouteI][-3]][routeI[subRouteI][-2]]  + SP[routeI[subRouteI][-2]][routeI[subRouteI][-1]]
                    solution[i]['Solution'][subRouteI][-2] = bestEndIF
                    change = bestEndIFcost - previousCost
                    solution[i]['Cost'] += change
                    solution[i]['Subtrip cost'][subRouteI] += change
                    solution['Total cost'] += change
                else:
                    bestEndIF = IFDnode[routeI[subRouteI][-2]][routeI[subRouteI+1][1]]
                    bestEndIFcost = SP[routeI[subRouteI][-2]][bestEndIF]
                    previousCost = SP[routeI[subRouteI][-2]][routeI[subRouteI][-1]]
                    solution[i]['Solution'][subRouteI][-1] = bestEndIF
                    change = bestEndIFcost - previousCost
                    solution[i]['Cost'] += change
                    solution[i]['Subtrip cost'][subRouteI] += change
                    solution['Total cost'] += change
                if subRouteI > 0:
                    bestBeginIF = IFDnode[routeI[subRouteI-1][-2]][routeI[subRouteI][1]]
                    bestBeginIFcost = SP[bestBeginIF][routeI[subRouteI][1]]
                    previousCost = SP[routeI[subRouteI][0]][routeI[subRouteI][1]]
                    solution[i]['Solution'][subRouteI][0] = bestBeginIF
                    change = bestBeginIFcost - previousCost
                    solution[i]['Cost'] += change
                    solution[i]['Subtrip cost'][subRouteI] += change
                    solution['Total cost'] += change
        return(solution)

    def IFplacementLocalSearch(self, solution):
        '''
        '''
        format = '%*d%*s%*d%*s%s'
        format2 = '%*s%*s%*d%*s%s'
        oldCost = solution['Total cost']
        solution = self.removeEmptySubTrips(deepcopy(solution))
        if solution['Total cost'] < oldCost:
                    line = ''
                    self.outputLines.append(line)
                    print(line)
                    line = '     Sub trip removal'
                    self.outputLines.append(line)
                    print(line)
                    line = format2 %(3,' ',10,'Delta : ',5,solution['Total cost'] - oldCost,5,' ','subtrip removal')
                    self.outputLines.append(line)
                    print(line)
                    line = ''
                    self.outputLines.append(line)
                    print(line)
        oldCost = solution['Total cost'] 
        solution = self.optIFinsert(deepcopy(solution))
        if solution['Total cost'] < oldCost:
                    line = ''
                    self.outputLines.append(line)
                    print(line)
                    line = '     Opt IF insert'
                    self.outputLines.append(line)
                    print(line)
                    line = format2 %(3,' ',10,'Delta : ',5,solution['Total cost'] - oldCost,5,' ','opt IF insert')
                    self.outputLines.append(line)
                    print(line)
                    line = ''
                    self.outputLines.append(line)
                    print(line)            
        (solutionList, costList) = self.dismantleSolution(solution)
        itteration = 0
        while True:
            self.genAllsingeRouteNeighbours(solutionList)
            self.genAllMultiRouteNeighbours(solutionList, costList)        
            if self.bestNeighbour:
                itteration += 1
                (solutionList, costList) = self.makeMove(deepcopy(solutionList), deepcopy(costList), self.bestNeighbour)
                if (self.printOutput) & (itteration == 1):
                    line = ''
                    self.outputLines.append(line)
                    print(line)
                    line = '     Refit Intermediate facilities'
                    self.outputLines.append(line)
                    print(line)
                if self.printOutput:
                    line = format2 %(3,' ',10,'Delta : ',5,self.bestNeighbour[0],5,' ',self.bestNeighbour[-2])
                    self.outputLines.append(line)
                    print(line)
                self.bestNeighbour = None
                self.bestChange = 0
            else:
                if itteration > 0:
                    line = ''
                    self.outputLines.append(line)
                    print(line)                    
                break
        solution = self.makeSolution(solutionList, costList)
        return(solution)
        
        
def unitTest(info, solution):
    er = testSolutions.testSolution(info, solution)
    er.checkFeasibilityIFs()
    er.testReportSolutionIFs()
    s1 = time.clock()
    IFsPalceMent = refitIFs(info)
    IFsPalceMent.invOptDir = True
    IFsPalceMent.straightInv = False   
    (solutionList, costList) = IFsPalceMent.dismantleSolution(solution)
    IFsPalceMent.genAllsingeRouteNeighbours(solutionList)
    IFsPalceMent.genAllMultiRouteNeighbours(solutionList, costList)

    if IFsPalceMent.bestNeighbour:
        (solutionListNew, costListNew) = IFsPalceMent.makeMove(deepcopy(solutionList), deepcopy(costList), IFsPalceMent.bestNeighbour)
        solution = IFsPalceMent.makeSolution(solutionListNew, costListNew)
    e1 = time.clock() - s1
    print('')
    print('TIME',e1)
    print('')
    er = testSolutions.testSolution(info, solution)
    er.checkFeasibilityIFs()
    er.testReportSolutionIFs()
    
def unitTest2(info, solution):
    er = testSolutions.testSolution(info, solution)
    er.checkFeasibilityIFs()
    er.testReportSolutionIFs()
    print('')
    s1 = time.clock()
    IFsPalceMent = refitIFs(info)
    IFsPalceMent.invOptDir = True
    IFsPalceMent.straightInv = False   
    solution = IFsPalceMent.IFplacementLocalSearch(solution)
    e1 = time.clock() - s1
    print('')
    print('TIME',e1)
    print('')
    er = testSolutions.testSolution(info, solution)
    er.checkFeasibilityIFs()
    er.testReportSolutionIFs()
    
if __name__=="__main__":
    import cPickle
    import LancommeARPconversions3 as LARP
    import time
    import testSolutions
#    import psyco
#    psyco.full()
    fileName1 = 'lpr_IF_ProblemInfo/Lpr-c-02_pickled.txt'
    info = LARP.ReadProblemDataIFs(fileName1)
    s1 = open('lpr_IF_Solutions_transformed/Ulusoy/Lpr-c-02_Init_MinDepo_sol.txt')
    solution1 = cPickle.load(s1)
    unitTest2(info, solution1)
                
                
                
                
                
                
                
                
                
                
                
                
                
