from ..Utils.GDB_Vertex_Color import GDB_Vertex_Color
from ..Utils.GDB_Polygon import GDB_Polygon
from ..Utils.GDB_Meta import GDB_Meta_Faces, GDB_Meta_Vertices, GDB_Meta_Bone


class GDB_Object:
    """A submodel of a GDB file, containing vertices, polygons, and a material.

    Attributes:
        vertices (list[GDB_Vertex_Color]): List of vertices with color and UV data.
        polygons (list[GDB_Polygon]): List of polygons (triangles).
        material_id (int): ID of the material used by this object.
        bone (int): Bone ID associated with this object.
    """

    vertices: list[GDB_Vertex_Color]
    polygons: list[GDB_Polygon]
    material_id: int
    bone: int

    meta_vertices: GDB_Meta_Vertices
    meta_indices: GDB_Meta_Faces
    meta_bone: GDB_Meta_Bone

    def __init__(
        self,
        vertices: list[GDB_Vertex_Color] | None = None,
        polygons: list[GDB_Polygon] | None = None,
        material_id: int = 0,
        meta_vertices: GDB_Meta_Vertices = GDB_Meta_Vertices(),
        meta_indices: GDB_Meta_Faces = GDB_Meta_Faces(),
        bone: int = 0,
    ) -> None:
        self.vertices = vertices if vertices is not None else []
        self.polygons = polygons if polygons is not None else []
        self.material_id = material_id
        self.meta_vertices = meta_vertices
        self.meta_indices = meta_indices
        self.bone = bone
