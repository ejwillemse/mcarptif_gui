"""
Creating and plotting unstructured triangular grids.
"""
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import numpy as np
import math
import b_read_OSM_files
import mpl_toolkits.axisartist as AA

class gen_network_graph(object):
    
    def __init__(self, area=None):
        self.OSM_rd = b_read_OSM_files.osm_read_network_info()
        if area:self.OSM_rd.readareadata(area)
        else: self.OSM_rd.readareadata()
        self.nodeallarray = []
        self.intersectnodearry = []
        self.fullnetworkcolor = 'grey'
        self.fullnetworklinewidth = 1
        self.arcnetcolor = 'blue'
        self.arcnetwidth = 1
        self.nodescolor = 'red'
        self.nodessym = 'o'
        self.nodesize = 5
        
        self.fig = None
        self.ax = None
        
        self.arcident = {}
        
        self.displayout = True
        self.saveoutput = False
        self.outputname = 'Dummy'
        self.outputtype = '.pdf'
        self.dpisize = 125

    def genintersectnodes(self):
        nodearray = []
        for node in self.OSM_rd.intersectnodes:
            nodearray.append([self.OSM_rd.nodes[node]['x'],self.OSM_rd.nodes[node]['y']])
        return(nodearray)
        
    def genallnodes(self):
        nodearray = []        
        for node in self.OSM_rd.nodes:
            nodearray.append([self.OSM_rd.nodes[node]['x'],self.OSM_rd.nodes[node]['y']])
        return(nodearray)
    
    def gennodes(self):
        self.intersectnodearry = self.genintersectnodes()
        self.nodeallarray = self.genallnodes()
        xyinter = np.asarray(self.intersectnodearry)
        xyall = np.asarray(self.nodeallarray)
        self.minmaxcoordinates(xyall[:,0], xyall[:,1])
        self.x = xyinter[:,0]#*180/3.14159
        self.y = xyinter[:,1]#*180/3.14159
        
    def minmaxcoordinates(self, x, y):
        x_max = max(x)
        x_min = min(x)
        y_min = max(y)
        y_max = min(y)

        self.x_max = x_max + (x_max-x_min)*0.02
        self.x_min = x_min - (x_max-x_min)*0.02
        self.y_max = y_max + (y_max-y_min)*0.02
        self.y_min = y_min - (y_max-y_min)*0.02
        
    def genarcs(self, arcs):
        codes = []
        verts = []
        for arc in arcs:
            nNodes = len(self.OSM_rd.arcs[arc]['nodes'])
            for i in range(nNodes-1): 
                bnode = self.OSM_rd.arcs[arc]['nodes'][i]
                enode = self.OSM_rd.arcs[arc]['nodes'][i+1]
                arcxy = ((self.OSM_rd.nodes[bnode]['x'],self.OSM_rd.nodes[bnode]['y']),
                         (self.OSM_rd.nodes[enode]['x'],self.OSM_rd.nodes[enode]['y']))
                codes.append(Path.MOVETO)
                verts.append((arcxy[0]))
                codes.append(Path.LINETO)
                verts.append((arcxy[1]))
        return(codes, verts)
    
    def arcpath(self, arcsforpath):
        (codes, verts) = self.genarcs(arcsforpath)
        path = Path(verts, codes)
        return(path)
    
    def makefullnetwork(self):
        pathAll = self.arcpath(self.OSM_rd.arcs.keys())
        patchfullnetwork = patches.PathPatch(pathAll, color=self.fullnetworkcolor, lw=self.fullnetworklinewidth)
        return(patchfullnetwork)
            
    def makearcnetwork(self, arcs):
        arcpath = self.arcpath(arcs)
        patcharcnetwork = patches.PathPatch(arcpath, color=self.arcnetcolor, lw=self.arcnetwidth)
        return(patcharcnetwork)
    
    def initiatefigure(self):
        self.gennodes()
        self.fig = plt.figure(frameon = False)
        self.ax = AA.Subplot(self.fig, 1, 1, 1, aspect='equal')
        self.fig.add_subplot(self.ax)
        self.ax.axis["bottom","top","right","left"].set_visible(False)
        self.ax.set_xlim(self.x_min, self.x_max)
        self.ax.set_ylim(self.y_min, self.y_max)
    
    def addnodesfigure(self, nodesdraw):
        ndraw = np.asarray(nodesdraw)
        self.ax.plot(ndraw[:,0], ndraw[:,1], self.nodessym, ms=self.nodesize, color=self.nodescolor)
    
        
    def drawfullgraph(self):
        self.initiatefigure()
        self.ax.add_patch(self.makefullnetwork())
        self.ax.add_patch(self.makearcnetwork(self.OSM_rd.reqarcs))
        self.nodescolor = 'red'
        self.addnodesfigure([self.OSM_rd.ifcordinates])
        self.nodescolor = 'black'
        self.addnodesfigure([self.OSM_rd.depotcordinates])
        if self.saveoutput: plt.savefig(self.outputname+self.outputtype,dpi=self.dpisize,bbox_inches='tight')
        if self.displayout: plt.show()
    
    def drawnetwork(self,arcsdraw):
        self.initiatefigure()
        self.ax.add_patch(self.makefullnetwork())
        self.ax.add_patch(self.makearcnetwork(arcsdraw))
        self.nodescolor = 'red'
        self.addnodesfigure([self.OSM_rd.ifcordinates])
        self.nodescolor = 'black'
        self.addnodesfigure([self.OSM_rd.depotcordinates])
        if self.saveoutput: plt.savefig(self.outputname+self.outputtype,dpi=self.dpisize,bbox_inches='tight')
        if self.displayout: plt.show()
        
    def drawnetworkkeys(self, arcsnodekey):
        actualarcs = []
        for keypair in arcsnodekey: actualarcs.append(self.OSM_rd.arcnodekeys[keypair])
        self.initiatefigure()
        self.fullnetworkcolor = 'grey'
        self.ax.add_patch(self.makefullnetwork())
        self.ax.add_patch(self.makearcnetwork(actualarcs))
        self.nodescolor = 'red'
        self.addnodesfigure([self.OSM_rd.ifcordinates])
        self.nodescolor = 'black'
        self.addnodesfigure([self.OSM_rd.depotcordinates])
        if self.saveoutput: plt.savefig(self.outputname+self.outputtype,dpi=self.dpisize,bbox_inches='tight')        
        if self.displayout: plt.show()
        
    def drawroute(self, reqarcsnodekey, deadarcsnodek):
        
        deadarcs = []
        
        
        for keypair in deadarcsnodek: deadarcs.append(self.OSM_rd.arcnodekeys[keypair])
        
        self.initiatefigure()
        
        self.arcnetwidth = 0.5
        self.fullnetworkcolor = 'grey'
        self.ax.add_patch(self.makefullnetwork())
        
        self.arcnetcolor = 'blue'
        self.arcnetwidth = 1.5
        self.drawreqroute(reqarcsnodekey)
        
        self.arcnetwidth = 1
        self.arcnetcolor = 'black'
        self.ax.add_patch(self.makearcnetwork(deadarcs))
        
        self.nodescolor = 'red'
        self.addnodesfigure([self.OSM_rd.ifcordinates])
        self.nodescolor = 'black'
        self.addnodesfigure([self.OSM_rd.depotcordinates])
        if self.saveoutput: plt.savefig(self.outputname+self.outputtype,dpi=self.dpisize,bbox_inches='tight')
        if self.displayout: plt.show()
    
    def drawreqroute(self, reqarcsnodekey):
        reqarcs = []
        for keypair in reqarcsnodekey: reqarcs.append(self.OSM_rd.arcnodekeys[keypair])
        self.ax.add_patch(self.makearcnetwork(reqarcs))
        
    def drawvehicleroute(self, routereqarcskeys):

        self.initiatefigure()
        
        self.arcnetwidth = 0.25
        self.fullnetworkcolor = 'grey'
        self.ax.add_patch(self.makefullnetwork())
        
        colourlist = ['blue','green','black','orange','blue','green','black','orange','blue','green','black','orange','blue','green','black','orange']
        i = -1
        for tripnodekey in routereqarcskeys:
            i += 1
            self.arcnetwidth = 1
            self.arcnetcolor = colourlist[i]            
            self.drawreqroute(tripnodekey)
        
        self.nodescolor = 'red'
        self.addnodesfigure([self.OSM_rd.ifcordinates])
        self.nodescolor = 'black'
        self.addnodesfigure([self.OSM_rd.depotcordinates])
        if self.saveoutput: plt.savefig(self.outputname+self.outputtype,dpi=self.dpisize, bbox_inches='tight')
        if self.displayout: plt.show()
        
if __name__ == "__main__":
    network = gen_network_graph()
    network.drawfullgraph()
     
     
     
     
     
     
     
     
     
     
     
     
     
     