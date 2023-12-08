import torch
from keyframed import Curve


def test_matrix_interpolation():
    start_matrix = torch.tensor([[0, 0], [0, 0]], dtype=torch.float32)
    end_matrix = torch.tensor([[1, 1], [1, 1]], dtype=torch.float32)
    curve = Curve({0: start_matrix, 10: end_matrix}, default_interpolation='linear')

    expected_mid = torch.tensor([[0.5, 0.5], [0.5, 0.5]], dtype=torch.float32)
    assert torch.allclose(curve[5], expected_mid)