---
name: twin-effects
description: Use when adding scan, energy-flow, outline, explosion, clipping, focus, or digital-twin effects to an existing 3D web scene without duplicating assets or losing state on reset.
---

# 数字孪生特效

同一场景、明确数据来源、可退出可复位。特效是对事实的表达层，不是构件身份或现场测量的替代品。

参考[长丰最终版](https://szls-changfeng.maip.top/EMS-changfeng/?twin=1#/page/ems-overview)与[版本清单](https://szls-changfeng.maip.top/version.json)（2026-10-28为V1.4.12）：已有场景原位增强、五栋导航、XYZ正反剖切/高度带、按需家具内景、模拟报警和可中断巡演。不要照抄旧本地候选或把源网站功能当新项目已实现。

## 集成契约

- 接收已有 scene/renderer/camera/canvas/资源注册表，不再次加载完整园区，也不另建隐藏WebGL上下文。
- 每个对象使用稳定 semanticId；展示编号与数据主键分离，不以名称近似匹配直接绑定生产设备。
- 数据必须注明 live/recorded/simulated/demo/unknown，带来源、单位、时间戳和质量码；无现场源时标“演示/模拟”。
- 修改前快照相机位置/目标/FOV、控制器状态、节点TRS、visible、material引用、裁剪参数和后处理开关。
- 同时保留原背景、environment、曝光、灯光、原自动运镜与回调；退出恢复进入前视图，不是随意调用默认相机。最终版“高度带”只按网格高度筛选，概念内景按代理尺度等比绑定，不宣称BIM层/实测还原。

## 特效选择

| 效果 | 方法 | 必查 |
| --- | --- | --- |
| 聚焦/轮廓 | 语义选择集、深度轮廓或边线 | 不以半透明整楼掩盖错误选择 |
| 扫描 | 世界坐标扫描面/局部着色 | 世界矩阵、法线、遮挡和低端GPU |
| 能流 | 实例化箭头/沿曲线粒子 | 方向来源、运动上限、模拟标签 |
| 分层/爆炸 | 从基线TRS计算偏移 | 不累加transform，不破坏父子坐标 |
| 剖切 | 明确世界/局部平面、可选截面 | 结构内景未知时不伪称真实BIM |

## 生命周期

建立 `idle → entering → active → exiting → idle` 状态机。相互排斥模式明确处理，连续点击不得重复注册事件。

进入：读取一次基线 → 创建本模式拥有的材质副本/临时几何 → 登记所有权 → 应用效果。

退出：取消本模式timer/RAF/监听器 → 移除临时对象 → 只dispose自己创建的资源 → 恢复原材质引用/TRS/显隐/相机/裁剪 → 清空注册表。

共享源geometry/texture不归特效所有，不得dispose。材质clone仍可能引用源纹理；释放材质不等于允许释放纹理。资源必须区分借用与拥有，不用“遍历全场景全部销毁”解决泄漏。

## 验证

1. 同一初态下逐个进入退出至少三轮；计数renderer/context、模型网络请求、objects、materials、textures、监听器、RAF。
2. 比较退出后快照：TRS、visible、material引用、camera/controls、clipping/后处理。像素对照需固定随机种子、时钟和曝光；时间相关画面不直接求完全相等。
3. 记录设备、浏览器、视口/DPR、版本、交互路径，测首帧/帧时间分位数与内存趋势。固定步录制不能替代实时测量。
4. shader error、共享资源被释放、退出后偏移、重复请求、计数持续增长均阻止发布。
5. 交付开关/复位、语义映射、资源所有权表、数据模式说明、性能/三轮复位日志及明确未验项。
