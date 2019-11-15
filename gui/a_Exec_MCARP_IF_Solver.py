'''
Created on 26 Jul 2010

@author: EWillemse
'''

import ConstructHeuristicMerge_IF as MergeConstruct
import EPSsolutions_IFs as EPSConstruct
import UlusoyHeuristics as UlusoyConstruct
import local_search_IF_new as LocalSearchImprove
import testSolutions as TEST

class MCARP_solver(object):
    
    def __init__(self, info):
        self.info = info
        self.constructiveHeuristic = 'EPS_balanced'
        self.localSearchHeuristic = 'Multi_move_local_search'
        self.neighbourhoods = 'All'
        self.testSolutions = False
        self.saveSolutions = False
        self.localsearch = False
        
    def generate_initial_solutions(self):
        
        if self.constructiveHeuristic == 'Efficient_Merge': 
            MERGE = MergeConstruct.MergeHeuristic(self.info)
            (solution, nTrips) = MERGE.mergeHeuristicIFs()
            
        elif self.constructiveHeuristic == 'EPS_balanced':
            EPS = EPSConstruct.EPSinitialSolution(self.info)
            (solution, nTrips) = EPS.completeInitialSolution('Real')[0]
            
        elif self.constructiveHeuristic == 'ULUSOY':
            ULUSOY = UlusoyConstruct.UlusoysIFs(self.info)
            (solution, nTrips) = ULUSOY.genCompleteSolution()[0]
            
        if self.testSolutions == True:
            TestReport = TEST.testSolution(self.info, solution)
            TestReport.checkFeasibilityIFs()
            if TestReport.raiseException:
                TestReport.testReportSolution()
                print('**************************************************************')
                print('Exceptions were raised while generating the initial solution')
                print('**************************************************************')
                
                raw_input('...Press any key to continue...')
        return(solution, nTrips)
    
    def improve_initial_solutions(self, initialSolution):
        
        print('')
        print('Start local search')
        print('')
        LS = LocalSearchImprove.LocalSearchIFs(self.info)
        if self.localSearchHeuristic == 'Multi_move_local_search':
            LS.neighbourSearchStrategy = 'MultiLocalSearch'
        (solution, nTrips) = LS.localSearch(initialSolution)
        print('')
        print(' Solution cost : %d' %solution['Total cost'])
        print('       n Trips : %d' %nTrips)
        if self.testSolutions == True:
            TestReport = TEST.testSolution(self.info, solution)
            TestReport.checkFeasibilityIFs()
            if TestReport.raiseException:
                TestReport.testReportSolution()
                print('**************************************************************')
                print('Exceptions were raised while improving the initial solution')
                print('**************************************************************')
                raw_input('...Press any key to continue...')
                
        return(solution, nTrips)
    
    def solveProblem(self):
        (solution, nTrips) = self.generate_initial_solutions()
        if self.localsearch: (solution, nTrips) = self.improve_initial_solutions(solution)
        return(solution, nTrips)
    
if __name__=="__main__":
    import a_Exec_ReadProblem_IF_Data as reader
    InputFile = 'Test/Lpr-a-02_pickled.txt'
    info = reader.readFile(InputFile)
    solve = MCARP_solver(info)
    (solution, nTrips) = solve.generate_initial_solutions()
    (solution, nTrips) = solve.improve_initial_solutions(solution)
    print(solution)