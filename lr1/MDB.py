

from .Utils.BinaryFileHelper import BinaryFileHelper
from .IO.LRBinaryReader import LRBinaryReader
from .Utils.Token import Token
from .JAM import JamItem
from .BMP import BMP
from .Utils.MDB_Material import MDB_Material

ID_MATERIALS: int = 0x27

class MDB:


    materials: dict[str, MDB_Material]

    def __init__(self, file: JamItem) -> None:

        helper: BinaryFileHelper = BinaryFileHelper()
        reader: LRBinaryReader = helper.decompress(file.data)

        self.materials = dict()

        # Read each material
        while reader.position < len(reader):
            block_id: int = reader.read_int(Token.Byte)
            if block_id == ID_MATERIALS:
                self.materials = reader.read_dict_block(
                    MDB_Material.read,
                    ID_MATERIALS
                )

            else:
                raise ValueError(f'Invalid block_id: {block_id}, position: {reader.position - 1}')

        # Add the texture to the material
        for material in self.materials.values():

            # Only some materials have textures
            if material.texture_name != '':
                bmp_file_path = f'{file.path.parent}/{material.texture_name.upper()}.BMP'
                try:
                    material.texture = BMP(file.jam.extract_file(bmp_file_path))
                except FileNotFoundError:

                    # Set a fallback texture
                    material.texture = BMP(
                        file.jam.extract_file('/GAMEDATA/RACEC0R1/CHECKER.BMP')
                    )

    def list_materials(self) -> None:
        """Lists each material with its name"""

        for key, material in self.materials.items():
            print(f'{key.ljust(8)} : {{ {material} }}')
