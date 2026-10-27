import os
import subprocess
import tempfile
from xml.sax.saxutils import escape
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def setup(context, *args, **kwargs):
    model_share = get_package_share_directory('model')
    world = LaunchConfiguration('world_path').perform(context)
    gui = LaunchConfiguration('gui').perform(context).lower() == 'true'
    name = LaunchConfiguration('name').perform(context)
    pose = LaunchConfiguration('pose').perform(context)
    runtime = tempfile.mkdtemp(prefix='rexrov_fortress_')
    xacro = os.path.join(model_share, 'urdf', 'rexrov_dave.urdf.xacro')
    urdf = os.path.join(runtime, f'{name}.urdf')
    subprocess.run(['xacro', xacro, f'namespace:={name}', '-o', urdf], check=True)
    with open(world, encoding='utf-8') as f:
        text = f.read()
    include = ('    <include>\n'
               f'      <uri>{escape(urdf)}</uri>\n'
               f'      <name>{escape(name)}</name>\n'
               f'      <pose>{escape(pose)}</pose>\n'
               '    </include>\n')
    generated = os.path.join(runtime, 'rexrov_world.sdf')
    with open(generated, 'w', encoding='utf-8') as f:
        f.write(text.replace('  </world>', include + '  </world>', 1))
    gz_args = '-r ' + generated + ('' if gui else ' -s')
    pkg = get_package_share_directory('ros_gz_sim')
    return [IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(pkg, 'launch', 'gz_sim.launch.py')), launch_arguments={'gz_args': gz_args}.items())]

def generate_launch_description():
    share = get_package_share_directory('model')
    return LaunchDescription([
        DeclareLaunchArgument('world_path', default_value=os.path.join(share, 'worlds', 'dave_ocean_waves_fortress.world')),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('name', default_value='rexrov'),
        DeclareLaunchArgument('pose', default_value='0 0 -5 0 0 0'),
        OpaqueFunction(function=setup),
    ])
