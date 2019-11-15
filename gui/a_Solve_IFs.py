'''
Created on 12 Aug 2010

@author: EWillemse
'''
import a_Exec_MCARP_IF_Solver as solver
from copy import deepcopy

class Solve_IFs(object):
    '''
    Very simple. Call the class with and give it the info data. 
    Then to solve a sector, call generateRoutes giving the sector arcs
    as input data. Returns the solution, number of trips AND solution cost.
    '''
    
    def __init__(self, info):
        self.info = deepcopy(info)
        self.solver = solver.MCARP_solver(self.info)
        self.orig_IF_dist = deepcopy(self.info.bestIFdistD)
        self.orig_IF_arc = deepcopy(self.info.bestIFD)

    def generateRoutes(self, listIFs):
        newIf_dist = {}
        newIf_arc = {}
        D = self.info.spDistanceD
        
        fullReqArcList = [self.info.depotArc] + deepcopy(self.info.reqArcList)
        
        for arcI in fullReqArcList:
            newIf_dist[arcI] = {}
            newIf_arc[arcI] = {}            
            for arcJ in fullReqArcList:
                dbest = 1e300000
                for IF in listIFs:
                    dTemp = D[arcI][IF] + D[IF][arcJ]
                    if dTemp < dbest:
                        best = IF
                        dbest = dTemp
                newIf_dist[arcI][arcJ] = dbest
                newIf_arc[arcI][arcJ] = best
                
        self.solver.info.bestIFdistD = deepcopy(newIf_dist)
        self.solver.info.bestIFD = deepcopy(newIf_arc)
        (solution, nTrips) = self.solver.solveProblem()
        self.solver.info.bestIFdistD = deepcopy(self.orig_IF_dist)
        self.solver.info.bestIFD = deepcopy(self.orig_IF_arc)
        
        return(solution, nTrips, solution['Total cost'])
