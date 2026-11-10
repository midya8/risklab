"""Development-only seeded search; selected controls are not held-out evidence."""
import random,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from risklab import solve
from risklab.controls import make,chance,decision,terminal
rng=random.Random(17021);found={}
for attempt in range(5000):
 a=rng.choice([[1,4],[1,2],[3,4]]);p=rng.choice([[1,4],[1,2],[3,4]]);pp=[p,[p[1]-p[0],p[1]]]
 weights=[rng.choice([[[1,4],[3,4]],[[1,2],[1,2]],[[3,4],[1,4]]])for _ in range(4)]
 zs=[rng.randrange(-4,17)for _ in range(8)]
 nodes=[chance([1,2],pp),decision([3,4]),decision([5,6])]+[chance([7+2*j,8+2*j],weights[j])for j in range(4)]+list(map(terminal,zs))
 prob=make(a,nodes);r=solve(prob);s=r['static_optima'];n=r['nested_root_optima']
 if 'reversal'not in found and len(s)==1 and len(n)==1 and s!=n and not r['policies'][s[0]]['static_locally_optimal_on_reached_decisions']:
  found['reversal']=prob;print('reversal at',attempt,s,n,r['static_optimal_value'],r['nested_optimal_value'],zs,file=sys.stderr)
 if len(found):break
Path('/tmp/risklab/examples/reversal.json').write_text(json.dumps(found['reversal'],indent=2)+'\n')
