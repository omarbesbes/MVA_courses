# Speaker notes — 10 minutes, 11 slides

A little under one minute per slide. The numbers to remember are in bold.

**1. Title (15 s).** "The paper proposes that DINOv2 represents an image token as a sum of convex mixtures of
archetypes. I will ask what this claim says, what supports it, and what could contradict it."

**2. The paper in one slide (60 s).** DINOv2 turns an image into 261 tokens of dimension 768. The usual
assumption is that a token is a sparse sum of directions; a sparse autoencoder with 32,000 atoms makes it
operational. Part I: which atoms each task uses, with the "Elsewhere" concepts as the surprise. Part II: the
dictionary is not what the assumption predicts. Part III: a new hypothesis. I focus on Part III.

**3. Two pictures (70 s).** Left, a concept is a direction and "more" means a larger coefficient. Right, a
concept is a point or region and "more" means closer to an archetype; tokens are sums of points, one per active
polytope. The paper's case: attention outputs convex combinations and heads add up; three empirical
signatures; two consequences.

**4. Nested hypotheses (70 s).** A bounded linear feature is a tile with two archetypes, the origin and the
far end. So every linear code is a Minkowski code with segments. The only real difference is how the codes
of a group are coupled: a box if they are independent, a simplex if they share a budget. The hexagon is the
sum of three segments and also the sum of two triangles: the set of activations cannot tell the hypotheses
apart; only the distribution of the codes can.

**5. Attention (70 s).** The attention statement is exact, but it is a statement about softmax. The values
are the other tokens of the same image, so the polytope changes with every image, and the statement is just
as true for a random network. The condition for equality cannot hold: rank **64** against 261 tokens. And a
token is not an attention update: within an image, **54%** of it comes from MLPs. Finally, after the last
LayerNorm all tokens lie on an ellipsoid, which contains no segment: no polytope fits, and every chord
leaves it. Measured: unit norm to **10⁻⁷**, midpoint at **10%** of the half-chord.

**6. E1 (60 s).** The paper's test: walk the straight line between two tokens and measure the distance to the
nearest token. Panel b: for points drawn inside a convex polytope the same triangle appears in high dimension
(0.37 of the chord at dimension 20, 0.49 at 50). Panel c: a Gaussian with the covariance of the tokens gives
the same triangle, **0.50**; along the neighbour graph **0.19** against **0.16**. What differs is local
density: the tokens are clustered. Chords leave the sample, not the support.

**7. E2 (60 s).** Archetypal analysis is always between PCA and k-means. We reproduce the paper's numbers,
and then k-means with ten centroids per image also beats the autoencoder: the comparison rewards any model
refitted on each image. Where archetypal analysis sits in the sandwich is the informative number:
**0.26** for a planted polytope, **0.51** for a Gaussian, **0.47** for DINOv2.

**8. E3 (55 s).** Blocks in the co-activation matrix mean each token uses one group of archetypes: a union,
that is, clusters. A true sum activates all tiles at once and gives a dense matrix. On DINOv2 the blocks
largely follow the image classes (**0.62** adjusted mutual information): one group per token, no sign of
tiles adding up.

**9. Identifiability (50 s).** The paper says a Minkowski sum does not determine its summands. Its proof has
a gap: it subtracts a sublinear function and assumes the result is sublinear. The corrected statement is
true but narrower: it is about supports when all tiles are active. A support cannot tell a linear code from a
block-convex one, the hexagon again. What identifies a dictionary is sparsity and the law of the codes.

**10. Position (50 s).** Position is the one factor we can observe. The mean token is a row effect plus a
column effect to **97.4%**: a genuine Minkowski sum, a positive result for the hypothesis. But each summand
is an arc, a one-parameter curve, not a simplex. And always-on signed axes explain the dense and antipodal
atoms of the paper's dictionary.

**11. Conclusion (45 s).** Parts I and II stand, and the additive composition holds where we can test it.
The hypothesis asks a real question, whether features compete inside groups. But its three signatures are
passed by data without archetypes, exact Minkowski geometry is impossible after LayerNorm, and
non-identifiability is a statement about supports. The decisive experiment is on the codes: box or simplex,
on factors of known value.

## Likely questions

- *Did you use the paper's autoencoder?* No. We reproduced its archetypal-analysis curve and placed its
  reported autoencoder error on our axes; the box-or-simplex test on its codes remains to be done.
- *Is the ellipsoid argument fair if the hypothesis is only approximate?* The paper presents it as a working
  hypothesis; our point is that the exact statement cannot hold after normalisation: chords do leave the set of
  attainable activations, slightly (10% of a half-chord). The peak of signature E1 itself is a sampling effect. Locally, at scales where the ellipsoid is flat, the hypothesis can still be a good model.
- *Why a Gaussian null?* It has a convex support and no archetype, and it matches the first two moments of
  the tokens. It is the simplest distribution that should fail a test of polytope structure.
- *Does the gap ratio exclude large polytopes?* No. It is calibrated for about ten vertices per image, the
  number the paper uses. Polytopes with many more vertices, or sums of several tiles, are not excluded.
- *Which activations?* Patch tokens after the final LayerNorm, the standard DINOv2 output; pre-normalisation
  tokens give the same picture for E1 and a slightly lower gap ratio (0.40).
- *What is an "Elsewhere" concept?* An atom that fires on tokens outside an object, only if the object is in
  the image; masking the object switches it off.
