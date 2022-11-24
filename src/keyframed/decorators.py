from .core import Keyframed

# an even simpler way to implement this would be a slicing operation.
# would be nice if there were two different slicing mechanisms, one on the 
# frame_ids directly, and one on just the actual keyframes
def frameContext(left=0, right=0):
    assert left+right > 0
    def decorator(f):
        def out_func(k, K: Keyframed, xs, ys):
            context_left = K.keyframe_neighbors_left(k, n=left)
            context_right = K.keyframe_neighbors_right(k, n=right)
            context = context_left + context_right
            return f(context, k, K, xs, ys)
        return out_func
    return decorator
