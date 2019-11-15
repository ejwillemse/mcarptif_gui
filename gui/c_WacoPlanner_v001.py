'''
Created on 09 Jun 2011

@author: elias
'''
import a_Exec_ReadProblem_IF_Data as read
import a_Exec_MCARP_IF_Solver as Solver
import b_gen_network_graph as Display
import b_genpaths
import pickle as cPickle
import numpy as np
from copy import deepcopy

def solveproblem(info, localsearch=False):
    print('Solving problem...')
    print('')
    genroutes = Solver.MCARP_solver(info)
    genroutes.localsearch = localsearch
    (solution, nTrips) = genroutes.solveProblem()
    print('')
    print('Done solving')
    print('')
    return(solution)

def loadsolutions(file):
    fileOpen = open(file)
    solution = cPickle.load(fileOpen)
    return(solution)

def readinfo(problemfile):
    print('Loading problem info...')
    probinfo = read.readFile(problemfile)
    print('Done loading')
    print('')
    return(probinfo)

class displaysolution(object):
    
    def __init__(self, area=None, info=None):
        if info: self.info = info
        else: self.info = readinfo('Problem_data/ActonvilleWatville/Data/ActonvilleWatville_pickled.dat')
        self.gp = b_genpaths.generate_paths(self.info)
        self.drawing = Display.gen_network_graph(area)
        self.displayout = True
        self.saveoutout = False
        self.savesolutionflag = False
        self.savename = None
        self.outputpath = 'Problem_data/ActonvilleWatville/Solution_routes/'
        self.outputtype = '.png'
        self.outputmetaname = 'solution'
        self.solution= None
        self.localsearch = False
        
        self.statsnp = []
        self.summarystats = {}
        
    def updatesolution(self):
        nRoutes = len(self.solution)-1
        for i in range(nRoutes):
            tripdeadhead = []
            distlist = []
            for trip in self.solution[i+1]['Solution']:
                dead = 0
                dist = 0      
                for k, arc in enumerate(trip[:-1]):
                    dead += self.info.spDistanceD[arc][trip[k+1]]
                    dist += dead + self.info.travelCostD[arc]
                dist += self.info.travelCostD[trip[-1]]
                tripdeadhead.append(dead)
                distlist.append(dead)
            self.solution[i+1]['Dead head'] = tripdeadhead
            self.solution[i+1]['Dist'] = distlist

    def changesettings(self):
        self.drawing.displayout = self.displayout
        self.drawing.saveoutput = self.saveoutout
        self.drawing.outputname = self.outputname
        self.drawing.outputtype = self.outputtype
        
    def drawtrip(self, trip):
        self.changesettings()
        self.gp.servicearcs = []
        self.gp.deadheadarcs = []
        self.gp.genarclists(trip)
        self.drawing.drawroute(self.gp.servicearcs, self.gp.deadheadarcs)
        
    def drawroute(self, route):
        self.changesettings()
        routereqarcs = []
        for trip in route:
            gptemp = b_genpaths.generate_paths(self.info)
            gptemp.genarclists(trip)
            routereqarcs.append(gptemp.servicearcs)
        self.drawing.drawvehicleroute(routereqarcs)
        
    def drawsolution(self, solution):
        self.changesettings()
        routereqarcs = []
        nVehicles = len(solution)-1
        for i in range(nVehicles):
            iReqArcs = []
            for trip in solution[i+1]['Solution']:
                gptemp = b_genpaths.generate_paths(self.info)
                gptemp.genarclists(trip)
                iReqArcs += gptemp.servicearcs
            routereqarcs.append(deepcopy(iReqArcs))
        self.drawing.drawvehicleroute(routereqarcs)    
    
    def drawfullnet(self):
        self.changesettings()
        self.drawing.drawfullgraph()
    
    def savesolution(self, solution):
        saveopen = open(self.savename,'w')
        cPickle.dump(solution, saveopen)
    
    def drawer(self):
        self.saveoutout = True
        self.displayout = False
        self.outputname = self.outputpath + self.outputmetaname + '_Full_Network'
        self.drawfullnet()
        self.outputname = self.outputpath + self.outputmetaname + '_All_Routes'
        self.drawsolution(self.solution)
        outpathmetaname = self.outputpath + self.outputmetaname
        for i in range(len(self.solution)-1):
            self.outputname = outpathmetaname + '_Route_' + str(i+1)
            self.drawroute(self.solution[i+1]['Solution'])
            tc = 0
            for trip in self.solution[i+1]['Solution']:
                tc += 1
                self.outputname = outpathmetaname + '_Route_' + str(i+1) + '_Trip_' + str(tc)
                self.drawtrip(trip)
                    
    def solveandsave(self):
        self.solution = solveproblem(self.info, self.localsearch)
        self.updatesolution()
        if self.savesolutionflag:self.savesolution(self.solution)
        print('Generating output...')
        self.drawer()
        print('Done generating output')
                
    def loadandsave(self, solutionfile):
        sfile = open(solutionfile)
        self.solution = cPickle.load(sfile)
        self.drawer()
        
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
            minload = min(self.solution[s]['Load'])
            maxload = max(self.solution[s]['Load'])
            travel = sum(self.solution[s]['Dist'])
            stats.append([s,cost,mintrip, maxtrip,  dead,  mindead, maxdead, load, minload, maxload,travel])
        self.statsnp = np.array(stats)
        self.summarystats['Total time'] = sum(self.statsnp[:,1])
        self.summarystats['Max time'], self.summarystats['Min cost'] =  max(self.statsnp[:,1]), min(self.statsnp[:,1])
        self.summarystats['Total D-time'] = sum(self.statsnp[:,4])
        self.summarystats['Max D-time'], self.summarystats['Min D-time'] = max(self.statsnp[:,4]), min(self.statsnp[:,4])
        self.summarystats['Total load'] =  sum(self.statsnp[:,7])
        self.summarystats['Max load'], self.summarystats['Min load'] = max(self.statsnp[:,7]), min(self.statsnp[:,7])        
        self.summarystats['Total trav'] = sum(self.statsnp[:,-1])
        
class solutionstats(object):
    
    def __init__(self, solutionfile):
        fopen = open(solutionfile)
        self.solution = cPickle.load(fopen)
        fopen.close()
        self.statsnp = []
        self.summarystats = {}
        
    def genstats(self):
        stats = []
        for s in range(1,len(self.solution)):
            self.solution[s]['Load'] = self.solution[s]['Load'][0:len(self.solution[s]['Solution'])]
            cost = self.solution[s]['Cost']
            load = sum(self.solution[s]['Load'])
            dead = sum(self.solution[s]['Dead head'])
            mintrip = min(self.solution[s]['Subtrip cost'])
            maxtrip = max(self.solution[s]['Subtrip cost'])
            mindead = min(self.solution[s]['Dead head'])
            maxdead =max(self.solution[s]['Dead head'])
            minload = min(self.solution[s]['Load'])
            maxload = max(self.solution[s]['Load'])
            stats.append([s,cost,mintrip, maxtrip,  dead,  mindead, maxdead, load, minload, maxload])
        self.statsnp = np.array(stats)
        self.summarystats['Total time'] = sum(self.statsnp[:,1])
        self.summarystats['Max time'], self.summarystats['Min cost'] =  max(self.statsnp[:,1]), min(self.statsnp[:,1])
        self.summarystats['Total D-time'] = sum(self.statsnp[:,4])
        self.summarystats['Max D-time'], self.summarystats['Min D-time'] = max(self.statsnp[:,4]), min(self.statsnp[:,4])
        self.summarystats['Total load'] =  sum(self.statsnp[:,7])
        self.summarystats['Max load'], self.summarystats['Min load'] = max(self.statsnp[:,7]), min(self.statsnp[:,7])
        
    def displaystats(self):
        print('')
        heading = ('Route #', 'Total time', 'Min trip', 'Max trip', 'Total D-time', 'Min D-time', 'Max D-time', 'Total load', 'Min load', 'Max load')
        print(    '%-9s %-12s %-10s %-10s %-14s %-12s %-12s %-12s %-12s %-10s' %heading)
        print('%s' %((113+8)*'-'))
        for trip in range(0,len(self.solution)-1):
            pout = tuple(self.statsnp[trip,:])
            print('%-9i %-12i %-10i %-10i %-14i %-12i %-12i %-12i %-12i %-10i' %pout)
        print('')
            
    def displaysummarystats(self):
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
        
if __name__=="__main__":
    area = 'Actonville'
    problemfile = 'Problem_data/ActonvilleWatville/Data/' + area + '_pickled.dat'
    solutionfile = 'Problem_data/ActonvilleWatville/Solution/' + area + '_solution_pickled.dat'
    outputmetaname = area + '_solution' 
    #probinfo = read.readFile(problemfile)
    draw = displaysolution(area)
    draw.savename = solutionfile
    draw.outputmetaname = outputmetaname
    draw.solveandsave()
    #draw.loadandsave(solutionfile)
    stats = solutionstats(solutionfile)
    stats.genstats()
    stats.displaystats()
    stats.displaysummarystats()
    
