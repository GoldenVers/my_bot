import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'my_bot'  # Your package name

    # path to the yaml bridge file
    bridge_config = os.path.join(
        get_package_share_directory(package_name),
        'config', 'bridge.yaml'
    )

    # Path to the XACRO file
    xacro_file = os.path.join(
        get_package_share_directory(package_name),
        'description', 'robot.urdf.xacro'  
    )

    # Use a writable directory for output
    output_dir = os.path.join(os.getcwd(), 'generated')  
    os.makedirs(output_dir, exist_ok=True)  

    # Path to the URDF and SDF files
    urdf_file = os.path.join(output_dir, 'robot.urdf')
    sdf_file = os.path.join(output_dir, 'robot.sdf')

    # Convert XACRO to URDF
    if not os.path.exists(urdf_file):
        os.system(f'xacro {xacro_file} > {urdf_file}')
    
    # Check if URDF was generated successfully
    if os.path.exists(urdf_file):
        # Convert URDF to SDF
        if not os.path.exists(sdf_file):
            os.system(f'gz sdf -p {urdf_file} > {sdf_file}')
    else:
        print("Error: URDF file was not generated!")

    # Include the robot_state_publisher launch file
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory(package_name), 'launch', 'rsp.launch.py')
        ]),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Start Gazebo Fortress
    gazebo = ExecuteProcess(
        cmd=['ign', 'gazebo', '-r', os.path.join(
            get_package_share_directory(package_name),
            'worlds', 'empty.world'  
        )],
        output='screen'
    )

    # Spawn the robot
    spawn_entity = ExecuteProcess(
        cmd=[
            'ign', 'service', '-s', '/world/default/create',
            '--reqtype', 'ignition.msgs.EntityFactory',
            '--reptype', 'ignition.msgs.Boolean',
            '--timeout', '1000',
            '--req', f'sdf_filename: "{sdf_file}", name: "my_bot"'
        ],
        output='screen'
    )



    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        
    ])