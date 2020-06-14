# Texture Export Blender Plugin

Texture Export Blender Plugin for exporting textures as images in PNG or JPG format. Plugin's primary use is to export texture image(png, jpg), object(obj) and texture materials(mtl) for game engines.

![Texture Export Blender Plugin Screenshot](https://raw.githubusercontent.com/markokosticdev/texture-export-blender-plugin/master/texture_export.png)

# Installation

1.  Download [the script](http://dl.dropboxusercontent.com/u/23340323/add_Window.py) (Right-click on the link or on the page it is on and choose  _Save As..._) and save it with a `.py` extension.
2.  Open _User Preferences_ (Edit > Preferences > Add-ons) and click on  _Install..._. Then navigate to the file you downloaded and select it.
3. Restart Blender and you will find plugin (View3D > Toolbar > Texture Export)


# Usage

1. Click on _Input_ and in import dialog select files(obj) for exporting texture
2. Change _Output_ folder path to match your needs _(optional)_
3. Change _Light Power_ of Point Lights around the place for objects that will be baked _(optional)_
4. Change _Light Distance_ of Point Lights around the place for objects that will be baked _(optional)_
5. Change _Image Size_ of the exporting textures, size is in pixels and represented as size x size _(optional)_
6. Change _Image Extension_ of the exporting textures _(optional)_

# Todo

 - [ ] Add Progress Bar
 - [ ] Fix UI freezing
 - [ ] Improve Lights
 - [ ] Improve Texture Shading


# Contributing

Please feel free to fork and contribute to the plugin. If you are not a developer but know a better way to do texture export manually, contact me to improve plugin together. :wink:
