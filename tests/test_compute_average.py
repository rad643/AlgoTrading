import math

import pytest

from data_loading import compute_average as ca

data = [([1, 2, 3, 4, 5], 3), ([5], 5)]


@pytest.mark.parametrize("input, result", data)
def test_correct_mean(input, result):

    assert ca.averageUpToDay(input) == result


data = [{1, 2, 3, 4, 5}, [1, 2, 3, ""]]  # type: ignore [list-item]


@pytest.mark.parametrize("bad_input", data)
def test_bad_input(bad_input):

    with pytest.raises(TypeError):
        ca.averageUpToDay(bad_input)


def test_empty_list():

    assert math.isnan(ca.averageUpToDay([])) is True
