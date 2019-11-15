'''
Created on 05 May 2010

@author: ejwillemse
'''
from copy import deepcopy
#===============================================================================
# 
#===============================================================================
class SinlgeRouteModifications(object):

    def __init__(self, info):
        self.info = info
        self.SP = self.info.spDistanceD
        self.Inv = self.info.invArcD

    def singleRemove1route(self, routeI, position):
        arcRemoved = routeI[position]
        costChange = self.SP[routeI[position-1]][routeI[position+1]] - self.SP[routeI[position-1]][routeI[position]] - self.SP[routeI[position]][routeI[position+1]]
        modifiedRoute = routeI[:]
        del modifiedRoute[position]
        return(modifiedRoute, arcRemoved, costChange)
    
    def singleInsert1Route(self, routeI, arcInsert, insertPosistion):
        i = insertPosistion
        costChange = self.SP[routeI[i-1]][arcInsert] + self.SP[arcInsert][routeI[i]] - self.SP[routeI[i-1]][routeI[i]]
        modifiedRoute = routeI[:]
        modifiedRoute[i:i] = [arcInsert]
        return(modifiedRoute, costChange)
    
    def findBestInversionArcInsert(self, routeI, arcRemoved, position):
        modifiedRoute1 = routeI[:]
        j = position
        (modifiedRoute2, costChange2) = self.singleInsert1Route(modifiedRoute1, arcRemoved, j)
        if self.Inv[arcRemoved]:
            (modifiedRoute3, costChange3) = self.singleInsert1Route(modifiedRoute1, self.Inv[arcRemoved], j)
            if costChange3 < costChange2: modifiedRoute2, costChange2 = modifiedRoute3[:], costChange3
        return(modifiedRoute2, costChange2)
    
    def singleBestInsert1Route(self, routeI, arcInsert, depots = True, tabuPositions = None):
        nPositions = len(routeI)
        bestCostChange = 1e300000
        if depots == True:
            for i in range(1,nPositions-1):
                if i not in tabuPositions:
                    costChange = self.SP[routeI[i-1]][arcInsert] + self.SP[arcInsert][routeI[i]] - self.SP[routeI[i-1]][routeI[i]]
                    if costChange < bestCostChange:
                        bestCostChange = costChange
                        bestInsertPosition = i
                        bestModifiedRoute = routeI[:]
                        bestModifiedRoute[i:i] = [arcInsert]
        return(bestModifiedRoute, bestCostChange, bestInsertPosition)

    def doubleRemove1route(self, routeI, position):
        twoArcsRemoved = (routeI[position],routeI[position+1])
        costChange = self.SP[routeI[position-1]][routeI[position+2]] - self.SP[routeI[position-1]][routeI[position]] - self.SP[routeI[position]][routeI[position+1]] - self.SP[routeI[position+1]][routeI[position+2]]
        modifiedRoute = routeI[:]
        del modifiedRoute[position+1]
        del modifiedRoute[position]
        return(modifiedRoute, twoArcsRemoved, costChange)

    def doubleInsert1Route(self, routeI, twoArcsInsert, insertPosistion):
        i = insertPosistion
        (arc1, arc2) = twoArcsInsert
        costChange = self.SP[routeI[i-1]][arc1] + self.SP[arc1][arc2] + self.SP[arc2][routeI[i]] - self.SP[routeI[i-1]][routeI[i]]
        modifiedRoute = routeI[:]
        modifiedRoute[i:i] = [arc1, arc2]
        return(modifiedRoute, costChange)
    
    def findBestInversionDoubleArcInsert(self, routeI, twoArcsRemoved, position):
            (arcs1, arcs2) = twoArcsRemoved
            modifiedRoute1 = routeI[:]
            j= position
            (modifiedRoute2, costChange2) = self.doubleInsert1Route(modifiedRoute1, (arcs1, arcs2), j)
            (modifiedRoute2a, costChange2a) = self.doubleInsert1Route(modifiedRoute1, (arcs1, arcs2), j)
            if costChange2a < costChange2: modifiedRoute2, costChange2 = modifiedRoute2a, costChange2a
            if self.Inv[arcs1]:
                (modifiedRoute3, costChange3) = self.doubleInsert1Route(modifiedRoute1, (self.Inv[arcs1], arcs2), j)
                if costChange3 < costChange2: modifiedRoute2, costChange2 = modifiedRoute3, costChange3
                (modifiedRoute3a, costChange3a) = self.doubleInsert1Route(modifiedRoute1, (arcs2, self.Inv[arcs1]), j)   
                if costChange3a < costChange2: modifiedRoute2, costChange2 = modifiedRoute3a, costChange3a
            if self.Inv[arcs2]:
                (modifiedRoute4, costChange4) = self.doubleInsert1Route(modifiedRoute1, (arcs1, self.Inv[arcs2]), j)
                if costChange4 < costChange2: modifiedRoute2, costChange2 = modifiedRoute4, costChange4
                (modifiedRoute4a, costChange4a) = self.doubleInsert1Route(modifiedRoute1, (self.Inv[arcs2], arcs1), j)
                if costChange4a < costChange2: modifiedRoute2, costChange2 = modifiedRoute4a, costChange4a
            if (self.Inv[arcs1]!=None) & (self.Inv[arcs2]!=None):
                (modifiedRoute5, costChange5) = self.doubleInsert1Route(modifiedRoute1, (self.Inv[arcs1], self.Inv[arcs2]), j)
                if costChange5 < costChange2: modifiedRoute2, costChange2 = modifiedRoute5, costChange5
                (modifiedRoute5a, costChange5a) = self.doubleInsert1Route(modifiedRoute1, (self.Inv[arcs2],self.Inv[arcs1]), j)
                if costChange5a < costChange2: modifiedRoute2, costChange2 = modifiedRoute5a, costChange5a 
            return(modifiedRoute2, costChange2) 
    
    def doubleBestInsert1Route(self, routeI, twoArcsInsert, depots = True, tabuPositions = None): 
        nPositions = len(routeI)
        bestCostChange = 1e300000
        [arc1, arc2] = twoArcsInsert
        if depots == True:
            for i in range(1,nPositions-1):
                if (i not in tabuPositions) & (i+1 not in tabuPositions):
                    costChange = self.SP[routeI[i-1]][arc1] + self.SP[arc1][arc2] + self.SP[arc2][routeI[i]] - self.SP[routeI[i-1]][routeI[i]]
                    if costChange < bestCostChange:
                        bestCostChange = costChange
                        bestInsertPosition = i
                        bestModifiedRoute = routeI[:]
                        bestModifiedRoute[i:i] = [arc1, arc2]
        return(bestModifiedRoute, bestCostChange, bestInsertPosition)



#===============================================================================
# 
#===============================================================================
class SingleRouteRemoveInsertProcedure(SinlgeRouteModifications):
    
    def __init__(self, info):
        SinlgeRouteModifications.__init__(self, info)
        self.info = info
        self.SP = self.info.spDistanceD
        self.Inv = self.info.invArcD
        self.bestChange = 1e300000
        self.bestNeighbour = [[self.bestChange]]

    def removeInsertAllArcs(self, routeI, routeP = None):
        nArcs = len(routeI)
        removalInsertionNeighbourhood = []
        for i in range(1,nArcs-1):
            (modifiedRoute1, arcRemoved, costChange1) = self.singleRemove1route(routeI, i)
            insertPosition = range(1, nArcs-1)
            del insertPosition[i-1]
            for j in insertPosition:
                (modifiedRoute2, costChange2) = self.findBestInversionArcInsert(modifiedRoute1, arcRemoved, j)
                if i < j:tabusTemp = [i-1,i,i+1,j,j+1]
                else:tabusTemp = [i-1,i,i+1,j-1,j]
                neighbour = {'routes':routeP,'pos':(i,j),'arc':arcRemoved,'costDelta':costChange1+costChange2,'loadDelta':(),'serviceDelta':(),'modifiedRoutes':modifiedRoute2,'tabus':deepcopy(tabusTemp)}
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
                neighbour = {'routes':routeP,'pos':(i,j),'arc':(arcRemoved1,arcRemoved2),'costDelta':costChange1+costChange2+costChange3+costChange4,'loadDelta':(),'serviceDelta':(),'modifiedRoutes':modifiedRoute2,'tabus':[i-1,i,i+1,j-1,j,j+1]}
                if (costChange1+costChange2+costChange3+costChange4 < self.bestChange):
                    self.bestChange = costChange1+costChange2+costChange3+costChange4
                    self.bestNeighbour = (costChange1+costChange2+costChange3+costChange4,neighbour,'ExchangeAllArcs','oneRoute')
        return(removalInsertionNeighbourhood)  
    
    def removeInsertAllDoubleArcs(self, routeI, routeP = None):
        nArcs = len(routeI)
        removalInsertionNeighbourhood = []
        for i in range(1,nArcs-2):
            (modifiedRoute1, twoArcsRemoved, costChange1) = self.doubleRemove1route(routeI, i)
            insertPosition = range(1, nArcs-2)
            del insertPosition[i-1]
            for j in insertPosition:
                if i < j:(modifiedRoute2, costChange2) = self.findBestInversionDoubleArcInsert(modifiedRoute1, twoArcsRemoved, j-1)
                else:(modifiedRoute2, costChange2) = self.findBestInversionDoubleArcInsert(modifiedRoute1, twoArcsRemoved, j)
                if i < j:tabusTemp = [i-1,i,i+1,i+2,j,j+1]
                else:tabusTemp = [i-1,i,i+1,i+2,j-1,j]
                neighbour = {'routes':routeP,'pos':(i,j),'arc':twoArcsRemoved,'costDelta':costChange1+costChange2,'loadDelta':(),'serviceDelta':(),'modifiedRoutes':modifiedRoute2,'tabus':deepcopy(tabusTemp)}
                if (costChange1+costChange2 < self.bestChange):
                    self.bestChange = costChange1+costChange2
                    self.bestNeighbour = (costChange1+costChange2,neighbour,'RemoveInsertAllDoubleArcs','oneRoute')
        return(removalInsertionNeighbourhood)
    
    def exchangeAllDoubleArcs(self, routeI, routeP = None):
        nArcs = len(routeI)
        removalInsertionNeighbourhood = []
        for i in range(1,nArcs-4):
            (modifiedRoute1, twoArcsRemoved1, costChange1) = self.doubleRemove1route(routeI, i)
            for j in range(i+3,nArcs-2):
                (modifiedRoute2, twoArcsRemoved2, costChange2) = self.doubleRemove1route(modifiedRoute1, j-2)
                (modifiedRoute2, costChange3) = self.findBestInversionDoubleArcInsert(modifiedRoute2, twoArcsRemoved1, j-2)
                (modifiedRoute2, costChange4) = self.findBestInversionDoubleArcInsert(modifiedRoute2, twoArcsRemoved2, i)
                neighbour = {'routes':routeP,'pos':(i,j),'arc':(twoArcsRemoved1,twoArcsRemoved2),'costDelta':costChange1+costChange2+costChange3+costChange4,'loadDelta':(),'serviceDelta':(),'modifiedRoutes':modifiedRoute2,'tabus':[i-1,i,i+1,i+2,j-1,j,j+1,j+2]}
                if (costChange1+costChange2+costChange3+costChange4 < self.bestChange):
                    self.bestChange = costChange1+costChange2+costChange3+costChange4
                    self.bestNeighbour = (costChange1+costChange2+costChange3+costChange4,neighbour,'ExchangeAllDoubleArcs','oneRoute')
        return(removalInsertionNeighbourhood)     

    def generateAllNeighbourhoodsSingleRoutes(self, route,routeP=None):
        self.removeInsertAllArcs(route,routeP)
        self.exchangeAllArcs(route,routeP)
        self.removeInsertAllDoubleArcs(route,routeP)
        self.exchangeAllDoubleArcs(route,routeP)
    
    def generateAllRoutesNeighbourhoodsSingleRoutes(self, routes):
        for routeP in range(len(routes)):
            self.generateAllNeighbourhoodsSingleRoutes(routes[routeP], routeP)

#===============================================================================
# 
#===============================================================================
class MultipleRouteRemoveInsertProcedure(SinlgeRouteModifications):
    
    def __init__(self, info):
        SinlgeRouteModifications.__init__(self, info)
        self.info = info
        self.capacity = info.capacity
        self.SP = self.info.spDistanceD
        self.Inv = self.info.invArcD
        self.demandD = self.info.demandD
        self.serviceD = self.info.serveCostD
        self.bestChange = 1e300000
        self.bestNeighbour = [[self.bestChange]]
        self.maxTrip = self.info.maxTrip
    
    def singleArcExchangeDeltas(self,arcRemovedI,arcRemovedJ,costsChange):
        loadI = self.demandD[arcRemovedI]
        loadJ = self.demandD[arcRemovedJ]
        serviceCostI = self.serviceD[arcRemovedI]
        serviceCostJ = self.serviceD[arcRemovedJ]
        (costChangeI1, costChangeI2, costChangeJ1, costChangeJ2) = costsChange
        costIdelta = costChangeI1 + costChangeI2
        costJdelta = costChangeJ1 + costChangeJ2
        loadIdelta = -loadI + loadJ
        loadJdelta = loadI - loadJ
        serviceCostIdelta = -serviceCostI + serviceCostJ
        serviceCostJdelta = serviceCostI - serviceCostJ
        Deltas = (costIdelta, costJdelta, loadIdelta, loadJdelta, serviceCostIdelta, serviceCostJdelta)
        return(Deltas)
    
    def doubleArcExchangeDeltas(self, twoArcsRemovedI, twoArcsRemovedJ, costsChange):
        loadI = self.demandD[twoArcsRemovedI[0]] + self.demandD[twoArcsRemovedI[1]]
        loadJ = self.demandD[twoArcsRemovedJ[0]] + self.demandD[twoArcsRemovedJ[1]]
        serviceCostI = self.serviceD[twoArcsRemovedI[0]] + self.serviceD[twoArcsRemovedI[1]]
        serviceCostJ = self.serviceD[twoArcsRemovedJ[0]] + self.serviceD[twoArcsRemovedJ[1]]
        (costChangeI1, costChangeI2, costChangeJ1, costChangeJ2) = costsChange
        costIdelta = costChangeI1 + costChangeI2
        costJdelta = costChangeJ1 + costChangeJ2
        loadIdelta = -loadI + loadJ
        loadJdelta = loadI - loadJ
        serviceCostIdelta = -serviceCostI + serviceCostJ
        serviceCostJdelta = serviceCostI - serviceCostJ
        Deltas = (costIdelta, costJdelta, loadIdelta, loadJdelta, serviceCostIdelta, serviceCostJdelta)
        return(Deltas)
    
    def removeInsertAllArcsRouteAllRoutes(self, routes,  loads):
        nRoutes = len(routes)
        removalInsertionNeighbourhood = []
        for routeIpos in range(nRoutes):
            routeI = routes[routeIpos]
            nRoutesJRange = range(nRoutes)
            del nRoutesJRange[routeIpos]
            nArcsI = len(routeI)
            actualI = self.routeCostIndex[routeIpos][0]
            for i in range(1,nArcsI-1):
                (modifiedRouteI, arcRemoved, costChangeI) = self.singleRemove1route(routeI, i)
                loadI = self.demandD[arcRemoved]
                serviceCostI = self.serviceD[arcRemoved]
                for routeJpos in nRoutesJRange:
                    actualJ = self.routeCostIndex[routeJpos][0]
                    costJ = self.tripCosts[actualJ]
                    routeJ = routes[routeJpos]
                    nArcsJ = len(routeJ)
                    for j in range(1, nArcsJ):
                        (modifiedRouteJ, costChangeJ) = self.findBestInversionArcInsert(routeJ, arcRemoved, j)
                        neighbour = {'routes':(routeIpos,routeJpos),'pos':(i,j),'arc':arcRemoved,'costDelta':(costChangeI,costChangeJ),'loadDelta':(-loadI,loadI),'serviceDelta':(-serviceCostI,serviceCostI),'modifiedRoutes':(modifiedRouteI,modifiedRouteJ),'tabus':{'I':[i-1,i,i+1],'J':[j-1,j]}}
                        if (actualI == actualJ) & (costChangeI+costChangeJ < self.bestChange) & (loads[routeJpos] + loadI <= self.capacity):
                            self.bestChange = costChangeI+costChangeJ
                            self.bestNeighbour = (costChangeI+costChangeJ,neighbour,'RemoveInsertAllArcsAllRoutes','twoRoutes')
                        elif ((costChangeI+costChangeJ) < self.bestChange) & (loads[routeJpos] + loadI <= self.capacity) & (costJ + costChangeJ + serviceCostI <= self.maxTrip):
                            self.bestChange = costChangeI+costChangeJ
                            self.bestNeighbour = (costChangeI+costChangeJ,neighbour,'RemoveInsertAllArcsAllRoutes','twoRoutes')
        return(removalInsertionNeighbourhood)
    
    def exchangeAllArcsAllRoutes(self, routes, loads):
        nRoutes = len(routes)
        removalInsertionNeighbourhood = []
        for routeIpos in range(nRoutes-1):
            routeI = routes[routeIpos]
            nRoutesJRange = range(routeIpos+1,nRoutes)
            nArcsI = len(routeI)
            actualI = self.routeCostIndex[routeIpos][0]
            costI = self.tripCosts[actualI]
            for i in range(1,nArcsI-1):
                (modifiedRouteIa, arcRemovedI, costChangeI1) = self.singleRemove1route(routeI, i)
                for routeJpos in nRoutesJRange:
                    actualJ = self.routeCostIndex[routeJpos][0]
                    costJ = self.tripCosts[actualJ]
                    routeJ = routes[routeJpos]
                    nArcsJ = len(routeJ)
                    for j in range(1, nArcsJ-1):
                        (modifiedRouteJ, arcRemovedJ, costChangeJ1) = self.singleRemove1route(routeJ, j)
                        (modifiedRouteI, costChangeI2) = self.findBestInversionArcInsert(modifiedRouteIa, arcRemovedJ, i)
                        (modifiedRouteJ, costChangeJ2) = self.findBestInversionArcInsert(modifiedRouteJ, arcRemovedI, j)
                        costsChange = (costChangeI1, costChangeI2, costChangeJ1, costChangeJ2)
                        Deltas = self.singleArcExchangeDeltas(arcRemovedI,arcRemovedJ,costsChange)
                        (costIdelta, costJdelta, loadIdelta, loadJdelta, serviceCostIdelta, serviceCostJdelta) = Deltas         
                        neighbour = {'routes':(routeIpos,routeJpos),'pos':(i,j),'arc':(arcRemovedI,arcRemovedI),'costDelta':(costIdelta,costJdelta),'loadDelta':(loadIdelta,loadJdelta),'serviceDelta':(serviceCostIdelta,serviceCostJdelta),'modifiedRoutes':(modifiedRouteI,modifiedRouteJ),'tabus':{'I':[i-1,i,i+1],'J':[j-1,j,j+1]}}
                        if (actualI == actualJ) & (costIdelta+costJdelta < self.bestChange) & (loads[routeIpos] + loadIdelta <= self.capacity) & (loads[routeJpos] + loadJdelta <= self.capacity):        
                            self.bestChange = costIdelta+costJdelta
                            self.bestNeighbour = (costIdelta+costJdelta,neighbour,{'I':[i-1,i,i+1],'J':[j-1,j,j+1]},'ExchangeAllArcsAllRoutes','twoRoutes')
                        elif (costIdelta+costJdelta < self.bestChange) & (loads[routeIpos] + loadIdelta <= self.capacity) & (loads[routeJpos] + loadJdelta <= self.capacity) & (costI + costIdelta + serviceCostIdelta <= self.maxTrip) & (costJ + costJdelta + serviceCostJdelta <= self.maxTrip):
                            self.bestChange = costIdelta+costJdelta
                            self.bestNeighbour = (costIdelta+costJdelta,neighbour,{'I':[i-1,i,i+1],'J':[j-1,j,j+1]},'ExchangeAllArcsAllRoutes','twoRoutes')
        return(removalInsertionNeighbourhood)
    
    def removeInsertAllDoubleArcsAllRoutes(self, routes, loads):
        nRoutes = len(routes)
        removalInsertionNeighbourhood = []
        for routeIpos in range(nRoutes):
            routeI = routes[routeIpos]
            nRoutesJRange = range(nRoutes)
            del nRoutesJRange[routeIpos]
            nArcsI = len(routeI)
            actualI = self.routeCostIndex[routeIpos][0]
            for i in range(1,nArcsI-2):
                (modifiedRouteI, twoArcsRemoved, costChangeI) = self.doubleRemove1route(routeI, i)
                loadI = self.demandD[twoArcsRemoved[0]] + self.demandD[twoArcsRemoved[1]]
                serviceCostI = self.serviceD[twoArcsRemoved[0]] + self.serviceD[twoArcsRemoved[1]]
                for routeJpos in nRoutesJRange:
                    actualJ = self.routeCostIndex[routeJpos][0]
                    costJ = self.tripCosts[actualJ]
                    routeJ = routes[routeJpos]
                    nArcsJ = len(routeJ)
                    for j in range(1, nArcsJ):
                        (modifiedRouteJ, costChangeJ) = self.findBestInversionDoubleArcInsert(routeJ, twoArcsRemoved, j)
                        neighbour = {'routes':(routeIpos,routeJpos),'pos':(i,j),'arc':twoArcsRemoved,'costDelta':(costChangeI,costChangeJ),'loadDelta':(-loadI,loadI),'serviceDelta':(-serviceCostI,serviceCostI),'modifiedRoutes':(modifiedRouteI,modifiedRouteJ),'tabus':{'I':[i-1,i,i+1,i+2],'J':[j-1,j]}}
                        if (actualI == actualJ) & (costChangeI+costChangeJ < self.bestChange) & (loads[routeJpos] + loadI <= self.capacity):
                            self.bestChange = costChangeI+costChangeJ
                            self.bestNeighbour = (costChangeI+costChangeJ,neighbour,'RemoveInsertAllDoubleArcsAllRoutes','twoRoutes')
                        elif (costChangeI+costChangeJ < self.bestChange) & (loads[routeJpos] + loadI <= self.capacity) & (costJ + costChangeJ + serviceCostI <= self.maxTrip):
                            self.bestChange = costChangeI+costChangeJ
                            self.bestNeighbour = (costChangeI+costChangeJ,neighbour,'RemoveInsertAllDoubleArcsAllRoutes','twoRoutes')
        return(removalInsertionNeighbourhood)

    def exchangeAllDoubleArcsAllRoutes(self, routes, loads):
        nRoutes = len(routes)
        removalInsertionNeighbourhood = []
        for routeIpos in range(nRoutes-1):
            routeI = routes[routeIpos]
            nRoutesJRange = range(routeIpos+1,nRoutes)
            nArcsI = len(routeI)
            actualI = self.routeCostIndex[routeIpos][0]
            costI = self.tripCosts[actualI]
            for i in range(1,nArcsI-2):
                (modifiedRouteIa, twoArcsRemovedI, costChangeI1) = self.doubleRemove1route(routeI, i)
                for routeJpos in nRoutesJRange:
                    routeJ = routes[routeJpos]
                    nArcsJ = len(routeJ)
                    routeJ = routes[routeJpos]
                    nArcsJ = len(routeJ)
                    actualJ = self.routeCostIndex[routeJpos][0]
                    costJ = self.tripCosts[actualJ]
                    for j in range(1, nArcsJ-2):
                        (modifiedRouteJ, twoArcsRemovedJ, costChangeJ1) = self.doubleRemove1route(routeJ, j)
                        (modifiedRouteI, costChangeI2) = self.findBestInversionDoubleArcInsert(modifiedRouteIa, twoArcsRemovedJ, i)
                        (modifiedRouteJ, costChangeJ2) = self.findBestInversionDoubleArcInsert(modifiedRouteJ, twoArcsRemovedI, j)
                        costsChange = (costChangeI1, costChangeI2, costChangeJ1, costChangeJ2)
                        Deltas = self.doubleArcExchangeDeltas(twoArcsRemovedI,twoArcsRemovedJ,costsChange)
                        (costIdelta, costJdelta, loadIdelta, loadJdelta, serviceCostIdelta, serviceCostJdelta) = Deltas
                        neighbour = {'routes':(routeIpos,routeJpos),'pos':(i,j),'arc':(twoArcsRemovedI,twoArcsRemovedJ),'costDelta':(costIdelta,costJdelta),'loadDelta':(loadIdelta,loadJdelta),'serviceDelta':(serviceCostIdelta,serviceCostJdelta),'modifiedRoutes':(modifiedRouteI,modifiedRouteJ),'tabus':{'I':[i-1,i,i+1,i+2],'J':[j-1,j,j+1,j+2]}}
                        if (actualI == actualJ) & (costIdelta+costJdelta < self.bestChange) & (loads[routeIpos] + loadIdelta <= self.capacity) & (loads[routeJpos] + loadJdelta <= self.capacity):
                                self.bestChange = costIdelta+costJdelta
                                self.bestNeighbour = (costIdelta+costJdelta,neighbour,{'I':[i-1,i,i+1,i+2],'J':[j-1,j,j+1,j+2]},'ExchangeAllDoubleArcsAllRoutes','twoRoutes')
                        elif (costIdelta+costJdelta < self.bestChange) & (loads[routeIpos] + loadIdelta <= self.capacity) & (loads[routeJpos] + loadJdelta <= self.capacity) & (costI + costIdelta + serviceCostIdelta <= self.maxTrip) & (costJ + costJdelta + serviceCostJdelta <= self.maxTrip):
                                self.bestChange = costIdelta+costJdelta
                                self.bestNeighbour = (costIdelta+costJdelta,neighbour,{'I':[i-1,i,i+1,i+2],'J':[j-1,j,j+1,j+2]},'ExchangeAllDoubleArcsAllRoutes','twoRoutes')
        return(removalInsertionNeighbourhood)

    def generateAllNeighbourhoodsMulitRoutes(self, routes, loads, tripCosts, routeCostIndex):
        self.tripCosts = tripCosts
        self.routeCostIndex = routeCostIndex
        self.removeInsertAllArcsRouteAllRoutes(routes, loads)
        self.exchangeAllArcsAllRoutes(routes, loads)
        self.removeInsertAllDoubleArcsAllRoutes(routes, loads)
        self.exchangeAllDoubleArcsAllRoutes(routes, loads)

#===============================================================================
# 
#===============================================================================
def unitTestRemoveInsert(info, solutionOld):
    import testSolutions
    er = testSolutions.testSolution(None, solutionOld, info)
    er.testReportSolution()
    RIP = SingleRouteRemoveInsertProcedure(info)
    solution = solutionOld.copy()
    while True:
        routeI = solution[1]['Solution']
        best = []
        removalInsertionNeighbourhood1 = RIP.removeInsertAllDoubleArcs(routeI)
        best += removalInsertionNeighbourhood1
        removalInsertionNeighbourhood2 = RIP.removeInsertAllArcs(routeI)
        best += removalInsertionNeighbourhood2
        removalInsertionNeighbourhood3 = RIP.exchangeAllArcs(routeI)
        best += removalInsertionNeighbourhood3
        removalInsertionNeighbourhood4 = RIP.exchangeAllDoubleArcs(routeI)
        best += removalInsertionNeighbourhood4
        bestNeighbour = min(best)
        print(bestNeighbour[0],bestNeighbour[-1])
        if bestNeighbour[0] >= 0: break
        solution[1]['Solution'] = bestNeighbour[1][2]
        solution[1]['Cost'] = solution[1]['Cost'] + bestNeighbour[0]
        solution['Total cost'] = solution['Total cost'] + bestNeighbour[0]


def unitTestRemoveInsert2(info, solutionOld):
    import testSolutions
    import time
    er = testSolutions.testSolution(None, solutionOld, info)
    er.testReportSolution()
    RIP = SingleRouteRemoveInsertProcedure(info)
    solution = deepcopy(solutionOld)
    while True:
        routeI = solution[1]['Solution']
        t1 = time.clock()
        removalInsertionNeighbourhood1  = RIP.removeInsertAllArcs(routeI)
        e1 = time.clock() - t1
        t2 = time.clock()
        removalInsertionNeighbourhood2 = RIP.removeInsertAllDoubleArcs(routeI)
        e2 = time.clock() - t2
        t3 = time.clock()
        removalInsertionNeighbourhood3 = RIP.exchangeAllArcs(routeI)
        e3 = time.clock() - t3 
        t4 = time.clock()
        removalInsertionNeighbourhood4 = RIP.exchangeAllDoubleArcs(routeI)
        e4 = time.clock() - t4
        break

    print(len(removalInsertionNeighbourhood1))
    print((len(routeI)-2)*(len(routeI)-3))
    print(min(removalInsertionNeighbourhood1)[0])
    print(e1)
    print('')
    print(len(removalInsertionNeighbourhood2))
    print((len(routeI)-3)*(len(routeI)-4))
    print(min(removalInsertionNeighbourhood2)[0])
    print(e2)
    print('')
    print(len(removalInsertionNeighbourhood3))
    print((len(routeI)-3)*(len(routeI)-4)/2)
    print(min(removalInsertionNeighbourhood3)[0])
    print(e3)
    print('')
    print(len(removalInsertionNeighbourhood4))
    print((len(routeI)-5)*(len(routeI)-6)/2)
    print(min(removalInsertionNeighbourhood4)[0])
    print(e4)
    print('')
    
    for neighbour in removalInsertionNeighbourhood4[0:5]:
        solution = deepcopy(solutionOld)
        bestNeighbour = neighbour
        solution[1]['Solution'] = bestNeighbour[1][2]
        solution[1]['Cost'] += bestNeighbour[0] #This is not working!!!!!
        solution['Total cost'] += bestNeighbour[0]
        er = testSolutions.testSolution(None, solution, info)
        er.checkFeasibility()
        print(er.errorReport['Exceptions']['Total exception'],bestNeighbour[0])

def unitTestRemoveInsertAllRoutes(info, solutionOld):
    print('unitTestRemoveInsertAllRoutes')
    print('')
    import testSolutions
    import time
    er = testSolutions.testSolution(None, solutionOld, info)
    er.testReportSolution()
    RIPij = MultipleRouteRemoveInsertProcedure(info)
    solution = deepcopy(solutionOld)
    while True:
        routeI = solution[1]['Solution']
        routeJ = solution[2]['Solution']
        routes = [routeI,routeJ]
        t1 = time.clock()
        removalInsertionNeighbourhood1  = RIPij.removeInsertAllArcsRouteAllRoutes(routes)
        e1 = time.clock() - t1
        t2 = time.clock()
        removalInsertionNeighbourhood2 = RIPij.removeInsertAllDoubleArcsAllRoutes(routes)
        e2 = time.clock() - t2
        t3 = time.clock()
        removalInsertionNeighbourhood3 = RIPij.exchangeAllArcsAllRoutes(routes)
        e3 = time.clock() - t3 
        t4 = time.clock()
        removalInsertionNeighbourhood4 = RIPij.exchangeAllDoubleArcsAllRoutes(routes)
        e4 = time.clock() - t4
        break

    print(len(removalInsertionNeighbourhood1))
    print(2*(len(routeI)-2)*(len(routeJ)-2))
    print(min(removalInsertionNeighbourhood1)[0])
    print(e1)
    print('')
    print(len(removalInsertionNeighbourhood2))
    print((len(routeI)-3)*(len(routeJ)-2))
    print(min(removalInsertionNeighbourhood2)[0])
    print(e2)
    print('')
    print(len(removalInsertionNeighbourhood3))
    print((len(routeI)-2)*(len(routeJ)-2))
    print(min(removalInsertionNeighbourhood3)[0])
    print(e3)
    print('')
    print(len(removalInsertionNeighbourhood4))
    print((len(routeI)-3)*(len(routeJ)-4))
    print(min(removalInsertionNeighbourhood4)[0])
    print(e4)
    print('')
    #print(solutionOld)
    for neighbour in removalInsertionNeighbourhood4:
        solution = deepcopy(solutionOld)
        bestNeighbour = neighbour
        modifications = bestNeighbour[1]
        (routeI,routeJ) = modifications['routes']
        routeI += 1
        routeJ += 1
        (solution[routeI]['Solution'],solution[routeJ]['Solution']) = modifications['modifiedRoutes']
        (costIdelta, costJdelta) = modifications['costDelta']
        (serviceIdelta, serviceJdelta) = modifications['serviceDelta']
        solution[routeI]['Cost'] += costIdelta + serviceIdelta
        solution[routeJ]['Cost'] += costJdelta + serviceJdelta
        (loadIdelta, loadJdelta) = modifications['loadDelta']
        solution[routeI]['Load'] += loadIdelta
        solution[routeJ]['Load'] += loadJdelta
        solution['Total cost'] += bestNeighbour[0]
        er = testSolutions.testSolution(None, solution, info)
        er.checkFeasibility()
        print(er.errorReport['Exceptions']['Total exception'],costIdelta,costJdelta,solution[routeI]['Cost']+solution[routeJ]['Cost'],solution['Total cost'])
        if er.errorReport['Exceptions']['Total exception']:
            er.testReportSolution()
            print(solution)

if __name__ == "__main__":
    import cPickle
    import LancommeARPconversions3 as LARP
    fileName1 = 'lpr_ProblemInfo/Lpr-a-01_pickled.txt'
    fileName2 = 'lpr_ProblemInfo/Lpr-b-01_pickled.txt'
    fileName3 = 'lpr_ProblemInfo/Lpr-c-01_pickled.txt'
    info1 = LARP.ReadProblemData(fileName1)
    info2 = LARP.ReadProblemData(fileName2)
    info3 = LARP.ReadProblemData(fileName3)
    s1 = open('lpr_Solutions/Lpr-a-01_Init_sol.txt')
    s2 = open('lpr_Solutions/Lpr-b-01_Init_sol.txt')
    s3 = open('lpr_Solutions/Lpr-c-01_Init_sol.txt')
    solution1 = cPickle.load(s1)
    solution2 = cPickle.load(s2)
    solution3 = cPickle.load(s3)
#    unitTestRemoveInsert(info1, solution1)
#    unitTestRemoveInsert2(info1, solution1)
#    unitTestRemoveInsertIJ(info3, solution3)
    unitTestRemoveInsertAllRoutes(info3, solution3)
    
    
    
    
