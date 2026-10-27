# UUV Simulator ROV 核对结果

官方 UUV Simulator 仓库确实包含配置好的工作级 ROV：`rexrov`。它的默认演示入口是 `uuv_gazebo/launch/rexrov_demos/rexrov_default.launch`，另有 `rexrov_bop_panel.launch`、声呐和机械臂演示。

需要区分两类东西：

- `rexrov` 是真正的可运动 ROV，带推进器、浮力/水动力参数、控制器和手柄遥控。
- `rov_bop_panel` 是海底 BOP 面板场景中的 ROV 模型入口，BOP 面板本身是环境目标，不是另一套浮力系统。

原仓库的 ROV 依赖：

- ROS 1（Kinetic/Lunar/Melodic）和 Gazebo Classic；launch 文件是 XML，节点使用 `rospy`/`roslaunch`。
- `libuuv_underwater_object_ros_plugin.so`：Fossen 水动力、浮力、附加质量、线性/二次阻尼。
- `uuv_thruster_manager`：根据 TF 中的推进器位置自动生成 6 自由度推进器分配矩阵。
- ROV 控制器：级联 PID、非线性 PID、滑模、模型反馈线性化、6-DOF PID 等。
- `rexrov` 关键参数来自 `rexrov.gazebo.xacro`：排水体积约 `1.83826 m³`，浮心 `z=0.3 m`，海水密度 `1028 kg/m³`，并给出了完整 6×6 附加质量矩阵、线性阻尼和二次阻尼。

## 在当前工程中的迁移策略

不能把 UUV Simulator 的 ROS 1 `.launch` 和 `libuuv_underwater_object_ros_plugin.so` 直接放进 ROS 2 Humble/Gazebo Fortress。迁移时应保留它最有价值的部分：

1. 复制 RexROV 的几何/碰撞体和推进器布局。
2. 将 `volume`、`center_of_buoyancy`、`fluid_density`、附加质量、阻尼参数转换到当前 `gz-sim-hydrodynamics-system` 和分层浮力插件。
3. 用当前工程的 ROS 2 `ros_gz_bridge` 替代 ROS 1 topic/plugin 接口。
4. 先提供键盘/定速推进器演示，再接入 6-DOF ROV 控制器；不要把 AUV 的单推进器+四舵面分配器直接套到 RexROV 上。

因此，后续最稳妥的展示目标是：在现有 ECA A9 仿真旁增加一个独立的 `rexrov_ros2` 演示包，先实现模型、浮力、8 推进器和 `/cmd_wrench` 接口，再逐步迁移 UUV 的控制器。
