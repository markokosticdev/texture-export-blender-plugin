import os, bpy, bpy_extras


bl_info = {
    'name': 'Texture Export',
    'author': 'Marko Kostich',
    'version': (1, 0),
    'blender': (2, 80, 0),
    'location': 'View3D > Toolbar > Texture Export',
    'description': 'Texture Export Blender Plugin for exporting textures as images in PNG or JPG format.',
    'warning': '',
    'wiki_url': '',
    'category': 'Texture Export',
}
 

# Extension Panel layout with properties and operators
class TextureExportPanel(bpy.types.Panel):
    bl_idname = 'TOOLBAR_PT_TextureExportPanel'
    bl_label = 'Texture Export'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Texture Export'
 
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.operator('texture_export.input', text='Input', icon='FILEBROWSER')
        
        row = layout.row()
        row.prop(scene.output_folder, "path", text="")
        
        row = layout.row()
        row.label(text= 'Light Power')
        row.prop(scene, 'export_light_power', text='')
        
        row = layout.row()
        row.label(text= 'Light Distance')
        row.prop(scene, 'export_light_distance', text='')
        
        row = layout.row()
        row.label(text= 'Image Size')
        row.prop(scene, 'export_image_size', text='')
        
        row = layout.row()
        row.label(text= 'Image Extension')
        row.prop(scene, 'export_image_extension', text='')
        
        row = layout.row()
        row.operator('texture_export.export', text='Export', icon='EXPORT')
 
 
# Input Files Operator configuration for global property input_files 
class TextureExportInputOperator(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = 'texture_export.input'
    bl_label = 'Import From'
    bl_description = 'Texture Export Input'
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".obj"

    filter_glob = bpy.props.StringProperty(
            default="*.obj",
            options={'HIDDEN'},
            )
            
    files = bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement)
      
    def execute(self, context):
        context.scene.input_files.clear()
        
        dir_path = os.path.dirname(self.filepath)
        
        for index, file in enumerate(self.files, 1):
            file_path = os.path.join(dir_path, file.name)
            file_path.replace('\\', '/')
            
            item = context.scene.input_files.add()
            item.name = file_path
        
        context.scene.output_folder.path = os.path.join(dir_path, 'Texture Export Output')
          
        return {'FINISHED'}


# Output Folder Property configuration for global property output_folder 
class TextureExportOutputProperty(bpy.types.PropertyGroup):
    path = bpy.props.StringProperty(
        name="",
        description="Path to Output Folder",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')


# Export Operator contains the whole workflow for image exporting
class TextureExportExportOperator(bpy.types.Operator):
    bl_idname = 'texture_export.export'
    bl_label = 'Texture Export'
    bl_description = 'Texture Export'
    bl_options = {'REGISTER', 'UNDO'}
 
    def execute(self, context):
        # Checks Input Files and Output Folder
        if not context.scene.input_files or not context.scene.output_folder.path:
            self.report({'WARNING'}, 'Input Files or Output Folder are missing!')
            return {'FINISHED'}
        
        # Checks existence of Output Folder
        if not os.path.exists(context.scene.output_folder.path):
            os.makedirs(context.scene.output_folder.path)
        
        # Change the context for adding light objects
        context.area.ui_type = 'VIEW_3D'
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_by_type(type='LIGHT')
        bpy.ops.object.delete()
        
        # Add light objects around the place for objects that will be baked
        light_distance = context.scene.export_light_distance
        bpy.ops.object.light_add(type='POINT', location=(light_distance, 0, 0))
        bpy.ops.object.light_add(type='POINT', location=(-light_distance, 0, 0))
        bpy.ops.object.light_add(type='POINT', location=(0, light_distance, 0))
        bpy.ops.object.light_add(type='POINT', location=(0, -light_distance, 0))
        bpy.ops.object.light_add(type='POINT', location=(0, 0, light_distance))
        bpy.ops.object.light_add(type='POINT', location=(0, 0, -light_distance))
        
        # Change light objects properties
        bpy.ops.object.select_by_type(type='LIGHT')
        for object in context.selected_objects:
            object.data.energy = context.scene.export_light_power
            object.data.shadow_soft_size = 0
            object.data.cycles.cast_shadow = False
        
        bpy.context.window_manager.progress_begin(0, len(context.scene.input_files))
        
        # Loop through the Input Files and export textures
        for index, file in enumerate(context.scene.input_files, 1):

            bpy.context.window_manager.progress_update(index)
            
            # Set export properties
            file_name = os.path.splitext(os.path.basename(file.name))[0]
            object_fullname = os.path.join(context.scene.output_folder.path,f'{file_name}.obj')
            image_fullname = os.path.join(context.scene.output_folder.path,f'{file_name}.{context.scene.export_image_extension.lower()}')
            
            # Change the context for adding new object
            context.area.ui_type = 'VIEW_3D'
            bpy.ops.object.mode_set(mode='OBJECT') 
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_by_type(type='MESH')       
            bpy.ops.object.delete() 
            
            # Import object from file
            bpy.ops.import_scene.obj(filepath=file.name)
            
            # Make object active for enabling edit mode
            for object in context.selected_objects:
                context.view_layer.objects.active = object
            
            # Activate the smart project
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.uv.smart_project(island_margin=0.05)
       
             # Change the context for adding new texture image
            context.area.ui_type = 'UV'
            bpy.ops.uv.select_all(action='SELECT')
            
            # Activate the pack islands and make new image
            bpy.ops.uv.pack_islands()
            bpy.ops.image.new(name=file_name, width=context.scene.export_image_size, height=context.scene.export_image_size)
            
            # Change the context for adding new shader nodes
            context.area.ui_type = 'ShaderNodeTree'
            
            # Add the image texture node and add the image to it
            for material in bpy.data.materials:
                context.object.active_material.name = material.name
                
                material.use_nodes = True
                mat_nodes = material.node_tree.nodes
                 
                node = mat_nodes.new('ShaderNodeTexImage')
                node.location = (300,100)
                node.image = bpy.data.images[file_name]

            # Change the context for baking and export image
            context.area.ui_type = 'UV'
            bpy.ops.uv.select_all(action='SELECT')
            
            # Set render properties
            context.scene.render.engine = 'CYCLES'
            context.scene.cycles.bake_type = 'COMBINED'
            
            # Bake texture, save object and image texture
            bpy.ops.object.bake()
            bpy.ops.export_scene.obj(filepath=object_fullname)
            bpy.ops.image.save_as(filepath=image_fullname)             
        
        bpy.context.window_manager.progress_end()
        
        # Change the context after export
        context.area.ui_type = 'VIEW_3D'
        bpy.ops.object.mode_set(mode='OBJECT')
    
        return {'FINISHED'}

# All Classes for register and unregister
classes = (
    TextureExportInputOperator,
    TextureExportOutputProperty,
    TextureExportExportOperator,
    TextureExportPanel
) 

# Register for Classes and Properties   
def register():
    # Classes register
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Properties register
    bpy.types.Scene.input_files = bpy.props.CollectionProperty(name='Input Files', type=bpy.types.OperatorFileListElement)
    bpy.types.Scene.output_folder = bpy.props.PointerProperty(name='Output Folder', type=TextureExportOutputProperty)
    bpy.types.Scene.export_light_power = bpy.props.IntProperty(name="Light Power", default=2000, min=0)
    bpy.types.Scene.export_light_distance = bpy.props.IntProperty(name="Light Distance", default=10, min=0)
    bpy.types.Scene.export_image_size = bpy.props.IntProperty(name="Image Size", default=1024, min=32)
    bpy.types.Scene.export_image_extension = bpy.props.EnumProperty(
        name="Image Extension",
        items = (
            ('PNG', 'png', 'Export texture extension'),
            ('JPG', 'jpg', 'Export texture extension')
        ),
        default='PNG'
    )

# Unregister for Classes and Properties 
def unregister():
    # Classes unregister
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Properties unregister
    del bpy.types.Scene.input_files
    del bpy.types.Scene.output_folder
    del bpy.types.Scene.export_light_power
    del bpy.types.Scene.export_light_distance
    del bpy.types.Scene.export_image_size
    del bpy.types.Scene.export_image_extension
 
 
if __name__ == '__main__':
    register()