from lr1.TDB import TDB
from lr1.JAM import JAM

filename_tdb: str = '/GAMEDATA/RACEC0R1/COMBINED.TDB'
filename_jam: str = 'tests/LEGO.JAM'


def test_tdb() -> None:
    tdb: TDB = TDB(JAM(filename_jam).extract_file(filename_tdb))

    assert len(tdb.textures) == 39
    assert 'caveroad' in tdb.textures
    assert (
        str(tdb.textures['netting'])
        == 'TDB_Texture: { 11-11 LRColor: {R: 39, G: 39, B: 39, A:255} }'
    )
