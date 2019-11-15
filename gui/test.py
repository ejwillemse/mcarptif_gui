'''
Created on 05 Aug 2010

@author: EWillemse
'''
import a_Exec_ReadProblem_IF_Data as read
import a_Exec_MCARP_IF_Solver as Solver

file = 'Problem_data/ActonvilleWatville_data_set/Watville_pickled.dat'

info = read.readFile(file)
info.maxTrip = 2*info.maxTrip
genroutes = Solver.MCARP_solver(info)
genroutes.localsearch = False
(solution, nTrips) = genroutes.solveProblem()
print(solution)
print(nTrips)

