"""Deterministic development checks; never held-out empirical evaluation."""
import random,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from risklab.controls import make,chance,decision,terminal,controls

def cases():
    yield from controls().values()
    rng=random.Random(73117)
    for _ in range(80):
        alpha=rng.choice([0,[1,4],[1,2],[3,4],[9,10]])
        ps=lambda:rng.choice([[0,1],[1,0],[[1,4],[3,4]],[[1,2],[1,2]],[[3,4],[1,4]]])
        ns=[chance([1,2],ps()),decision([3,4]),decision([5,6])]+[chance([7+2*j,8+2*j],ps())for j in range(4)]+[terminal(rng.randrange(-10,21))for _ in range(8)]
        yield make(alpha,ns)
    # Complete 3^4 loss grid with 3 confidences and 3 first-branch laws.
    import itertools
    for zs in itertools.product([-1,0,2],repeat=4):
        for alpha in [0,[1,2],[3,4]]:
            for ps in [[[1,4],[3,4]],[[1,2],[1,2]],[[3,4],[1,4]]]:
                yield make(alpha,[chance([1,2],ps),chance([3,4],[[1,2],[1,2]]),chance([5,6],[[1,2],[1,2]])]+list(map(terminal,zs)))
