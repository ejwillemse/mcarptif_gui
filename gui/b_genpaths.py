'''
Created on 09 Jun 2011

@author: elias
'''
import SPmodules2 as SP

class generate_paths(object):
    
    def __init__(self,info):
        self.info = info
        self.piEst = info.spPreD
        self.servicearcs = []
        self.deadheadarcs = []
        
    def genarclists(self, path):
                
        for arc in path:
            minnode = min(self.info.allIndexD[arc])
            maxnode = max(self.info.allIndexD[arc])
            if minnode != maxnode:self.servicearcs.append((minnode,maxnode))
        
        for i, arc in enumerate(path[0:-1]):
            shortestarcpath = SP.spSource1Listv2(self.piEst, path[i], path[i+1])
            for deadarc in shortestarcpath:
                minnodedead = min(self.info.allIndexD[deadarc])
                maxnodedead = max(self.info.allIndexD[deadarc])
                deadarcnodekey = (minnodedead, maxnodedead)
                if (deadarcnodekey not in self.servicearcs) & (deadarcnodekey not in self.deadheadarcs):
                    self.deadheadarcs.append(deadarcnodekey)
            