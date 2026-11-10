import unittest,copy,json,itertools,subprocess,sys,tempfile,random
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
from risklab import solve
from risklab.checker import verify,reconstruct
from risklab.schema import compile_problem
from risklab.controls import controls,make,terminal,decision,chance
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from cases import cases

class RiskTests(unittest.TestCase):
 def test_all_reports(self):
  n=0
  for p in cases():
   r=solve(p);self.assertTrue(verify(r));self.assertEqual(r,reconstruct(p));n+=1
  self.assertEqual(n,821)
 def test_boundary_atom(self):
  r=solve(controls()['boundary_atom'])['policies'][0]['static'];self.assertEqual(r['value'],[4,1]);self.assertEqual(r['weights'],[[1,2],[1,2]]);self.assertNotEqual(r['value'],[2,1]);self.assertNotEqual(r['value'],[8,1])
 def test_reversal(self):
  r=solve(controls()['reversal']);self.assertEqual(r['static_optima'],[3]);self.assertEqual(r['nested_root_optima'],[2]);self.assertEqual(r['static_optimal_value'],[7,3]);self.assertEqual(r['nested_optimal_value'],[22,9]);self.assertFalse(r['policies'][3]['static_locally_optimal_on_reached_decisions']);self.assertTrue(r['policies'][2]['nested_locally_optimal_on_reached_decisions'])
 def test_root_optimal_not_locally_optimal(self):
  r=solve(controls()['ignored_branch']);self.assertEqual(r['nested_root_optima'],[0,1]);self.assertFalse(r['policies'][0]['nested_locally_optimal_on_reached_decisions']);self.assertEqual(r['bellman']['policy_index'],1);self.assertTrue(r['policies'][1]['nested_locally_optimal_on_reached_decisions'])
 def test_law_dependence(self):
  a,b=(solve(controls()[n])for n in ['grouped_law','flat_law']);self.assertEqual(a['static_optimal_value'],b['static_optimal_value']);self.assertEqual(a['nested_optimal_value'],[16,9]);self.assertEqual(b['nested_optimal_value'],[4,3])
 def test_alpha_zero(self):
  for p in list(cases())[:91]:
   p=copy.deepcopy(p);p['alpha']=0;r=solve(p)
   for row in r['policies']:self.assertEqual(row['static']['mean'],row['static']['value']);self.assertEqual(row['static_values'],row['nested_values'])
 def test_zero_mass(self):
  r=solve(controls()['zero_mass']);self.assertEqual(r['static_optima'],[0,1]);self.assertEqual(r['policies'][0]['reach'][2],[0,1]);self.assertEqual(r['policies'][0]['decision_audit'][0]['static_regret'],[200,1]);self.assertTrue(r['policies'][0]['static_locally_optimal_on_reached_decisions'])
 def test_independent(self):
  with patch('risklab.solver.solve',side_effect=AssertionError),patch('risklab.solver.tail',side_effect=AssertionError):self.assertTrue(verify(reconstruct(controls()['reversal'])))
 def test_mutations(self):
  r=solve(controls()['reversal']);leaves=[]
  def walk(x,p):
   if isinstance(x,dict):
    for k,v in x.items():
     if k!='problem':walk(v,p+[k])
   elif isinstance(x,list):
    for k,v in enumerate(x):walk(v,p+[k])
   elif x is not None:leaves.append(p)
  walk(r,[])
  for path in leaves:
   q=copy.deepcopy(r);at=q
   for k in path[:-1]:at=at[k]
   old=at[path[-1]];at[path[-1]]=not old if type(old)is bool else old+1 if type(old)is int else 'changed';self.assertFalse(verify(q),path)
  print('rejected mutation leaves',len(leaves));self.assertGreater(len(leaves),1000)
 def test_type_forgery(self):
  r=solve(controls()['one_leaf']);r['version']=True;self.assertFalse(verify(r));r=solve(controls()['one_leaf']);r['policies'][0]['index']=False;self.assertFalse(verify(r))
 def test_strict_schema(self):
  base=controls()['boundary_atom']
  for v in [True,0.5,'1/2',[True,2],[1,0],[1,-2],[1000001,2],1,-1]:
   p=copy.deepcopy(base);p['alpha']=v
   with self.assertRaises(ValueError):solve(p)
  for p in [{},dict(base,extra=1),make(0,[decision([1,1]),terminal(0)]),make(0,[decision([1]),terminal(0),terminal(1)]),make(0,[chance([1,2],[1,1]),terminal(1),terminal(2)])]:
   with self.assertRaises(ValueError):solve(p)
 def test_limits(self):
  with self.assertRaises(ValueError):solve(make(0,[terminal(101)]))
  with self.assertRaises(ValueError):solve(make([1,991],[chance([1,2],[[1,997],[996,997]]),terminal([1,983]),terminal(0)]))
  with self.assertRaises(ValueError):solve(make(0,[decision([1]),decision([2]),decision([3]),decision([4]),decision([5]),terminal(1)]))
 def test_large_exact_denominators(self):
  r=solve(controls()['deep_fractions']);self.assertTrue(verify(r));self.assertGreater(max(q[1]for q in r['policies'][0]['reach']),2**53)
 def test_nested_is_not_an_upper_bound(self):
  r=solve(controls()['nested_below_static']);self.assertEqual(r['static_optimal_value'],[23,6]);self.assertEqual(r['nested_optimal_value'],[11,3])
 def test_isolation(self):
  p=controls()['reversal'];q=copy.deepcopy(p);state=random.getstate();r=solve(p);self.assertEqual(p,q);self.assertEqual(state,random.getstate());r['policies'][0]['choices'][0]=999;self.assertNotEqual(r,solve(p))
 def test_cli(self):
  with tempfile.TemporaryDirectory()as d:
   f=Path(d)/'input.json';f.write_text(json.dumps(controls()['reversal']));r=subprocess.run([sys.executable,'-m','risklab','run',str(f)],capture_output=True,text=True);self.assertEqual(r.returncode,0);self.assertTrue(verify(json.loads(r.stdout)));f.write_text(r.stdout);a=subprocess.run([sys.executable,'-m','risklab','verify',str(f)],capture_output=True,text=True);self.assertEqual(a.returncode,0)
   for raw in ['{"version":1,"version":1}','{"x":0.1}','{"x":NaN}','x'*65537]:
    f.write_text(raw);a=subprocess.run([sys.executable,'-m','risklab','run',str(f)],capture_output=True,text=True);self.assertEqual(a.returncode,2);self.assertEqual(a.stdout,'')
