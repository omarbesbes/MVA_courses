"""rh — small numerical toolbox for the Rabbit Hull project.

Modules
-------
aa      archetypal analysis, k-means and PCA baselines (numpy only)
interp  the chord test: distance to the nearest sample along straight and graph paths
nulls   null models (Gaussian surrogates, LayerNorm push-forward, planted polytopes)
dino    DINOv2 loading, preprocessing and feature caching (needs torch)
"""

__all__ = ["aa", "interp", "nulls"]
