# RiskLab

RiskLab compares static CVaR and nested conditional CVaR on a supplied finite
scenario tree. It enumerates every full deterministic policy on that tree and shows terminal
probabilities, tail weights and independently replayable certificates. The two
objectives can select different policies.

Python 3.10+, no runtime dependencies, with a separate BigInt browser inspector.

## Static and nested policy choices

The original `reversal` control has confidence alpha `1/4`. A first observation reaches two decisions with probabilities `3/4` and `1/4`. Each decision chooses between two small loss lotteries. Enumerating all four policies gives:

| Policy choices at nodes 1, 2 | Expected loss | Static CVaR | Nested CVaR |
|---|---:|---:|---:|
| p0: [0, 0] | 3/2 | 8/3 | 8/3 |
| p1: [0, 1] | 11/8 | 5/2 | 26/9 |
| p2: [1, 0] | 9/8 | 5/2 | **22/9** |
| p3: [1, 1] | **1** | **7/3** | 8/3 |

Lower loss is better. The unique static optimum p3 is not the nested optimum p2. At the second reached decision, p3's conditional static CVaR is 10, while the best continuation has 28/3: after seeing that observation, a decision maker reusing the same conditional objective would change the plan. This is a difference between objectives and information timing, not an optimization failure or a risk estimate with better calibration.

This example was selected at candidate 15 (zero-based) by the disclosed seed-17021 development search in `tools/find_controls.py`, not drawn from a held-out evaluation set. All twelve controls are supplied teaching problems.

## A root-optimal policy can still have a worse continuation

The `ignored_branch` tree reaches a decision on a low-loss branch with probability 1/2 and a loss-10 branch with probability 1/2. At confidence 1/2, the root tail ignores the low-loss branch. Both complete policies have nested root value 10, even though one chooses loss 2 where loss 1 is available. The full root-optimal tie set contains both. Backward Bellman selection chooses the locally optimal continuation.

Nested CVaR is not strictly monotone. RiskLab does **not** claim that every nested-root-optimal policy has optimal continuations. It separately exposes the root-optimal set, a first-index Bellman-selected policy and reached-decision continuation regrets. Off-path choices remain distinct full policies, and zero nominal reach does not invent a conditional posterior.

## Static and nested tail calculations

At confidence alpha, `1-alpha` is the upper loss-tail probability. For a finite loss law:

```text
CVaR_alpha(loss) = min_eta eta + sum_i p_i max(loss_i-eta, 0)/(1-alpha)
                = max_q sum_i q_i loss_i
                  subject to sum_i q_i=1 and 0<=q_i<=p_i/(1-alpha)
```

The tail may use only part of an atom. With loss 0 at probability 3/4 and loss 8 at probability 1/4, confidence 1/2 gives CVaR 4. Neither conditioning on loss >= VaR (mean 2) nor loss > VaR (mean 8) gives the right answer. The certificate includes exact tail weights, upper caps, loss contributions, a threshold witness, positive excesses and every supported-loss threshold candidate.

Static CVaR evaluates the final leaf law once. Nested CVaR recursively evaluates the conditional risk of child continuation values. Two controls have the same final loss law but static value 4/3 and nested values 4/3 versus 16/9. A separate control has static CVaR 23/6 and nested value 11/3. Nested risk is not a universal upper bound on static risk. At alpha zero both objectives reduce to expected loss.

## Reproduce locally

```sh
python -m risklab demo
python -m risklab run examples/reversal.json > report.json
python -m risklab verify report.json
python -m pip install .
risklab demo
python -m unittest discover -s tests -v
node --test --test-concurrency=1 tests/test_engine.cjs tests/test_browser.cjs
python tools/check_installed.py
# Optional external numerical reference only:
python tools/check_highs.py
# Serve docs/ with any static server for the browser inspector.
```

[Browser inspector](https://midya8.github.io/risklab/) · [Derivation, contract and source ledger](METHOD.md)

The browser lets you edit the complete exact input, select every full policy, inspect all leaf/node/continuation rows and nested chance-node certificates, and download the full report for native replay. Editing invalidates the old report and disables download until a successful run. All calculations stay local. No API, network model, paid service, private data or dataset is used.

## Verification

- 16 Python tests. Tail-fill generation is checked by a separate path-enumeration and bounded-simplex-vertex checker, with no generator imports. The checker rejects 1,608 separately altered non-input primitive leaves in the reversal report, including hidden fields, and uses strict types rather than Python's boolean/integer equality.
- 821 complete Python/checker/BigInt report comparisons, serialized losslessly, covering twelve controls, 80 seeded trees and all 729 combinations of a declared four-leaf loss/confidence/branch-law grid. This covers 1,121 full policies. A six-level control has denominators beyond `2**53`; ordinary `JSON.parse` is not used to validate those exact integers.
- The optional SciPy 1.15.3 HiGHS reference executes 9,896 primal/dual LP solves across all 821 problems, checking every policy's root risk and every nested chance certificate. Worst absolute objective error is below `1.8e-15`, compared with a `1e-8` tolerance. This is a small reference check, not a speed or scale benchmark. Production has no SciPy dependency.
- The installed-wheel check builds a wheel and runs outside the checkout. It checks six module origins in `site-packages`, all twelve controls through both console and module entrypoints, and 24 direct plus 48 CLI forgery rejections outside the checkout.
- Actual Chrome checks 36 control/width reports at 1280, 390 and 320 pixels, 216 policy selections, 1,518 leaf rows, 2,334 node rows, 696 continuation rows, 120 nested chance proofs and twelve trusted completed downloads checked by the native verifier. The browser tests cover scrolled table states and invalid-input clearing. These checks cover the declared controls and widths, not every input or device.

## Input scope and limits

Input is exactly `version`, `alpha` and `nodes`. Nodes are terminal losses, chance nodes or decision nodes. Node 0 is the root. Every other node has exactly one structural parent, and children have later IDs. No shared subtrees or cycles. Each nonterminal has one to three children. Chance probabilities sum exactly to one; zero edges remain visible. One confidence alpha in `[0,1)` applies at every chance node. Terminal losses only, no intermediate costs, discount, hidden state, learning or ambiguous probability model.

Bounds: 15 nodes, eight terminal leaves, four decision nodes, depth six and 64 full deterministic policies. Loss magnitude <=100. Rationals are exact non-boolean integers or integer pairs, raw components bounded by 1,000,000, positive denominators and combined normalized input-denominator LCM <=1,000,000. CLI run input is capped at 64 KiB, report verification at 8 MiB. Unknown/duplicate keys, floats, exponent numbers, nonfinite values and malformed trees fail without partial stdout. Representation counts do not bound integer bit complexity, bytes of output, wall time or RAM.

The policy family is complete deterministic contingent choices on this supplied tree, not unrestricted randomized policies or a general risk-sensitive MDP. Cross-language/reference agreement shares mathematical assumptions and schema; it is evidence, not a formal proof. Exact arithmetic does not make a supplied tree true, calibrated or safe. No financial advice, financial performance, new CVaR algorithm, empirical ranking or real-world decision guarantee is claimed. MIT licensed. Original code, schema, controls and inspector; classical methods are attributed in [METHOD.md](METHOD.md).
