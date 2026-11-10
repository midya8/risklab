"""Independent path enumeration and bounded-simplex-vertex report replay.

No imports from the generator. Shared schema and rational serialization only.
"""
from fractions import Fraction as F
from itertools import product
from functools import lru_cache
from .schema import compile_problem,pack

@lru_cache(maxsize=4096)
def _envelope(losses,ps,alpha):
    caps=tuple(p/(1-alpha)for p in ps);active=[i for i,p in enumerate(ps)if p];vertices=set()
    # All but at most one positive-support coordinate are at a box bound.
    for free in active:
        bound=[i for i in active if i!=free]
        for bits in product([0,1],repeat=len(bound)):
            q=[F(0)]*len(ps)
            for i,b in zip(bound,bits):q[i]=caps[i]*b
            q[free]=1-sum(q)
            if 0<=q[free]<=caps[free]:vertices.add(tuple(q))
    if not vertices:raise ValueError('empty risk envelope')
    val=max(sum(qi*z for qi,z in zip(q,losses))for q in vertices)
    # Canonical tie among optimal vertices. This is not the tail-fill algorithm.
    order=sorted(range(len(ps)),key=lambda i:(-losses[i],i))
    q=max((q for q in vertices if sum(a*b for a,b in zip(q,losses))==val),key=lambda q:tuple(q[i]for i in order))
    etas=sorted({z for z,p in zip(losses,ps)if p})
    cs=[{'threshold':e,'value':e+sum(p*max(F(0),z-e)for z,p in zip(losses,ps))/(1-alpha)}for e in etas]
    assert min(c['value']for c in cs)==val
    eta=next(c['threshold']for c in cs if c['value']==val)
    return {'value':val,'mean':sum(z*p for z,p in zip(losses,ps)),'weights':list(q),'caps':list(caps),'contributions':[a*b for a,b in zip(q,losses)],'threshold':eta,'excesses':[max(F(0),z-eta)for z in losses],'threshold_candidates':cs,'gap':F(0)}

def reconstruct(problem):
    alpha,ns,ds,ls,count=compile_problem(problem);losses=tuple(ns[l]['loss']for l in ls);policies=[]
    def risk(z,p):return _envelope(tuple(z),tuple(p),alpha)
    for choices in product(*(range(len(ns[d]['children']))for d in ds)):
        chosen=dict(zip(ds,choices));reach=[F(0)]*len(ns)
        def paths(node,mass,record=False):
            if record:reach[node]+=mass
            n=ns[node]
            if n['kind']=='terminal':return [(node,mass)]
            if n['kind']=='decision':return paths(n['children'][chosen[node]],mass,record)
            return [row for c,p in zip(n['children'],n['probabilities'])for row in paths(c,mass*p,record)]
        paths(0,F(1),True)
        laws=[];stat=[]
        for i in range(len(ns)):
            law=dict(paths(i,F(1)));prob=tuple(law.get(l,F(0))for l in ls);laws.append(prob);stat.append(risk(losses,prob)['value'])
        local=[None]*len(ns);nested=[None]*len(ns)
        def nest(i):
            if nested[i]is not None:return nested[i]
            n=ns[i]
            if n['kind']=='terminal':v=n['loss']
            elif n['kind']=='decision':v=nest(n['children'][chosen[i]])
            else:local[i]=risk([nest(c)for c in n['children']],n['probabilities']);v=local[i]['value']
            nested[i]=v;return v
        for i in range(len(ns)):nest(i)
        policies.append({'index':len(policies),'choices':list(choices),'reach':reach,'leaf_probabilities':list(laws[0]),'static':risk(losses,laws[0]),'static_values':stat,'nested_values':nested,'nested_chance_witnesses':local})
    sb=[min(p['static_values'][i]for p in policies)for i in range(len(ns))];nb=[min(p['nested_values'][i]for p in policies)for i in range(len(ns))]
    ties=[[]for _ in ns];ch=[]
    for d in ds:
        vs=[nb[c]for c in ns[d]['children']];ties[d]=[i for i,v in enumerate(vs)if v==min(vs)];ch.append(ties[d][0])
    di=next(p['index']for p in policies if p['choices']==ch)
    assert policies[di]['nested_values']==nb
    for p in policies:
        audit=[{'node':d,'reach':p['reach'][d],'static_regret':p['static_values'][d]-sb[d],'nested_regret':p['nested_values'][d]-nb[d]}for d in ds];p['decision_audit']=audit
        p['static_locally_optimal_on_reached_decisions']=all(a['static_regret']==0 for a in audit if a['reach']>0)
        p['nested_locally_optimal_on_reached_decisions']=all(a['nested_regret']==0 for a in audit if a['reach']>0)
    m=min(p['static']['mean']for p in policies)
    return pack({'version':1,'problem':{'version':1,'alpha':alpha,'nodes':ns},'decision_nodes':ds,'terminal_nodes':ls,'policy_count':count,'policies':policies,'static_optima':[p['index']for p in policies if p['static']['value']==sb[0]],'nested_root_optima':[p['index']for p in policies if p['nested_values'][0]==nb[0]],'mean_optima':[p['index']for p in policies if p['static']['mean']==m],'static_optimal_value':sb[0],'nested_optimal_value':nb[0],'mean_optimal_value':m,'static_subtree_optima':sb,'nested_subtree_optima':nb,'bellman':{'values':nb,'optimal_actions':ties,'choices':ch,'policy_index':di}})

def _same(a,b):
    if type(a)is not type(b):return False
    if type(a)is dict:return a.keys()==b.keys()and all(_same(a[k],b[k])for k in a)
    if type(a)is list:return len(a)==len(b)and all(_same(x,y)for x,y in zip(a,b))
    return a==b

def verify(report):
    try:return type(report)is dict and _same(report,reconstruct(report['problem']))
    except (KeyError,ValueError,TypeError,OverflowError,RecursionError):return False
