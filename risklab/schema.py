"""Bounded supplied trees and exact, canonical JSON rationals."""
from fractions import Fraction as F
from math import lcm, prod

def pack(x):
    if isinstance(x,F): return [x.numerator,x.denominator]
    if isinstance(x,list): return [pack(v) for v in x]
    if isinstance(x,dict): return {k:pack(v) for k,v in x.items()}
    return x

def exact(x):
    if type(x) is int: a,b=x,1
    elif type(x) is list and len(x)==2 and all(type(v)is int for v in x): a,b=x
    else: raise ValueError('rational must be an integer or integer pair')
    if abs(a)>1000000 or not 1<=b<=1000000: raise ValueError('rational components exceed limits')
    return F(a,b)

def keys(x,want):
    if type(x)is not dict or set(x)!=set(want): raise ValueError('unknown or missing keys')

def compile_problem(p):
    keys(p,['version','alpha','nodes'])
    if type(p['version'])is not int or p['version']!=1: raise ValueError('version must be 1')
    alpha=exact(p['alpha'])
    if not 0<=alpha<1: raise ValueError('confidence alpha must be in [0,1)')
    ns=p['nodes']
    if type(ns)is not list or not 1<=len(ns)<=15: raise ValueError('need 1..15 nodes')
    nodes=[]; parents=[0]*len(ns);depth=[0]*len(ns);den=[alpha.denominator];dec=[];leaves=[]
    for i,n in enumerate(ns):
        if type(n)is not dict: raise ValueError('node must be object')
        kind=n.get('kind')
        if kind=='terminal':
            keys(n,['kind','loss']);z=exact(n['loss'])
            if abs(z)>100: raise ValueError('absolute loss exceeds 100')
            den.append(z.denominator);nodes.append({'kind':kind,'loss':z});leaves.append(i);continue
        if kind not in ['chance','decision']: raise ValueError('invalid node kind')
        keys(n,['kind','children','probabilities']if kind=='chance'else['kind','children'])
        cs=n['children']
        if type(cs)is not list or not 1<=len(cs)<=3 or any(type(c)is not int or not i<c<len(ns)for c in cs)or len(set(cs))!=len(cs): raise ValueError('children must be 1..3 distinct increasing node IDs')
        for c in cs: parents[c]+=1;depth[c]=max(depth[c],depth[i]+1)
        out={'kind':kind,'children':cs.copy()}
        if kind=='chance':
            ps=n['probabilities']
            if type(ps)is not list or len(ps)!=len(cs):raise ValueError('probability shape')
            ps=list(map(exact,ps))
            if any(v<0 for v in ps)or sum(ps)!=1: raise ValueError('probability simplex')
            den.extend(v.denominator for v in ps);out['probabilities']=ps
        else:dec.append(i)
        nodes.append(out)
    count=prod(len(nodes[i]['children'])for i in dec)
    if parents[0]or any(x!=1 for x in parents[1:]):raise ValueError('must be one rooted tree, no shared or disconnected nodes')
    if max(depth)>6 or len(dec)>4 or len(leaves)>8 or count>64:raise ValueError('tree resource limit')
    if lcm(*den)>1000000:raise ValueError('combined denominator LCM exceeds 1000000')
    return alpha,nodes,dec,leaves,count
