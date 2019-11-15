'''
Created on 26 Jul 2010

@author: EWillemse
'''
import LancommeARPconversions3 as LARP

def readFile(InputFile):
    info = LARP.ReadProblemDataIFs(InputFile)
    return(info)