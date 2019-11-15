'''
Created on 11 May 2010

@author: BowenKT
'''
import gen_neighbours_beta1 as RN_single
import local_search_IF_new as LS
from copy import deepcopy

class ReduceNumberOfVehicleRoutes(object):
    
    def __init__(self, info):
        self.info = info
        self.RoutMod = RN_single.SinlgeRouteModifications(self.info)
        self.MakeLists = LS.ImplementLocalSearchIFs(info)
        self.nVehciles = self.info.nVehicles
        self.cap = self.info.capacity
        self.demand = self.info.demandD
        self.sCost = self.info.serveCostD
        self.temp = []
        self.printOutput = True
        self.outputLines = []
        self.maxTrip = self.info.maxTrip
        self.printOutput2 = True    
    
    def dismantleSolution(self, solution, nDismantlements):
        newRoutes = []
        newLoads = []
        newCosts = []
        newTripCosts = []
        unservicedArcs = []
        unservicedDemandArcs = []
        routeIndex = {}
        newSolution = {}
        nRoutes = len(solution.keys())-1
        loads = []
        for i in range(nRoutes):
            loads.append(sum(solution[i+1]['Load']))
        
        for i in range(nDismantlements):
            minRoute = loads.index(min(loads))+1
            routeI = solution[minRoute]['Solution']
            loads[minRoute-1] = 1e300000
            for subRouteI in range(len(routeI)):
                if subRouteI == len(routeI) - 1: unservicedArcs += routeI[subRouteI][1:-2]
                else: unservicedArcs += routeI[subRouteI][1:-1]
                
        k = -1
        reduce = 0
        for i in range(nRoutes):
            routeI = deepcopy(solution[i+1])
            if loads[i] != 1e300000:
                newSolution[i-reduce+1] = deepcopy(solution[i+1])
                for subRouteI in range(len(routeI['Solution'])):
                    k += 1
                    if subRouteI == len(routeI['Solution']) - 1:
                        newRoutes.append(routeI['Solution'][subRouteI][0:-1])
                        routeIndex[k] = (i-reduce, subRouteI, True)
                    else: 
                        newRoutes.append(routeI['Solution'][subRouteI])
                        routeIndex[k] = (i-reduce, subRouteI, False)
                    newLoads.append(routeI['Load'][subRouteI])
                    newCosts.append(routeI['Subtrip cost'][subRouteI])
                newTripCosts.append(routeI['Cost'])
            else:reduce += 1
        newSolution['Total cost'] = solution['Total cost']
        for arc in unservicedArcs:
            unservicedDemandArcs.append((self.demand[arc],arc))
        unservicedDemandArcs.sort()
        unservicedDemandArcs.reverse()
        return(newRoutes, newLoads, newCosts, newTripCosts, routeIndex, unservicedDemandArcs, newSolution)
        
    def addExtraArcs(self, newRoutes, newLoads, newCosts, newTripCosts, routeIndex, unservicedDemandArcs):
        nRoutes = len(newRoutes)
        reductionPossible = True
        while unservicedDemandArcs:
            insertionPossible = False
            if unservicedDemandArcs: unservicedArc = unservicedDemandArcs.pop(0)
            bestInsert = 1e300000
            for i in range(nRoutes):
                actualI = routeIndex[i][0]
                if newLoads[i] + unservicedArc[0] <= self.cap:
                    (bestInsertRoute, bestCostChange) = self.RoutMod.findBestSingleArcInsertion(newRoutes[i], unservicedArc[1])
                    if (bestCostChange < bestInsert) & (newTripCosts[actualI] + bestCostChange + self.sCost[unservicedArc[1]] <= self.maxTrip):
                        bestRoute = deepcopy(bestInsertRoute)
                        bestInsert = bestCostChange
                        bestP = i
                        insertionPossible = True
                        bestActualI = actualI
            if insertionPossible == False:
                reductionPossible = False
                break
            else:
                newRoutes[bestP] = deepcopy(bestRoute)
                newLoads[bestP] += unservicedArc[0]
                newCosts[bestP] += bestInsert + self.sCost[unservicedArc[1]]
                newTripCosts[bestActualI] += bestInsert + self.sCost[unservicedArc[1]]
            if not unservicedDemandArcs:break
        return(newRoutes, newLoads, newCosts, newTripCosts, reductionPossible)
                
        
    def fixedReduction(self, solution):
        line = ' Reduce number of vehicle trips'
        self.outputLines.append(line)
        if self.printOutput: print(line)
        line = '------------------------------------------ '
        self.outputLines.append(line)
        if self.printOutput: print(line)
        reducedSolution = deepcopy(solution)
        nTrips = len(solution.keys())-1
        reductionPossible = False
        if len(nTrips) > self.nVehciles:
            line = ' Original number of trips : %d ' % (len(nTrips))
            self.outputLines.append(line)
            if self.printOutput: print(line)
            nDismantlements = len(nTrips) - self.nVehciles
            line = '  Allowed number of trips : %d ' % (self.nVehciles)
            self.outputLines.append(line)
            if self.printOutput: print(line)
            line = '            Original cost : %d ' % (solution['Total cost'])
            self.outputLines.append(line)
            if self.printOutput: print(line)
            (newRoutes, newLoads, newCosts, newTripCosts, routeIndex, unservicedDemandArcs, newSolution) = self.dismantleSolution(solution, nDismantlements)
            (newRoutes, newLoads, newCosts, newTripCosts, reductionPossible) = self.addExtraArcs(newRoutes, newLoads, newCosts, newTripCosts, routeIndex, unservicedDemandArcs)
            if reductionPossible:
                reducedSolution = self.MakeLists.makeSolutionDictionaryIFs(newSolution, newRoutes, newLoads, newCosts, routeIndex, newTripCosts)
                line = ''
                self.outputLines.append(line)
                if self.printOutput: print(line)
                line = '         Trips removed : %d ' % (nDismantlements)
                self.outputLines.append(line)
                if self.printOutput: print(line)
                line = '     New solution cost : %d ' % (reducedSolution['Total cost'])
                self.outputLines.append(line)
                if self.printOutput: print(line)
                line = 'Solution cost increase : %d ' % (reducedSolution['Total cost']-solution['Total cost'])
                self.outputLines.append(line)
                if self.printOutput: print(line)
                line = ''
                self.outputLines.append(line)
                if self.printOutput: print(line)
            else:
                line = ''
                self.outputLines.append(line)
                if self.printOutput: print(line)
                line = '  Can not reduce the number trips'
                self.outputLines.append(line)
                if self.printOutput: print(line)
        else:
            line = '  Solution already feasible'
            self.outputLines.append(line)
            if self.printOutput: print(line) 
        return(reducedSolution, reductionPossible)
    
    def variableReduction(self, solution):
        reducedSolution = deepcopy(solution)
        nTrips = len(solution.keys())-1
        reduced = False
        nDismantlements = 0
        if self.printOutput: 
            line = ' Reduce number of vehicle trips variable'
            self.outputLines.append(line)
            print(line)
            line = '------------------------------------------ '
            self.outputLines.append(line)
            print(line)
            line = ' Original number of trips : %d ' % (nTrips)
            self.outputLines.append(line) 
            print(line)
            line = '  Allowed number of trips : %d ' % (self.nVehciles)
            self.outputLines.append(line)
            print(line)
            line = '            Original cost : %d ' % (solution['Total cost'])
            self.outputLines.append(line)
            print(line)
        if nTrips == 1:
            if self.printOutput: 
                line = ''
                self.outputLines.append(line)
                print(line)
                line = 'Cannot reduce solution'
                self.outputLines.append(line)
                print(line)
        else:
            while True:
                nDismantlements += 1
                (newRoutes, newLoads, newCosts, newTripCosts, routeIndex, unservicedDemandArcs, reducedSolutionTemp) = self.dismantleSolution(solution, nDismantlements)
                (newRoutes, newLoads, newCosts, newTripCosts, reductionPossible) = self.addExtraArcs(newRoutes, newLoads, newCosts, newTripCosts, routeIndex, unservicedDemandArcs)
                if reductionPossible:
                    reducedSolution = self.MakeLists.makeSolutionDictionaryIFs(reducedSolutionTemp, newRoutes, newLoads, newCosts, routeIndex, newTripCosts)
                    if self.printOutput2: 
                        line = ''
                        self.outputLines.append(line)
                        print(line) 
                        line = '         Trips removed : %d ' % (nDismantlements)
                        self.outputLines.append(line)
                        print(line)
                        line = '     New solution cost : %d ' % (reducedSolution['Total cost'])
                        self.outputLines.append(line)
                        print(line)
                        line = 'Solution cost increase : %d ' % (reducedSolution['Total cost']-solution['Total cost'])
                        self.outputLines.append(line)
                        print(line)
                        line = ''
                        self.outputLines.append(line)
                        print(line)
                    reduced = True
                else:
                    if self.printOutput: 
                        line = ''
                        self.outputLines.append(line)
                        print(line)
                    break
        nTrips = len(reducedSolution.keys())-1
        return(reducedSolution, reduced, nTrips)
 
    def iterativeReduction(self, solution):
        line = ' Reduce number of vehicle trips variable'
        self.outputLines.append(line)
        if self.printOutput: print(line)
        line = '------------------------------------------ '
        self.outputLines.append(line)
        if self.printOutput: print(line)
        (routes, loads, costs,  serviceCosts) = self.MakeLists.makeSolutionList(solution)
        self.temp = (loads, costs, serviceCosts)
        reducedSolution = deepcopy(solution)
        reduced = False
        line = ' Original number of trips : %d ' % (len(routes))
        self.outputLines.append(line)
        if self.printOutput: print(line)
        line = '  Allowed number of trips : %d ' % (self.nVehciles)
        self.outputLines.append(line)
        if self.printOutput: print(line)
        line = '            Original cost : %d ' % (solution['Total cost'])
        self.outputLines.append(line)
        if self.printOutput: print(line)
        nDismantlements = 1
        while True:
            (newRoutes, newLoads, newCosts, newServiceCosts, unservicedDemandArcs) = self.dismantleSolution(solution, nDismantlements)
            (newRoutes, newLoads, newCosts, newServiceCosts, reductionPossible) = self.addExtraArcs(newRoutes, newLoads, newCosts, newServiceCosts, unservicedDemandArcs)
            if reductionPossible:
                reducedSolution = self.MakeLists.makeSolutionDictionary(newRoutes, newLoads, newCosts)
                line = ''
                self.outputLines.append(line)
                if self.printOutput: print(line)
                line = '         Trips removed : %d ' % (nDismantlements)
                self.outputLines.append(line)
                if self.printOutput: print(line)
                line = '     New solution cost : %d ' % (reducedSolution['Total cost'])
                self.outputLines.append(line)
                if self.printOutput: print(line)
                line = 'Solution cost increase : %d ' % (reducedSolution['Total cost']-solution['Total cost'])
                self.outputLines.append(line)
                if self.printOutput: print(line)
                line = ''
                self.outputLines.append(line)
                if self.printOutput: print(line)
                reduced = True
                solution = deepcopy(reducedSolution)
            else:
                line = ''
                self.outputLines.append(line)
                if self.printOutput: print(line)
                break
        return(reducedSolution, reduced)
 
        
def unitTest(info, solution):
    import testSolutions
    er = testSolutions.testSolution(info, solution)
    er.checkFeasibility()
    er.testReportSolution()
    print('')
    Reduce = ReduceNumberOfVehicleRoutes(info)
    (solution, reductionPossible) = Reduce.fixedReduction(solution)
    print('')
    print(reductionPossible)
    er = testSolutions.testSolution(info, solution)
    er.checkFeasibility()
    er.testReportSolution()    

#def unitTest2(info, solution):
#    import testSolutions
#    if not solution[1].get('Subtrip cost'):
#        solution = transformSolution.transformSolution(info, solution).newRoute()
#    er = testSolutions.testSolution(info, solution)
#    er.checkFeasibilityIFs()
#    er.testReportSolutionIFs()
#    print('')
#    Reduce = ReduceNumberOfVehicleRoutes(info)
#    (solution, reductionPossible, nRoutes) = Reduce.variableReduction(solution)
#    print('')
#    er = testSolutions.testSolution(info, solution)
#    er.checkFeasibilityIFs()
#    er.testReportSolutionIFs()
    
def unitTest3(info, solution):
    import testSolutions
    er = testSolutions.testSolution(info, solution)
    er.checkFeasibility()
    er.testReportSolution()
    print('')
    Reduce = ReduceNumberOfVehicleRoutes(info)
    (solution, reductionPossible) = Reduce.iterativeReduction(solution)
    print('')
    print(reductionPossible)
    er = testSolutions.testSolution(info, solution)
    er.checkFeasibility()
    er.testReportSolution()
    
if __name__=="__main__":
    import cPickle
    import LancommeARPconversions3 as LARP
#    import transformSolution
#    import psyco
#    psyco.full()
    fileName1 = 'lpr_IF_ProblemInfo/Lpr-b-03_pickled.txt'
    info = LARP.ReadProblemDataIFs(fileName1)
    s1 = open('lpr_IF_Solutions_transformed/Ulusoy/Lpr-b-03_Init_MinDepo_sol.txt')
    solution1 = cPickle.load(s1)
    unitTest(info, solution1)

    