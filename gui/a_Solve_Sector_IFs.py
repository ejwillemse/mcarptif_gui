'''
Created on 17 Sep 2010

@author: EWillemse
'''
import a_Exec_MCARP_IF_Solver as solver
from copy import deepcopy

class Solve_MCARP_IF_sector(object):
    '''
    Very simple. Call the class with and give it the info data. 
    Then to solve a sector, call generateRoutes giving the sector arcs
    as input data. Returns the solution, number of trips AND solution cost.
    '''
    
    def __init__(self, info):
        self.info = deepcopy(info)
        self.solver = solver.MCARP_solver(self.info)
        self.origArcs = deepcopy(self.info.reqArcList)
        
    def generateRoutes(self, arcs):
        self.solver.info.reqArcList = deepcopy(arcs)
        (solution, nTrips) = self.solver.solveProblem()
        self.solver.info.reqArcList = deepcopy(self.origArcs)
        return(solution, nTrips, solution['Total cost'])