from enum import IntEnum

from .Utils.BinaryFileHelper import BinaryFileHelper
from .IO.LRBinaryReader import LRBinaryReader
from .Utils.Token import Token
from .IO.LRFile import LRFile

from .Utils.GDB_Vertex_Normal import GDB_Vertex_Normal
from .Utils.GDB_Vertex_Color import GDB_Vertex_Color
from .Utils.GDB_Polygon import GDB_Polygon
from .Utils.GDB_Meta import (
    GDB_Meta,
    GDB_Meta_Material,
    GDB_Meta_Faces,
    GDB_Meta_Vertices,
    GDB_Meta_Bone,
)
from .Utils.GDB_Object import GDB_Object


class ID(IntEnum):
    MATERIALS = 0x27
    VERTEX_NORMALED = 0x29
    VERTEX_COLORED = 0x2A
    INDICES = 0x2D
    INDICES_META = 0x2E
    SCALE = 0x33


class GDB:
    """
    A GDB file, containing materials, vertices, polygons, and objects.

    Attributes:
        materials (list[str]): List of material names, references to an MDB file
        vertices (list[GDB_Vertex_Color]): List of vertices with color and UV data
        polygons (list[GDB_Polygon]): List of polygons (triangles)
        objects: (list[GDB_Object]): A submodel, with vertices, polygons, and a material

    """

    materials: list[str]
    vertex_normals: list[GDB_Vertex_Normal]
    vertices: list[GDB_Vertex_Color]
    vertex_format: str
    polygons: list[GDB_Polygon]
    objects: list[GDB_Object]
    meta: list[GDB_Meta]
    scale: float

    def __init__(self, file: LRFile) -> None:
        helper: BinaryFileHelper = BinaryFileHelper()
        reader: LRBinaryReader = helper.decompress(file.data)

        self.materials = []
        self.vertices = []
        self.vertex_format = 'color'
        self.polygons = []
        self.meta = []
        self.objects = []
        self.scale = 1.0

        self.file = file

        while reader.position < len(reader):
            block_id: int = reader.read_int(Token.Byte)

            match block_id:
                case ID.MATERIALS:
                    self.materials = reader.read_str_array_block()

                case ID.SCALE:
                    self.scale = reader.read_float(True)

                case ID.VERTEX_NORMALED:
                    self.vertex_normals = reader.read_array_block(
                        GDB_Vertex_Normal.read
                    )

                case ID.VERTEX_COLORED:
                    self.vertices = reader.read_array_block(GDB_Vertex_Color.read)

                case ID.INDICES:
                    self.polygons = reader.read_array_block(GDB_Polygon.read)

                case ID.INDICES_META:
                    self.meta = reader.read_array_block(GDB_Meta.read)

                case _:
                    raise ValueError(
                        f'Unexpected block: {hex(block_id)}, Position: {hex(reader.position)}'
                    )

        self.generate_objects()

        return

    def add_vertices_to_object(
        self, object: GDB_Object, vertex_selector: list[int]
    ) -> None:
        for vertex_index in range(vertex_selector[2]):
            object.vertices.append(self.vertices[vertex_selector[1] + vertex_index])

    def get_absolute_face_vertices(
        self,
        relative_indices: GDB_Polygon,
        obj_index: list[int],
        vertex_selector: list[int],
        previous_vertex_selector: list[int],
        vertex_selector_obj_offset: int,
        previous_vertex_selector_obj_offset: int,
    ) -> bool:
        for i in range(3):
            if relative_indices[i] < vertex_selector[0]:
                if previous_vertex_selector[0] > relative_indices[i]:
                    assert False

                obj_index[i] = previous_vertex_selector_obj_offset + (
                    relative_indices[i] - previous_vertex_selector[0]
                )

                continue

            relative_index_with_look_back = relative_indices[i] - vertex_selector[0]

            if relative_index_with_look_back >= vertex_selector[2]:
                previous_relative_index_with_look_back: int = (
                    relative_indices[i] - previous_vertex_selector[0]
                )
                if (
                    previous_relative_index_with_look_back
                    >= previous_vertex_selector[2]
                ):
                    assert False

                obj_index[i] = (
                    previous_vertex_selector_obj_offset
                    + previous_relative_index_with_look_back
                )
                continue

            obj_index[i] = vertex_selector_obj_offset + relative_index_with_look_back
            continue

        return True

    def add_faces_to_object(
        self,
        object: GDB_Object,
        vertex_selector: list[int],
        previous_vertex_selector: list[int],
        current_face_selector: list[int],
        current_group: int,
    ) -> None:
        vertex_selector_obj_offset = len(object.vertices) - vertex_selector[2]
        previous_vertex_selector_obj_offset = (
            vertex_selector_obj_offset - previous_vertex_selector[2]
        )

        for face_index in range(current_face_selector[1]):
            face: GDB_Polygon = self.polygons[current_face_selector[0] + face_index]
            absolute_vertices: list[int] = [0, 0, 0]

            self.get_absolute_face_vertices(
                face,
                absolute_vertices,
                vertex_selector,
                previous_vertex_selector,
                vertex_selector_obj_offset,
                previous_vertex_selector_obj_offset,
            )

            assert self.vertex_format == 'color'  # TODO: support other formats

            # Add a triangle
            object.polygons.append(
                GDB_Polygon(
                    absolute_vertices[0],
                    absolute_vertices[1],
                    absolute_vertices[2],
                    [absolute_vertices[0], absolute_vertices[1], absolute_vertices[2]],
                    current_group,
                )
            )

    def generate_objects(self) -> None:
        # TODO: Make real data types for these
        current_vertex_selector: list[int] = [0, 0, 0]
        previous_vertex_selector: list[int] = [0, 0, 0]
        current_face_selector: list[int] = [0, 0]

        has_object: bool = False
        current_object: GDB_Object = GDB_Object()
        current_group: int = -1

        for meta in self.meta:
            if type(meta) is GDB_Meta_Material:
                if has_object:
                    has_object = False
                    current_vertex_selector = [0, 0, 0]
                    previous_vertex_selector = [0, 0, 0]
                    current_face_selector = [0, 0]
                    self.objects.append(current_object)

                if meta.material_id >= 0 and meta.material_id <= len(self.materials):
                    current_object = GDB_Object(material_id=meta.material_id)
                    has_object = True
                else:
                    raise IndexError(f'material_id: {meta.material_id} out of range')

            elif type(meta) is GDB_Meta_Bone:
                current_group = meta.bone_id

            elif type(meta) is GDB_Meta_Vertices:
                if (
                    meta.offset >= 0
                    and meta.length >= 0
                    and meta.offset + meta.length <= len(self.vertices)
                ):
                    previous_vertex_selector = current_vertex_selector
                    current_vertex_selector = [
                        meta.shift_forward_count,
                        meta.offset,
                        meta.length,
                    ]
                else:
                    raise IndexError('Vertices out of range')

                self.add_vertices_to_object(current_object, current_vertex_selector)

            elif type(meta) is GDB_Meta_Faces:
                if (
                    meta.offset >= 0
                    and meta.length >= 0
                    and meta.offset + meta.length <= len(self.polygons)
                ):
                    current_face_selector = [meta.offset, meta.length]
                else:
                    raise IndexError('Faces out of range')

                self.add_faces_to_object(
                    current_object,
                    current_vertex_selector,
                    previous_vertex_selector,
                    current_face_selector,
                    current_group,
                )

        if has_object:
            self.objects.append(current_object)
