# ECA A9 仿真启动说明（Ubuntu 22.04 / ROS 2 Humble）

工程目录：`/home/lu/eca_a9_ws`

## 1. 编译

```bash
cd /home/lu/eca_a9_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## 2. 启动三艘 AUV

推荐先使用无界面模式确认仿真稳定：

```bash
source /opt/ros/humble/setup.bash
source /home/lu/eca_a9_ws/install/setup.bash
ros2 launch auv_leaders_planner leaders_planner.launch.py \
  gui:=false current_predictor:=false
```

需要 Gazebo 图形界面时：

```bash
ros2 launch auv_leaders_planner leaders_planner.launch.py \
  gui:=true current_predictor:=false
```

如果当前桌面会话出现 EGL/OpenGL 警告并关闭 Gazebo，使用 `gui:=false`；控制器、桥接和浮力仍然完整运行。

## 3. 检查运行状态

```bash
ros2 topic echo /auv0/odom --once
ros2 topic echo /auv1/odom --once
ros2 topic echo /auv2/odom --once
```

## 3. 关闭仿真并释放内存

如果是从终端启动的，回到启动命令所在终端按 `Ctrl+C`，等待几秒即可。不要只关闭 Gazebo 窗口，因为 ROS 2 控制器和桥接节点可能仍在后台运行。

如果启动终端已经关闭，可以在新终端执行下面的清理命令：

```bash
pkill -f 'ros2 launch auv_leaders_planner' || true
pkill -f 'ign gazebo' || true
pkill -f 'ros_gz_bridge/parameter_bridge' || true
pkill -f 'leader_planner_node|sf_local_tracking|thruster_allocator|static_transform_publisher' || true
```

确认是否清理干净：

```bash
pgrep -af 'ign gazebo|parameter_bridge|leader_planner_node|sf_local_tracking|thruster_allocator' || true
free -h
```

录制 GIF 的 Python 进程在录制结束后会自动退出；如果中途停止，也可以按 `Ctrl+C`。

## 4. 浮力兼容说明

Humble 使用 Gazebo Fortress。Fortress 对运行中动态插入的 URDF 可能在 collision 尚未生成时记录零排水体积，因此本工程在启动 Gazebo 前把三艘 AUV 写入临时世界文件。这样保留了原项目的分层浮力：`z<0` 为密度 1025 的海水，`z>=0` 为空气。

模型碰撞体已按原参数校准到约 `0.0985 m³`，并将碰撞几何的浮心位置放在 `z=0.06 m`，与控制器使用的重心关系一致。

## 5. 海流预测节点

默认关闭 `current_predictor`，因为仓库中的旧 LSTM 权重要求 2 维输入，而旧脚本会传入 5 维。浮力、动力学、规划和多 AUV 控制不依赖这个节点。修复输入特征或替换权重后，可显式打开：

```bash
ros2 launch auv_leaders_planner leaders_planner.launch.py \
  gui:=false current_predictor:=true
```

## 6. 录制结果

已生成三艘 AUV 的 3D 轨迹 GIF：

`/home/lu/eca_a9_ws/eca_a9_three_auv_motion.gif`

该 GIF 使用三艘 AUV 的真实 `/odom` 数据绘制，棕色半透明平面表示约 `z=-95 m` 的海底。
