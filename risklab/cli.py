"""Atomic, strict local JSON CLI."""
import argparse,json,sys
from pathlib import Path
from .solver import solve
from .checker import verify
from .controls import controls

def no_float(_):raise ValueError('only integer JSON numbers are allowed')
def pairs(xs):
    d={}
    for k,v in xs:
        if k in d:raise ValueError('duplicate object key')
        d[k]=v
    return d

def load(path,limit):
    raw=Path(path).read_bytes()
    if len(raw)>limit:raise ValueError('JSON file exceeds byte cap')
    return json.loads(raw,object_pairs_hook=pairs,parse_float=no_float,parse_constant=no_float)

def main(argv=None):
    p=argparse.ArgumentParser(prog='risklab');sub=p.add_subparsers(dest='mode',required=True)
    for name in ['run','verify']:sub.add_parser(name).add_argument('path')
    sub.add_parser('demo');a=p.parse_args(argv)
    try:
        if a.mode=='verify':
            if not verify(load(a.path,8*1024*1024)):raise ValueError('invalid report')
            result={'verified':True}
        else:result=solve(controls()['reversal']if a.mode=='demo'else load(a.path,65536))
        print(json.dumps(result,separators=(',',':'),allow_nan=False))
    except (ValueError,TypeError,OSError,RecursionError)as e:
        print('risklab: '+str(e),file=sys.stderr);return 2
    return 0
