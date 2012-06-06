import random
random.random()

from corpus import dependency,tree

tr = tree.WSJ10(nousepickle=False)

"""
    Tests for Tree Models
"""
print "Test left branching parser"
tr.evaluate(parser=tree.leftParse)
print "Test random branching parser"
tr.evaluate(parser=tree.randomTreeParse)
print "Test right branching parser"
tr.evaluate(parser=tree.rightParse)
print "Test upper bound parser"
tr.evaluate(parser=tree.uBoundParse)


dep = dependency.WSJ10(nousepickle=False)
#dep.validate()

"""
    Tests for Dependency Models
"""
print "Test forward dependency parser"
dep.evaluate(dependency.forwardDependency, directed=True)

print "Test forward dependency parser with undirected dependencies"
dep.evaluate(dependency.forwardDependency, directed=False)

print "Test backward dependency parser"
dep.evaluate(dependency.backwardDependency, directed=True)

print "Test backward dependency parser with undirected dependencies"
dep.evaluate(dependency.backwardDependency, directed=False)

# Correct Sentence length Distribution 
#    {1: 159, 2: 340, 3: 377, 4: 518, 5: 614, 6: 737, 7: 878, 8: 1107, 9: 1208, 10: 1484}

# Correct Tag Distribution
# {'PRP$': 412, 'VBG': 735, 'VBD': 2633, 'VBN': 1282, 'VBP': 1361, 'WDT': 66, 'JJ': 3658, 
#    'WP': 145, 'VBZ': 2320, 'DT': 4586, 'RP': 141, 'NN': 7718, 'FW': 22, 'POS': 332, 'TO': 1183, 'PRP': 2000, 'RB': 3071, 
#    'NNS': 3927, 'NNP': 5570, 'VB': 1616, 'WRB': 96, 'CC': 1036, 'LS': 24, 'PDT': 31, 'RBS': 26, 'RBR': 113, 'CD': 3004, 
#    'EX': 120, 'IN': 3720, 'MD': 678, 'NNPS': 192, 'JJS': 106, 'JJR': 228, 'SYM': 51, 'UH': 45}
  
"""
Expected Right Branch Results:
    Sentences: 7422
    Micro-averaged measures:
      Precision: 55.2
      Recall: 70.0
      Harmonic mean F1: 61.7
     
    Brackets ok: 24724 
    Brackets parse: 44826
    Brackets gold: 35302

    Macro-averaged measures:
      Precision: 58.1
      Recall: 72.3
      Harmonic mean F1: 64.4
"""
