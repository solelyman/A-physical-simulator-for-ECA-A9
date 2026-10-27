# Ubuntu 22.04 / ROS 2 Humble 运行指南

## 版本选择

Ubuntu 22.04 使用 ROS 2 Humble + Gazebo Fortress。这是 ROS/Gazebo 官方
支持的组合，无需在 Humble 上强行安装 Harmonic。本仓库使用的
`ros_gz_sim` 接口以及浮力、水动力、推进器和 LiftDrag 系统在两个
组合中共用。

## 安装缺少的依赖

```bash
sudo apt update
sudo apt install ros-humble-ros-gz
```

本机已有 ROS 2 Humble，但目前缺少 `ros-humble-ros-gz-sim` 和
`ros-humble-ros-gz-bridge`。上面的元包会安装与 Humble 匹配的
Fortress 及 bridge。

## 编译

ROSIDL 在某些非 ASCII 工作区路径下会把 CMake 目标解析错。建议将
仓库放在纯英文路径，例如 `~/eca_a9_ws`：

```bash
cd ~/eca_a9_ws
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
python3 tests/test_vehicle_configuration.py
```

## 启动

首次展示建议先关闭 RViz，只启动 Gazebo：

```bash
ros2 launch auv_leaders_planner leaders_planner.launch.py gui:=true rviz:=false
```

如果现场网络不稳定，请在面试前至少启动一次，让 Gazebo Fuel 将
海底和水面模型缓存到本机。

## 姿态稳定修改

原分配器把 N·m 力矩除以常数 `3` 后直接当作 rad 舵角，导致大部分
俯仰命令都打到舵角上限，形成过冲。现在按实时纵向速度计算动压和
舵效，且设置 0.6 m/s 的最小控制速度。模型和控制器的质量/排水体积
也已统一为 100.8 kg / 0.0985 m³。

现场调参时优先调整 `vehicle_params.yaml` 中的：

- `allocator.min_control_speed`：低速时的虚拟舵效；
- `allocator.fin_lift_coefficient`：整体舵效；
- `controller_gains.k_theta` 和 `k_q`：俯仰跟踪与阻尼。

## DAVE / UUV Simulator 备选展示

原始 DAVE 和 UUV Simulator 主要是 ROS 1 + Gazebo Classic 技术栈。不建议在
面试前两天将它们混入当前 Humble 工作区。如必须展示原版 ROV，
使用独立的 Ubuntu 20.04 + ROS Noetic + Gazebo 11 容器/虚拟机，与本项目
分开。本仓库的 ECA A9 已保留 DAVE/UUV 的模型来源，但运行时不依赖
旧 DAVE 工作区。
