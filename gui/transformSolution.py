'''
Created on 18 May 2010

@author: BowenKT
'''

from copy import deepcopy

class transformSolution(object):
    
    def __init__(self, info):
        self.info = info
        self.SP = self.info.spDistanceD
        self.serve = self.info.serveCostD
        self.dumpCost = self.info.dumpCost
        self.demand = self.info.demandD
    
    def newRoute(self, solution):
        nRoutes = len(solution.keys())-1
        newSolution = deepcopy(solution)
        for i in range(1, nRoutes+1):
            mainRouteI = solution[i]['Solution']
            solutionICostList = []
            for j in range(len(mainRouteI)):
                routeI = mainRouteI[j]
                subCost = 0
                for k in range(len(routeI)-1):
                    subCost += self.SP[routeI[k]][routeI[k+1]] + self.serve[routeI[k]]
                subCost += self.serve[routeI[k+1]] + self.dumpCost
                solutionICostList.append(subCost)
            newSolution[i]['Subtrip cost'] = deepcopy(solutionICostList)
        return(newSolution)

if __name__=="__main__":
    import LancommeARPconversions3 as LARP
    import cPickle
    fileName = 'lpr_IF_ProblemInfo/lpr-a-05_pickled.txt'
    solutionFilePath = 'lpr_IF_Solutions/Lpr-a-05_Init_Hybrid_sol.txt'
    initSolutionFile = open(solutionFilePath)
    info = LARP.ReadProblemDataIFs(fileName)
    initSol = cPickle.load(initSolutionFile)
    transFormedSol = transformSolution(info, initSol).newRoute()
    print(transFormedSol)
        