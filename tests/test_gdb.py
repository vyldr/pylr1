from lr1.JAM import JAM
from lr1.GDB import GDB
from lr1.MDB import MDB, MDB_Material

filename_jam: str = 'tests/LEGO.JAM'

filename: str = '/GAMEDATA/RACEC0R1/TRACK.GDB'  # IGP


materials: str = "['caveroad', 'iaroad0', 'dock', 'rckwall', 'railing', 'adrbbk', 'iagrass', 'minetrck', 'ipside', 'nub6', 'a1no', 'pilings', 'undrside', 'mate2646', 'twrroof', 'twrwall', 'holeinwl', 'brcknwal', 'iawater', 'yllwwndw', 'igrail', 'net', 'a1door', 'barrel2', 'checker']"
caveroad_material: str = (
    'Texture: caveroad  -11------1  Alpha: 255  Ambient: #7F7F7FFF  Diffuse: #7F7F7FFF'
)


def test_GDB() -> None:
    jam: JAM = JAM(filename_jam)

    file = jam.extract_file(filename)

    gdb: GDB = GDB(file)

    assert str(gdb.materials) == materials

    materials_dict: dict[str, MDB_Material] = dict()

    # Read every MDB file in the same directory
    for f in file.parent.directory_contents:
        if f.path.suffix == '.MDB':
            mdb = MDB(f)
            materials_dict.update(mdb.materials)

    assert str(materials_dict['caveroad']) == caveroad_material
    assert len(gdb.objects) == 299
    assert gdb.objects[80].vertices[0].color.hex() == '#A4A4A4FF'
    assert len(gdb.objects[80].vertices) == 15
    assert len(gdb.objects[80].polygons) == 7
    assert gdb.objects[80].material_id == 11
