from lr1.JAM import JAM

filename_jam: str = 'tests/LEGO.JAM'


def test_JAM() -> None:
    jam: JAM = JAM(filename_jam)

    # Different tests for different JAM versions
    match len(jam.data):
        # 1999 version
        case 19592720:
            assert len(jam.files) == 5444
            assert len(jam.directories) == 64
            assert (
                str(jam.files[69])
                == 'File: {Path: /GAMEDATA/COMMON/WNDSUS1.PCM, Position: 0x4f564, Size: 6010}'
            )

        # 2001 version
        case 19642024:
            assert len(jam.files) == 5471
            assert len(jam.directories) == 66

            assert (
                str(jam.files[69])
                == 'File: {Path: /GAMEDATA/COMMON/WNDSUS1.PCM, Position: 0x4f764, Size: 6010}'
            )

        case _:
            raise AssertionError('Unknown JAM file')
