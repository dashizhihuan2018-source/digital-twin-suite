---
name: twin-product-film
description: Use when producing or repairing a digital-twin product launch film, recording authentic interface operations, aligning visual reveals with narration, or verifying native resolution and unchanged frames.
---

# 数字孪生产品发布视频

用真实功能构建“问题—操作—价值—行动”的故事。先确认允许公开的功能、画面、配音与参考视频权利；参考节奏，不复制他人的镜头或品牌身份。

录制长丰同类功能时，以用户指定[最终网站](https://szls-changfeng.maip.top/EMS-changfeng/?twin=1#/page/ems-overview)为产品权威；2026-10-28网站为V1.4.12、模拟数据且无现场设备连接。选定V3.5.5是影片版本，不是网站版本。先从最终版真实操作取景。作者于2026-10-28追加[这份完整4K成片的公开要求](https://github.com/dashizhihuan2018-source/digital-twin-suite/releases/tag/changfeng-film-v3.5.5)，不开放原私有工程或源资产，不授权AI审片、截帧或加工。没有最终媒体或对应权限时列缺口，不另造园区或使用过程片补位。

## 输入与边界

- 目标观众、片长、画幅、发布端、语言、必须展示的功能与禁止披露内容。
- 锁定源码 commit、模型版本、场景初态、数据模式与输出目录；源片只读，小修复另存版本。
- 真实界面展示真实能力；模拟能流、概念内景、假数据明确标注，不以效果片冒充验收成果。
- 默认无背景音乐、原速原调。声音仅在有使用权的参考下复现；缺参考时交付静音样例并报告，不擅自替换真人或其他项目声音。

## 制作顺序

1. 写一页分镜：镜头编号、台词、真实操作、主体、眼点/目标/FOV、全局起止帧、画面标签。
2. 对每个功能先做可交互验证再录制。浏览器影片复用当前 renderer/canvas/模型，固定状态与随机种子。
3. 使用唯一时钟 `t = globalFrame / fps`；分段不能重置导致材质动画、粒子或转场跳变。固定时间步不代表实时帧率。
4. 按台词词点定义“完全可辨认”的画面时刻，不能只将三类设备平均三等分。允许叠化重叠，但镜头范围采用半开区间 `[start,end)`。
5. 登记 CSS 视口、DPR、WebGL backing size、源画面及封面像素、编码输出。放大封面单独披露；输出4K不等于输入原生4K。
6. 先出短样片检查主体与字幕，再全帧录制。推荐兼容输出 H.264 + yuv420p + faststart；静音示例不得伪装有配音。
7. 正常音量听审发音、口型/字幕与词点；技术通过不能替代视觉风格与用户接受。

## 附带时序校验器

本技能目录中执行：

```bash
python3 scripts/check_timeline.py timeline.json
ffprobe -v error -show_streams -show_format -of json output.mp4
ffmpeg -v error -i output.mp4 -f null -
```

`timeline.json` 最小例：

```json
{"fps":30,"frames":1075,"shots":[{"id":"solar","start":705,"end":851}],"anchors":[{"wordSeconds":24.52,"fullyVisibleFrame":735}]}
```

校验器只检查声明的范围、ID、词点先后，不识别语音、不证明目标真的清晰可见。识别结果和人工核验时间均要存证。

## 修复与交付

- 小修锁定允许变化帧、GOP影响区和音频包；直接拷贝帧查解码哈希，重编码区单独用相似度说明，不混称无损。
- 音轨包哈希与PTS、总帧数、黑场、长静音、网页播放error/stalled分别检查。
- 交付成片、封面、分镜、时序JSON、录制脚本、源版本、媒体哈希、版权清单和验证报告。
- 报告分开写：自动检查、人工视听、目标平台实播、用户接受；未知项保持待验，不标成全部通过。
