# 本地模型安装与离线运行

资料核对日期：2026-10-28。

本文给出两条彼此独立的本地路径：Ollama 用于文本推理；Qwen3-TTS 用于语音合成。命令是可复现教程，不是本仓库的自动安装脚本。本次编写仅核对官方文档和 Python 语法，**没有安装库、下载权重或调用模型**，因此不能把下文当成任何平台已经实跑通过的证明。

## 先做四项检查

1. **架构**：Apple Silicon 才走 MLX-Audio；NVIDIA CUDA 主机才走官方 `qwen-tts` CUDA 示例。Intel Mac、AMD GPU 或纯 CPU 不应照抄其中任一路径。
2. **磁盘**：先看模型页的文件清单和许可证，再预留“权重体积 + 下载临时文件 + 输出音频 + 至少数 GB 余量”。0.6B Base 官方 Hugging Face 文件页当前显示仓库约 2.52 GB、主权重约 1.83 GB；转换后的 MLX 权重体积可能不同，下载前仍以所选模型页为准。
3. **内存／显存**：参数量不是运行峰值。若发生 OOM，先换更小模型或更低精度的官方转换，不要假定磁盘放得下就一定能运行。
4. **许可证与声音权利**：逐一检查运行库、具体 checkpoint、参考音频和输出用途。官方 Qwen 0.6B Base 模型页在核对日标注 Apache-2.0；MLX 社区转换也应打开自己的模型卡复核，不能只继承上游结论。克隆声音前还必须拥有说话人授权与参考素材使用权。

常用自检：

```bash
# macOS / Linux
uname -s
uname -m
python3 --version
df -h .
```

```powershell
# Windows PowerShell
[System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture
py --version
Get-PSDrive -PSProvider FileSystem
```

## 路径 A：Ollama 本地文本推理

Ollama 同时支持本地与云端模型。本文只使用已下载到本机的模型、`127.0.0.1:11434` 回环 API，不使用以 `:cloud` 结尾的模型，也不创建云 API Key。官方文档给出的本地 API 基址是 `http://localhost:11434/api`，本地请求不需要授权头。

### 安装

优先从 [Ollama 官方下载页](https://ollama.com/download) 获取当前安装器并查看系统要求。

**macOS**

- 官方当前要求 macOS 14 Sonoma 或更新版本。
- 从下载页取得 `.dmg`，拖入 Applications 并首次启动；或在审阅官方脚本后使用下载页给出的命令。

```bash
ollama --version
```

**Windows**

- 从官方下载页运行 Windows 安装器；当前官方也给出 PowerShell 安装方式。企业环境应先按组织规则审阅脚本。

```powershell
irm https://ollama.com/install.ps1 | iex
ollama --version
```

**Linux**

- 先在 [Linux 下载页](https://ollama.com/download/linux) 查看脚本源码或手动安装说明，再执行：

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama --version
```

以上安装命令需要联网。若安全策略不允许管道执行远程脚本，请改用官方手动安装包并校验其来源。

### 有意下载一个本地模型

在 [Ollama 模型库](https://ollama.com/search) 选择模型与量化版本，先阅读来源、许可证、能力和页面标注的体积，再替换占位符：

```bash
ollama pull <model-name>
ollama list
ollama show <model-name>
ollama run <model-name> "只用一句话解释数字孪生。"
```

`pull` 是明确的网络下载动作；不要把 `:cloud` 模型当成本地模型。下载后可用 `ollama list` 核对名称与体积，用 `ollama ps` 查看实际加载到 CPU／GPU 的比例。

### 只监听回环地址

默认服务应只供本机使用。不要设置 `OLLAMA_HOST=0.0.0.0:11434`，不要配置反向代理、端口转发或公网隧道。若以前改过配置，恢复为回环地址后重启 Ollama：

```bash
OLLAMA_HOST=127.0.0.1:11434 ollama serve
```

Windows PowerShell 临时会话：

```powershell
$env:OLLAMA_HOST = "127.0.0.1:11434"
ollama serve
```

另开终端检查 API：

```bash
curl --fail http://127.0.0.1:11434/api/tags
curl --fail http://127.0.0.1:11434/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"model":"<model-name>","messages":[{"role":"user","content":"用一句话说明当前是本地推理。"}],"stream":false}'
```

macOS／Linux 可额外检查监听；输出应是 `127.0.0.1:11434` 或 `::1:11434`，不应是 `0.0.0.0:11434`：

```bash
lsof -nP -iTCP:11434 -sTCP:LISTEN
```

Windows：

```powershell
Get-NetTCPConnection -LocalPort 11434 -State Listen
```

### 证明“下载后可离线”

1. 联网完成安装与 `ollama pull`，记录 `ollama list` 和模型名。
2. 关闭 Wi-Fi／拔掉网线，确认没有 VPN、代理或移动热点。
3. 使用同一个本地模型运行 CLI 和 `127.0.0.1` API 冒烟。
4. 若程序仍尝试登录或访问 `https://ollama.com`，检查是否误选 `:cloud` 模型或云端基址。

离线运行不等于安装、更新和首次拉取也离线；也不等于所用应用没有其他联网功能。

## 路径 B：Apple Silicon 上的 MLX-Audio + Qwen3-TTS

MLX-Audio 官方要求 Apple Silicon Mac 和 Python 3.10+。本教程使用独立 Python 3.12 环境，避免污染项目或系统 Python。WAV 输出不要求 ffmpeg；只有保存 MP3、FLAC、OGG、Opus 等格式时才需要它。

### 1. 确认架构并创建隔离环境

```bash
uname -m
# 必须是 arm64；若是 x86_64，请停止走本节。

python3.12 -m venv .venv-mlx-audio
source .venv-mlx-audio/bin/activate
python -m pip install --upgrade pip
python -m pip install mlx-audio soundfile
python -m pip check
```

如果没有 `python3.12`，先通过可信的 Python 发行渠道安装；不要用 Rosetta 下的 x86 Python 混装 MLX。生产项目应在首次验证后把 `python -m pip freeze` 和所用模型 revision 写入自己的锁定记录。

### 2. 选择正确的 Qwen3-TTS 变体

| 目标 | 模型 | 调用方式 | 关键输入 |
| --- | --- | --- | --- |
| 克隆一段已获授权的参考声音 | **Base** | `generate`（MLX）／`generate_voice_clone`（官方 CUDA） | `ref_audio` + 与音频严格一致的 `ref_text` |
| 使用官方内置 speaker 并控制情绪 | **CustomVoice** | `generate_custom_voice` | `speaker`、`language`、可选 `instruct` |
| 从文字描述设计新声音 | **VoiceDesign** | `generate_voice_design` | `language` + `instruct` |

只有 Base 支持参考音频克隆。给 Base 同时传 `speaker` 会造成配置冲突。CustomVoice 的 `Vivian` 只是官方内置 speaker 名称，不能因此宣称与某个项目参考音色相同。

### 3. 有意下载并固定本地目录

直接用模型 ID 首次加载会联网自动下载。更可审计的做法是在联网阶段明确下载到项目外的模型目录，记录模型卡、许可证、revision、文件总大小与哈希，再在代码中只传本地路径。以下命令只展示官方 Hugging Face CLI 流程，请在检查模型卡后自行执行：

```bash
python -m pip install "huggingface_hub[hf_xet]"
hf download \
  mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16 --dry-run
# 先在模型页取得实际commit，替换下面占位符；不要直接执行未替换命令。
hf download \
  mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16 \
  --revision <actual-model-commit> \
  --local-dir ./models/Qwen3-TTS-12Hz-0.6B-Base-bf16
du -sh ./models/Qwen3-TTS-12Hz-0.6B-Base-bf16
```

模型转换仓库和 revision 会变化；下载前以 [MLX-Audio Qwen3-TTS 文档](https://github.com/Blaizzy/mlx-audio/blob/main/mlx_audio/tts/models/qwen3_tts/README.md) 当前列出的模型为准，并打开对应模型卡检查许可证。

### 4. Base 最小生成示例

准备一段你有权使用的短 WAV `reference.wav`，并把 `ref_text` 改成逐字匹配的转写。下面示例与 MLX-Audio 当前 Qwen3-TTS 接口一致；本次只做了 Python 语法检查，**没有导入运行库、加载权重或生成音频**。

```python
from pathlib import Path

import numpy as np
import soundfile as sf
from mlx_audio.tts.utils import load_model

model_dir = Path("models/Qwen3-TTS-12Hz-0.6B-Base-bf16")
model = load_model(str(model_dir))
results = list(
    model.generate(
        text="这是一次本地语音合成冒烟测试。",
        ref_audio="reference.wav",
        ref_text="这里填写与参考音频逐字一致的文本。",
    )
)
result = results[0]
sf.write("smoke.wav", np.asarray(result.audio), result.sample_rate)
```

先用一句短文本测试，确认 `smoke.wav` 可解码、采样率合理、无削波，再扩大文本。模型能加载不代表音色一致、发音自然或可公开使用；这些需要人工听审与权利审核。

### 5. 离线复测

完成依赖和权重下载后断网，并强制 Hugging Face 离线模式：

```bash
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
python smoke_mlx_tts.py
```

代码必须引用本地模型目录、本地参考音频，不能引用 URL。若仍联网，先停止并定位缺失文件，不要把自动回退到网络误判为离线成功。

## 路径 C：NVIDIA CUDA 上的官方 `qwen-tts`

这是 Qwen 团队的官方 PyTorch 路径，适合受支持的 NVIDIA CUDA 环境。本文没有在任何 CUDA 主机上实跑，驱动、CUDA、PyTorch 和 GPU 兼容性应按目标机器重新核对。

### 1. 创建官方建议的 Python 3.12 隔离环境

```bash
conda create -n qwen3-tts python=3.12 -y
conda activate qwen3-tts
python -m pip install --upgrade pip
python -m pip install -U qwen-tts
python -m pip check
nvidia-smi
```

### 2. FlashAttention 不是必装项

官方将 FlashAttention 2 列为性能建议，但要求兼容硬件，并且模型以 `torch.float16` 或 `torch.bfloat16` 加载。它不是 Apple Silicon／MLX 的安装步骤；Mac 上不要照抄 `flash-attn`。CUDA 主机若不满足条件，省略安装并使用 `attn_implementation="sdpa"`；只有兼容时才考虑：

```bash
MAX_JOBS=4 python -m pip install -U flash-attn --no-build-isolation
```

### 3. 官方 Base 克隆最小示例

先在联网阶段按官方仓库说明下载模型到本地目录；离线运行时将 `model_dir` 指向该目录。以下代码仅验证过 Python 语法，没有运行模型：

```python
from pathlib import Path

import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel

model_dir = Path("models/Qwen3-TTS-12Hz-0.6B-Base")
model = Qwen3TTSModel.from_pretrained(
    str(model_dir),
    device_map="cuda:0",
    dtype=torch.bfloat16,
    attn_implementation="sdpa",
)
wavs, sample_rate = model.generate_voice_clone(
    text="这是一次本地语音合成冒烟测试。",
    language="Chinese",
    ref_audio="reference.wav",
    ref_text="这里填写与参考音频逐字一致的文本。",
)
sf.write("smoke-cuda.wav", wavs[0], sample_rate)
```

若目标 GPU 不适合 BF16，不能盲目改精度；先查目标 PyTorch／GPU 支持矩阵和 Qwen 官方问题记录。

## 常见错误与停止条件

| 症状 | 常见原因 | 处理 |
| --- | --- | --- |
| MLX 报架构或动态库错误 | Intel Mac、Rosetta x86 Python、混用环境 | `uname -m` 与 `python -c 'import platform; print(platform.machine())'` 都应为 `arm64`；重建原生隔离环境 |
| `No module named ...` | 没激活正确 venv／conda，或安装中断 | 核对 `which python`／`Get-Command python`，再运行 `python -m pip check` |
| 首次运行卡在下载 | 权重未提前下载、网络受限或磁盘不足 | 停止进程，检查模型卡、剩余空间和缓存；改为显式下载到本地目录 |
| 断网时报找不到文件 | checkpoint、tokenizer 或配置未完整缓存 | 回到联网阶段补齐并记录文件清单；不要偷偷解除离线模式 |
| CUDA OOM | 模型／精度／上下文超出显存 | 停止，选更小的官方模型或合适精度；不要靠无限交换空间冒充可用 |
| `flash-attn` 构建失败 | GPU、CUDA、编译器或精度不兼容 | 卸掉可选包并用 SDPA；Mac 不安装 FlashAttention |
| Base 报 voice/speaker 冲突 | 把 CustomVoice 参数传给 Base | Base 只传参考音频与转写；内置 speaker 改用 CustomVoice |
| 有音频但不像参考声音 | 转写不匹配、参考质量差、采样随机性或模型差异 | 修正逐字转写和干净参考，固定版本与参数，做人工盲听；不以“成功生成”替代相似度验收 |
| API 可从局域网访问 | 监听了 `0.0.0.0` 或配置了代理／隧道 | 立即停止服务，改回 `127.0.0.1`，移除端口转发并复查监听 |

遇到未知模型代码、许可证不清、权重来源不明、参考声音授权不明、服务意外监听非回环或离线阶段仍发起网络请求时，应停止而不是继续试错。

## 缓存与卸载

- Ollama 官方默认模型目录：macOS `~/.ollama/models`，Linux `/usr/share/ollama/.ollama/models`，Windows `%USERPROFILE%\.ollama\models`。先用 `ollama list`／`ollama rm <model-name>` 管理，不要手删共享 blob。
- Python 环境可通过删除独立 `.venv-mlx-audio` 或 `conda env remove -n qwen3-tts` 回收；先确认没有其他项目引用。
- Hugging Face／ModelScope 缓存可能被多个环境共享。删除前先列出真实占用和引用，不要把缓存目录一锅端。
- 参考音频与输出音频按项目的数据分级和授权处理，不能随教程或公开仓库打包。

## 官方来源

- [Ollama Quickstart](https://docs.ollama.com/quickstart)
- [Ollama API：本地与云端基址](https://docs.ollama.com/api/introduction)
- [Ollama FAQ：监听配置与模型目录](https://docs.ollama.com/faq)
- [Qwen3-TTS 官方仓库](https://github.com/QwenLM/Qwen3-TTS)
- [Qwen3-TTS 0.6B Base 官方模型卡](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base)
- [MLX-Audio 官方仓库](https://github.com/Blaizzy/mlx-audio)
- [MLX-Audio 的 Qwen3-TTS 接口说明](https://github.com/Blaizzy/mlx-audio/blob/main/mlx_audio/tts/models/qwen3_tts/README.md)
- [Hugging Face CLI：下载与固定 revision](https://huggingface.co/docs/huggingface_hub/guides/cli)
