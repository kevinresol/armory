import shutil
import os
import stat
import bpy
import arm.utils

assets = []
reserved_names = ['return.']
khafile_defs = []
khafile_defs_last = []
embedded_data = []
shaders = []
shaders_last = []
shaders_external = []
shader_datas = []
shader_passes = []
shader_passes_assets = {}
shader_cons = {}

def reset():
    global assets
    global khafile_defs
    global khafile_defs_last
    global embedded_data
    global shaders
    global shaders_last
    global shaders_external
    global shader_datas
    global shader_passes
    global shader_cons
    assets = []
    khafile_defs_last = khafile_defs
    khafile_defs = []
    embedded_data = []
    shaders_last = shaders
    shaders = []
    shaders_external = []
    shader_datas = []
    shader_passes = []
    shader_cons = {}
    shader_cons['mesh_vert'] = []
    shader_cons['depth_vert'] = []
    shader_cons['depth_frag'] = []
    shader_cons['voxel_vert'] = []
    shader_cons['voxel_frag'] = []
    shader_cons['voxel_geom'] = []

def add(file):
    global assets
    if file in assets:
        return
    base = os.path.basename(file)
    for f in assets:
        if f.endswith(base):
            print('Armory Warning: Asset name "{0}" already exists, skipping'.format(base))
            return
    assets.append(file)
    # Reserved file name
    for f in reserved_names:
        if f in file:
            print('Armory Warning: File "{0}" contains reserved keyword, this will break C++ builds!'.format(file))

def add_khafile_def(d):
    global khafile_defs
    if d not in khafile_defs:
        khafile_defs.append(d)

def add_embedded_data(file):
    global embedded_data
    if file not in embedded_data:
        embedded_data.append(file)

def add_shader(file):
    global shaders
    global shaders_last
    if file not in shaders:
        shaders.append(file)

def add_shader_data(file):
    global shader_datas
    if file not in shader_datas:
        shader_datas.append(file)

def add_shader_pass(data_name):
    global shader_passes
    # Shader data for passes are written into single shader_datas.arm file
    add_shader_data(arm.utils.build_dir() + '/compiled/Shaders/shader_datas.arm')
    if data_name not in shader_passes:
        shader_passes.append(data_name)

def add_shader_external(file):
    global shaders_external
    shaders_external.append(file)
    name = file.split('/')[-1].split('\\')[-1]
    add_shader(arm.utils.build_dir() + '/compiled/Shaders/' + name)

invalidate_enabled = True # Disable invalidating during build process

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def invalidate_shader_cache(self, context):
    # compiled.glsl changed, recompile all shaders next time
    global invalidate_enabled
    if invalidate_enabled == False:
        return
    # import traceback
    # traceback.print_stack()
    fp = arm.utils.get_fp_build()
    if os.path.isdir(fp + '/compiled/Shaders'):
        shutil.rmtree(fp + '/compiled/Shaders', onerror=remove_readonly)
    if os.path.isdir(fp + '/debug/html5-resources'):
        shutil.rmtree(fp + '/debug/html5-resources', onerror=remove_readonly)
    if os.path.isdir(fp + '/krom-resources'):
        shutil.rmtree(fp + '/krom-resources', onerror=remove_readonly)
    if os.path.isdir(fp + '/debug/krom-resources'):
        shutil.rmtree(fp + '/debug/krom-resources', onerror=remove_readonly)
    if os.path.isdir(fp + '/windows-resources'):
        shutil.rmtree(fp + '/windows-resources', onerror=remove_readonly)
    if os.path.isdir(fp + '/linux-resources'):
        shutil.rmtree(fp + '/linux-resources', onerror=remove_readonly)
    if os.path.isdir(fp + '/osx-resources'):
        shutil.rmtree(fp + '/osx-resources', onerror=remove_readonly)

def invalidate_compiled_data(self, context):
    global invalidate_enabled
    if invalidate_enabled == False:
        return
    fp = arm.utils.get_fp_build()
    if os.path.isdir(fp + '/compiled'):
        shutil.rmtree(fp + '/compiled', onerror=remove_readonly)

def invalidate_mesh_data(self, context):
    fp = arm.utils.get_fp_build()
    if os.path.isdir(fp + '/compiled/Assets/meshes'):
        shutil.rmtree(fp + '/compiled/Assets/meshes', onerror=remove_readonly)

def invalidate_envmap_data(self, context):
    fp = arm.utils.get_fp_build()
    if os.path.isdir(fp + '/compiled/Assets/envmaps'):
        shutil.rmtree(fp + '/compiled/Assets/envmaps', onerror=remove_readonly)

def shader_equal(sh, ar, shtype):
    # Merge equal shaders
    for e in ar:
        if sh.is_equal(e):
            sh.context.data[shtype] = e.context.data[shtype]
            sh.is_linked = True
            return
    ar.append(sh)

def vs_equal(c, ar):
    shader_equal(c.vert, ar, 'vertex_shader')

def fs_equal(c, ar):
    shader_equal(c.frag, ar, 'fragment_shader')

def gs_equal(c, ar):
    shader_equal(c.geom, ar, 'geometry_shader')

def tcs_equal(c, ar):
    shader_equal(c.tesc, ar, 'tesscontrol_shader')

def tes_equal(c, ar):
    shader_equal(c.tese, ar, 'tesseval_shader')
