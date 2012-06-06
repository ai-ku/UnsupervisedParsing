'''
Created on May 5, 2012

@author: husnusensoy
'''
from sets import Set
class Metric(object):
    def __init__(self, actual, predicted):
        self.actualSet = actual
        self.predictedSet = predicted
        
    def recall(self):
        return (len (self.actualSet & self.predictedSet), len(self.predictedSet))
    
    def precision(self):
        return (len (self.actualSet & self.predictedSet), len(self.actualSet))
    
    def evaluation(self):
        return [len (self.actualSet & self.predictedSet), len(self.actualSet),len(self.predictedSet)]
    
    def report(self):
        r = self.recall()
        print "Recall : (%d,%d) (%f)"%(r[0],r[1],r[0]*1.0/r[1])
        r = self.precision()
        print "Precision : (%d,%d) (%f)"%(r[0],r[1],r[0]*1.0/r[1])
        
