import numpy as np
from keyframed import Curve

def test_vector_interpolation_linear():
    # Test linear interpolation with vectors
    start_vec = np.array([0, 0, 0])
    end_vec = np.array([10, 10, 10])
    curve = Curve({0: start_vec, 10: end_vec}, default_interpolation='linear')

    assert np.allclose(curve[5], np.array([5, 5, 5]))
    assert np.allclose(curve[2.5], np.array([2.5, 2.5, 2.5]))
    assert np.allclose(curve[7.5], np.array([7.5, 7.5, 7.5]))

# def test_vector_interpolation_custom():
#     # Test custom interpolation function for vectors
#     def custom_interp(t, t0, value0, t1, value1):
#         # Example: simple linear interpolation
#         return value0 + (value1 - value0) * (t - t0) / (t1 - t0)

#     start_vec = np.array([1, 2, 3])
#     end_vec = np.array([4, 5, 6])
#     curve = Curve({0: start_vec, 10: end_vec})
#     curve.set_interpolation(custom_interp)

#     assert np.allclose(curve[5], np.array([2.5, 3.5, 4.5]))
#     assert np.allclose(curve[2], np.array([1.3, 2.3, 3.3]))

def test_vector_keyframe_insertion():
    # Test inserting vector keyframes
    curve = Curve()
    curve[0] = np.array([1, 2, 3])
    curve[5] = np.array([4, 5, 6])

    assert np.allclose(curve[0], np.array([1, 2, 3]))
    assert np.allclose(curve[5], np.array([4, 5, 6]))

# def test_vector_interpolation_bounds():
#     # Test vector interpolation at curve bounds
#     curve = Curve({0: np.array([0, 0]), 10: np.array([10, 10])}, default_interpolation='linear')

#     assert np.allclose(curve[-5], np.array([0, 0]))  # Test extrapolation if your curve supports it
#     assert np.allclose(curve[15], np.array([10, 10]))

# def test_vector_mixed_interpolation():
#     # Test curves with mixed scalar and vector interpolation
#     curve = Curve({0: 0, 5: np.array([5, 10, 15]), 10: 10}, default_interpolation='linear')

#     assert curve[2.5] == 2.5  # Scalar interpolation
#     assert np.allclose(curve[7.5], np.array([7.5, 12.5, 17.5]))  # Vector interpolation

# Add more tests for edge cases, different vector lengths, and other interpolation methods as needed
