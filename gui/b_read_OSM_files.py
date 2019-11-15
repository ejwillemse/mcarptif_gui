'''
Created on 07 Jun 2011

@author: EWillemse
'''

class osm_read_network_info(object):
    
    def __init__(self, areaname='ActonvilleWatville'):
        self.areaname   = areaname
        self.inpath     = 'Files/OSM_display/'
        self.nodesextension = '_Nodes.txt'
        self.nonreqarcsextension = '_NonreqArcs.txt'
        self.reqarcsextension = '_ReqArcs.txt'
        self.nodesextension = '_Nodes.txt'
        self.depotnodesextension = '_DepotNode.txt'
        self.ifnodesextension = '_IFNode.txt'
        self.nnodes = 0
        self.intersectnodes = []
        self.nodes = {}
        self.narcs = 0
        self.arcs = {}
        self.arcnodekeys = {}
        self.reqarcs = []
        self.nonreqarcs = []
        self.depotnode = None
        self.depotcordinates = None
        self.ifnode = None
        self.ifcordinates = None
        self.printoutput = False

    def readareadata(self, subarea='ActonvilleWatville'):
        if subarea == 'ActonvilleWatville':self.readActonvilleWatvilleData()
        elif subarea == 'Actonville':self.readActonvilleData()
        elif subarea == 'Watville':self.readWatvilleData()

    def readActonvilleData(self):
        self.read_node_file()
        self.read_non_req_arc_file()
        self.nonreqarcsextension = '_Watville_ReqArcs.txt'
        self.read_non_req_arc_file()
        self.reqarcsextension = '_Actonville_ReqArcs.txt'
        self.read_req_arc_file()
        self.read_depot_node_file()
        self.read_if_node_file()
        if self.printoutput:self.printarcinfo() 

    def readWatvilleData(self):
        self.read_node_file()
        self.read_non_req_arc_file()
        self.nonreqarcsextension = '_Actonville_ReqArcs.txt'
        self.read_non_req_arc_file()
        self.reqarcsextension = '_Watville_ReqArcs.txt'
        self.read_req_arc_file()
        self.read_depot_node_file()
        self.read_if_node_file()
        if self.printoutput:self.printarcinfo() 
 
    def readActonvilleWatvilleData(self):
        self.read_node_file()
        self.read_non_req_arc_file()
        self.reqarcsextension = '_Actonville_ReqArcs.txt'
        self.read_req_arc_file()
        self.reqarcsextension = '_Watville_ReqArcs.txt'
        self.read_req_arc_file()
        self.read_depot_node_file()
        self.read_if_node_file()
        if self.printoutput:self.printarcinfo()  

    def read_node_file(self):
        areanodesfilename = self.inpath + self.areaname + self.nodesextension
        with open(areanodesfilename) as nodesfile:
            for nodesfileline in nodesfile:
                interpret_value = self.interpret_node_line(nodesfileline)
                if interpret_value == 'begin_node_info': 
                    self.nnodes += 1
                    (nodeId,nodex,nodey) = self.split_node_info(nodesfileline)
                    if nodeId in self.nodes:print('ERROR: Duplicate node', nodeId)
                    self.nodes[nodeId] = {'nodeId':nodeId, 'x':nodex, 'y':nodey, 'arcs':[]}
                elif interpret_value == 'arc':self.nodes[nodeId]['arcs'].append(int(nodesfileline))

    def read_non_req_arc_file(self):
        nonreqarcsfilename = self.inpath + self.areaname + self.nonreqarcsextension
        self.read_arc_file(nonreqarcsfilename, 'nonreq')       

    def read_req_arc_file(self):
        areareqarcsfilename = self.inpath + self.areaname + self.reqarcsextension
        self.read_arc_file(areareqarcsfilename, 'req')
    
    def read_depot_node_file(self):
        depotnodefilename = self.inpath + self.areaname + self.depotnodesextension
        with open(depotnodefilename) as nodesfile:
            depotinfoline = nodesfile.readline()
            depotnodetemp = depotinfoline.split()
            self.depotnode = int(depotnodetemp[1][depotnodetemp[1].find('=')+1:])
        self.depotcordinates = [self.nodes[self.depotnode]['x'],self.nodes[self.depotnode]['y']]
    
    def read_if_node_file(self):
        ifnodefilename = self.inpath + self.areaname + self.ifnodesextension
        with open(ifnodefilename) as ifsfile:
            ifsinfoline = ifsfile.readline()
            ifnodetemp = ifsinfoline.split()
            self.ifnode = int(ifnodetemp[1][ifnodetemp[1].find('=')+1:])
        self.ifcordinates = [self.nodes[self.ifnode]['x'],self.nodes[self.ifnode]['y']]   
    
    def printarcinfo(self):
        print('Non-required arcs : ')
        for arc in self.nonreqarcs:print(self.arcs[arc])
        print('')
        print('Required arcs : ')
        for arc in self.reqarcs:print(self.arcs[arc])
                
    def interpret_node_line(self, nodesfileline):
        if 'Node' in nodesfileline: return('begin_node_info')
        elif 'way referrer' in nodesfileline: return(0)
        else:
            try:
                int(nodesfileline)
                return('arc')
            except ValueError:return(0)

    def split_node_info(self, nodesfileline):
        split_info = nodesfileline.split()
        nodeId = int(split_info[1][split_info[1].find('=')+1:])
        
        nodextemp = split_info[5].split(',')[0]
        nodex = float(nodextemp[nodextemp.find('=')+1:])
        
        nodeytemp = split_info[6].split(')')[0]
        nodey = float(nodeytemp[nodeytemp.find('=')+1:])
        nodey *= -1
        
        return(nodeId,nodex,nodey)

    def read_arc_file(self, arcsfilename, arctype = 'nonreq'):
        with open(arcsfilename) as arcsfile:
            for arcsfileline in arcsfile:
                interpret_value = self.interpret_reqarc_line(arcsfileline)
                if interpret_value == 'begin_reqarc_info': 
                    self.narcs += 1
                    (arcId,nnodes) = self.split_arc_info(arcsfileline)
                    if arcId in self.arcs:print('ERROR: Duplicate arc', arcId)
                    self.arcs[arcId] = {'arcId':arcId, 'nNodes':nnodes, 'nodes':[]}
                    if arctype == 'req':self.reqarcs.append(arcId)
                    elif arctype == 'nonreq':self.nonreqarcs.append(arcId)
                elif interpret_value == 'nhouseholds': self.arcs[arcId]['households']=self.split_surface(arcsfileline)
                elif interpret_value == 'node' :self.arcs[arcId]['nodes'].append(int(arcsfileline))
                
        for arc in self.arcs:
            self.arcs[arc]['length'] = self.calc_arc_length(self.arcs[arc])
            self.arcs[arc]['node_key'] = (self.arcs[arc]['nodes'][0],self.arcs[arc]['nodes'][-1])
            tempnodekey = (min(self.arcs[arc]['nodes'][0],self.arcs[arc]['nodes'][-1]),max(self.arcs[arc]['nodes'][0],self.arcs[arc]['nodes'][-1]))
            self.arcnodekeys[tempnodekey] = arc
            if self.arcs[arc]['nodes'][0] not in self.intersectnodes:self.intersectnodes.append(self.arcs[arc]['nodes'][0])
            if self.arcs[arc]['nodes'][-1] not in self.intersectnodes:self.intersectnodes.append(self.arcs[arc]['nodes'][-1])

    def interpret_reqarc_line(self, reqarcsfileline):
        if 'Way' in reqarcsfileline: return('begin_reqarc_info')
        elif 'nodes' in reqarcsfileline: return('begin_reqarc_nodes')
        elif 'surface' in reqarcsfileline: return('nhouseholds')
        else:
            try:
                int(reqarcsfileline)
                return('node')
            except ValueError:return(0)

    def split_arc_info(self, reqarcsfileline):
        split_info = reqarcsfileline.split()
        arcId = int(split_info[1][split_info[1].find('=')+1:])
        nnodes = int(split_info[2])       
        return(arcId,nnodes)
    
    def split_surface(self, reqarcsfileline):
        split_info = reqarcsfileline.split('"')
        arc = int(split_info[3])
        return(arc)
    
    def calc_arc_length(self, arc_info):
        nNodes = len(arc_info['nodes'])
        if nNodes != arc_info['nNodes']:print('ERROR: Arc has more nodes than specified')
        length = 0;
        for i in range(nNodes-1):
            nodeI = arc_info['nodes'][i]
            nodeIx, nodeIy = self.nodes[nodeI]['x'], self.nodes[nodeI]['y']
            nodeJ = arc_info['nodes'][i+1]
            nodeJx, nodeJy = self.nodes[nodeJ]['x'], self.nodes[nodeJ]['y']
            length += ((nodeIx-nodeJx)**2 + (nodeIy-nodeJy)**2)**0.5
        return(int(length))
          
if __name__=="__main__":   
    osm_rd = osm_read_network_info()
    osm_rd.readareadata()
    
    