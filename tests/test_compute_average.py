import compute_average as ca 

def test_compute_average():
    assert ca.averageUpToDay([1,2,3,4,5,6,7,8,9])==5
    assert ca.averageUpToDay([53,234,1321,312131])==78434.75

