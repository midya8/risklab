"""Original supplied controls. Losses, never financial advice or trained policies."""
from copy import deepcopy

def terminal(z):return {'kind':'terminal','loss':z}
def decision(cs):return {'kind':'decision','children':cs}
def chance(cs,ps):return {'kind':'chance','children':cs,'probabilities':ps}
def make(alpha,nodes):return {'version':1,'alpha':alpha,'nodes':nodes}
def controls():
    # 3/4 chance of no loss; CVaR at confidence 1/2 uses only part of zero atom.
    boundary=make([1,2],[chance([1,2],[[3,4],[1,4]]),terminal(0),terminal(8)])
    # Positive-mass low-loss branch is ignored by root tail: bad local choices can tie.
    ignored=make([1,2],[chance([1,2],[[1,2],[1,2]]),decision([3,4]),terminal(10),terminal(2),terminal(1)])
    # The same terminal distribution grouped differently changes nested risk.
    grouped=make([1,4],[chance([1,2],[[1,2],[1,2]]),chance([3,4],[[1,2],[1,2]]),chance([5,6],[[1,2],[1,2]]),terminal(0),terminal(0),terminal(0),terminal(4)])
    flat=make([1,4],[chance([1,2],[[3,4],[1,4]]),terminal(0),terminal(4)])
    zero=make([1,2],[chance([1,2],[1,0]),terminal(-2),decision([3,4]),terminal(100),terminal(-100)])
    dense=make([1,2],[decision([1,2,3]),decision([4,5,6]),decision([7,8,9]),decision([10,11])]+[terminal(z)for z in [1,1,2,0,2,2,3,0]])
    deep=[]
    for i in range(6):deep.extend([chance([2*i+1,2*i+2],[[996,997],[1,997]]),terminal(i)])
    deep.append(terminal(7))
    return {'nested_below_static':{'version': 1, 'alpha': [1, 4], 'nodes': [{'kind': 'chance', 'children': [1, 2], 'probabilities': [[3, 4], [1, 4]]}, {'kind': 'chance', 'children': [3, 4], 'probabilities': [[1, 2], [1, 2]]}, {'kind': 'chance', 'children': [5, 6], 'probabilities': [[3, 4], [1, 4]]}, {'kind': 'terminal', 'loss': 3}, {'kind': 'terminal', 'loss': 4}, {'kind': 'terminal', 'loss': -3}, {'kind': 'terminal', 'loss': 7}]},'dense_policies':dense,'deep_fractions':make([1,997],deep),'reversal':{'version': 1, 'alpha': [1, 4], 'nodes': [{'kind': 'chance', 'children': [1, 2], 'probabilities': [[3, 4], [1, 4]]}, {'kind': 'decision', 'children': [3, 4]}, {'kind': 'decision', 'children': [5, 6]}, {'kind': 'chance', 'children': [7, 8], 'probabilities': [[1, 4], [3, 4]]}, {'kind': 'chance', 'children': [9, 10], 'probabilities': [[1, 4], [3, 4]]}, {'kind': 'chance', 'children': [11, 12], 'probabilities': [[1, 2], [1, 2]]}, {'kind': 'chance', 'children': [13, 14], 'probabilities': [[1, 4], [3, 4]]}, {'kind': 'terminal', 'loss': 2}, {'kind': 'terminal', 'loss': -2}, {'kind': 'terminal', 'loss': 3}, {'kind': 'terminal', 'loss': -3}, {'kind': 'terminal', 'loss': 10}, {'kind': 'terminal', 'loss': 8}, {'kind': 'terminal', 'loss': 4}, {'kind': 'terminal', 'loss': 10}]},'boundary_atom':boundary,'ignored_branch':ignored,'grouped_law':grouped,'flat_law':flat,'zero_mass':zero,'expectation':make(0,deepcopy(ignored['nodes'])),'one_leaf':make([9,10],[terminal(-3)]),'decision_tie':make([1,3],[decision([1,2]),terminal(1),terminal(1)])}
