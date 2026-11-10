# RiskLab: exact tails, information timing and policy witnesses

## 1. A finite supplied experiment

A model is a structurally rooted finite tree. Terminal nodes carry signed losses. Chance nodes carry a full rational probability simplex, including zeros. Decision nodes select one child. A full deterministic policy specifies an action at every decision node, including those never reached under that policy. Policies are enumerated lexicographically in ascending decision-node ID order. Distinct off-path choices are not deduplicated.

The root loss distribution is formed from complete selected paths. For a forced subtree, the path starts at that node with mass one. That is a well-defined supplied subproblem even when the original root gives that node zero probability; it is not conditioning on a null event. Root reach is propagated separately, with zero mass assigned to unchosen decision children.

## 2. Confidence alpha and atom splitting

RiskLab uses **confidence alpha**, with `0 <= alpha < 1`. Tail probability is `beta = 1-alpha`. Some literature uses alpha for beta. Formula labels must be translated, not silently exchanged.

For losses z_i with nominal probabilities p_i, normalized adverse weights obey `0 <= q_i <= p_i/beta` and `sum q_i = 1`. Maximizing `sum q_i z_i` fills high-loss atoms first and splits the final boundary atom if needed. Equal losses use ascending leaf ID for a canonical weight vector. This canonical vector is one witness, not a claim that the optimal tail allocation is unique.

For any threshold eta, the inequality

```text
sum_i q_i z_i <= eta + sum_i p_i max(z_i-eta,0)/beta
```

follows from the cap on each q and their sum. A sorted tail allocation and an attaining supported-loss threshold make the two sides equal. The report includes every distinct positive-probability loss as a threshold candidate, all positive excesses, the chosen first minimizing candidate and both objective witnesses. It does not claim to enumerate every minimizing real threshold. In particular, at alpha zero every eta below the smallest supported loss minimizes the expression. Zero-probability loss values do not create extra threshold candidates.

The plotted orange mass is `beta*q_i`, not q_i itself. It is at most the nominal atom mass p_i, and sums to beta. Its weighted mean divided by beta is CVaR. Display widths use rounded coordinates; exact rational tables make all decisions.

## 3. Static and nested are different objectives

For one fixed policy, static risk is the CVaR of its root terminal law. At each subtree the same construction gives a conditional or forced-subproblem static value.

Nested fixed-policy values obey:

```text
terminal: V(n) = supplied loss
selected decision: V(n) = V(selected child)
chance: V(n) = CVaR_alpha(child values, supplied conditional probabilities)
```

To select a nested-optimal policy, replace the decision equation with the minimum over children, and retain all minimizing actions. Choosing the first tie at every decision gives a complete policy with optimal continuation values at every node. The checker confirms the entire value vector equals the per-node minimum over every enumerated full policy.

Static policy minimization is instead complete enumeration of terminal laws. RiskLab does not replace it with an unjustified ordinary Bellman recurrence. The optimum family is explicitly limited to the supplied full deterministic policies. No optimality theorem for arbitrary randomized, partially observed or general MDP policies is asserted.

## 4. Root optimality is weaker than local optimality

CVaR need not be strictly monotone. An adverse tail can ignore a reached branch, making a worse continuation invisible at the root. Therefore a nested-root-optimal policy need not be locally optimal on every reached decision. The `ignored_branch` control makes this visible without equating it with a failure of backward selection.

For each decision node, the report subtracts the best static or nested subtree continuation value over all full policies from the selected policy's corresponding subtree value. These regrets are nonnegative. The reached-decision flags require zero regret only at strictly positive nominal reach. Zero-reach rows still show their forced-subproblem values, but are excluded from those flags. This is a comparison of complete continuations, not merely changing the immediate action while freezing later choices.

The `reversal` control was selected by seed 17021 after candidate 15 in the retained development search. Static p3 minimizes the root tail at 7/3, yet has conditional regret 2/3 at node 2. Nested p2 minimizes its different root objective at 22/9 and is locally optimal. Neither objective's optimum is an estimate of the other optimum.

Static risk depends only on the terminal law; nested risk depends on the information grouping. The paired `grouped_law` and `flat_law` controls have the same terminal law and static value 4/3, but nested values 16/9 and 4/3. The seed-7309 development-selected `nested_below_static` control has static value 23/6 and nested value 11/3. There is no claimed universal ordering between the two objectives.

## 5. Independent computational checks

The generator uses reverse-node dynamic evaluation, path-law propagation and high-loss tail filling. The checker imports only schema/serialization from the production package, not generator code. It traverses full selected paths from each node and enumerates vertices of the risk-envelope box intersected with the sum-one hyperplane. At a vertex, all but at most one positive-support coordinate are at a bound. Every possible free coordinate and lower/upper assignment of the others is enumerated exactly. It maximizes weighted loss over those vertices, uses a lexicographic tie among equal optima, and separately checks threshold-objective equality.

The browser uses separate BigInt arithmetic, complete path replay and threshold minimization. Its risk weights are checked against its primal threshold value. The test oracle compares complete exact serialized reports, not rounded JSON numbers; the actual Chrome oracle uses lossless revival of beyond-safe-range integers. The Python verifier also checks reports downloaded by real trusted Chrome clicks.

The optional SciPy reference actually solves both formulations using HiGHS: a threshold/slack primal LP and an adverse-weight dual LP. It checks objectives, probability normalization and caps numerically. This is an additional small finite reference, not a production dependency or independent validation of the model assumptions. Runtime SciPy is 1.15.3; fetched documentation may describe a later release.

## 6. Boundaries

Exactly one rooted tree, one alpha, terminal losses, at most 15 nodes/eight leaves/four decisions/depth six/64 policies. Signed losses are allowed. No general MDP recurrence, intermediate-cost accumulation, random policy mixing, uncertain transition law, learned agent, held-out data or calibration claim. The API validates normalized denominator LCM and raw component limits before enumeration. Bounds cover finite representations, not arithmetic bit lengths, time or memory.

## Source ledger

Classical methods, not external code, inform this implementation. The schema, exact witnesses, controls, verifier and inspector are original. No paper's numerical example is copied.

1. **Rockafellar and Uryasev, Conditional Value-at-Risk for General Loss Distributions**, November 28, 2001 version. Primary theory. The atom-splitting discussion and Theorem 10 support finite discrete CVaR and threshold minimization. [Paper](https://sites.math.washington.edu/~rtr/papers/rtr187-CVaR2.pdf).
2. **Rockafellar and Uryasev, Optimization of Conditional Value-at-Risk.** Primary theory. Optimization formulation; its earlier smooth-law assumptions are not used to justify discrete atoms. [Paper](https://sites.math.washington.edu/~rtr/papers/rtr179-CVaR1.pdf).
3. **Shapiro and Pichler, Time and Dynamic Consistency of Risk Averse Stochastic Programs**, October 2016. Primary theory. Sections 3 and 6, especially equations 6.7-6.10 and the nested-risk discussion, support the confidence convention, density envelope, static/nonrecursive distinction and non-strict-monotonicity caveat. Only the applicable finite formulations are used. [Paper](https://optimization-online.org/wp-content/uploads/2016/09/5654.pdf).
4. **Boda and Filar, Time Consistent Dynamic Risk Measures.** Primary theory. Principle-of-optimality definition and static CVaR counterexample discussion. [Paper](https://www.math.vu.nl/~koole/publications/2005mmor/bodafilar.pdf).
5. **Structure of Risk-Averse Multistage Stochastic Programs.** Primary technical paper. Section 4.1 gives a nested CVaR formulation. Its displayed alpha is a tail probability, unlike RiskLab's confidence alpha. [Paper](https://www2.karlin.mff.cuni.cz/~kopa/papers/ICSP_OR_Spectrum_rev3.pdf).
6. **SciPy linprog, method='highs'.** Official software documentation for the optional reference solver's objective, constraints, bounds and result contract. [Documentation](https://docs.scipy.org/doc/scipy/reference/optimize.linprog-highs.html).
7. **Python fractions.** Official documentation for exact numerator/denominator arithmetic; only APIs available in Python 3.10+ are used. [Documentation](https://docs.python.org/3/library/fractions.html).

Sources inspected November 10, 2026. This is mathematical software research; primary theory and official API documents are the relevant source types, rather than product reviews or community claims. Cross-checks share theory and schema. They do not prove correctness, validate supplied probabilities or establish real-world safety.
