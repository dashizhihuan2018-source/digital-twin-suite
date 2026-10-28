# 数字孪生技能套件 V1.0.0

从长丰产业园最终项目提炼的五个独立技能：轻量模型、真实产品影片、穿越镜头和同场景可逆特效。只采用核对后的最终网站与已发布成果，不以过程版或另造园区充当案例。已发布技术示例与正式人工验收分开标注。

[下载技能套件](https://github.com/dashizhihuan2018-source/digital-twin-suite/releases/latest) · [长丰最终网站](https://szls-changfeng.maip.top/EMS-changfeng/?twin=1#/page/ems-overview) · [验证记录](docs/validation.md)

## 真实项目示例

![长丰真实项目海报V1.3.0，仅供人工查看，非正式验收作品](https://raw.githubusercontent.com/dashizhihuan2018-source/fpv-video-skill/f1e49e3cb38ac001433db2244c905d77f5598881/media/changfeng/poster-v1.3.0.png)

https://github.com/user-attachments/assets/59b0d548-94f7-4efa-b0c3-7ba8c73ee697

[同版R5视频文件](https://github.com/dashizhihuan2018-source/fpv-video-skill/blob/f1e49e3cb38ac001433db2244c905d77f5598881/media/changfeng/changfeng-r5-demo.mp4)为1080p/30fps/922帧、约30.73秒的有损分享压缩版。两媒体均已获准非商业公开展示，仍待正式人工视听验收，完整画面HUMAN-ONLY，不交AI查看或处理；不是V1.4.12新录屏。海报二维码指向原FPV技能仓库。

© 2026 Nankong。保留[原媒体许可](https://github.com/dashizhihuan2018-source/fpv-video-skill/blob/f1e49e3cb38ac001433db2244c905d77f5598881/media/changfeng/LICENSE.md)与[来源和完整配乐署名](https://github.com/dashizhihuan2018-source/fpv-video-skill/blob/f1e49e3cb38ac001433db2244c905d77f5598881/media/changfeng/README.md)。Kinetic by Punch Deck | https://soundcloud.com/punch-deck · Royalty Free Music by https://www.free-stock-music.com · [CC BY 3.0 Unported](https://creativecommons.org/licenses/by/3.0/deed.en_US)。截取约33.97秒起、音量降低约6.15dB、淡入0.4秒/淡出1.4秒；作者未背书。媒体及第三方作品不按本套件文档许可重新授权。

## 最终成果选择

- 网站：[长丰最终入口](https://szls-changfeng.maip.top/EMS-changfeng/?twin=1#/page/ems-overview)，2026-10-28核对为V1.4.12；修正了用户要求删除的7组装饰树。
- 模型：以该版实际引用的建筑、环境GLB为准；文件名版本较旧不代表已淘汰。保持源模型只读，不随套件重分发。
- 产品成片：选定V3.5.5，4K/30fps/1075帧；有明确私有约定，不公开嵌入或转存。
- 公开媒体：真实项目海报V1.3.0、R5已发布分享版；原聊天已授权指定媒体非商业公开展示，路径/哈希见[允许清单](docs/final-artifacts.json)。仍待人工视听验收，不称正式验收作品或V1.4.12新录屏。
- 误选的程序化园区、演示影片和海报已撤出活动发布目录。

详见[最终成果选材规则](docs/final-selection.md)与[长丰最终版经验](docs/changfeng-case.md)。

## 五个技能

| 技能 | 内容 |
| --- | --- |
| [digital-twin](skills/digital-twin/SKILL.md) | 总体流程、真实性、权利与验收 |
| [twin-model-lightweight](skills/twin-model-lightweight/SKILL.md) | 模型盘点、近景与语义保护、可逆优化 |
| [twin-product-film](skills/twin-product-film/SKILL.md) | 最终产品实录、台词时点、原生像素与帧时钟 |
| [twin-fpv-film](skills/twin-fpv-film/SKILL.md) | 连续航线、视角与净空；区分已发布示例与正式验收 |
| [twin-effects](skills/twin-effects/SKILL.md) | 复用同一场景、资源所有权与复位 |

## 教程

- [本地大模型安装](docs/local-models.md)：Ollama、Apple Silicon语音和CUDA路线；未声称全平台实跑。
- [默认配音参考](docs/voice-reference.md)：PDFMaster公开合成旁白的试听区间与复现参数；不打包私有WAV。

## 本地预览安装与测试

需要Python 3.10+，工具使用标准库；安装器默认只预览，不覆盖已有技能。

```bash
python3 scripts/install.py
python3 scripts/install.py --apply
python3 -B -m unittest discover -s tests -v
```

安装后保留各技能完整目录。默认读取`CODEX_HOME/skills`，否则为`~/.codex/skills`；也可用`--dest <目录>`指定位置，已有同名技能绝不覆盖。

## 构建展示站

Python 3.10+标准库即可构建，无npm安装或模型下载。允许清单只包含选定的两份媒体；未知文件、符号链接及哈希不符会在修改输出前阻止构建。

```bash
python3 -B scripts/build.py
python3 -B -m http.server 8000 --bind 127.0.0.1 --directory dist
```

构建产物含HTML教程、技能原文、同版海报/视频、无媒体的技能安装ZIP及逐文件SHA256清单。浏览器回归脚本需要单独可用的Playwright与Chrome；通过`PLAYWRIGHT_MODULE`指定已安装的模块路径，不随技能套件安装浏览器。

## 公开边界

未确认版本或公开权限的媒体不进入发布包。产品影片V3.5.5仍私有；R5和海报仅按既有许可完整非商业展示、保留署名与来源，HUMAN-only完整画面不得交AI处理。网页可浏览不代表允许重新分发源模型、贴图、声音和视频。

原创内容采用[非商业交流许可](LICENSE)，不是MIT/Apache；第三方权利见[说明](THIRD_PARTY_NOTICES.md)。自动测试、真实界面验证、听审、用户接受与公开授权分别记录。
