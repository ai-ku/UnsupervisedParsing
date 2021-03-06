'''
Created on May 20, 2012

@author: husnusensoy
'''
from nltk.corpus import dependency_treebank
import networkx as nx
from common import print_metrics

"""
    Converts nltk.corpus.dependency_treebank sentences into directed networkx graphs.
"""
def graph(orginal):
    i = 0
    G = nx.DiGraph()
    lbl = {}
    while orginal.contains_address(i):
        w = orginal.get_by_address(i)
        
        G.add_node(i, attr_dict=w)
        lbl[i] = w['word']
        for sink in w['deps']:
            if orginal.contains_address(sink):
                G.add_edge(i, sink)
            
        i+=1
    
    return G

"""
    Remove bad nodes from networkx graph.
"""
def prune(orginal):
    import copy
    pruned = copy.deepcopy(orginal)
    
    for i in pruned.nodes():
        if pruned.node[i]['rel'] in ('P') or pruned.node[i]['word'] in ["A$","C$","$","#",".", ",","?","/","("]:
            pruned.remove_node(i)
            
    return pruned

"""
    After the removal off nodes (prune) there might/will be gaps in enumeration of graph nodes.
    This function renumares all nodes (0..number_of_words)
"""
def renumarate(graph):
    dct = {}
    for i, e in enumerate(graph.nodes()):
        dct[e] = i
        
    #print dct
    
    G = nx.DiGraph()
    
    for i in graph.nodes():
        G.add_node(dct[i], attr_dict=graph.node[i])
        
    for (source,sink) in graph.edges():
        G.add_edge(dct[source], dct[sink])
    
    return G

"""
    This is the dependency graph version of right-branching tree
"""
def forwardDependency(nwords):
    G=nx.DiGraph()
    
    for i in range(nwords):
        G.add_edge(i, i+1)
        
    assert len(G.edges()) == nwords
    return G.edges()

"""
    This is the dependency graph version of left-branching tree
"""
def backwardDependency(nwords):
    G=nx.DiGraph()
    
    for i in range(1,nwords):
        G.add_edge(i+1, i)
    
    G.add_edge(0, nwords)
    
    assert len(G.edges()) == nwords
    return G.edges()

class WSJ10(object):
    """
       Dependency tree structure of WSJ10 corpus
           Try to load from binary pickle format. 
           Fail back to PennTree bank source generated by penncoverter.jar in case of a failure
           
           Generation of dependency graph representation from penn tree bank
               ls  *.mrg | parallel java -jar <full pennconverter.jar path> -f {} -t <dependency_treebank directory>/{.}.dp -splitSlash=false
           Example:
               ls  *.mrg | parallel java -jar /Users/husnusensoy/Downloads/pennconverter.jar -f {} -t /Users/husnusensoy/nltk_data/corpora/dependency_treebank/{.}.dp -splitSlash=false
    """
    def __init__(self, nousepickle):
        def fromRaw():
            for sent in dependency_treebank.parsed_sents():
                
                g = prune(graph(sent))
                
                if g.number_of_nodes()-1 <= 10:
                    yield (g,sent)
            
        import cPickle as pickle
        try:
            if nousepickle:
                self.ldependency = [ s for s in fromRaw ]
            else:
                self.ldependency = pickle.load(open("dependency.p", "rb"))
        except:
            print "No pickle found for dependency corpus."
            self.ldependency = [ s for s in fromRaw() ]
            pickle.dump(self.ldependency, open("dependency.p", "wb"))
            

    """
        Iterator of all dependecy graphs in WSJ10 corpus
    """
    def iterator(self,renum=False):
        
        for g,_ in self.ldependency:
            if renum:
                yield renumarate(g)
            else:
                yield g
    
    """
        Validates dependency graphs by using WSJ10 trees.
    """
    def validate(self):
        import tree
        def compare(s1,s2):
            for w1,w2 in zip(s1,s2):
                if w1 != w2:
                    print s1
                    print s2
            
                    return False
                
            return True
    
        cnt=0
        for dep, tree in zip(self.iterator(),tree.WSJ10(nousepickle=False).tagged()):
            s1 = []
            
            for i in dep.nodes():
                if i != 0:
                    s1.append(dep.node[i]['word'])
                    
            s2 = []
            
            for w in tree:
                s2.append(w[1])
                
            if not compare(s1, s2):
                raise NameError("Corpus broken in %.2f sentences"%(cnt*100./7422))
            
            cnt+=1
            
        print "Dependency corpus is validated"
    
    '''
        Evaluate the parser on WSJ10
        
            parser: parser function
            directed: whether to ignore dependency direction
    '''    
    def evaluate(self,parser=forwardDependency, directed = True):
        noverlap = 0
        nmodel = 0
        ngolden = 0
    
        for dep in self.iterator(renum=True):
            if ( dep.number_of_nodes() - 1 >= 2 ):
                gold = set(dep.edges())
                model = set(parser(dep.number_of_nodes() - 1))
            
            #if len(gold) != len(model):
            #    print gold
            #    print model
            #    print [sent.node[i]['word'] for i in sent.nodes()]
            #    print o
            #print "Gold: ",
            #print gold
            #print "Model: ",
            #print model
                if len(gold) == len(model):
                    if directed:
                        for c in gold:
                            if c in model:
                                noverlap += 1
                    else:
                        for head,sink in gold:
                            if (head,sink) in model or (sink,head) in model:
                                noverlap += 1
                                
                    ngolden += len(gold)
                    nmodel += len(model) 
                
        print_metrics(noverlap, ngolden, nmodel)
        
