# Read data from Lpr MCARP based instance set
# Elias Willemse, CSIR Pretoria, Created 7 October 2009. Edited 7 October 2009.

# Derived from the article:
# Lacomme, P., Prins, C., Ramdane-Cherif, W. (2000). Competitive Memetic 
# Algorithms for Arc Routing Problems. Annals of Operations Research, 131(4) 
# p. 159-185.
# Specifically pages 161-162.

import SPmodules2 as SPmodules
import pickle
import time

#===============================================================================
# Read data from standard text file
#===============================================================================
class ArcInfo(object):
    
    def __init__(self, filePath):
        ''' 
        Initiate standard data for lpr instances. Possible extenstions are also 
        initiated, such as intermediate facilities and a mximum vehicle trip 
        length. Current format can not cope with multiple depots (future work. 
        '''
        self.filePath = filePath
        self.name = None
        self.dataFile = open(self.filePath)
        self.dataList = self.dataFile.readlines()
        self.nonReqArcs = None # One-ways without waste
        self.nonReqEdges = None # Two-ways without waste
        self.reqArcs = None # One-ways or splitted large two-ways with waste
        self.reqEdges = None # Small one-waste with waste. Zig-zag collections
        self.depot = None # Single vehicle depot
        self.IFs = None # Multiple dumpsites
        self.nVehicles = None # Number of avaialable vehicles - assuming homogenious fleet
        self.capacity = None # Capacity of each vehicle - assuming homogenious fleet
        self.maxTrip = None # Maximum trip length (usually time) of a vehicle e.g. 8 hours
        self.dumpCost = None # Cost or time of unloading at a dumpsite
        
#    def problemName(self):
#        '''
#        Determines problem name and convert to a single string. Must be first 
#        entry in file and be of the form 'Name : name'. Not very good. Should
#        incorperate this in next module
#        '''
#        nameWithExt = (self.dataList[0].split())[2]
#        self.name = nameWithExt[:nameWithExt.find('.')]
    
    def problemInfo(self):
        '''
        Gets all the basic info from the text file. Everything except arcs and
        edges. 
        '''
        inputList = self.dataList
        for line in inputList:
            if line.find('NAME') != - 1: # get problem name and convert to a single string.
                nameWithExt = (line.split())[2] 
                self.name = nameWithExt[:nameWithExt.find('.')]
            if line.find('VEHICLES') != - 1: # get number of vehicles and convert to integer.
                self.nVehicles = int((line.split())[2])
            if line.find('CAPACITY') != - 1: # get vehicle capacity and convert to integer
                self.capacity = int((line.split())[2])
            if line.find('DUMPING_COST') != - 1: # get dumping cost and convert to integer
                self.dumpCost = int((line.split())[2])
            if line.find('MAX_TRIP') != - 1: # get the maximum trip length and convert to integer
                self.maxTrip = int((line.split())[2]) 
            if line.find('DEPOT') != - 1: # get depot and convert to integer. For multiple depots this will be a list
                self.depot = int((line.split())[2])
            if line.find('DUMPING_SITES') != - 1:# get dumping sites or IFs and converts to List. IFs must be seperated by ',' in data file
                IFstring = ((line.split())[2]).split(',')
                _IFs = []
                for i in IFstring:
                    _IFs.append(int(i))                
                self.IFs = _IFs
        
    def reqArcInfo(self, ArcLine):
        '''
        Standard dictionary containing required arc (with waste) info. Single 
        line is split and appropriate data stored. Data file must be in the 
        sequence '(v, u)  serv_cost : x trav_cost : y demand : z'.
        '''
        arcInfo = ArcLine.split() # Split line in conjunction with spaces.
        nodesTemp = arcInfo[0].replace('(', '') # Determine begin and end nodes. Converts string to a list.
        nodesTemp = nodesTemp.replace(')', '')
        nodesTemp = nodesTemp.split(',')
        arcNodes = (int(nodesTemp[0]), int(nodesTemp[1]))
        reqArcsDict = {}
        reqArcsDict['nodes'] = arcNodes # standard entry data
        reqArcsDict['serv_cost'] = int(arcInfo[2])
        reqArcsDict['trav_cost'] = int(arcInfo[4])
        reqArcsDict['demand'] = int(arcInfo[6])
        return(reqArcsDict)
        
    def nonReqArcInfo(self, ArcLine):
        '''
        Standard dictionary containing non-required arc (no waste) info. Single 
        line is  split and appropriate data stored. Data file must be in the 
        sequence 
        '(v, u)  serv_cost : x  cost : y'.
        '''
        arcInfo = ArcLine.split() # Split line in conjunction with spaces.
        nodesTemp = arcInfo[0].replace('(', '') # Determine begin and end nodes. Converts string to a list.
        nodesTemp = nodesTemp.replace(')', '')
        nodesTemp = nodesTemp.split(',')
        arcNodes = (int(nodesTemp[0]), int(nodesTemp[1]))
        reqArcsDict = {}
        reqArcsDict['nodes'] = arcNodes # standard entry data
        reqArcsDict['trav_cost'] = int(arcInfo[2])
        return(reqArcsDict)

    def getReqArcs(self):
        '''
        Get required arcs data. Required arcs must begin with 
        'LIST_REQ_ARCS'
        '''
        inputList = self.dataList # All data file lines
        start = False #
        arcs = []
        for line in inputList: # check each line
            if (start == True) & (line[0] != '('): break; # end of required arc data in text file. New file heading.
            if start == True: # start of required arc data in text file.
                info = self.reqArcInfo(line) # generate required arc data line for line.
                arcs.append(info) # generates a list of arc data. List is usefull since there may be same source destination arcs.
            if line.find('LIST_REQ_ARCS') !=- 1: start = True # req arcs info starts in data file.
        self.reqArcs = arcs
        
    def getReqEdges(self): # See getReqArcs.
        inputList = self.dataList
        start = False
        edges = []
        for line in inputList:
            if (start == True) & (line[0] != '('): break;
            if start == True:
                info = self.reqArcInfo(line)
                edges.append(info)
            if line.find('LIST_REQ_EDGES') !=- 1: start = True
        self.reqEdges = edges
        
    def getNonReqArcs(self): # See getReqArcs.
        inputList = self.dataList
        start = False
        arcs = []
        for line in inputList:
            if (start == True) & (line[0] != '('): break;
            if start == True:
                info = self.nonReqArcInfo(line)
                arcs.append(info)
            if line.find('LIST_NOREQ_ARCS') !=- 1: start = True
        self.nonReqArcs = arcs
        
    def getNonReqEdges(self): # See getReqArcs.
        inputList = self.dataList
        start = False
        arcs = []
        for line in inputList:
            if (start == True) & (line[0] != '('): break;
            if start == True:
                info = self.nonReqArcInfo(line)
                arcs.append(info)
            if line.find('LIST_NOREQ_EDGES') !=- 1: start = True
        self.nonReqEdges = arcs
        
    def generateAllData(self):
        '''
        Generate all problem date
        '''
        #self.name()
        self.problemInfo()
        self.getReqEdges()
        self.getReqArcs()
        self.getNonReqEdges()
        self.getNonReqArcs()


#===============================================================================
# Convert text file data into standard dictionaries
#===============================================================================
class ArcConvert(ArcInfo):
    
    def __init__(self, fileName):
        '''
        Converts data file information to multiple dictionaries. All arcs, 
        depots and dumpsites are assigned unique keys, which are used in all
        dictionaries. Original arcs are stored in allIndexD
        '''
        ArcInfo.__init__(self, fileName)
        self.nArcs = 0 # number of arcs including two arcs per edge, depots and ifs.
        self.depotArc = None # index of the depot arc. Mulitple depots will require a dictionary
        self.IFarcs = [] # List of intermedaite facility arcs
        self.beginD = {} # begin node of every arcs u of (u,v)
        self.endD = {} # end node of every arc v of (v,u)
        self.serveCostD = {} # cost of servicing a required arc
        self.travelCostD = {} # cost of travesing any arc
        self.demandD = {} # demand (kg of waste for example) of required arcs
        self.invArcD = {} # inverse of an arc. Applies to edges where each are presented as two arcs, and each being the inverse of the other.
        self.sucArcD = {} # succesor arcs of an arc, i.e. arcs whos begin vertex is the same as the arc in question's en vertex suc(u, v) = (v, x) and (v,y) 
        self.allIndexD = {} # dictionary with arc keys relating the keys back to the original arcs
        self.generateAllData()
        self.generateKeys()
        self.reqArcList = [] # list of all the required arcs.
    
    def generateKeys(self):
        '''
        Determines number unique keys required for all arcs, edges, depots and ifs.
        '''
        nArcKeys = 0
        if self.nonReqArcs: 
            nArcKeys = nArcKeys + len(self.nonReqArcs) # one to one relation. Each arc has on key 
        if self.nonReqEdges: 
            nArcKeys = nArcKeys + 2 * len(self.nonReqEdges) # one to two relation. Each edge has two arcs, each with a key 
        if self.reqArcs: 
            nArcKeys = nArcKeys + len(self.reqArcs) # one to one relation. Each arc has on key 
        if self.reqEdges: 
            nArcKeys = nArcKeys + 2 * len(self.reqEdges) # one to two relation. Each edge has two arcs, each with a key 
        if self.depot: 
            nArcKeys = nArcKeys + 1 # one key per depot
        if self.IFs: 
            nArcKeys = nArcKeys + len(self.IFs) # one key per dumbsite
        self.nArcs = nArcKeys
    
    def generateDepoIFDict(self, keysIter, depot=None):
        '''
        Generate depot info. Demand, service and traversal cost is included and
        can thus be treated as a required arcs.
        '''
        if depot == None: depot = self.depot
        key = keysIter.pop(0) # take first key and assigne to depot arc
        self.allIndexD[key] = (depot, depot) #(v,v)
        self.beginD[key] = depot # Loop arc
        self.endD[key] = depot # Loop arc
        self.serveCostD[key] = 0 
        self.travelCostD[key] = 0
        self.demandD[key] = 0
        self.invArcD[key] = None # directed
        return(keysIter, key)
    
    def generateNonArcDict(self, keysIter, arc):
        '''
        Generate info for a non-required arcs - also used for required edges. 
        Works with arcs not edges.
        '''
        key = keysIter.pop(0)
        self.allIndexD[key] = arc['nodes'] # refers to (u, v)
        self.beginD[key] = arc['nodes'][0] 
        self.endD[key] = arc['nodes'][1] 
        self.travelCostD[key] = arc['trav_cost']
        self.invArcD[key] = None # directed so there is no inverse
        return(keysIter, key)
    
    def generateNonEdgeDict(self, keysIter, arc):
        '''
        Generates info for non-required edge. Two arcs are created, one for each
        side of the road, and are linked with the inverse key.
        '''
        key1 = keysIter.pop(0)
        key2 = keysIter.pop(0)
        
        self.allIndexD[key1] = arc['nodes']
        self.allIndexD[key2] = (arc['nodes'][1], arc['nodes'][0]) # edge reversed
        self.beginD[key1] = self.endD[key2] = arc['nodes'][0] # begin node of one arcs is the same as end node of the opesite arc 
        self.endD[key1] = self.beginD[key2] = arc['nodes'][1] # same as above
        self.travelCostD[key1] = self.travelCostD[key2] = arc['trav_cost'] # both arcs have the same cost
        self.invArcD[key1] = key2 # rever to the opesite arc
        self.invArcD[key2] = key1 #
        return(keysIter, key1, key2)
    
    def addRequiredData(self, key, arc):
        '''
        Adds demand and service cost to required arcs. With required edge the 
        same information is assigned to both arcs.
        '''
        self.serveCostD[key] = arc['serv_cost']
        self.demandD[key] = arc['demand']
        self.reqArcList.append(key)
    
    def genSuccesorArcs(self):
        '''
        Generates a dictionary of successor arcs for each arc. Used with 
        shortest path algorithms. Each arc is compared to all other arcs and if
        the begin node is the same as the end node, then it is a successor arc.
        Might be usefull to include turn penalties here by expanding dictionaries.
        Also, successor arcs with TPs dictionary may be provided as input.
        '''
        beginDComplete = self.beginD.items()
        endDComplete = self.endD.items()
        for i in endDComplete: #Every arc and its endnode
            tempAdjacentArcs = []
            for j in beginDComplete:#every arc and its begin node
                if i[1] == j[1]:tempAdjacentArcs.append(j[0])#check if arc j's begin node is same as arc i's end node and add to list
            self.sucArcD[i[0]] = tempAdjacentArcs# add complete list to dictionary key 
    
    def generateDict(self):
        '''
        Gnerate all the required dictionaries by calling each of gen 
        definitions for the different type of arcs.
        '''
        keysIter = range(self.nArcs)
        if self.depot: # generate depot info
            (keysIter, key) = self.generateDepoIFDict(keysIter)
            self.depotArc = key # links arc index to depot
        if self.IFs: # same as above, only done for each if
            for IF in self.IFs:
                (keysIter, key) = self.generateDepoIFDict(keysIter, IF)
                self.IFarcs.append(key)
        if self.nonReqArcs:
            for arc in self.nonReqArcs:
                (keysIter, key) = self.generateNonArcDict(keysIter, arc)
        if self.nonReqEdges:
            for edge in self.nonReqEdges:
                (keysIter, key1, key2) = self.generateNonEdgeDict(keysIter, edge)
        if self.reqArcs:
            for arc in self.reqArcs:
                (keysIter, key) = self.generateNonArcDict(keysIter, arc) # add general info by treating edge as non-required 
                self.addRequiredData(key, arc) # add required info - service cost and demand
        if self.reqEdges:
            for edge in self.reqEdges:
                (keysIter, key1, key2) = self.generateNonEdgeDict(keysIter, edge) # add general info by creating two arcs for each edge 
                self.addRequiredData(key1, edge) # add required edge info to each arc
                self.addRequiredData(key2, edge)
        self.genSuccesorArcs()


#===============================================================================
# Calculate shortest path arc to matrix based on text file. All generated info
# can be stored in a pickle text file.
#===============================================================================
class GenerateSP(ArcConvert):
    
    def __init__(self, fileName):
        ArcConvert.__init__(self, fileName)
        self.spDistanceD = {}
        self.spPreD = {}
        self.generateDict()
        self.bestIFD = {}
        self.bestIFdistD = {}
    
    
    def genFloyedWarshallSP(self):
        '''
        Call an arc to arc adaptation of the Floyd-Warshall algorithm to compute
        shortest arc to arc paths for all arcs. Algorithm also deals with 
        turn penalties. Arc to arc shortest distances does not include the
        cost of servicing or traversing the actual arc.
        '''
        (self.spDistanceD, self.spPreD) = SPmodules.FloydWarshallTP(self.travelCostD, self.sucArcD)

    def genBestIFs(self):
        '''
        '''
        self.bestIFD = {}
        self.bestIFdistD = {}
        self.depotArc
        reqArcListTemp = [self.depotArc] + self.reqArcList
        for i in reqArcListTemp:
            self.bestIFD[i] = {}
            self.bestIFdistD[i] = {} 
            for j in reqArcListTemp:
                if i != j:
                    bestIF = 1e300000
                    for k in self.IFarcs:
                        IFdist = self.spDistanceD[i][k] + self.spDistanceD[k][j]
                        if IFdist < bestIF:
                            bestIF = IFdist
                            self.bestIFD[i][j] = k
                            self.bestIFdistD[i][j] = IFdist
                            

    def writeData(self, WritePath):
        '''
        Stores date in a predifined path. Sequence of the data file is important
        since info must be read in the same sequence/
        '''
        ActualPath = WritePath + self.name + '_pickled' + '.dat'
        data = [self.name,
                self.nonReqArcs,
                self.nonReqEdges,
                self.reqArcs,
                self.reqEdges,
                self.depot,
                self.IFs,
                self.nVehicles,
                self.capacity,
                self.maxTrip,
                self.dumpCost,
                self.nArcs,
                self.depotArc,
                self.IFarcs,
                self.beginD,
                self.endD,
                self.serveCostD,
                self.travelCostD,
                self.demandD,
                self.invArcD,
                self.sucArcD,
                self.allIndexD,
                self.reqArcList,
                self.spDistanceD,
                self.spPreD,
                self.bestIFD,
                self.bestIFdistD]
        fileOpen = open(ActualPath, 'w')
        pickle.dump(data, fileOpen)
        fileOpen.close()
        
#===============================================================================
# Calculate shortest path arc to matrix based on text file. All generated info
# can be stored in a pickle text file.
#===============================================================================        
class pickleAllDataIFs(object):
    
    def __init__(self, files, outputFolder = 'TransformedInput/LPR_benchmarkProblems/Read_Write_times.txt'):
        self.files = files
        self.outputFolder = outputFolder
        
    def readAndWriteFiles(self):
        timesDict = {}
        for fileName in self.files:
            timesDict[fileName] = {}
            startime = time.clock()
            y = GenerateSP(fileName)
            endtime1 = startime - time.clock()
            timesDict[fileName]['Read data'] = endtime1
            startime2 = time.clock()
            y.genFloyedWarshallSP()
            endtime2 = startime2 - time.clock()
            timesDict[fileName]['Calc SP data'] = endtime2
            startime2b = time.clock()
            y.genBestIFs()
            endtime2b = startime2b - time.clock()
            timesDict[fileName]['Calc best IFs'] = endtime2b
            startime3 = time.clock()
            y.writeData(self.outputFolder)
            endtime3 = startime3 - time.clock()
            timesDict[fileName]['Write data'] = endtime3
            totalTime = startime - time.clock()
            timesDict[fileName]['Total time'] = totalTime
        fileOpen = open(self.outputFolder + 'Read_Write_times.txt','w')
        pickle.dump(timesDict,fileOpen)
        fileOpen.close()
        
    def readAndWriteFilesNoSPs(self):
        timesDict = {}
        for fileName in self.files:
            timesDict[fileName] = {}
            startime = time.clock()
            y = GenerateSP(fileName)
            endtime1 = startime - time.clock()
            timesDict[fileName]['Read data'] = endtime1
            startime2 = time.clock()
#            y.genFloyedWarshallSP()
            endtime2 = startime2 - time.clock()
            timesDict[fileName]['Calc SP data'] = endtime2
            startime2b = time.clock()
#            y.genBestIFs()
            endtime2b = startime2b - time.clock()
            timesDict[fileName]['Calc best IFs'] = endtime2b
            startime3 = time.clock()
            y.writeData(self.outputFolder)
            endtime3 = startime3 - time.clock()
            timesDict[fileName]['Write data'] = endtime3
            totalTime = startime - time.clock()
            timesDict[fileName]['Total time'] = totalTime
#        fileOpen = open(self.outputFolder + 'Read_Write_times.txt','w')
#        pickle.dump(timesDict,fileOpen)
#        fileOpen.close()
            
        
#===============================================================================
# Read all benchmark problem data from a pickled text file. 
#===============================================================================
class ReadProblemDataReduced(object):
    
    def __init__(self, fileName):
        '''
        Read all required data from a specified file path and name. List 
        sequence of information must be consistent with GenerateSP.writeData 
        module.
        '''
        fileOpen1 = open(fileName + '_Standard_Info.dat')
        [self.name,
         self.reqEdges,
         self.nVehicles,
         self.capacity,
         self.maxTrip,
         self.dumpCost,
         self.nArcs,
         self.depotArc,
         self.IFarcs,
         self.serveCostD,
         self.travelCostD,
         self.demandD,
         self.invArcD,
         self.reqArcList] = pickle.load(fileOpen1)
        fileOpen1.close()
        print('read standard info')
        fileOpen2 = open(fileName + '_ShortestPath_Info.dat')
        self.spDistanceD = pickle.load(fileOpen2)
        fileOpen2.close()
        print('read sp info')
        fileOpen3 = open(fileName + '_bestIFarc_Info.dat')
        self.bestIFD = pickle.load(fileOpen3)
        fileOpen3.close()
        print('read if info 1')
        fileOpen4 = open(fileName + '_bestIFdistance_Info.dat')
        self.bestIFdistD = pickle.load(fileOpen4)
        fileOpen4.close()
        print('read if info 2')

class ReadProblemData(object):
    
    def __init__(self, fileName):
        '''
        Read all required data from a specified file path and name. List 
        sequence of information must be consistent with GenerateSP.writeData 
        module.
        '''
        fileOpen = open(fileName)
        [self.name,
         self.nonReqArcs,
         self.nonReqEdges,
         self.reqArcs,
         self.reqEdges,
         self.depot,
         self.IFs,
         self.nVehicles,
         self.capacity,
         self.maxTrip,
         self.dumpCost,
         self.nArcs,
         self.depotArc,
         self.IFarcs,
         self.beginD,
         self.endD,
         self.serveCostD,
         self.travelCostD,
         self.demandD,
         self.invArcD,
         self.sucArcD,
         self.allIndexD,
         self.reqArcList,
         self.spDistanceD,
         self.spPreD] = pickle.load(fileOpen)
        fileOpen.close()     

class ReadProblemDataIFs(object):
    
    def __init__(self, fileName):
        '''
        Read all required data from a specified file path and name. List 
        sequence of information must be consistent with GenerateSP.writeData 
        module.
        '''
        fileOpen = open(fileName, 'rb')
        [self.name,
         self.nonReqArcs,
         self.nonReqEdges,
         self.reqArcs,
         self.reqEdges,
         self.depot,
         self.IFs,
         self.nVehicles,
         self.capacity,
         self.maxTrip,
         self.dumpCost,
         self.nArcs,
         self.depotArc,
         self.IFarcs,
         self.beginD,
         self.endD,
         self.serveCostD,
         self.travelCostD,
         self.demandD,
         self.invArcD,
         self.sucArcD,
         self.allIndexD,
         self.reqArcList,
         self.spDistanceD,
         self.spPreD,                
         self.bestIFD,
         self.bestIFdistD] = pickle.load(fileOpen)
        fileOpen.close()

if __name__ == "__main__":
#    import os
#    import psyco
#    psyco.full()
    inputDirectory = 'cen_IF_ProblemRaw/'
    outPutFolder = 'cen_IF_ProblemInfo/'
    fileNames = ['Centurion_a.dat']
    for i in range(len(fileNames)):
        fileNames[i] = inputDirectory + fileNames[i]
    print(fileNames)
        
    y = pickleAllDataIFs(fileNames, outPutFolder)
    y.readAndWriteFiles()