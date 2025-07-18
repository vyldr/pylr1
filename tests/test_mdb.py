from lr1.MDB import MDB
from lr1.JAM import JAM


filename_mdb: str = '/GAMEDATA/RACEC0R1/COMBINED.MDB'
filename_jam: str = 'tests/LEGO.JAM'

def test_mdb() -> None:
    mdb: MDB = MDB(JAM(filename_jam).extract_file(filename_mdb))

    assert len(mdb.materials) == 42
    assert (
        str(mdb.materials['caveroad'])
        == 'Texture: caveroad  -11------1  Alpha: 255  Ambient: #7F7F7FFF  Diffuse: #7F7F7FFF'
    )

