import data_loader as dl

def test_data_loader():
    
    
    generator=dl.read_ticker_csv("tests/test_file.txt")
    exp1=(1, "2026-05-01", 44.5, None)
    exp2=(2, "2026-05-02", 48, None)
    exp3=(3, "2026-05-03", 46, 46.25)

    gen1=next(generator)
    gen2=next(generator)
    gen3=next(generator)


    assert exp1==gen1
    assert exp2==gen2
    assert exp3==gen3




