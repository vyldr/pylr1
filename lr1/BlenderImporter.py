# type: ignore

from enum import IntEnum

import bpy
import colorsys

from .JAM import JAM
from .BVB import BVB
from .GDB import GDB
from .MDB import MDB
from .TDB import TDB
from .IO.LRFile import LRFile, LRFileItem
from .Utils.MDB_Material import MDB_Material
from .Utils.TDB_Texture import TDB_Texture


class BlenderImporter:
    file: LRFile
    jam: JAM | None

    def __init__(self, file: str | LRFile, jam: str | JAM | None = None) -> None:
        if type(jam) is str:
            self.jam = JAM(jam)
        else:
            self.jam = jam

        if type(file) is str:
            if self.jam is not None:
                self.file = self.jam.extract_file(file)
            else:
                self.file = LRFileItem(file)
        else:
            self.file = file

        # Import the file based on its type
        match self.file.path.suffix:
            case '.BVB':
                self.bvb_import(BVB(self.file))

            case '.GDB':
                self.gdb_import(GDB(self.file))

            case _:
                pass

    def new_collection(self, name: str):
        """Creates a collection to hold our objects"""

        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)

        return collection

    def bvb_import(self, bvb: BVB) -> set[str]:
        collection = self.new_collection(self.file.path.name)

        # Create a mesh for each material
        for i, material in enumerate(bvb.materials):
            #  Choose a color
            hue = i / len(bvb.materials)  # Evenly space hues
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            rgba = (*rgb, 1.0)  # Add alpha

            # Create or get material with our color
            mat = bpy.data.materials.get(material)
            if not mat:
                mat = bpy.data.materials.new(name=material)
                mat.use_nodes = True
                bsdf = mat.node_tree.nodes.get('Principled BSDF')
                if bsdf:
                    bsdf.inputs['Base Color'].default_value = rgba

            # Create mesh and object
            mesh = bpy.data.meshes.new(f'Mesh_{material}')
            obj = bpy.data.objects.new(f'Obj_{material}', mesh)
            collection.objects.link(obj)

            # Filter only faces with the current material
            filtered_faces = filter(lambda tri: tri.material == i, bvb.polygons)

            # Build the mesh
            mesh.from_pydata(bvb.vertices, [], list(filtered_faces))
            mesh.update()

            # Assign the material
            mesh.materials.append(mat)

        return {'FINISHED'}

    def gdb_import(self, gdb: GDB) -> set[str]:
        collection = self.new_collection(self.file.path.name)

        textures_dict: dict[str, TDB_Texture] = dict()
        materials_dict: dict[str, MDB_Material] = dict()

        # Read every TDB file in the same directory
        for file in self.file.parent.directory_contents:
            if file.path.suffix == '.TDB':
                tdb = TDB(file)
                textures_dict.update(tdb.textures)

        # Read every MDB file in the same directory
        for file in self.file.parent.directory_contents:
            if file.path.suffix == '.MDB':
                mdb = MDB(file)
                materials_dict.update(mdb.materials)

        # Set texture transparency
        for key, material in materials_dict.items():
            if hasattr(material, 'texture'):
                # Check if there is a matching texture in the TDB
                if material.texture_name in textures_dict:
                    texture = textures_dict[material.texture_name]
                    if texture.trans_color:
                        color = texture.color.to_tuple()
                        for bmp_color in material.texture.palette:
                            if bmp_color.as_float() == color:
                                bmp_color.a = 0.0  # Set alpha to 0 for transparency

        # Generate the images
        for material in materials_dict.values():
            if hasattr(material, 'texture'):
                image = bpy.data.images.new(
                    material.texture_name,
                    width=material.texture.width,
                    height=material.texture.height,
                    alpha=True,
                    float_buffer=False,
                )
                image.pixels = material.texture.flat_pixels()
                image.pack()
                material.image = image

        class PROPERTY(IntEnum):
            MATERIAL_ID = 0x27
            INDICES_META = 0x2D
            VERTEX_META = 0x31
            BONE_ID = 0x32

        for i, object in enumerate(gdb.objects):
            # Create mesh and object
            mesh = bpy.data.meshes.new(f'Mesh_{i}')
            obj = bpy.data.objects.new(f'Obj_{i}', mesh)
            collection.objects.link(obj)

            # Build the mesh
            mesh.from_pydata(object.vertices, [], object.polygons)
            mesh.update()

            # Create the material
            mat = self.generate_material(
                object,
                mesh,
                f'{gdb.materials[object.material_id]} obj_{i}',
                materials_dict[gdb.materials[object.material_id]],
            )

            # Assign material
            obj.data.materials.append(mat)

        return {'FINISHED'}

    def generate_material(self, object, mesh, name, mdb_material):
        # Create new material
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links

        # Clear nodes
        for node in nodes:
            nodes.remove(node)

        # Material Output node
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (600, 0)

        # Principled BSDF node
        bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf_node.location = (300, 100)
        bsdf_node.inputs['Base Color'].default_value = mdb_material.diffuse_color
        bsdf_node.inputs['Alpha'].default_value = mdb_material.alpha / 0xFF
        bsdf_node.inputs['Roughness'].default_value = 1.0
        bsdf_node.inputs['Emission Strength'].default_value = 0.3
        links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

        # Overlay node
        overlay_node = nodes.new(type='ShaderNodeMix')
        overlay_node.location = (100, 0)
        overlay_node.data_type = 'RGBA'
        overlay_node.blend_type = 'OVERLAY'
        overlay_node.inputs[0].default_value = 1.0
        links.new(overlay_node.outputs['Result'], bsdf_node.inputs['Base Color'])
        links.new(overlay_node.outputs['Result'], bsdf_node.inputs['Emission Color'])

        # Create UV layer
        uv_layer = mesh.uv_layers.new(name='UVMap')

        # If the material has an image texture, create nodes for it
        if hasattr(mdb_material, 'image'):
            # Image Texture node
            tex_image_node = nodes.new(type='ShaderNodeTexImage')
            tex_image_node.image = mdb_material.image
            tex_image_node.interpolation = 'Closest'
            tex_image_node.location = (-200, 0)
            links.new(tex_image_node.outputs['Color'], overlay_node.inputs['A'])
            links.new(tex_image_node.outputs['Alpha'], bsdf_node.inputs['Alpha'])

            # Apply the UV coordinates
            for poly in mesh.polygons:
                for loop_index in range(
                    poly.loop_start, poly.loop_start + poly.loop_total
                ):
                    vert_index = mesh.loops[loop_index].vertex_index
                    uv_layer.data[loop_index].uv = object.vertices[
                        vert_index
                    ].tex_coords

            # Mapping node
            map_node = nodes.new(type='ShaderNodeMapping')
            map_node.location = (-400, -100)
            map_node.inputs[3].default_value[1] = -1  # Scale Y
            links.new(map_node.outputs['Vector'], tex_image_node.inputs['Vector'])

            # Texture Coordinate node
            tex_coord_node = nodes.new(type='ShaderNodeTexCoord')
            tex_coord_node.location = (-600, -100)
            links.new(tex_coord_node.outputs['UV'], map_node.inputs['Vector'])

        # Create vertex color layer
        color_layer = mesh.vertex_colors.new(name='Color')

        # Assign colors per face corner (loop)
        loop_colors = color_layer.data
        for poly in mesh.polygons:
            for loop_idx in poly.loop_indices:
                vert_idx = mesh.loops[loop_idx].vertex_index
                loop_colors[loop_idx].color = object.vertices[
                    vert_idx
                ].color.to_tuple()  # RGBA

        # Color Attribute node
        vc_node = nodes.new(type='ShaderNodeVertexColor')
        vc_node.location = (-100, -300)
        vc_node.layer_name = color_layer.name
        links.new(vc_node.outputs['Color'], overlay_node.inputs['B'])

        return material
