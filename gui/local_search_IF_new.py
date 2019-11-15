'''
Created on 06 May 2010

@author: EWillemse
'''

import routes_neighbours_IF_all as RN
import time
import transformSolution
import reduceNumberTrips_IF as RED
import refitIFs
import testSolutions
import gen_neighbours_beta1

from copy import deepcopy

#===============================================================================
# 
#===============================================================================
class ImplementLocalSearchIFs(object):

    def __init__(self, info):
        self.info = info
        self.Capacity = info.capacity
        self.serviceCostD = info.serveCostD
        self.SP = info.spDistanceD
        self.depot = self.info.depotArc
        self.maxTrip = self.info.maxTrip
        self.captureStats = True

    def makeRouteList(self, solution):
        routes = solution.keys()
        nRoutes = len(routes)-1
        routes = []
        k = -1
        routeIndex = {}
        for routeIkey in range(nRoutes):
            routesI = solution[routeIkey+1]['Solution']
            for subRouteIkey in range(len(routesI)):
                k += 1
                if subRouteIkey == len(routesI) - 1: 
                    subRouteI = routesI[subRouteIkey][:-1]
                    routeIndex[k] = (routeIkey, subRouteIkey, True)
                else: 
                    subRouteI = routesI[subRouteIkey]
                    routeIndex[k] = (routeIkey, subRouteIkey, False)
                routes.append(subRouteI)
        return(routes, routeIndex)
    
    def makeLoadList(self, solution):
        routes = solution.keys()
        nRoutes = len(routes)-1
        loads = []
        k = -1
        routeLoadIndex = {}
        for routeIkey in range(nRoutes):
            loadI = solution[routeIkey+1]['Load']
            for subRouteIkey in range(len(loadI)):
                k += 1
                subLoadI = loadI[subRouteIkey]
                routeLoadIndex[k] = (routeIkey, subRouteIkey)
                loads.append(subLoadI)
        return(loads)
    
    def makeCostList(self, solution):
        routes = solution.keys()
        nRoutes = len(routes)-1
        routeCostIndex = {}
        costs = []
        tripCosts = []
        k = -1
        for routeIkey in range(nRoutes):
            costI = solution[routeIkey+1]['Subtrip cost']
            for subRouteIkey in range(len(costI)):
                k += 1
                subCostI = costI[subRouteIkey]
                routeCostIndex[k] = (routeIkey, subRouteIkey)
                costs.append(subCostI)
            tripCosts.append(solution[routeIkey+1]['Cost'])
        return(costs, tripCosts)

    def makeServiceCostList(self, solution):
        nRoutes = len(solution.keys())-1
        routeServiceCostIndex = {}
        serviceCosts = []
        k = -1
        for routeIkey in range(nRoutes):
            j = -1
            for subRouteI in solution[routeIkey+1]['Solution']:
                j += 1
                k += 1
                serviceCostTemp = 0
                for arc in subRouteI:
                    serviceCostTemp += self.serviceCostD[arc]
                serviceCosts.append(serviceCostTemp)
                routeServiceCostIndex[k] = (routeIkey, j)
        return(serviceCosts)

    def makeSolutionList(self, solution):
        (routes, routeIndex) = self.makeRouteList(solution)
        (loads) = self.makeLoadList(solution)
        (costs, tripCosts) = self.makeCostList(solution)
        (serviceCosts) = self.makeServiceCostList(solution)
        return((routes, loads, costs,  serviceCosts, routeIndex)) 

    def makeSolutionDictionaryIFs(self, solution, routes, loads, costs, routeIndex, tripCost):
        nRoutes = len(routes)
        for i in range(nRoutes):
            routeI = routeIndex[i][0]
            subRouteI = routeIndex[i][1]
            if routeIndex[i][2]: solution[routeI+1]['Solution'][subRouteI] = deepcopy(routes[i]) + [self.depot]
            else:  solution[routeI+1]['Solution'][subRouteI] = deepcopy(routes[i])
            solution[routeI+1]['Load'][subRouteI] = loads[i]
            solution[routeI+1]['Subtrip cost'][subRouteI] = costs[i]
        for i in range(len(tripCost)):
            solution[i+1]['Cost'] = tripCost[i]
        solution['Total cost'] = sum(costs)
        return(solution) 

    def changeSingleSolution(self, solutionOld, neighbour, routeIndex):
        solution = deepcopy(solutionOld)
        legalMove = True
        if self.captureStats:
            self.neighbourhoodSearchStats2[neighbour[-2]]['Executions'] += 1
            self.neighbourhoodSearchStats2[neighbour[-2]]['Total saving'] += neighbour[0]
        if neighbour[-1] == 'oneRoute':
            modifications = neighbour[1]
            routeItemp = modifications['routes']
            routeI = routeIndex[routeItemp][0]
            subRouteI = routeIndex[routeItemp][1]
            routeI += 1
            if routeIndex[routeItemp][2]: solution[routeI]['Solution'][subRouteI] = modifications['modifiedRoutes'] + [self.depot]
            else: solution[routeI]['Solution'][subRouteI] = modifications['modifiedRoutes']
            costIdelta = modifications['costDelta']
            solution[routeI]['Subtrip cost'][subRouteI] += costIdelta
            solution[routeI]['Cost'] += costIdelta
            solution['Total cost'] += neighbour[0]
        elif neighbour[-1] == 'twoRoutes':
            bestNeighbour = neighbour
            modifications = bestNeighbour[1]
            (routeItemp, routeJtemp) = modifications['routes']
            routeI = routeIndex[routeItemp][0]
            subRouteI = routeIndex[routeItemp][1]
            routeJ = routeIndex[routeJtemp][0]
            subRouteJ = routeIndex[routeJtemp][1]
            routeI += 1
            routeJ += 1
            if routeIndex[routeItemp][2]: solution[routeI]['Solution'][subRouteI] = modifications['modifiedRoutes'][0] + [self.depot]
            else: solution[routeI]['Solution'][subRouteI] = modifications['modifiedRoutes'][0]
            if routeIndex[routeJtemp][2]: solution[routeJ]['Solution'][subRouteJ] = modifications['modifiedRoutes'][1] + [self.depot]
            else: solution[routeJ]['Solution'][subRouteJ] = modifications['modifiedRoutes'][1]
            (costIdelta, costJdelta) = modifications['costDelta']
            solution[routeI]['Cost'] += costIdelta
            solution[routeJ]['Cost'] += costJdelta
            solution[routeI]['Subtrip cost'][subRouteI] += costIdelta
            solution[routeJ]['Subtrip cost'][subRouteJ] += costJdelta
            (loadIdelta, loadJdelta) = modifications['loadDelta']
            solution[routeI]['Load'][subRouteI] += loadIdelta
            solution[routeJ]['Load'][subRouteJ] += loadJdelta
            if (solution[routeI]['Load'][subRouteI] > self.Capacity) | (solution[routeJ]['Load'][subRouteJ] > self.Capacity):legalMove = False
            if (solution[routeI]['Cost'] > self.maxTrip) | ((solution[routeJ]['Cost'] > self.maxTrip) > self.maxTrip):legalMove = False
            solution['Total cost'] += bestNeighbour[0]
        return(solution, legalMove)

#===============================================================================
# 
#===============================================================================
class checkAllMoves(object):
    
    def __init__(self, info):
        self.info = info
        self.Capacity = self.info.capacity        
        self.maxTrip = self.info.maxTrip
        self.captureStats = True
        self.printOutput = True
        self.outputLines = []

    
    def captureNeighbourStats(self, deltaChange, statType):
        if self.captureStats:
            self.neighbourhoodSearchStats[statType]['Executions'] += 1
            self.neighbourhoodSearchStats[statType]['Total saving'] += deltaChange

    def captureNeighbourStats2(self, deltaChange, statType):
        if self.captureStats:
            self.neighbourhoodSearchStats2[statType]['Executions'] += 1
            self.neighbourhoodSearchStats2[statType]['Total saving'] += deltaChange

    def checkSingleRouteMoves(self, move, tabuMovePositions):
        makeSingleRouteMoveCheck = False
        moveInfo = move[1]
        routeI = moveInfo['routes']
        if (move[-2] ==  'RemoveInsertAllArcs') | (move[-2] == 'ExchangeAllArcs'):
            (pI, pJ) = moveInfo['pos']
            if (pI not in tabuMovePositions[routeI]) & (pJ not in tabuMovePositions[routeI]):
                makeSingleRouteMoveCheck = True
        elif (move[-2] ==  'RemoveInsertAllDoubleArcs'):
            (pI, pJ) = moveInfo['pos']
            if (pI not in tabuMovePositions[routeI]) & ((pI + 1) not in tabuMovePositions[routeI]) & (pJ not in tabuMovePositions[routeI]):
                makeSingleRouteMoveCheck = True
        elif (move[-2] == 'ExchangeAllDoubleArcs'):
            (pI, pJ) = moveInfo['pos']
            if (pI not in tabuMovePositions[routeI]) & ((pI + 1) not in tabuMovePositions[routeI]) & (pJ not in tabuMovePositions[routeI]) & ((pJ + 1) not in tabuMovePositions[routeI]):
                makeSingleRouteMoveCheck = True
        return(makeSingleRouteMoveCheck)
    
    def checkTwoRouteMoves(self, move, tabuMovePositions):
        makeTwoRouteMoveCheck = False 
        moveInfo = move[1]
        (routeI, routeJ) = moveInfo['routes']
        if (move[-2] ==  'RemoveInsertAllArcsAllRoutes') | (move[-2] == 'ExchangeAllArcsAllRoutes'):
            (pI, pJ) = moveInfo['pos']
            if (pI not in tabuMovePositions[routeI]) & (pJ not in tabuMovePositions[routeJ]):
                makeTwoRouteMoveCheck = True
        elif (move[-2] ==  'RemoveInsertAllDoubleArcsAllRoutes'):
            (pI, pJ) = moveInfo['pos']
            if (pI not in tabuMovePositions[routeI]) & ((pI+1) not in tabuMovePositions[routeI]) & (pJ not in tabuMovePositions[routeJ]):
                makeTwoRouteMoveCheck = True
        elif (move[-2] == 'ExchangeAllDoubleArcsAllRoutes'):
            (pI, pJ) = moveInfo['pos']
            if (pI not in tabuMovePositions[routeI]) & ((pI+1) not in tabuMovePositions[routeI]) & (pJ not in tabuMovePositions[routeJ]) & ((pJ+1) not in tabuMovePositions[routeJ]):
                makeTwoRouteMoveCheck = True
        return(makeTwoRouteMoveCheck)
    
    def updateMoveInfo(self, input):
        (moveInfo, routeIndex, tempLoads, tempCosts, tempTripCosts, tempServiceCosts, tabuMovePositions, totalCostChange) = input
        moveInfo = moveInfo
        (routeI, routeJ) = moveInfo['routes']
        actualI = routeIndex[routeI][0] 
        actualJ = routeIndex[routeJ][0]
        (deltaLoadI, deltaLoadJ) = moveInfo['loadDelta']
        (costDeltaI, costDeltaJ) = moveInfo['costDelta']
        (serviceCostDeltaI, serviceCostDeltaJ) = moveInfo['serviceDelta']
        tempLoads[routeI] += deltaLoadI
        tempLoads[routeJ] += deltaLoadJ
        tempCosts[routeI] += costDeltaI
        tempCosts[routeJ] += costDeltaJ
        tempTripCosts[actualI] += costDeltaI
        tempTripCosts[actualJ] += costDeltaJ
        tempServiceCosts[routeI] += serviceCostDeltaI
        tempServiceCosts[routeJ] += serviceCostDeltaJ
        tabuMovePositions[routeI] +=  moveInfo['tabus']['I']
        tabuMovePositions[routeJ] +=  moveInfo['tabus']['J']
        totalCostChange += costDeltaI +  costDeltaJ
        return(tempLoads, tempCosts, tempTripCosts, tempServiceCosts, tabuMovePositions, totalCostChange)

    def chechMoves(self, neighbourhoods, solution,  routeIndex, tripCosts):
        (routes, loads, costs,  serviceCosts, routeIndex) = self.makeSolutionList(solution)
        nRoutes = len(loads)
#        print('{250}',neighbourhoods)
#        print('{251}',len(neighbourhoods))
        neighbourhoods.sort()
        tabuMovePositions = {}.fromkeys(range(nRoutes))
        for i in range(nRoutes):
            tabuMovePositions[i] = []
        movesToMake = []
        tempTripCosts = deepcopy(tripCosts)
        tempCosts = deepcopy(costs)
        tempLoads = deepcopy(loads)
        tempServiceCosts = deepcopy(serviceCosts)
        totalCostChange = 0
        for move in neighbourhoods:
            self.captureNeighbourStats2(move[0], move[-2])
            if move[-1] == 'oneRoute':
                moveInfo = move[1]
                routeI = moveInfo['routes']
                actualI = routeIndex[routeI][0]
                costDeltaI = moveInfo['costDelta']
                if self.checkSingleRouteMoves(move, tabuMovePositions):
                    movesToMake.append(move)
                    tabuMovePositions[routeI] +=  moveInfo['tabus']
                    tempCosts[routeI] += costDeltaI
                    totalCostChange += costDeltaI
                    tempTripCosts[actualI] += costDeltaI
                    self.captureNeighbourStats(move[0], move[-2])
            elif move[-1] == 'twoRoutes':
                moveInfo = move[1]
                (routeI, routeJ) = moveInfo['routes']
                actualI = routeIndex[routeI][0] 
                actualJ = routeIndex[routeJ][0]
                (deltaLoadI, deltaLoadJ) = moveInfo['loadDelta']
                (costDeltaI, costDeltaJ) = moveInfo['costDelta']
                if (actualI == actualJ) & (tempLoads[routeI] + deltaLoadI <= self.Capacity) & (tempLoads[routeJ] + deltaLoadJ <= self.Capacity):
                    if self.checkTwoRouteMoves(move, tabuMovePositions):
                        movesToMake.append(move)
                        input = (moveInfo, routeIndex, tempLoads, tempCosts, tempTripCosts, tempServiceCosts, tabuMovePositions, totalCostChange)
                        output = self.updateMoveInfo(input)
                        (tempLoads, tempCosts, tempTripCosts, tempServiceCosts, tabuMovePositions, totalCostChange) = output
                        self.captureNeighbourStats(move[0], move[-2])
                elif (tempLoads[routeI] + deltaLoadI <= self.Capacity) & (tempLoads[routeJ] + deltaLoadJ <= self.Capacity) & (tempTripCosts[actualI] + costDeltaI <= self.maxTrip) & (tempTripCosts[actualJ] + costDeltaJ <= self.maxTrip):
                    if self.checkTwoRouteMoves(move, tabuMovePositions):
                        movesToMake.append(move)
                        input = (moveInfo, routeIndex, tempLoads, tempCosts, tempTripCosts, tempServiceCosts, tabuMovePositions, totalCostChange)
                        output = self.updateMoveInfo(input)
                        (tempLoads, tempCosts, tempTripCosts, tempServiceCosts, tabuMovePositions, totalCostChange) = output
                        self.captureNeighbourStats(move[0], move[-2])
        return(movesToMake,tempLoads,tempCosts,tempServiceCosts,totalCostChange, tempTripCosts)
    
#===============================================================================
# 
#===============================================================================
class makeAllMoves(object):

    def __init__(self, info):
        self.info = info
        self.printOutput = True
        self.outputLines = []

    def singleRouteMove(self, move, routeI, iPosActual, jPosActual, positionList):
        iPos = positionList[iPosActual]
        jPos = positionList[jPosActual]
        if move[-2] == 'RemoveInsertAllArcs':
            routeI = self.RNsingleRoute.removeInsertGivenArcs(routeI, iPos, jPos)
            if iPos < jPos:
                for i in range(iPosActual+1,jPosActual):
                    positionList[i] += -1
            elif iPos > jPos:
                for i in range(jPosActual, iPosActual-1):
                    positionList[i] += 1
        elif move[-2] == 'ExchangeAllArcs':
            routeI = self.RNsingleRoute.exchangeGivenArcs(routeI, iPos, jPos)
        elif move[-2] == 'RemoveInsertAllDoubleArcs': 
            routeI = self.RNsingleRoute.removeInsertGivenDoubleArcs(routeI, iPos, jPos)
            if iPos < jPos:
                for i in range(iPosActual+1,jPosActual+1):
                    positionList[i] += -2
            elif iPos > jPos:
                for i in range(jPosActual, iPosActual-1):
                    positionList[i] += 2
        elif move[-2] == 'ExchangeAllDoubleArcs':
            routeI = self.RNsingleRoute.exchangeGivenDoubleArcs(routeI, iPos, jPos)      
        return(routeI, positionList)
    
    def doubleRouteMove(self, move, routeI, routeJ, iPosActual, jPosActual, positionListI, positionListJ):
        posI, posJ = positionListI[iPosActual], positionListJ[jPosActual]
        if (move[-2] ==  'RemoveInsertAllArcsAllRoutes'):
            (routeI, routeJ) = self.RNmultiRoute.removeInsertGivenArcsTwoRoutes(routeI, routeJ, posI, posJ)
            for i in range(iPosActual, len(positionListI)):
                positionListI[i] += -1
            for i in range(jPosActual, len(positionListJ)):
                positionListJ[i] += 1
        elif (move[-2] == 'ExchangeAllArcsAllRoutes'):
            (routeI, routeJ) = self.RNmultiRoute.exchangeGivenArcsTwoRoutes(routeI, routeJ, posI, posJ)
        elif (move[-2] ==  'RemoveInsertAllDoubleArcsAllRoutes'):
            (routeI, routeJ) = self.RNmultiRoute.removeInsertGivenDoubleArcsTwoRoutes(routeI, routeJ, posI, posJ)
            for i in range(iPosActual+1, len(positionListI)):
                positionListI[i] += -2
            for i in range(jPosActual, len(positionListJ)):
                positionListJ[i] += 2
        elif (move[-2] == 'ExchangeAllDoubleArcsAllRoutes'):
            (routeI, routeJ) = self.RNmultiRoute.exchangeGivenDoubleArcsTwoRoutes(routeI, routeJ, posI, posJ)
        return(routeI, routeJ, positionListI, positionListJ)
        
    def makeMoves(self, solution, movesToMake):
        format = '%s%*d%*s%*d%*s%s'
        (routes, loads, costs,  serviceCosts, routeIndex) = self.makeSolutionList(solution)
        self.temp = (loads, costs,  serviceCosts)
        nRoutes = len(routes)
        positionDict = {}.fromkeys(range(nRoutes))
        for i in range(nRoutes):
            positionDict[i] = range(len(routes[i]))
        itteration = 0
        for move in movesToMake:
            moveInfo = move[1]
            itteration += 1
            if move[-1] == 'oneRoute':
                routeI = moveInfo['routes']
                (iPos, jPos) = moveInfo['pos']
                positionList = positionDict[routeI]
                (routes[routeI], positionDict[routeI]) = self.singleRouteMove(move, routes[routeI], iPos, jPos, positionList)
            elif move[-1] == 'twoRoutes':
                (routeI, routeJ) = moveInfo['routes']
                (iPos, jPos) = moveInfo['pos']
                positionListI, positionListJ = positionDict[routeI], positionDict[routeJ]
                (routes[routeI], routes[routeJ], positionDict[routeI], positionDict[routeJ]) = self.doubleRouteMove(move,  routes[routeI], routes[routeJ], iPos, jPos, positionListI, positionListJ)          
            if self.printOutput:
                line = format %('       ',3,itteration,10,'Delta : ',5,move[0],5,' ',move[-2])
                self.outputLines.append(line)
                print(line)
        return(routes)
    
#===============================================================================
# 
#===============================================================================
class LocalSearchIFs(ImplementLocalSearchIFs, makeAllMoves, checkAllMoves):

    def __init__(self, info, timeIt = False):
        self.info = info
        ImplementLocalSearchIFs.__init__(self, self.info)
        makeAllMoves.__init__(self, self.info)
        checkAllMoves.__init__(self, self.info)
        self.gen_neighbours = gen_neighbours_beta1.genAllNeighbourhoods(self.info)
        self.RNsingleRoute = gen_neighbours_beta1.SingleRouteRemoveInsertProcedure(info)
        self.RNmultiRoute = gen_neighbours_beta1.MultipleRouteRemoveInsertProcedure(info)
        self.neighbourSearchStrategy = 'MultiLocalSearch'
        #--------------------
        self.reduceRoutes = True
        if self.reduceRoutes:
            self.reduce = RED.ReduceNumberOfVehicleRoutes(self.info)
            self.reduce.printOutput = False
        #--------------------
        self.redetermineIFs = True
        if self.redetermineIFs:
            self.retFit = refitIFs.refitIFs(self.info)
        #--------------------
        self.captureStats = True
        self.neighbourhoodSearchStats = {'RemoveInsertAllArcs'                  :{'Executions':0, 'Total saving':0},
                                         'ExchangeAllArcs'                      :{'Executions':0, 'Total saving':0},
                                         'RemoveInsertAllDoubleArcs'            :{'Executions':0, 'Total saving':0},
                                         'ExchangeAllDoubleArcs'                :{'Executions':0, 'Total saving':0},
                                         'RemoveInsertAllArcsAllRoutes'         :{'Executions':0, 'Total saving':0},
                                         'ExchangeAllArcsAllRoutes'             :{'Executions':0, 'Total saving':0},
                                         'RemoveInsertAllDoubleArcsAllRoutes'   :{'Executions':0, 'Total saving':0},
                                         'ExchangeAllDoubleArcsAllRoutes'       :{'Executions':0, 'Total saving':0},
                                         'ReduceRoutes'                         :{'Executions':0, 'Total saving':0},
                                         'DeterminIFs'                          :{'Executions':0, 'Total saving':0}}
        
        self.neighbourhoodSearchStats2 = {'RemoveInsertAllArcs'                  :{'Executions':0, 'Total saving':0},
                                          'ExchangeAllArcs'                      :{'Executions':0, 'Total saving':0},
                                          'RemoveInsertAllDoubleArcs'            :{'Executions':0, 'Total saving':0},
                                          'ExchangeAllDoubleArcs'                :{'Executions':0, 'Total saving':0},
                                          'RemoveInsertAllArcsAllRoutes'         :{'Executions':0, 'Total saving':0},
                                          'ExchangeAllArcsAllRoutes'             :{'Executions':0, 'Total saving':0},
                                          'RemoveInsertAllDoubleArcsAllRoutes'   :{'Executions':0, 'Total saving':0},
                                          'ExchangeAllDoubleArcsAllRoutes'       :{'Executions':0, 'Total saving':0},
                                          'ReduceRoutes'                         :{'Executions':0, 'Total saving':0},
                                          'DeterminIFs'                          :{'Executions':0, 'Total saving':0}}
        #--------------------
        self.printOutput = True
        self.outputLines = []
    
                
    def captureStatsDef(self, oldSolution, newSolution, statType):
        if self.captureStats:
            if newSolution < oldSolution:
                self.neighbourhoodSearchStats[statType]['Executions'] += 1
                self.neighbourhoodSearchStats[statType]['Total saving'] += newSolution - oldSolution
    
    def intialiseLocalSearch(self, solution):
        solutionOldCost =  solution['Total cost']
        if self.reduceRoutes:
            (solution, reduced, nTrips) = self.reduce.variableReduction(solution)
            self.captureStatsDef(solutionOldCost, solution['Total cost'], 'ReduceRoutes')
            solutionOldCost = solution['Total cost']
            if self.printOutput: 
                self.outputLines += self.reduce.outputLines
                self.reduce.outputLines  = []
        if self.redetermineIFs:
            solution = self.retFit.IFplacementLocalSearch(solution)
            self.captureStatsDef(solutionOldCost, solution['Total cost'], 'DeterminIFs')
            if self.printOutput: 
                self.outputLines += self.retFit.outputLines
                self.retFit.outputLines  = []
        return(solution)

    def performFullLocalSearch(self, solution):
        format = '%s%*d%*s%*d%*s%s'
        (routes, routeIndex) = self.makeRouteList(solution)
        (loads) = self.makeLoadList(solution)
        (costs, tripCosts) = self.makeCostList(solution)
        neighbours = self.gen_neighbours.genBestNeighbour(routes, loads, routeIndex, tripCosts)
        movesToMake = False
        if neighbours:
            solutionOldCost = solution['Total cost']
            (solution, legalMove) = self.changeSingleSolution(solution, neighbours[0], routeIndex)
            solutionNewCost = solution['Total cost']
            self.captureStatsDef(solutionOldCost, solutionNewCost, neighbours[0][-2])
            if self.printOutput:
                line = format %('       ',3,self.iteration,10,'Delta : ',5,neighbours[0][0],5,' ',neighbours[0][-2])
                self.outputLines.append(line)
                print(line)
            movesToMake = True
        return(movesToMake, solution)

    def performFastLocalSearch(self, solution):
        format = '%s%*d%*s%*d%*s%s'
        (routes, routeIndex) = self.makeRouteList(solution)
        (loads) = self.makeLoadList(solution)
        (costs, tripCosts) = self.makeCostList(solution)
        neighbours = self.gen_neighbours.genFirstNeighbourOrdered(routes, loads, routeIndex, tripCosts)
        movesToMake = False
        if neighbours:
            solutionOldCost = solution['Total cost']
            (solution, legalMove) = self.changeSingleSolution(solution, neighbours[0], routeIndex)
            solutionNewCost = solution['Total cost']
            self.captureStatsDef(solutionOldCost, solutionNewCost, neighbours[0][-2])
            if self.printOutput:
                line = format %('       ',3,self.iteration,10,'Delta : ',5,neighbours[0][0],5,' ',neighbours[0][-2])
                self.outputLines.append(line)
                print(line)
            movesToMake = True
        return(movesToMake, solution)

    def performFastLocalSearch2(self, solution):
        format = '%s%*d%*s%*d%*s%s'
        (routes, routeIndex) = self.makeRouteList(solution)
        (loads) = self.makeLoadList(solution)
        (costs, tripCosts) = self.makeCostList(solution)
        neighbours = self.gen_neighbours.genFirstNeighbour(routes, loads, routeIndex, tripCosts)
        movesToMake = False
        if neighbours:
            solutionOldCost = solution['Total cost']
            (solution, legalMove) = self.changeSingleSolution(solution, neighbours[0], routeIndex)
            solutionNewCost = solution['Total cost']
            self.captureStatsDef(solutionOldCost, solutionNewCost, neighbours[0][-2])
            if self.printOutput:
                line = format %('       ',3,self.iteration,10,'Delta : ',5,neighbours[0][0],5,' ',neighbours[0][-2])
                self.outputLines.append(line)
                print(line)
            movesToMake = True
        return(movesToMake, solution)

    def performMulitLocalSearch(self, solution):
        format = '%*s%*d%*s%*d%*s%*d%*s%*d'
        (routes, routeIndex) = self.makeRouteList(solution)
        (loads) = self.makeLoadList(solution)
        (costs, tripCosts) = self.makeCostList(solution)
        self.nRoutes = len(routes)
        neighbours = self.gen_neighbours.genMulitNeighbour(routes,loads)
        (movesToMake, tempLoads, tempCosts, tempServiceCosts, totalCostChange, tripCostsTemp) = self.chechMoves(neighbours, solution, routeIndex, tripCosts)
        self.temp = tempServiceCosts
        if movesToMake:
            if self.printOutput:
                line = format %(5,'-',5,self.iteration,18,' # of neighbours : ',3,len(neighbours),18,'# of moves : ',3,len(movesToMake),25,'Total delta change : ',5,totalCostChange)
                self.outputLines.append(line)
                print(line)
            routes = self.makeMoves(solution, movesToMake)
            solution = self.makeSolutionDictionaryIFs(solution, routes, tempLoads, tempCosts, routeIndex, tripCostsTemp)
            if self.printOutput:
                line = ''
                self.outputLines.append(line)
                print(line)
        return(movesToMake, solution)
                    
    def localSearch(self, solutionOld):
        format = '%*s%*d%*s%*d%*s%*d%*s%*d'
        self.iteration = 0
        solution = self.intialiseLocalSearch(solutionOld)
                            
        while True:
            self.iteration += 1
            if self.neighbourSearchStrategy == 'MultiLocalSearch':
                (movesToMake, solution) = self.performMulitLocalSearch(solution)
            elif self.neighbourSearchStrategy == 'FastLocalSearch':
                (movesToMake, solution) = self.performFastLocalSearch(solution)
            elif self.neighbourSearchStrategy == 'FastLocalSearch2':
                (movesToMake, solution) = self.performFastLocalSearch(solution)
            elif self.neighbourSearchStrategy == 'FullLocalSearch':
                (movesToMake, solution) = self.performFullLocalSearch(solution)
            if not movesToMake:break
            solution = self.intialiseLocalSearch(solution)
        nTrips = len(solution.keys())-1
        return(solution, nTrips)  

#===============================================================================
# 
#===============================================================================
def unitTest(info, solution):
    import testSolutions
    FS = LocalSearchIFs(info)
#    FS.neighbourSearchStrategy = 'MultiLocalSearch'
    FS.neighbourSearchStrategy = 'MultiLocalSearch'
    #FS.neighbourSearchStrategy = 'FullLocalSearch'
    if not solution[1].get('Subtrip cost'):
        solution = transformSolution.transformSolution(info).newRoute(solution)
    er = testSolutions.testSolution(info, solution)
    er.checkFeasibilityIFs()
    er.testReportSolutionIFs()
    print('')
    t1 = time.clock()
    (solution, nTrips) = FS.localSearch(solution)
    e1 = time.clock() - t1
    print(e1)
    print('')
    er = testSolutions.testSolution(info, solution)
    er.checkFeasibilityIFs()
    er.testReportSolutionIFs()
    
    
if __name__ == "__main__":
    import cPickle
    import LancommeARPconversions3 as LARP
#    import psyco
#    psyco.full()
    fileName1 = 'cen_IF_ProblemInfo/Centurion_a_pickled.dat'
    info1 = LARP.ReadProblemDataIFs(fileName1)
    s1 = open('cen_IF_Results/Centurion_a_Init_sol.txt')
    solution1 = cPickle.load(s1)
    unitTest(info1, solution1)
