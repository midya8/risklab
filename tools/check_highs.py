"""Independent real SciPy LP references; not a scale or timing benchmark."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import scipy
from scipy.optimize import linprog
from fractions import Fraction as F
from risklab import solve
from cases import cases
solves=0;worst=0.;reports=0
for problem in cases():
 r=solve(problem);alpha=float(F(*r['problem']['alpha']));reports+=1
 for row in r['policies']:
  checks=[([F(*r['problem']['nodes'][i]['loss'])for i in r['terminal_nodes']],[F(*q)for q in row['leaf_probabilities']],row['static']['value'])]
  for i,w in enumerate(row['nested_chance_witnesses']):
   if w is not None:
    n=r['problem']['nodes'][i];checks.append(([F(*row['nested_values'][c])for c in n['children']],[F(*p)for p in n['probabilities']],w['value']))
  for zs,ps,v in checks:
   z=list(map(float,zs));p=list(map(float,ps));n=len(z)
   primal=linprog([1]+[pi/(1-alpha)for pi in p],A_ub=[[-1]+[-1 if j==i else 0 for j in range(n)]for i in range(n)],b_ub=[-zi for zi in z],bounds=[(None,None)]+[(0,None)]*n,method='highs')
   dual=linprog([-zi for zi in z],A_eq=[[1]*n],b_eq=[1],bounds=[(0,pi/(1-alpha))for pi in p],method='highs')
   assert primal.success and dual.success
   exact=float(F(*v));error=max(abs(primal.fun-exact),abs(-dual.fun-exact));worst=max(worst,error);assert error<1e-8,(error,z,p)
   assert abs(sum(dual.x)-1)<1e-8 and all(-1e-8<=q<=pi/(1-alpha)+1e-8 for q,pi in zip(dual.x,p))
   solves+=2
print(json.dumps({'reports':reports,'lp_solves':solves,'scipy':scipy.__version__,'worst_absolute_error':worst}))
