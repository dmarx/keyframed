import pytest
import numpy as np
import torch
from keyframed import Curve, Keyframe

# Test linear interpolation with PyTorch tensors
def test_linear_interpolation_tensor():
    start_tensor = torch.tensor([0, 0, 0])
    end_tensor = torch.tensor([10, 10, 10])
    curve = Curve({0: start_tensor, 10: end_tensor}, default_interpolation='linear')

    assert torch.allclose(curve[5], torch.tensor([5, 5, 5]))
    assert torch.allclose(curve[2.5], torch.tensor([2.5, 2.5, 2.5]))
    assert torch.allclose(curve[7.5], torch.tensor([7.5, 7.5, 7.5]))

# Test mixed NumPy array and PyTorch tensor interpolation
def test_mixed_interpolation():
    start_array = np.array([1, 2, 3])
    end_tensor = torch.tensor([4, 5, 6])
    curve = Curve({0: start_array, 10: end_tensor}, default_interpolation='linear')

    expected_midpoint = torch.tensor([2.5, 3.5, 4.5])
    assert torch.allclose(curve[5], expected_midpoint)

# Test PyTorch tensor interpolation with custom interpolation method
def test_custom_tensor_interpolation():
    def custom_interp(t, t0, value0, t1, value1):
        value0, value1 = torch.tensor(value0), torch.tensor(value1)
        return value0 + (value1 - value0) * (t - t0) / (t1 - t0)

    start_tensor = torch.tensor([1, 1, 1])
    end_tensor = torch.tensor([2, 2, 2])
    curve = Curve({0: start_tensor, 1: end_tensor})
    curve.set_interpolation(custom_interp)

    assert torch.allclose(curve[0.5], torch.tensor([1.5, 1.5, 1.5]))

# Test tensor keyframe insertion
def test_tensor_keyframe_insertion():
    curve = Curve()
    curve[0] = torch.tensor([1, 2, 3])
    curve[5] = torch.tensor([4, 5, 6])

    assert torch.allclose(curve[0], torch.tensor([1, 2, 3]))
    assert torch.allclose(curve[5], torch.tensor([4, 5, 6]))

# Test tensor interpolation at curve bounds
def test_tensor_interpolation_bounds():
    curve = Curve({0: torch.tensor([0, 0]), 10: torch.tensor([10, 10])}, default_interpolation='linear')

    assert torch.allclose(curve[-5], torch.tensor([0, 0]))  # Test extrapolation if your curve supports it
    assert torch.allclose(curve[15], torch.tensor([10, 10]))

# Add more tests for edge cases and different tensor shapes if necessary
