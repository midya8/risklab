"""Build and reproduce outside the checkout, with two real CLI entrypoints."""
import json,os,subprocess,sys,tempfile,venv
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from risklab import solve
from risklab.controls import controls
expected={k:solve(p)for k,p in controls().items()}
def run(args,**kw):
 p=subprocess.run(args,capture_output=True,text=True,**kw)
 if p.returncode:raise RuntimeError(str(args)+'\n'+p.stdout+'\n'+p.stderr)
 return p
with tempfile.TemporaryDirectory(prefix='risklab-installed-')as tmp:
 d=Path(tmp);wheel=d/'wheel';wheel.mkdir();run([sys.executable,'-m','pip','wheel','--no-deps','--no-build-isolation',str(root),'-w',str(wheel)],cwd=d)
 venv.EnvBuilder(with_pip=True).create(d/'venv');py=d/'venv/bin/python';entry=d/'venv/bin/risklab';whl=next(wheel.glob('*.whl'));run([str(py),'-m','pip','install','--no-deps','--force-reinstall',str(whl)],cwd=d)
 env=os.environ.copy();env.pop('PYTHONPATH',None)
 code='import json,pathlib,risklab,risklab.solver,risklab.schema,risklab.checker,risklab.controls,risklab.cli;ms=[risklab,risklab.solver,risklab.schema,risklab.checker,risklab.controls,risklab.cli];assert all("site-packages" in m.__file__ for m in ms);print(len(ms))'
 origins=int(run([str(py),'-c',code],cwd=d,env=env).stdout)
 direct=cli=0
 for name,p in controls().items():
  src=d/'input.json';src.write_text(json.dumps(p));report=d/'report.json'
  for cmd in [[str(entry)],[str(py),'-m','risklab']]:
   raw=run(cmd+['run',str(src)],cwd=d,env=env).stdout;r=json.loads(raw);assert r==expected[name];report.write_text(raw);assert json.loads(run(cmd+['verify',str(report)],cwd=d,env=env).stdout)=={'verified':True}
  for mode in ['count','root']:
   r=json.loads(json.dumps(expected[name]));r['policy_count']+=1 if mode=='count'else 0
   if mode=='root':r['static_optimal_value'][0]+=1
   report.write_text(json.dumps(r));x=run([str(py),'-c','import sys,json;from risklab.checker import verify;assert not verify(json.load(open(sys.argv[1])))',str(report)],cwd=d,env=env);direct+=1
   for cmd in [[str(entry)],[str(py),'-m','risklab']]:
    out=subprocess.run(cmd+['verify',str(report)],cwd=d,env=env,capture_output=True,text=True);assert out.returncode==2 and out.stdout=='';cli+=1
 demo=json.loads(run([str(entry),'demo'],cwd=d,env=env).stdout);assert demo==expected['reversal']
 print(json.dumps({'wheel':whl.name,'module_origins':origins,'controls':len(expected),'entrypoints':2,'direct_forgery_rejections':direct,'cli_forgery_rejections':cli}))
