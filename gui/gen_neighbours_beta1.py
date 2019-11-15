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


    def findBestSingleArcInsertion(self, routeI, arcInsert):
        modifiedRouteI = routeI[:]
        nArcs = len(modifiedRouteI)
        bestCostChange = 1e300000
        for j in range(1,nArcs):
            (modifiedRoute2, costChange2) = self.singleInsert1Route(modifiedRouteI, arcInsert, j)
            if self.Inv[arcInsert]:
                (modifiedRoute3, costChange3) = self.singleInsert1Route(modifiedRouteI, self.Inv[arcInsert], j)
                if costChange3 < costChange2: modifiedRoute2, costChange2 = modifiedRoute3[:], costChange3
            if costChange2 < bestCostChange:
                bestInsertRoute = modifiedRoute2
                bestCostChange = costChange2
        return(bestInsertRoute, bestCostChange)

#===============================================================================
# 
#===============================================================================
class SingleRouteRemoveInsertProcedure(SinlgeRouteModifications):
    
    def __init__(self, info):
        SinlgeRouteModifications.__init__(self, info)
        self.info = info
        self.SP = self.info.spDistanceD
        self.Inv = self.info.invArcD
        self.bestChange = 0
        self.bestNeighbour = []
        self.neighbourhoodsToUse = ['RemoveInsert','Exchange','TwoRemoveInsert','TwoExchange']
        self.typeToUse = 'ReturnAll'
        self.stopSearch = False
    
    def contsructReturnAllNeighbourhoodListSingleRoute(self, deltaChange, neighbour, moveType):
        (info1, info2) = moveType
        if deltaChange < self.bestChange:
            if self.typeToUse == 'ReturnBest':
                self.bestNeighbour = []
                self.bestChange = deltaChange
            self.bestNeighbour.append((deltaChange,neighbour,info1,info2))
            if self.typeToUse == 'ReturnFirst':self.stopSearch = True
            
                                      
    def removeInsertAllArcs(self, routeI, routeP = None):
        nArcs = len(routeI)
        moveType = ('RemoveInsertAllArcs','oneRoute')
        for i in range(1,nArcs-1):
            if self.stopSearch:break
            (modifiedRoute1, arcRemoved, costChange1) = self.singleRemove1route(routeI, i)
            insertPosition = range(1, nArcs-1)
            del insertPosition[i-1]
            for j in insertPosition:
                (modifiedRoute2, costChange2) = self.findBestInversionArcInsert(modifiedRoute1, arcRemoved, j)
                if i < j:tabusTemp = [i-1,i,i+1,j,j+1]
                else:tabusTemp = [i-1,i,i+1,j-1,j]
                neighbour = {'routes':routeP,'pos':(i,j),'arc':arcRemoved,'costDelta':costChange1+costChange2,'loadDelta':(),'serviceDelta':(),'modifiedRoutes':modifiedRoute2,'tabus':deepcopy(tabusTemp)}
                neighbourDeltaChange = costChange1+costChange2
                self.contsructReturnAllNeighbourhoodListSingleRoute(neighbourDeltaChange, neighbour, moveType)
                if self.stopSearch:break
    
    def exchangeAllArcs(self, routeI, routeP = None):
        nArcs = len(routeI)
        moveType = ('ExchangeAllArcs','oneRoute')
        for i in range(1,nArcs-3):
            if self.stopSearch:break    
            (modifiedRoute1, arcRemoved1, costChange1) = self.singleRemove1route(routeI, i)
            for j in range(i+2,nArcs-1):
                (modifiedRoute2, arcRemoved2, costChange2) = self.singleRemove1route(modifiedRoute1, j-1)
                (modifiedRoute2, costChange3) = self.findBestInversionArcInsert(modifiedRoute2, arcRemoved1, j-1)
                (modifiedRoute2, costChange4) = self.findBestInversionArcInsert(modifiedRoute2, arcRemoved2, i)
                neighbour = {'routes':routeP,'pos':(i,j),'arc':(arcRemoved1,arcRemoved2),'costDelta':costChange1+costChange2+costChange3+costChange4,'loadDelta':(),'serviceDelta':(),'modifiedRoutes':modifiedRoute2,'tabus':[i-1,i,i+1,j-1,j,j+1]}
                neighbourDeltaChange = costChange1+costChange2+costChange3+costChange4
                self.contsructReturnAllNeighbourhoodListSingleRoute(neighbourDeltaChange, neighbour, moveType) 
                if self.stopSearch:break
    
    def removeInsertAllDoubleArcs(self, routeI, routeP = None):
        nArcs = len(routeI)
        moveType = ('RemoveInsertAllDoubleArcs','oneRoute')
        for i in range(1,nArcs-2):
            if self.stopSearch:break    
            (modifiedRoute1, twoArcsRemoved, costChange1) = self.doubleRemove1route(routeI, i)
            insertPosition = range(1, nArcs-2)
            del insertPosition[i-1]
            for j in insertPosition:
                if i < j:(modifiedRoute2, costChange2) = self.findBestInversionDoubleArcInsert(modifiedRoute1, twoArcsRemoved, j-1)
                else:(modifiedRoute2, costChange2) = self.findBestInversionDoubleArcInsert(modifiedRoute1, twoArcsRemoved, j)
                if i < j:tabusTemp = [i-1,i,i+1,i+2,j,j+1]
                else:tabusTemp = [i-1,i,i+1,i+2,j-1,j]
                neighbour = {'routes':routeP,'pos':(i,j),'arc':twoArcsRemoved,'costDelta':costChange1+costChange2,'loadDelta':(),'serviceDelta':(),'modifiedRoutes':modifiedRoute2,'tabus':deepcopy(tabusTemp)}
                neighbourDeltaChange = costChange1+costChange2
                self.contsructReturnAllNeighbourhoodListSingleRoute(neighbourDeltaChange, neighbour, moveType) 
                if self.stopSearch:break
    
    def exchangeAllDoubleArcs(self, routeI, routeP = None):
        nArcs = len(routeI)
        moveType = ('ExchangeAllDoubleArcs','oneRoute')
        for i in range(1,nArcs-4):
            if self.stopSearch:break
            (modifiedRoute1, twoArcsRemoved1, costChange1) = self.doubleRemove1route(routeI, i)
            for j in range(i+3,nArcs-2):
                (modifiedRoute2, twoArcsRemoved2, costChange2) = self.doubleRemove1route(modifiedRoute1, j-2)
                (modifiedRoute2, costChange3) = self.findBestInversionDoubleArcInsert(modifiedRoute2, twoArcsRemoved1, j-2)
                (modifiedRoute2, costChange4) = self.findBestInversionDoubleArcInsert(modifiedRoute2, twoArcsRemoved2, i)
                neighbour = {'routes':routeP,'pos':(i,j),'arc':(twoArcsRemoved1,twoArcsRemoved2),'costDelta':costChange1+costChange2+costChange3+costChange4,'loadDelta':(),'serviceDelta':(),'modifiedRoutes':modifiedRoute2,'tabus':[i-1,i,i+1,i+2,j-1,j,j+1,j+2]}
                neighbourDeltaChange = costChange1+costChange2+costChange3+costChange4
                self.contsructReturnAllNeighbourhoodListSingleRoute(neighbourDeltaChange, neighbour, moveType) 
                if self.stopSearch:break
               
    def removeInsertGivenArcs(self, routeI, iPos, jPos):
        (routeI, arcRemoved, costChange1) = self.singleRemove1route(routeI, iPos)
        (routeI, costChange2) = self.findBestInversionArcInsert(routeI, arcRemoved, jPos)
        self.temp = costChange1 + costChange2
        return(routeI)

    def exchangeGivenArcs(self, routeI, iPos, jPos):
        (routeI, arcRemoved1, costChange1) = self.singleRemove1route(routeI, iPos)
        (routeI, arcRemoved2, costChange2) = self.singleRemove1route(routeI, jPos-1)
        (routeI, costChange3) = self.findBestInversionArcInsert(routeI, arcRemoved1, jPos-1)
        (routeI, costChange4) = self.findBestInversionArcInsert(routeI, arcRemoved2, iPos)
        self.temp = costChange1 + costChange2 + costChange3 + costChange4
        return(routeI)
    
    def removeInsertGivenDoubleArcs(self, routeI, iPos, jPos):
        (routeI, twoArcsRemoved, costChange1) = self.doubleRemove1route(routeI, iPos)
        if iPos < jPos:(routeI, costChange2) = self.findBestInversionDoubleArcInsert(routeI, twoArcsRemoved, jPos-1)
        else: (routeI, costChange2) = self.findBestInversionDoubleArcInsert(routeI, twoArcsRemoved, jPos)
        self.temp = costChange1 + costChange2
        return(routeI)
    
    def exchangeGivenDoubleArcs(self, routeI, iPos, jPos):
        (routeI, twoArcsRemoved1, costChange1) = self.doubleRemove1route(routeI, iPos)
        (routeI, twoArcsRemoved2, costChange2) = self.doubleRemove1route(routeI, jPos-2)
        (routeI, costChange3) = self.findBestInversionDoubleArcInsert(routeI, twoArcsRemoved1, jPos-2)
        (routeI, costChange4) = self.findBestInversionDoubleArcInsert(routeI, twoArcsRemoved2, iPos)
        self.temp = costChange1 + costChange2 + costChange3 + costChange4
        return(routeI)
    
    def generateAllNeighbourhoodsSingleRoutes(self, route,routeP=None):
        while True:
            if 'RemoveInsert' in self.neighbourhoodsToUse: self.removeInsertAllArcs(route,routeP)
            if self.stopSearch: break
            if 'Exchange' in self.neighbourhoodsToUse: self.exchangeAllArcs(route,routeP)
            if self.stopSearch: break
            if 'TwoRemoveInsert' in self.neighbourhoodsToUse: self.removeInsertAllDoubleArcs(route,routeP)
            if self.stopSearch: break
            if 'TwoExchange' in self.neighbourhoodsToUse: self.exchangeAllDoubleArcs(route,routeP)
            break
    
    def generateAllRoutesNeighbourhoodsSingleRoutes(self, routes):
        for routeP in range(len(routes)):
            if self.stopSearch: break
            self.generateAllNeighbourhoodsSingleRoutes(routes[routeP], routeP)

    def generateAllNeighbourhoodsSingleRoutesOrdered(self, route,routeP, ordered):
        if 'RemoveInsert' == ordered: self.removeInsertAllArcs(route,routeP)
        if 'Exchange' == ordered: self.exchangeAllArcs(route,routeP)
        if 'TwoRemoveInsert' == ordered: self.removeInsertAllDoubleArcs(route,routeP)
        if 'TwoExchange' == ordered: self.exchangeAllDoubleArcs(route,routeP)
            
    def generateAllRoutesNeighbourhoodsSingleRoutesOrder(self, routes, searchType='RemoveInsert'):
        for routeP in range(len(routes)):
            if self.stopSearch: break
            self.generateAllNeighbourhoodsSingleRoutesOrdered(routes[routeP], routeP, searchType) 

#===============================================================================
# 
#===============================================================================
class MultipleRouteRemoveInsertProcedure(SinlgeRouteModifications):
    
    def __init__(self, info):
        SinlgeRouteModifications.__init__(self, info)
        self.info = info
        self.capacity = info.capacity
        self.SP = self.info.spDistanceD
        self.maxTrip = self.info.maxTrip
        self.Inv = self.info.invArcD
        self.demandD = self.info.demandD
        self.serviceD = self.info.serveCostD
        self.bestChange = 0
        self.bestNeighbour = []
        self.neighbourhoodsToUse = ['RemoveInsert','Exchange','TwoRemoveInsert','TwoExchange']
        self.typeToUse = 'ReturnAll'
        self.stopSearch = False
        self.routeIndex = []
        self.costIndex = []
        self.loads = []
        
    def singleArcExchangeDeltas(self,arcRemovedI,arcRemovedJ,costsChange):
        loadI = self.demandD[arcRemovedI]
        loadJ = self.demandD[arcRemovedJ]
        serviceCostI = self.serviceD[arcRemovedI]
        serviceCostJ = self.serviceD[arcRemovedJ]
        (costChangeI1, costChangeI2, costChangeJ1, costChangeJ2) = costsChange
        loadIdelta = -loadI + loadJ
        loadJdelta = loadI - loadJ
        serviceCostIdelta = -serviceCostI + serviceCostJ
        serviceCostJdelta = serviceCostI - serviceCostJ
        costIdelta = costChangeI1 + costChangeI2 + serviceCostIdelta
        costJdelta = costChangeJ1 + costChangeJ2 + serviceCostJdelta
        Deltas = (costIdelta, costJdelta, loadIdelta, loadJdelta, serviceCostIdelta, serviceCostJdelta)
        return(Deltas)
    
    def doubleArcExchangeDeltas(self, twoArcsRemovedI, twoArcsRemovedJ, costsChange):
        loadI = self.demandD[twoArcsRemovedI[0]] + self.demandD[twoArcsRemovedI[1]]
        loadJ = self.demandD[twoArcsRemovedJ[0]] + self.demandD[twoArcsRemovedJ[1]]
        serviceCostI = self.serviceD[twoArcsRemovedI[0]] + self.serviceD[twoArcsRemovedI[1]]
        serviceCostJ = self.serviceD[twoArcsRemovedJ[0]] + self.serviceD[twoArcsRemovedJ[1]]
        (costChangeI1, costChangeI2, costChangeJ1, costChangeJ2) = costsChange
        loadIdelta = -loadI + loadJ
        loadJdelta = loadI - loadJ
        serviceCostIdelta = -serviceCostI + serviceCostJ
        serviceCostJdelta = serviceCostI - serviceCostJ
        costIdelta = costChangeI1 + costChangeI2 + serviceCostIdelta
        costJdelta = costChangeJ1 + costChangeJ2 + serviceCostJdelta
        Deltas = (costIdelta, costJdelta, loadIdelta, loadJdelta, serviceCostIdelta, serviceCostJdelta)
        return(Deltas)
    
    def constructReturnFirstMultiRoute(self, deltaChange, neighbour, moveType):
        (info1, info2) = moveType
        if deltaChange < self.bestChange:
            (routeI, routeJ) = neighbour['routes']
            loadI, loadJ = self.loads[routeI], self.loads[routeJ]
            actualI, actualJ = self.routeIndex[routeI],  self.routeIndex[routeJ]
            costI, costJ = self.costIndex[actualI[0]], self.costIndex[actualJ[0]]
            (loadIdelta, loadJdelta) = neighbour['loadDelta']
            (costIdelta, costJdelta) = neighbour['costDelta']
            if (actualI == actualJ) & (loadIdelta + loadI <= self.capacity) &  (loadJdelta + loadJ <= self.capacity):
                self.bestNeighbour.append((deltaChange,neighbour, info1, info2))
                self.stopSearch = True
            elif (loadIdelta + loadI <= self.capacity) &  (loadJdelta + loadJ <= self.capacity) & (costI + costIdelta <= self.maxTrip) & (costJ + costJdelta <= self.maxTrip):
                self.bestNeighbour.append((deltaChange,neighbour,info1, info2))
                self.stopSearch = True
                   
    def contsructReturnAllNeighbourhoodListMultiRoute(self, deltaChange, neighbour, moveType):
        (info1, info2) = moveType
        if (self.typeToUse == 'ReturnAll') & (deltaChange < self.bestChange):
            self.bestNeighbour.append((deltaChange,neighbour,info1,info2))
        elif self.typeToUse == 'ReturnFirst':
            self.constructReturnFirstMultiRoute(deltaChange, neighbour, moveType)
        elif self.typeToUse == 'ReturnBest':
            self.constructReturnFirstMultiRoute(deltaChange, neighbour, moveType)
            if self.stopSearch:
                self.stopSearch = False
                if len(self.bestNeighbour)==2: del self.bestNeighbour[0] 
                self.bestChange = deltaChange
    
    def removeInsertAllArcsRouteAllRoutes(self, routes,  loads):
        nRoutes = len(routes)
        moveType = ('RemoveInsertAllArcsAllRoutes','twoRoutes')
        for routeIpos in range(nRoutes):
            if self.stopSearch: break
            routeI = routes[routeIpos]
            nRoutesJRange = range(nRoutes)
            del nRoutesJRange[routeIpos]
            nArcsI = len(routeI)
            for i in range(1,nArcsI-1):
                if self.stopSearch: break
                (modifiedRouteI, arcRemoved, costChangeI) = self.singleRemove1route(routeI, i)
                loadI = self.demandD[arcRemoved]
                serviceCostI = self.serviceD[arcRemoved]
                for routeJpos in nRoutesJRange:
                    if self.stopSearch: break
                    routeJ = routes[routeJpos]
                    nArcsJ = len(routeJ)
                    for j in range(1, nArcsJ):
                        (modifiedRouteJ, costChangeJ) = self.findBestInversionArcInsert(routeJ, arcRemoved, j)
                        neighbour = {'routes':(routeIpos,routeJpos),'pos':(i,j),'arc':arcRemoved,'costDelta':(costChangeI - serviceCostI,costChangeJ + serviceCostI),'loadDelta':(-loadI,loadI),'serviceDelta':(-serviceCostI,serviceCostI),'modifiedRoutes':(modifiedRouteI,modifiedRouteJ),'tabus':{'I':[i-1,i,i+1],'J':[j-1,j]}}
                        neighbourDeltaChange = costChangeI+costChangeJ
                        self.contsructReturnAllNeighbourhoodListMultiRoute(neighbourDeltaChange, neighbour, moveType)
                        if self.stopSearch: break

    def exchangeAllArcsAllRoutes(self, routes, loads):
        nRoutes = len(routes)
        moveType = ('ExchangeAllArcsAllRoutes','twoRoutes')
        for routeIpos in range(nRoutes-1):
            routeI = routes[routeIpos]
            nRoutesJRange = range(routeIpos+1,nRoutes)
            nArcsI = len(routeI)
            for i in range(1,nArcsI-1):
                if self.stopSearch: break
                (modifiedRouteIa, arcRemovedI, costChangeI1) = self.singleRemove1route(routeI, i)
                for routeJpos in nRoutesJRange:
                    if self.stopSearch: break
                    routeJ = routes[routeJpos]
                    nArcsJ = len(routeJ)
                    if self.stopSearch: break
                    for j in range(1, nArcsJ-1):
                        (modifiedRouteJ, arcRemovedJ, costChangeJ1) = self.singleRemove1route(routeJ, j)
                        (modifiedRouteI, costChangeI2) = self.findBestInversionArcInsert(modifiedRouteIa, arcRemovedJ, i)
                        (modifiedRouteJ, costChangeJ2) = self.findBestInversionArcInsert(modifiedRouteJ, arcRemovedI, j)
                        costsChange = (costChangeI1, costChangeI2, costChangeJ1, costChangeJ2)
                        Deltas = self.singleArcExchangeDeltas(arcRemovedI,arcRemovedJ,costsChange)
                        (costIdelta, costJdelta, loadIdelta, loadJdelta, serviceCostIdelta, serviceCostJdelta) = Deltas         
                        neighbour = {'routes':(routeIpos,routeJpos),'pos':(i,j),'arc':(arcRemovedI,arcRemovedJ),'costDelta':(costIdelta,costJdelta),'loadDelta':(loadIdelta,loadJdelta),'serviceDelta':(serviceCostIdelta,serviceCostJdelta),'modifiedRoutes':(modifiedRouteI,modifiedRouteJ),'tabus':{'I':[i-1,i,i+1],'J':[j-1,j,j+1]}}
                        neighbourDeltaChange = costIdelta+costJdelta
                        self.contsructReturnAllNeighbourhoodListMultiRoute(neighbourDeltaChange, neighbour, moveType)
                        if self.stopSearch: break

    def removeInsertAllDoubleArcsAllRoutes(self, routes, loads):
        nRoutes = len(routes)
        moveType = ('RemoveInsertAllDoubleArcsAllRoutes','twoRoutes')
        for routeIpos in range(nRoutes):
            if self.stopSearch: break
            routeI = routes[routeIpos]
            nRoutesJRange = range(nRoutes)
            del nRoutesJRange[routeIpos]
            nArcsI = len(routeI)
            for i in range(1,nArcsI-2):
                if self.stopSearch: break
                (modifiedRouteI, twoArcsRemoved, costChangeI) = self.doubleRemove1route(routeI, i)
                loadI = self.demandD[twoArcsRemoved[0]] + self.demandD[twoArcsRemoved[1]]
                serviceCostI = self.serviceD[twoArcsRemoved[0]] + self.serviceD[twoArcsRemoved[1]]
                for routeJpos in nRoutesJRange:
                    if self.stopSearch: break
                    routeJ = routes[routeJpos]
                    nArcsJ = len(routeJ)
                    for j in range(1, nArcsJ):
                        (modifiedRouteJ, costChangeJ) = self.findBestInversionDoubleArcInsert(routeJ, twoArcsRemoved, j)
                        neighbour = {'routes':(routeIpos,routeJpos),'pos':(i,j),'arc':twoArcsRemoved,'costDelta':(costChangeI-serviceCostI,costChangeJ+serviceCostI),'loadDelta':(-loadI,loadI),'serviceDelta':(-serviceCostI,serviceCostI),'modifiedRoutes':(modifiedRouteI,modifiedRouteJ),'tabus':{'I':[i-1,i,i+1,i+2],'J':[j-1,j]}}
                        neighbourDeltaChange = costChangeI+costChangeJ
                        self.contsructReturnAllNeighbourhoodListMultiRoute(neighbourDeltaChange, neighbour, moveType)
                        if self.stopSearch: break

    def exchangeAllDoubleArcsAllRoutes(self, routes, loads):
        nRoutes = len(routes)
        moveType = ('ExchangeAllDoubleArcsAllRoutes','twoRoutes')
        for routeIpos in range(nRoutes-1):
            if self.stopSearch: break
            routeI = routes[routeIpos]
            nRoutesJRange = range(routeIpos+1,nRoutes)
            nArcsI = len(routeI)
            for i in range(1,nArcsI-2):
                if self.stopSearch: break
                (modifiedRouteIa, twoArcsRemovedI, costChangeI1) = self.doubleRemove1route(routeI, i)
                for routeJpos in nRoutesJRange:
                    if self.stopSearch: break
                    routeJ = routes[routeJpos]
                    nArcsJ = len(routeJ)
                    for j in range(1, nArcsJ-2):
                        (modifiedRouteJ, twoArcsRemovedJ, costChangeJ1) = self.doubleRemove1route(routeJ, j)
                        (modifiedRouteI, costChangeI2) = self.findBestInversionDoubleArcInsert(modifiedRouteIa, twoArcsRemovedJ, i)
                        (modifiedRouteJ, costChangeJ2) = self.findBestInversionDoubleArcInsert(modifiedRouteJ, twoArcsRemovedI, j)
                        costsChange = (costChangeI1, costChangeI2, costChangeJ1, costChangeJ2)
                        Deltas = self.doubleArcExchangeDeltas(twoArcsRemovedI,twoArcsRemovedJ,costsChange)
                        (costIdelta, costJdelta, loadIdelta, loadJdelta, serviceCostIdelta, serviceCostJdelta) = Deltas
                        neighbour = {'routes':(routeIpos,routeJpos),'pos':(i,j),'arc':(twoArcsRemovedI,twoArcsRemovedJ),'costDelta':(costIdelta,costJdelta),'loadDelta':(loadIdelta,loadJdelta),'serviceDelta':(serviceCostIdelta,serviceCostJdelta),'modifiedRoutes':(modifiedRouteI,modifiedRouteJ),'tabus':{'I':[i-1,i,i+1,i+2],'J':[j-1,j,j+1,j+2]}}
                        neighbourDeltaChange = costIdelta+costJdelta
                        self.contsructReturnAllNeighbourhoodListMultiRoute(neighbourDeltaChange, neighbour, moveType)
                        if self.stopSearch: break

    def removeInsertGivenArcsTwoRoutes(self, routeI, routeJ, posI, posJ):
        (routeI, arcRemoved, costChangeI) = self.singleRemove1route(routeI, posI)
        (routeJ, costChangeJ) = self.findBestInversionArcInsert(routeJ, arcRemoved, posJ)
        self.temp = costChangeI + costChangeJ
        return(routeI,routeJ)

    def exchangeGivenArcsTwoRoutes(self, routeI, routeJ, posI, posJ):
        (routeI, arcRemovedI, costChangeI1) = self.singleRemove1route(routeI, posI)
        (routeJ, arcRemovedJ, costChangeJ1) = self.singleRemove1route(routeJ, posJ)
        (routeI, costChangeI2) = self.findBestInversionArcInsert(routeI, arcRemovedJ, posI)
        (routeJ, costChangeJ2) = self.findBestInversionArcInsert(routeJ, arcRemovedI, posJ)
        self.temp = costChangeI1 + costChangeI2 + costChangeJ1 + costChangeJ2
        return(routeI,routeJ)

    def removeInsertGivenDoubleArcsTwoRoutes(self, routeI, routeJ, posI, posJ):
        (routeI, twoArcsRemoved, costChangeI) = self.doubleRemove1route(routeI, posI)
        (routeJ, costChangeJ) = self.findBestInversionDoubleArcInsert(routeJ, twoArcsRemoved, posJ)
        self.temp = costChangeI + costChangeJ
        return(routeI,routeJ)

    def exchangeGivenDoubleArcsTwoRoutes(self, routeI, routeJ, posI, posJ):
        (routeI, twoArcsRemovedI, costChangeI1) = self.doubleRemove1route(routeI, posI)
        (routeJ, twoArcsRemovedJ, costChangeJ1) = self.doubleRemove1route(routeJ, posJ)
        (routeI, costChangeI2) = self.findBestInversionDoubleArcInsert(routeI, twoArcsRemovedJ, posI)
        (routeJ, costChangeJ2) = self.findBestInversionDoubleArcInsert(routeJ, twoArcsRemovedI, posJ)
        self.temp = costChangeI1 + costChangeI2 + costChangeJ1 + costChangeJ2
        return(routeI,routeJ)

    def generateAllNeighbourhoodsMulitRoutes(self, routes, loads):
        while True:
            if 'RemoveInsert' in self.neighbourhoodsToUse: self.removeInsertAllArcsRouteAllRoutes(routes, loads)
            if self.stopSearch: break
            if 'Exchange' in self.neighbourhoodsToUse: self.exchangeAllArcsAllRoutes(routes, loads)
            if self.stopSearch: break
            if 'TwoRemoveInsert' in self.neighbourhoodsToUse: self.removeInsertAllDoubleArcsAllRoutes(routes, loads)
            if self.stopSearch: break
            if 'TwoExchange' in self.neighbourhoodsToUse: self.exchangeAllDoubleArcsAllRoutes(routes, loads)
            break

    def generateAllNeighbourhoodsMulitRoutesOrdered(self, routes, loads, typeNeigh):
        nRoutes = len(routes)
        self.tabuDict = {}.fromkeys(range(nRoutes), [])
        if 'RemoveInsert' == typeNeigh: self.removeInsertAllArcsRouteAllRoutes(routes, loads)
        if 'Exchange'  == typeNeigh: self.exchangeAllArcsAllRoutes(routes, loads)
        if 'TwoRemoveInsert'  == typeNeigh: self.removeInsertAllDoubleArcsAllRoutes(routes, loads)
        if 'TwoExchange'  == typeNeigh: self.exchangeAllDoubleArcsAllRoutes(routes, loads)

#===============================================================================
# 
#===============================================================================
class genAllNeighbourhoods(SingleRouteRemoveInsertProcedure, MultipleRouteRemoveInsertProcedure):
    
    def __init__(self, info):
        self.info = info
        SingleRouteRemoveInsertProcedure.__init__(self, info)
        MultipleRouteRemoveInsertProcedure.__init__(self, info)
        
    def genMulitNeighbour(self, routes, loads):
        self.bestChange = 0
        self.bestNeighbour = []
        self.typeToUse = 'ReturnAll'
        self.stopSearch = False
        self.generateAllRoutesNeighbourhoodsSingleRoutes(routes)
        self.generateAllNeighbourhoodsMulitRoutes(routes, loads)
        return(self.bestNeighbour)
    
    def genBestNeighbour(self, routes, loads, routeIndex, costIndex):
        self.bestChange = 0
        self.bestNeighbour = []
        self.typeToUse = 'ReturnBest'
        self.stopSearch = False
        self.routeIndex = routeIndex
        self.costIndex = costIndex
        self.loads = loads
        self.generateAllRoutesNeighbourhoodsSingleRoutes(routes)
        self.generateAllNeighbourhoodsMulitRoutes(routes, loads)
        return(self.bestNeighbour)
    
    def genFirstNeighbour(self, routes, loads, routeIndex, costIndex):
        self.bestChange = 0
        self.bestNeighbour = []
        self.typeToUse = 'ReturnFirst'
        self.stopSearch = False
        self.routeIndex = routeIndex
        self.costIndex = costIndex
        self.loads = loads
        self.generateAllRoutesNeighbourhoodsSingleRoutes(routes)
        if not self.stopSearch:
            self.generateAllNeighbourhoodsMulitRoutes(routes, loads)
        return(self.bestNeighbour)
    
    def genFirstNeighbourOrdered(self, routes, loads, routeIndex, costIndex):
        self.bestChange = 0
        self.bestNeighbour = []
        self.typeToUse = 'ReturnFirst'
        self.stopSearch = False
        self.routeIndex = routeIndex
        self.costIndex = costIndex
        self.loads = loads
        self.generateAllNeighbourhoodsMulitRoutesOrdered(routes, loads, 'RemoveInsert') #1
        if not self.stopSearch:
            self.generateAllNeighbourhoodsMulitRoutesOrdered(routes, loads, 'TwoRemoveInsert') #2
        if not self.stopSearch:
            self.generateAllRoutesNeighbourhoodsSingleRoutesOrder(routes, 'RemoveInsert') #3
        if not self.stopSearch:
            self.generateAllNeighbourhoodsMulitRoutesOrdered(routes, loads, 'Exchange') #4
        if not self.stopSearch:
            self.generateAllRoutesNeighbourhoodsSingleRoutesOrder(routes,'TwoRemoveInsert') #5
        if not self.stopSearch:
            self.generateAllNeighbourhoodsMulitRoutesOrdered(routes, loads, 'TwoExchange') #6
        if not self.stopSearch:
            self.generateAllRoutesNeighbourhoodsSingleRoutesOrder(routes, 'TwoExchange') #7
        if not self.stopSearch:
            self.generateAllRoutesNeighbourhoodsSingleRoutesOrder(routes, 'Exchange') #8
        return(self.bestNeighbour)
