"""Exact tail filling and backward nested conditional-risk planning."""
from fractions import Fraction as F
from itertools import product
from .schema import compile_problem,pack

def tail(losses,probabilities,alpha):
    """Split the boundary atom; do not condition on loss >= VaR."""
    cap=[p/(1-alpha)for p in probabilities];q=[F(0)]*len(cap);remaining=F(1)
    order=sorted(range(len(cap)),key=lambda i:(-losses[i],i))
    for i in order:q[i]=min(cap[i],remaining);remaining-=q[i]
    assert remaining==0
    value=sum(qi*z for qi,z in zip(q,losses))
    candidates=[]
    for eta in sorted(set(z for z,p in zip(losses,probabilities)if p)):
        excess=[max(F(0),z-eta)for z in losses]
        candidates.append({'threshold':eta,'value':eta+sum(p*e for p,e in zip(probabilities,excess))/(1-alpha)})
    eta=next(c['threshold']for c in candidates if c['value']==value)
    return {'value':value,'mean':sum(p*z for p,z in zip(probabilities,losses)), 'weights':q,'caps':cap,'contributions':[q[i]*losses[i]for i in range(len(q))], 'threshold':eta,'excesses':[max(F(0),z-eta)for z in losses], 'threshold_candidates':candidates,'gap':F(0)}

def solve(problem):
    alpha,ns,ds,leaves,count=compile_problem(problem);dpos={d:i for i,d in enumerate(ds)}
    policies=[]
    for index,choices in enumerate(product(*(range(len(ns[d]['children']))for d in ds))):
        laws=[None]*len(ns);static=[None]*len(ns);nested=[None]*len(ns);local=[None]*len(ns)
        for i in reversed(range(len(ns))):
            n=ns[i]
            if n['kind']=='terminal':laws[i]={i:F(1)};nested[i]=n['loss']
            elif n['kind']=='decision':
                c=n['children'][choices[dpos[i]]];laws[i]=laws[c].copy();nested[i]=nested[c]
            else:
                laws[i]={l:sum((p*laws[c].get(l,F(0))for c,p in zip(n['children'],n['probabilities'])),F(0))for l in leaves}
                local[i]=tail([nested[c]for c in n['children']],n['probabilities'],alpha);nested[i]=local[i]['value']
            static[i]=tail([ns[l]['loss']for l in leaves],[laws[i].get(l,F(0))for l in leaves],alpha)['value']
        reach=[F(0)]*len(ns);reach[0]=F(1)
        for i,n in enumerate(ns):
            if n['kind']=='decision':reach[n['children'][choices[dpos[i]]]]=reach[i]
            elif n['kind']=='chance':
                for c,p in zip(n['children'],n['probabilities']):reach[c]=reach[i]*p
        probabilities=[laws[0].get(l,F(0))for l in leaves]
        policies.append({'index':index,'choices':list(choices),'reach':reach,'leaf_probabilities':probabilities,'static':tail([ns[l]['loss']for l in leaves],probabilities,alpha),'static_values':static,'nested_values':nested,'nested_chance_witnesses':local})
    dp=[None]*len(ns);ties=[[]for _ in ns];choices=[0]*len(ds)
    for i in reversed(range(len(ns))):
        n=ns[i]
        if n['kind']=='terminal':dp[i]=n['loss']
        elif n['kind']=='chance':dp[i]=tail([dp[c]for c in n['children']],n['probabilities'],alpha)['value']
        else:
            vs=[dp[c]for c in n['children']];dp[i]=min(vs);ties[i]=[a for a,v in enumerate(vs)if v==dp[i]];choices[dpos[i]]=ties[i][0]
    dp_index=next(p['index']for p in policies if p['choices']==choices)
    static_best=[min(p['static_values'][i]for p in policies)for i in range(len(ns))]
    nested_best=[min(p['nested_values'][i]for p in policies)for i in range(len(ns))]
    for p in policies:
        p['decision_audit']=[{'node':d,'reach':p['reach'][d],'static_regret':p['static_values'][d]-static_best[d],'nested_regret':p['nested_values'][d]-nested_best[d]}for d in ds]
        p['static_locally_optimal_on_reached_decisions']=all(a['static_regret']==0 for a in p['decision_audit']if a['reach'])
        p['nested_locally_optimal_on_reached_decisions']=all(a['nested_regret']==0 for a in p['decision_audit']if a['reach'])
    s=min(p['static']['value']for p in policies);v=min(p['nested_values'][0]for p in policies);m=min(p['static']['mean']for p in policies)
    assert dp[0]==v and dp==nested_best
    return pack({'version':1,'problem':{'version':1,'alpha':alpha,'nodes':ns},'decision_nodes':ds,'terminal_nodes':leaves,'policy_count':count,'policies':policies,'static_optima':[p['index']for p in policies if p['static']['value']==s],'nested_root_optima':[p['index']for p in policies if p['nested_values'][0]==v],'mean_optima':[p['index']for p in policies if p['static']['mean']==m],'static_optimal_value':s,'nested_optimal_value':v,'mean_optimal_value':m,'static_subtree_optima':static_best,'nested_subtree_optima':nested_best,'bellman':{'values':dp,'optimal_actions':ties,'choices':choices,'policy_index':dp_index}})
