#===============================================================================
# Improve existing routes through exact and approximate algorihtms
# EJ Willemse CSIR: Built Environmnet 4 November 2009
#
# Addapted from:
# Grove, GW., Van Vuuren, JH (2005). Efficient heuristics for the Rural Postman 
# Problem, ORiON vol 21 (1), pp-33-51.
# Specifically page 37-39.
#===============================================================================

import SPmodules2 as SPmodules

class optArcDirect(object):
    
    def __init__(self, route, info=None, fileName = None):
        if info: self.info = info
        elif fileName == None: print('Error: need to provide file or data.')
        self.route = route
        self.impRoute = []
        self.cost = 0
        
    def optRoute(self, route=None):
        
        huge = 1e30000
        if route == None: route = self.route
        routeChange = route[:]
        serviceCost = self.info.serveCostD
        invArcD = self.info.invArcD
        SP = self.info.spDistanceD
        nArcs = len(route)
        change = False
        change2 = False
        if route[0] == route[-1]:
            change = True
            dummy = {'s2':route[-1]}
            routeChange[-1] = 's2'
            if invArcD[route[-1]]:
                invArcD['s2'] = 's3'
                dummy['s3'] = invArcD[route[-1]]
        if (route[0] == route[-2]) & (len(route)>2):
            change2 = True
            dummy2 = {'s4':route[-2]}
            routeChange[-2] = 's4'
            if invArcD[route[-2]]:
                invArcD['s4'] = 's5'
                dummy2['s5'] = invArcD[route[-2]]
        D = {}
        PI = {}
        
        D[routeChange[0]] = serviceCost[route[0]]
        PI[routeChange[0]] = 's'
        if invArcD[route[0]]:
            D[invArcD[routeChange[0]]] = serviceCost[routeChange[0]]
            PI[invArcD[routeChange[0]]] = 's'
        for i in range(1,nArcs):
            edge1 = D[route[i-1]] +  SP[route[i-1]][route[i]] + serviceCost[route[i]]
            edge2 = huge
            edge4 = huge
            if invArcD[route[i-1]]:
                edge2 =  D[invArcD[route[i-1]]] +  SP[invArcD[route[i-1]]][route[i]] + serviceCost[route[i]]
                if invArcD[route[i]]:
                    edge4 = D[invArcD[route[i-1]]] +  SP[invArcD[route[i-1]]][invArcD[route[i]]] + serviceCost[route[i]]               
            if edge1 < edge2:
                D[routeChange[i]] = edge1
                PI[routeChange[i]] = routeChange[i-1]
            else:
                D[routeChange[i]] = edge2
                PI[routeChange[i]] = invArcD[routeChange[i-1]]
            if invArcD[route[i]]:
                edge3 = D[route[i-1]] + SP[route[i-1]][invArcD[route[i]]] + serviceCost[route[i]]
                if edge3 < edge4:
                    D[invArcD[routeChange[i]]] = edge3
                    PI[invArcD[routeChange[i]]] = routeChange[i-1]
                else:
                    D[invArcD[routeChange[i]]] = edge4
                    PI[invArcD[routeChange[i]]] = invArcD[routeChange[i-1]]
                    
        if invArcD[route[i]]:
            if D[route[i]] < D[invArcD[route[i]]]:
                D['t'] = D[routeChange[i]]
                PI['t'] = routeChange[i]                
            else:
                D['t'] = D[invArcD[routeChange[i]]]
                PI['t'] = invArcD[routeChange[i]]  
        else:
            D['t'] = D[routeChange[i]]
            PI['t'] = routeChange[i]
        self.cost = D['t']
        optimalRoute = SPmodules.sp1SourceList(PI, 's', 't')
        if change:
            optimalRoute[-2] = dummy[optimalRoute[-2]]
        if change2:
            optimalRoute[-3] = dummy2[optimalRoute[-3]]
        self.impRoute = optimalRoute[1:-1]
                             
#if __name__ == "__main__":
#import UlusoyHeuristics as UH
#import time
#import NeighbourHoodsRe as NH
#    import LancommeARPconversions as LARP
#    file = 'TransformedInput/LPR_benchmarkProblems/Lpr-c-01_pickled.txt'
#    start = time.clock()
#    info = LARP.ReadProblemData(file)
#    initialSol = UH.giantRoute(file, info)
#    initialSol.genRoute()
#    bigRoute = initialSol.RouteBig
#    elapsed = time.clock() - start
#    print(bigRoute)
#    better = optArcDirect(bigRoute[1]['Solution'], info)
#    better.optRoute()
#    better.impRoute
#    (routeCost,serv) = NH.solutionTest(bigRoute[1]['Solution'], info)
#    print('Original route Test : ',routeCost,serv)
#    (routeCost,serv) = NH.solutionTest(better.impRoute, info)
#    print('New route : ',routeCost,serv)
#    print('Opt direction cost : ',better.cost, better.cost + serv)
                            
        