from lr1.BMP import BMP
from lr1.JAM import JAM

filename_jam: str = 'tests/LEGO.JAM'
jam: JAM = JAM(filename_jam)

filename_bmp: str = '/MENUDATA/PIECEDB/SQUAREZ2.BMP'


def test_BMP() -> None:
    jam: JAM = JAM(filename_jam)
    bmp: BMP = BMP(jam.extract_file(filename_bmp))

    assert len(bmp.image) == 256
    assert bmp.width == 16
    assert bmp.height == 16
    assert bmp.image[20].as_float() == (0.0, 1.0, 0.0, 1.0)
    assert bmp.image[238].as_float() == (1.0, 1.0, 0.0, 1.0)
