# type: ignore


try:
    from pathlib import Path
    import bpy

    from bpy.props import StringProperty
    from bpy.types import Operator
    from bpy_extras.io_utils import ImportHelper

    from .BlenderImporter import BlenderImporter

except ImportError:
    pass

else:

    class IMPORT_OT_LRFile(Operator, ImportHelper):
        bl_idname = 'import_scene.import_lrfiles'
        bl_label = 'Import Lego Racers Files'
        bl_description = 'Import Lego Racers files (.gdb, .bvb, .rrb)'
        bl_options = {'PRESET', 'UNDO'}
        filename_ext = '.gdb;.bvb;.rrb'
        filter_glob: StringProperty(default='*.gdb;*.bvb;*.rrb', options={'HIDDEN'})

        def execute(self, context):
            filepath = Path(self.filepath)
            ext = filepath.suffix.upper()
            if ext not in {'.GDB', '.BVB', '.RRB'}:
                self.report({'ERROR'}, f'Unsupported file extension: {ext}')
                return {'CANCELLED'}

            BlenderImporter(self.filepath)
            return {'FINISHED'}

    def menu_func_import(self, context) -> None:
        self.layout.operator(
            IMPORT_OT_LRFile.bl_idname, text='Lego Racers Files (.gdb/.bvb/.rrb)'
        )

    def register() -> None:
        bpy.utils.register_class(IMPORT_OT_LRFile)
        bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

    def unregister() -> None:
        bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
        bpy.utils.unregister_class(IMPORT_OT_LRFile)

    if __name__ == '__main__':
        register()
