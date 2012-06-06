'''
Created on May 6, 2012

@author: husnusensoy
'''
import random
import nltk
from util import memoized
from Evaluate import Metric
from common import print_metrics

badtokens = [".", ",", "``", "''", ":", "$", "-NONE-", "-RRB-", "-LRB-","#"]
word_tags = ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'NN', 'NNS', 'NNP', 'NNPS', 'PDT', 
             'POS', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'RP', 'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 
             'VBZ', 'WDT', 'WP', 'WP$', 'WRB']
currency_tags_words = ['#', '$', 'C$', 'A$']
ellipsis = ['*', '*?*', '0', '*T*', '*ICH*', '*U*', '*RNR*', '*EXP*', '*PPA*', '*NOT*']
punctuation_tags = ['.', ',', ':', '-LRB-', '-RRB-', '\'\'', '``']
punctuation_words = ['.', ',', ':', '-LRB-', '-RRB-', '\'\'', '``', '--', ';', '-', '?', '!', '...', '-LCB-', '-RCB-']

"""
    Checks for terminal node.
"""
def isterminal(tree):
    return not isinstance(tree, nltk.Tree)

"""
    Checks for parent of terminal non-terminal node.
"""
def ispreterminal(tree):
    return False  in [isinstance(c, nltk.Tree) for c in tree]

"""
    Remove bad tokens in given sentences gold tree
"""
def nopunct(sent):
    return nltk.Tree(sent.node, [nopunct(c) for c in sent if c.node not in badtokens ]) if not ispreterminal(sent) else sent
    
def noemptysubtree(sent):
    if ispreterminal(sent):
        return sent
    else:
        return nltk.Tree(sent.node, [noemptysubtree(c) for c in sent if len(c) > 0 ]) 
    
"""
    Extract (word,tag) from sentences parse tree.
"""
def tagit(sent):
    def _tagit(sent, words):
        if isinstance(sent,nltk.Tree):
            if ispreterminal(sent):
                words.append( (sent.node, sent[0]))
            else:
                return [_tagit(s,words) for s in sent]
        
    words = []
    
    _tagit(sent,words)
    
    return words

"""
    Right growing parse tree
"""
def rightParse(sent):
    if len(sent) > 0:
        if len(sent) >= 2:
            return nltk.Tree('S', [nltk.Tree(sent[0][1], [sent[0][0]]),
                                   rightParse(sent[1:])])
        else:
            return nltk.Tree(sent[0][1], [sent[0][0]])
"""
    Left growing parse tree
"""
def leftParse(sent):
    if len(sent) > 0:
        if len(sent) >= 2:
            return nltk.Tree('S', [leftParse(sent[:-1]), nltk.Tree(sent[-1][1], [sent[-1][0]])])
        else:
            return nltk.Tree(sent[0][1], [sent[0][0]])
"""
    Upper Bound for binary parsing
"""        
def uBoundParse(sent):
    return len(sent.leaves()) - 2
        
def randomDecisionParse(sent):
    if len(sent) > 0:
        if len(sent) >= 2:
            if random.random() <= 0.5:
                return nltk.Tree('S', [randomDecisionParse(sent[:-1]), nltk.Tree(sent[-1][1], [sent[-1][0]])])
            else:
                return nltk.Tree('S', [nltk.Tree(sent[0][1], [sent[0][0]]),
                                   randomDecisionParse(sent[1:])])
        else:
            return nltk.Tree(sent[0][1], [sent[0][0]])


"""
    All binary bracketings for n word sentences.
"""
def _binary_bracketings(n):
    def add(B, x):
        return map(lambda s: map(lambda (a,b): (a+x,b+x), s), B)
    
    if n == 1:
        return [[]]
    elif n == 2:
        return [[(0,2)]]
    else:
        b = {}
        for i in range(1, n):
            b[i] = _binary_bracketings(i)
        B = []
        for i in range(1, n):
            # todas las combinaciones posibles de b[i] y add(b[n-i], i):
            b1 = b[i]
            b2 = add(b[n-i], i)
            for j in range(len(b1)):
                for k in range(len(b2)):
                    B = B + [[(0,n)] + b1[j] + b2[k]]
        
        return B
    
"""
    Randomly pick one of binary bracketings
"""
@memoized     
def randomTreeParse(length):
    possiblebracketings =  _binary_bracketings( length )
    
    return random.choice(possiblebracketings)

def spannings(tree, leaves=True, root=True, unary=True):
    """Returns the set of unlabeled spannings.
    """
    queue = tree.treepositions()
    stack = [(queue.pop(0), 0)]
    j = 0
    result = set()
    while stack != []:
        (p, i) = stack[-1]
        if queue == [] or queue[0][:-1] != p:

            if isinstance(tree[p], nltk.Tree):
                result.add((i, j))
            else:

                if leaves:
                    result.add((i, i + 1))
                j = i + 1
            stack.pop()
        else:
            q = queue.pop(0)
            stack.append((q, j))
    if not root:
        result.remove((0, len(tree.leaves())))
    if not unary:
        result = set(filter(lambda (x, y): x != y - 1, result))
    
    return result

class WSJ10(object):
    '''
    Corpus defined in Klein 2004
    Sentences of Length <= 10 after the removal of bad tokens (punctuation and PennTree specific things.)
    '''
            
    def __init__(self,nousepickle=False):
        """
            Parsed Sentences
                Try to load from binary pickle format. 
                Fail back to PennTree bank source in case of a failure
        """
        import cPickle as pickle
        try:
            if nousepickle:
                self.lparsed = [ s for s in  [noemptysubtree(nopunct(tree)) for tree in nltk.corpus.treebank.parsed_sents()] if len(s.leaves()) <= 10 ]
            else:
                self.lparsed = pickle.load(open("parsed.p", "rb"))
        except:
            print "No pickle found for tree corpus."
            self.lparsed = [ s for s in  [noemptysubtree(nopunct(tree)) for tree in nltk.corpus.treebank.parsed_sents()] if len(s.leaves()) <= 10 ]
            pickle.dump(self.lparsed, open("parsed.p", "wb"))
        

        self.ltagged = [tagit(sent) for sent in self.lparsed]
        
        print "Size of WSJ10 parsed corpus %d" % (len(self.lparsed))
        
                
    """
        Simple frequency analysis of sentences in WSJ10
    """
    def analyze(self, wordcount=True, tagcount=True):
        from pprint import pprint
        """
            Length distribution of sentences
        """
        def _nwords():
            dict = {}
            for tagged in self.ltagged:
                if len(tagged) in dict:
                    dict[len(tagged)] += 1
                else:
                    dict[len(tagged)] = 1
                
            pprint( dict )
        
        """
            Tag distributions
        """
        def _ntags():
            dict = {}
            for sent in self.ltagged:
                for tag,_ in sent:
                    if tag in dict:
                        dict[tag] += 1
                    else:
                        dict[tag] = 1
                
            pprint( dict )
        
        if wordcount:
            _nwords()
            
        if tagcount:
            _ntags()
                
    def tagged(self):
        return self.ltagged
    
    def parsed(self):
        return self.lparsed
    
    def size(self):
        return len(self.ltagged)
    
    """
        In comparing bracketings include sentence boundaries but not the single word constituents
        TODO: Verify from Klein's paper...
    """
    def evaluate(self, parser=rightParse):
        noverlap = 0
        nmodel = 0
        ngolden = 0
        
        for parsed, tagged in zip(self.parsed(), self.tagged()):
            if (len(tagged) >= 2):
                golden = spannings(parsed, unary=False, root=True)
                
                if parser != uBoundParse:
                    
                    if parser != randomTreeParse:
                        model = spannings(parser(tagged), unary=False, root=True)
                    else:
                        model = set(parser(len(tagged)))
            
                    m = Metric(golden, model)
                    e = m.evaluation()
                    
                else:
                    e = [ len(golden), len(golden), len(tagged) - 1 ]
                    
                noverlap += e[0]
                ngolden += e[1]
                nmodel += e[2]        
            else:
                if len(parsed.leaves()) != len(tagged):
                    print tagged, "doesn't match."
                    
        print_metrics(noverlap, ngolden, nmodel)
    
    