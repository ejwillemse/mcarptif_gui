'''
Created on 21 Jun 2012

@author: elias
'''
import a_Exec_ReadProblem_IF_Data as read
import a_Exec_MCARP_IF_Solver as Solver
import numpy as np
import cPickle

class solutionstats(object):
    
    def __init__(self, solution):
        self.solution = solution
        self.statsnp = []
        self.summarystats = {}
        
    def genstats(self):
        stats = []
        for s in range(1,len(self.solution)):
            self.solution[s]['Load'] = self.solution[s]['Load'][0:len(self.solution[s]['Solution'])]
            cost = self.solution[s]['Cost']
            load = sum(self.solution[s]['Load'])/1000
            dead = sum(self.solution[s]['Dead head'])
            mintrip = min(self.solution[s]['Subtrip cost'])
            maxtrip = max(self.solution[s]['Subtrip cost'])
            mindead = min(self.solution[s]['Dead head'])
            maxdead =max(self.solution[s]['Dead head'])
            minload = min(self.solution[s]['Load'])/1000
            maxload = max(self.solution[s]['Load'])/1000
            stats.append([s,cost,mintrip, maxtrip,  dead,  mindead, maxdead, load, minload, maxload])
        self.statsnp = np.array(stats)
        self.summarystats['Total time'] = sum(self.statsnp[:,1])
        self.summarystats['Max time'], self.summarystats['Min cost'] =  max(self.statsnp[:,1]), min(self.statsnp[:,1])
        self.summarystats['Total D-time'] = sum(self.statsnp[:,4])
        self.summarystats['Max D-time'], self.summarystats['Min D-time'] = max(self.statsnp[:,4]), min(self.statsnp[:,4])
        self.summarystats['Total load'] =  sum(self.statsnp[:,7])
        self.summarystats['Max load'], self.summarystats['Min load'] = max(self.statsnp[:,7]), min(self.statsnp[:,7])
        
    def displaystats(self):
        self.genstats()
        print('')
        heading = ('Route #', 'Total time', 'Min trip', 'Max trip', 'Total D-time', 'Min D-time', 'Max D-time', 'Total load', 'Min load', 'Max load')
        print(    '%-9s %-12s %-10s %-10s %-14s %-12s %-12s %-12s %-12s %-10s' %heading)
        print('%s' %((113+8)*'-'))
        for trip in range(0,len(self.solution)-1):
            pout = tuple(self.statsnp[trip,:])
            print('%-9i %-12i %-10i %-10i %-14i %-12i %-12i %-12i %-12i %-10i' %pout)
        print('')

            
    def displaysummarystats(self):
        self.genstats()
        totalcost = self.summarystats['Total time']
        maxcost, mincost = self.summarystats['Max time'], self.summarystats['Min cost']
        totaldead = self.summarystats['Total D-time']
        maxdead, mindead = self.summarystats['Max D-time'], self.summarystats['Min D-time']
        totalload = self.summarystats['Total load']
        maxload, minload = self.summarystats['Max load'], self.summarystats['Min load']
        print('')
        heading = ('','Total','Min','Max')
        print('%-10s %-10s %-10s %-10s' %heading)
        print('%s' %(40*'-'))
        print('%-10s %-10d %-10d %-10d' %('Time',totalcost, mincost, maxcost))
        print('%-10s %-10d %-10d %-10d' %('D-time',totaldead, mindead, maxdead))
        print('%-10s %-10d %-10d %-10d' %('Load',totalload, minload, maxload))
        print('')
        for i in xrange(len(self.solution[1]['Load'])):
            print(i, self.solution[1]['Load'][i]/1000, self.solution[1]['Subtrip cost'][i], )
        print(sum(self.solution[1]['Load'])/1000)
        
def updatesolution(info, solution):
    nRoutes = len(solution)-1
    for i in range(nRoutes):
        tripdeadhead = []
        distlist = []
        for trip in solution[i+1]['Solution']:
            dead = 0
            dist = 0      
            for k, arc in enumerate(trip[:-1]):
                dead += info.spDistanceD[arc][trip[k+1]]
                dist += dead + info.travelCostD[arc]
            dist += info.travelCostD[trip[-1]]
            tripdeadhead.append(dead)
            distlist.append(dead)
        solution[i+1]['Dead head'] = tripdeadhead
        solution[i+1]['Dist'] = distlist
    return(solution)    
    
def readinfo(problemfile):
    print('Loading problem info...')
    probinfo = read.readFile(problemfile)
    print('Done loading')
    print('')
    return(probinfo)

def solveproblem(info, localsearch=True):
    print('Solving problem...')
    print('')
    genroutes = Solver.MCARP_solver(info)
    genroutes.localsearch = localsearch
    (solution, nTrips) = genroutes.solveProblem()
    solution = updatesolution(info, solution)
    print('')
    print('Done solving')
    print('')
    print(solution)
    return(solution)

def solve(name):
    info = readinfo(name)
    print(info.allIndexD[710])
    info.maxTrip = 1e300000
    info.Capacity = 30000
    solution = solveproblem(info, False)
    sol = solutionstats(solution)
    sol.displaystats()
    sol.displaysummarystats()
    print(sum(info.demandD.values())/2/1000)
    
solve('Files/Input_Data/Actonville/Actonville_recycle_Schools_pickled.dat')