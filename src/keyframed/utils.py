from .core import Keyframed


def to_keyframed(curve, n=None):
    """
    dummy-proof coersion
    """
    if isinstance(curve, Keyframed):
        k = curve
    elif isinstance(curve, str):
        k = Keyframed.from_string(curve)
    elif isinstance(curve, dict):
        k = Keyframed(curve)
    if n:
        k.set_length(n)
    return k
