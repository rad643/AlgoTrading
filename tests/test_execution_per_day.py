import main

def test_execution_per_day()->None:
    test1=main.Engine()
    
    assert test1.execution_per_day()==-3

test_execution_per_day()
