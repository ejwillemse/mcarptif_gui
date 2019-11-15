import copy

class testSolution(object):
    
    def __init__(self, info, solution):
        self.info = info
        self.solution = solution
        self.errorReport = {}
        self.TeversalReport = []
        self.additionalTraversalReport = []
        self.outPutLines = []
        self.raiseException = False
        
    def testReportSolution(self):
        line = []
        line.append('TEST SOLUTION')
        print(line[-1])
        line.append('-------------------------------------------------------------------')
        print(line[-1])
        self.checkFeasibility()
        line.append(' Vehicle load exceptions      = %d' % self.errorReport['Exceptions']['Vehicle load exceptions'])
        print(line[-1])
        line.append(' Max vehicle trip exceptions  = %d' % self.errorReport['Exceptions']['Max vehicle trip exceptions'])
        print(line[-1])
        line.append(' Available vehicle exceptions = %d' % self.errorReport['Exceptions']['Available vehicles exception'])
        print(line[-1])
        line.append(' ')
        print(line[-1])
        line.append(' T cost reporting exception   = %d' % self.errorReport['Exceptions']['Cost exception'])
        print(line[-1])
        line.append(' Sub cost reporting exception = %d' % self.errorReport['Exceptions']['Sub cost exception'])
        print(line[-1])
        line.append(' Load reporting exception     = %d' % self.errorReport['Exceptions']['Load report exception'])
        print(line[-1])
        line.append(' ')
        print(line[-1])
        line.append('             Total Exceptions = %d' % self.errorReport['Exceptions']['Total exception'])
        print(line[-1])
        line.append(' ')
        print(line[-1])
        if self.errorReport['Exceptions']['Total exception']:
            self.raiseException = True
            line.append(' ')
            print(line[-1])
        if self.errorReport['Exceptions']['Sub cost exception']:
            line.append(' Trip cost miscalculated on')
            print(line[-1])
            for i in self.errorReport['Exceptions']['Sub cost exception routes']:
                line.append('         Route : %d' %i)
                print(line[-1])
                line.append(' ')
                print(line[-1])
        if self.errorReport['Exceptions']['Available vehicles exception']:
            line.append(' Number of allowed vehicle trips %d' %self.info.nVehicles)
            print(line[-1])
            line.append('          Actual number of trips %d' % (self.errorReport['Vehicle fleet exceeded'][1]+self.info.nVehicles))
            print(line[-1])   
            line.append(' ')
            print(line[-1])       
        self.checkService()
        line.append(' Number of required edges/arcs not serviced = %d' % len(self.TeversalReport))
        print(line[-1])
        if len(self.TeversalReport):
            self.raiseException = True
            line.append('     Edges/arcs not serviced : ')
            print(line[-1])
            for i in self.TeversalReport: 
                line.append(i)
                print(line[-1])
        line.append(' ')
        print(line[-1])
        line.append(' Reported final answer = %d' % self.solution['Total cost'])
        print(line[-1])
        line.append(' Actual final answer   = %d' % self.errorReport['Total Cost'][0])
        print(line[-1])
        line.append('           Difference  = %d' % (self.solution['Total cost']-self.errorReport['Total Cost'][0]))
        print(line[-1])
        self.outPutLines = self.outPutLines + line
        if (self.solution['Total cost']-self.errorReport['Total Cost'][0]):
            self.raiseException = True
            line.append(' ')
            print(line[-1])   

    def testReportSolutionIFs(self):
        line = []
        line.append('TEST SOLUTION')
        print(line[-1])
        line.append('-------------------------------------------------------------------')
        print(line[-1])
        self.checkFeasibilityIFs()
        line.append(' Vehicle load exceptions      = %d' % self.errorReport['Exceptions']['Vehicle load exceptions'])
        print(line[-1])
        line.append(' Max vehicle trip exceptions  = %d' % self.errorReport['Exceptions']['Max vehicle trip exceptions'])
        print(line[-1])
        line.append(' Available vehicle exceptions = %d' % self.errorReport['Exceptions']['Available vehicles exception'])
        print(line[-1])
        line.append(' ')
        print(line[-1])
        line.append(' T cost reporting exception   = %d' % self.errorReport['Exceptions']['Cost exception'])
        print(line[-1])
        line.append(' Sub cost reporting exception = %d' % self.errorReport['Exceptions']['Sub cost exception'])
        print(line[-1])
        line.append(' Sbtrip cst reprting excption = %d' % self.errorReport['Exceptions']['Subroute cost exception'])
        print(line[-1])
        line.append(' Load reporting exception     = %d' % self.errorReport['Exceptions']['Load report exception'])
        print(line[-1])
        line.append(' Depot or IF exception        = %d' % self.errorReport['Exceptions']['IF depot exception'])
        print(line[-1])
        line.append(' IF start end exception       = %d' % self.errorReport['Exceptions']['IF start end exception'])
        print(line[-1])
        line.append(' ')
        print(line[-1])
        line.append('             Total Exceptions = %d' % self.errorReport['Exceptions']['Total exception'])
        print(line[-1])
        line.append(' ')
        print(line[-1])
        
        if self.errorReport['Exceptions']['Total exception']:
            self.raiseException = True
            line.append(' ')
            print(line[-1])
            
        if self.errorReport['Exceptions']['Sub cost exception']:
            line.append(' Trip cost miscalculated on')
            print(line[-1])
            for i in self.errorReport['Exceptions']['Sub cost exception routes']:
                line.append('         Route : %d' %i)
                print(line[-1])
            line.append(' ')
            print(line[-1])
            
        if self.errorReport['Exceptions']['Subroute cost exception']:
            line.append(' Subtrip cost miscalculated on')
            print(line[-1])
            for i in self.errorReport['Exceptions']['Subroute cost exception routes']:
                line.append('         Route : %i %i' %i)
                print(line[-1])
            line.append(' ')
            print(line[-1])
            
        if self.errorReport['Exceptions']['Load report exception']:
            line.append(' Subtrip load miscalculated on')
            print(line[-1])
            for i in self.errorReport['Exceptions']['Load report exception routes']:
                line.append('         Route : %i %i' %i)
                print(line[-1])
            line.append(' ')
            print(line[-1])
            
        if self.errorReport['Exceptions']['Available vehicles exception']:
            line.append(' Number of allowed vehicle trips %d' %self.info.nVehicles)
            print(line[-1])
            line.append('          Actual number of trips %d' % (self.errorReport['Vehicle fleet exceeded'][1]+self.info.nVehicles))
            print(line[-1])   
            line.append(' ')
            print(line[-1])
            
        if self.errorReport['Exceptions']['IF depot exception']:
            line.append(' Depot or IF exception on')
            print(line[-1])
            for i in self.errorReport['Exceptions']['IF depot exception routes']:
                line.append('         Route : %i %i' %i)
                print(line[-1])
            line.append(' ')
            print(line[-1])
            
        if self.errorReport['Exceptions']['IF start end exception']:
            line.append(' IF start end exception on')
            print(line[-1])
            for i in self.errorReport['Exceptions']['IF start end exception routes']:
                line.append('         Route : %i subroutes %i %i' %i)
                print(line[-1])
            line.append(' ')
            print(line[-1])            
            
        if len(self.TeversalReport):
            line.append(' Number of required edges/arcs not serviced = %d' % len(self.TeversalReport))
            print(line[-1])
            self.raiseException = True
            line.append('     Edges/arcs not serviced : ')
            print(line[-1])
            for i in self.TeversalReport: 
                line.append(str(i))
                print(line[-1])
                
        if len(self.additionalTraversalReport):
            line.append(' Number of redundant required edges/arcs serviced = %d' % len(self.additionalTraversalReport))
            print(line[-1])
            self.raiseException = True
            line.append('    Unnecessary edges/arcs serviced : ')
            print(line[-1])
            for i in self.additionalTraversalReport: 
                line.append(str(i))
                print(line[-1])
                
        line.append(' ')
        print(line[-1])
        line.append(' Reported final answer = %d' % self.solution['Total cost'])
        print(line[-1])
        line.append(' Actual final answer   = %d' % self.errorReport['Total Cost'][0])
        print(line[-1])
        line.append('           Difference  = %d' % (self.solution['Total cost']-self.errorReport['Total Cost'][0]))
        print(line[-1])
        self.outPutLines = self.outPutLines + line
        if (self.solution['Total cost']-self.errorReport['Total Cost'][0]):
            self.raiseException = True
            line.append(' ')
            print(line[-1]) 
       
    def calcRouteCostCap(self,route):
        nArcs = len(route)
        cost = 0
        load = 0
        for i in (range(nArcs-1)):
            cost = cost + self.info.spDistanceD[route[i]][route[i+1]] + self.info.serveCostD[route[i]]
            load = load + self.info.demandD[route[i]]
        cost = cost + self.info.serveCostD[route[i+1]]# + self.info.dumpCost
        load = load + self.info.demandD[route[i+1]]
        return(cost,load)


    def checkFeasibility(self):
        huge = 1e30000
        nVehicles = self.solution.keys()
        vehicleCap = self.info.capacity
        allowedVehicles = self.info.nVehicles
        if self.info.maxTrip: maxTrip = self.info.maxTrip
        else: maxTrip = huge
        wrongSubcosts = []
        actualVehicles = 0
        tCost = 0
        loadExeptions = 0
        routeLenExceptions = 0
        nVehicleExceptions = 0
        loadReportExceptions = 0
        subCostExceptions = 0
        for i in nVehicles:
            if i != 'Total cost':
                actualVehicles = actualVehicles + 1
                route = self.solution[i]['Solution']
                (cost,load) = self.calcRouteCostCap(route)
                cost = cost + self.info.dumpCost
                self.errorReport[i] = {}
                tCost = tCost + cost
                if load > vehicleCap:
                    loadExeptions = loadExeptions + 1
                    self.errorReport[i]['Route load'] = [load,self.solution[i]['Load'],'Exceed load',load-vehicleCap]
                else:
                    self.errorReport[i]['Route load'] = [load,self.solution[i]['Load']]             
                if load != self.solution[i]['Load']:loadReportExceptions += 1
                if cost > maxTrip:
                    routeLenExceptions = routeLenExceptions + 1
                    self.errorReport[i]['Route length'] = [cost,self.solution[i]['Cost'],'Exceed max trip',cost-maxTrip]
                else:
                    self.errorReport[i]['Route length'] = [cost,self.solution[i]['Cost']]
                if cost != self.solution[i]['Cost']: 
                    wrongSubcosts.append(i)
                    subCostExceptions += 1
                
        self.errorReport['Total Cost'] = [tCost,self.solution['Total cost']]
        if tCost != self.solution['Total cost']:
            totalCostException = 1
        else:
            totalCostException = 0
            
        if actualVehicles > allowedVehicles:
            self.errorReport['Vehicle fleet exceeded'] = ['Yes',actualVehicles-allowedVehicles]
            nVehicleExceptions = 1
        
        self.errorReport['Exceptions'] = {}
        self.errorReport['Exceptions']['Vehicle load exceptions'] = loadExeptions
        self.errorReport['Exceptions']['Max vehicle trip exceptions'] = routeLenExceptions
        self.errorReport['Exceptions']['Available vehicles exception'] = nVehicleExceptions
        self.errorReport['Exceptions']['Sub cost exception'] = subCostExceptions
        self.errorReport['Exceptions']['Subtrip cost exception'] = wrongSubcosts      
        self.errorReport['Exceptions']['Load report exception'] = loadReportExceptions
        self.errorReport['Exceptions']['Cost exception'] = totalCostException
        self.errorReport['Exceptions']['Total exception'] = loadExeptions + routeLenExceptions + nVehicleExceptions + totalCostException + loadReportExceptions + subCostExceptions
        if self.errorReport['Exceptions']['Total exception']: self.raiseException = True

    def checkFeasibilityIFs(self):
        depot = self.info.depotArc
        IFs = self.info.IFarcs
        huge = 1e30000
        nVehicles = self.solution.keys()
        vehicleCap = self.info.capacity
        allowedVehicles = self.info.nVehicles
        if self.info.maxTrip: maxTrip = self.info.maxTrip
        else: maxTrip = huge
        wrongSubcosts = []
        wrongSubLoad = []
        wrongSubRouteCosts = []
        actualVehicles = 0
        tCost = 0
        loadExeptions = 0
        routeLenExceptions = 0
        nVehicleExceptions = 0
        loadReportExceptions = 0
        subCostExceptions = 0
        subRouteCostExceptions = 0
        IfDepotError = 0
        IfDeptErrorRoutes = []
        startEndIFerror = 0
        startEndIFerrorRoutes = []
        for i in nVehicles:
            if i != 'Total cost':
                actualVehicles = actualVehicles + 1
                route = self.solution[i]['Solution']
                routeCost = 0
                self.errorReport[i] = {}
                self.errorReport[i]['Route load'] = {}
                for subRoute in range(len(route)):
                    if subRoute == 0:
                        if route[subRoute][0] != depot:
                            IfDepotError += 1
                            IfDeptErrorRoutes.append((i,subRoute))
                    else:
                        if route[subRoute][0] not in IFs:
                            IfDepotError += 1
                            IfDeptErrorRoutes.append((i,subRoute))
                    if subRoute == (len(route)-1):
                        if route[subRoute][-1] != depot:
                            IfDepotError += 1
                            IfDeptErrorRoutes.append((i,subRoute))
                        if route[subRoute][-2] not in IFs:
                            IfDepotError += 1
                            IfDeptErrorRoutes.append((i,subRoute))
                    else:
                        if route[subRoute][-1] not in IFs:
                            IfDepotError += 1
                            IfDeptErrorRoutes.append((i,subRoute))                   
                    if subRoute > 0:
                        if route[subRoute][0] != route[subRoute-1][-1]:
                            startEndIFerror += 1
                            startEndIFerrorRoutes.append((i, subRoute-1, subRoute))
                    (cost,load) = self.calcRouteCostCap(route[subRoute])
                    cost += self.info.dumpCost
                    routeCost += cost
                    if load > vehicleCap:
                        loadExeptions = loadExeptions + 1
                        self.errorReport[i]['Route load'][subRoute] = [load,self.solution[i]['Load'][subRoute],'Exceed load',load-vehicleCap]
                        self.line.append('')
                        print(self.line[-1])
                        self.line.append('LOAD EXCEPTION ERROR --- Route: %d     Subroute: %d     Load: %d    Cap: %d' %(i,subRoute,load,vehicleCap))
                        print(self.line[-1])
                    else:
                        self.errorReport[i]['Route load'][subRoute] = [load,self.solution[i]['Load'][subRoute]]             
                        if load != self.solution[i]['Load'][subRoute]:
                            loadReportExceptions += 1
                            wrongSubLoad.append((i,subRoute))
                    if self.solution[i].get('Subtrip cost'):
                        if self.solution[i].get('Subtrip cost')[subRoute] != cost:
                            subRouteCostExceptions += 1
                            wrongSubRouteCosts.append((i,subRoute))

                if routeCost > maxTrip:
                    routeLenExceptions = routeLenExceptions + 1
                    self.errorReport[i]['Route length'] = [cost,self.solution[i]['Cost'],'Exceed max trip',cost-maxTrip]
                    self.line.append('')
                    print(self.line[-1])
                    self.line.append('COST EXCEPTION ERROR --- Route: %d     Cost: %d    Cap: %d' %(i,cost,maxTrip))
                    print(self.line[-1])  
                else:
                    self.errorReport[i]['Route length'] = [cost,self.solution[i]['Cost']]
                if routeCost != self.solution[i]['Cost']: 
                    wrongSubcosts.append(i)
                    subCostExceptions += 1
                tCost += routeCost

                
        self.errorReport['Total Cost'] = [tCost,self.solution['Total cost']]
        if tCost != self.solution['Total cost']:
            totalCostException = 1
        else:
            totalCostException = 0
            
        if actualVehicles > allowedVehicles:
            self.errorReport['Vehicle fleet exceeded'] = ['Yes',actualVehicles-allowedVehicles]
            nVehicleExceptions = 1
        
        self.checkService()
            
        totalExceptions = loadExeptions + routeLenExceptions + nVehicleExceptions + subCostExceptions + subRouteCostExceptions + loadReportExceptions + IfDepotError + totalCostException + startEndIFerror
        if len(self.TeversalReport):totalExceptions+=1
        if len(self.TeversalReport):totalExceptions+=1
        self.errorReport['Exceptions'] = {}
        self.errorReport['Exceptions']['Vehicle load exceptions'] = loadExeptions
        self.errorReport['Exceptions']['Max vehicle trip exceptions'] = routeLenExceptions
        self.errorReport['Exceptions']['Available vehicles exception'] = nVehicleExceptions
        self.errorReport['Exceptions']['Sub cost exception'] = subCostExceptions
        self.errorReport['Exceptions']['Sub cost exception routes'] = wrongSubcosts
        self.errorReport['Exceptions']['Subroute cost exception'] = subRouteCostExceptions
        self.errorReport['Exceptions']['Subroute cost exception routes'] = wrongSubRouteCosts      
        self.errorReport['Exceptions']['Load report exception'] = loadReportExceptions
        self.errorReport['Exceptions']['Load report exception routes'] = wrongSubLoad
        self.errorReport['Exceptions']['Cost exception'] = totalCostException
        self.errorReport['Exceptions']['IF depot exception'] = IfDepotError
        self.errorReport['Exceptions']['IF depot exception routes'] = IfDeptErrorRoutes
        self.errorReport['Exceptions']['IF start end exception'] = startEndIFerror
        self.errorReport['Exceptions']['IF start end exception routes'] = startEndIFerrorRoutes
        self.errorReport['Exceptions']['Total exception'] = totalExceptions
        if self.errorReport['Exceptions']['Total exception']: self.raiseException = True
       
    def checkIFsMaxServiceLoad(self):
        huge = 1e30000
        tCost=0
        vehicleCap = self.info.capacity
        allowedVehicles = self.info.nVehicles
        if self.info.maxTrip: maxTrip = self.info.maxTrip
        else: maxTrip = huge
        Solutions = copy.deepcopy(self.solution)
        nVehicles = len(Solutions) - 1
        loadExeptions = 0
        routeLenExceptions = 0
        nVehicleExceptions = 0
        for i in range(nVehicles):
            self.errorReport[i+1] = {}
            routesWif = Solutions[i+1]['Solution']
            nRoutes = len(routesWif)
            newSolution = []
            self.errorReport[i+1]['Intermediate routes'] = {}
            for j in range(nRoutes):
                self.errorReport[i+1]['Intermediate routes'][j+1] = {}
                newSolution = newSolution + routesWif[j]
                (cost,load) = self.calcRouteCostCap(routesWif[j])
                cost = cost + self.info.dumpCost
                if load > vehicleCap:
                    loadExeptions = loadExeptions + 1 
                    self.errorReport[i+1]['Intermediate routes'][j+1] = [load,load,'Exceed Capacity',load-vehicleCap]
                    print('')
                    print('LOAD EXCEPTION ERROR --- Route: %d     Subroute: %d     Load: %d    Cap: %d' %(i,j,load,vehicleCap))
                    print('')
                else:
                    self.errorReport[i+1]['Intermediate routes'][j+1] = [load,load]
            Solutions[i+1]['Solution'] = newSolution
            (cost,load) = self.calcRouteCostCap(newSolution)
            cost = cost + self.info.dumpCost*nRoutes
            print(cost,self.solution[i+1]['Cost'])
            self.errorReport[i+1]['Route load']   = [load,sum(self.solution[i+1]['Load'])]
            if cost > maxTrip:
                routeLenExceptions = routeLenExceptions + 1
                self.errorReport[i+1]['Route length'] = [cost,self.solution[i+1]['Cost'],'Exceed max trip',cost-maxTrip]
                print('')
                print('COST EXCEPTION ERROR --- Route: %d     Cost: %d    Cap: %d' %(i,cost,maxTrip))
                print('')                
            else:
                self.errorReport[i+1]['Route length'] = [cost,self.solution[i+1]['Cost']]
            tCost = tCost + cost
        self.errorReport['Total Cost'] = [tCost,self.solution['Total cost']]
        if nVehicles > allowedVehicles:
            self.errorReport['Vehicle fleet exceeded'] = ['Yes',nVehicles-allowedVehicles]
            nVehicleExceptions = 1
        self.errorReport['Exceptions'] = {}
        self.errorReport['Exceptions']['Vehicle load exceptions'] = loadExeptions
        self.errorReport['Exceptions']['Max vehicle trip exceptions'] = routeLenExceptions
        self.errorReport['Exceptions']['Avaialble vehicles exception'] = nVehicleExceptions
        self.errorReport['Exceptions']['Total exception'] = loadExeptions + routeLenExceptions + nVehicleExceptions
        
                
    def checkService(self):
        Solutions = self.solution
        nVehicles = len(self.solution) - 1
        requiredArcs = self.info.reqArcList
        checkRequiredArcs = requiredArcs[:]
        aditionalArcsServiced = []
        for i in range(nVehicles):
            route = Solutions[i+1]['Solution']
            try:
                nIFsRoute = len(route[0])
            except:
                nIFsRoute = None
            if nIFsRoute:
                nIFsRoute = len(route)
                for j in range(nIFsRoute):
                    routeIF =  route[j]
                    nArcs = len(routeIF)
                    for q in range(nArcs):
                        if routeIF[q] in checkRequiredArcs:
                            checkRequiredArcs.remove(routeIF[q])
                            if self.info.invArcD[routeIF[q]]:
                                checkRequiredArcs.remove(self.info.invArcD[routeIF[q]])
                        elif (routeIF[q] != self.info.depotArc) & (routeIF[q] not in self.info.IFarcs):
                            aditionalArcsServiced.append(routeIF[q])
#                            print('{484}',routeIF[q], i, j)
                            
            else:
                nArcs = len(route)
                for q in range(nArcs):
                    if route[q] in checkRequiredArcs:
                        checkRequiredArcs.remove(route[q])
                        if self.info.invArcD[route[q]]:
                            checkRequiredArcs.remove(self.info.invArcD[route[q]])
                    elif route[q] != self.info.depotArc:
                        aditionalArcsServiced.append(route[q])
                        if self.info.invArcD[route[q]]:aditionalArcsServiced.append(self.info.invArcD[route[q]])
        checkRequiredArcsCopy = checkRequiredArcs[:]
        if checkRequiredArcsCopy:
            for arc in checkRequiredArcsCopy:
                if self.info.invArcD[arc]:
                    if self.info.invArcD[arc] in checkRequiredArcs:
                        checkRequiredArcs.remove(arc)
        aditionalArcsServicedCopy = aditionalArcsServiced[:]
        if aditionalArcsServicedCopy:
            for arc in aditionalArcsServicedCopy:
                if self.info.invArcD[arc]:
                    if self.info.invArcD[arc] in aditionalArcsServiced:
                        aditionalArcsServiced.remove(arc)
        self.TeversalReport = checkRequiredArcs
        self.additionalTraversalReport = aditionalArcsServiced
        