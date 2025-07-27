from lr1.RRB import RRB
from lr1.JAM import JAM

filename_rrb: str = '/GAMEDATA/RACEC1R3/R1_F_0.RRB'
filename_jam: str = 'tests/LEGO.JAM'


def test_RRB() -> None:
    rrb: RRB = RRB(JAM(filename_jam).extract_file(filename_rrb))

    test_rrb: str = 'RRB_Node: {DX:-0.06640625, DY:-0.86328125, DZ:0.0, RX:0.7322834645669292, RY:0.6771653543307087, RZ:0.0, RW:0.0, F1:40, F2:40, Time:197}'

    assert str(rrb.nodes[1]) == test_rrb
    assert rrb.milliseconds == 87712
