from pytest import approx
import application.calcscripts.ConcreteBeam as ConcBm


def test_concreteBeam():
    results = ConcBm.create_calculation()
    # for result in results.get('calc'):
    #     if result.__class__.__name__ =='CalcVariable':
    #         print(result.name + " = " + str( result.result()))
    calcs = results.get('calc')
    c = 0
    Mn = 0
    for calc in calcs:
        if calc.__class__.__name__ == 'CalcVariable':
            if calc.name == 'c':
                c = calc.result()
            elif calc.name == '\phi M_n':
                Mn = calc.result()
    assert approx(c, 0.001) == 2.284
    assert approx(Mn, 0.001) == 125.6
