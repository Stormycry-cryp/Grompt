<div align="center">

# Grompt

#### 一个给 Agent 用的自迭代生图提示词 Skill

[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](./LICENSE)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-8B5CF6?style=for-the-badge)](https://agentskills.io)
[![Cold Start](https://img.shields.io/badge/Cold_Start-awesome--gpt--image--2-10B981?style=for-the-badge)](#致谢)

![Codex](https://img.shields.io/badge/Codex-Skill-10B981?style=flat-square&logo=openai&logoColor=white)
![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-D97706?style=flat-square&logo=anthropic&logoColor=white)
![OpenCode](https://img.shields.io/badge/OpenCode-Skill-3B82F6?style=flat-square)
![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-8B5CF6?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)

</div>

我自己做图、调图、写生图提示词时想要的一套东西。

不是那种“给你一堆风格词自己拼”的提示词库，也不是一个固定模板生成器。它更像一个会翻参考库的视觉提示词导演：你给它一个作图任务，它先判断这张图到底需要什么，再去提示词参考库里找 3-5 个相近案例，抽取里面真正有用的视觉基因和结构，然后重新写一个专属于当前任务的新提示词。

如果当前 Agent 有可用的生图能力，它会继续调用生图 provider。  
如果没有，它也不会假装能生图，而是直接进入 prompt-only 模式，把可用的新提示词交给你。

你可以很随意地说：

```text
帮我做一张中文信息图，主题是城市生命系统，竖版，信息层级要清楚
做一个酸奶新品海报，干净高级一点，中文可读
给这个活动写一版适合 gpt-image-2 的提示词，参考成熟案例
生成一张赛博朋克音乐节主视觉，如果不能生图就先给我 prompt
```

Agent 应该做的不是直接硬写 prompt，而是先查参考、再提取、再合成。

---

## 它解决什么

生图提示词最烦的是几件事：

- 用户一句话很短，但作图需求其实很复杂。
- 风格词堆得很多，真正控制构图、层级、材质、文字和画面关系的内容很少。
- 每次写 prompt 都从零开始，前面跑出来的好结果没有沉淀。
- Agent 很容易凭感觉编一个“看起来很会写”的 prompt，但没有参考依据。
- 没有生图 provider 时，Agent 还可能把“生成了”说得像真的一样。

`Grompt` 的思路很简单：  
**让 Agent 先做参考检索和结构提取，再写提示词。**

它会按这个流程工作：

1. 分析用户任务里的作图目标、画面类型、风格、主体、文字、比例和约束。
2. 分层查看参考库标签，而不是一次性把整个库塞进上下文。
3. 找出 3-5 个最接近当前任务的参考提示词。
4. 从参考里抽取视觉基因：构图、主体关系、光线、材质、镜头、文字策略、版式策略。
5. 从参考里抽取提示词结构：先描述什么、怎么约束文字、怎么控制风格、怎么写负向限制。
6. 合成一个新的、只服务当前任务的提示词。
7. 如果生图能力可用，就调用 provider 生图；不可用就只输出提示词。
8. 完成后询问用户：这次结果要不要加入参考库。

它的关键不是“收藏提示词”，而是让 Agent 学会复用提示词背后的结构。

---

## 它包含什么

这个仓库本质上是一个 Agent Skill 文件夹：

```text
SKILL.md
agents/openai.yaml
references/index.md
references/prompt_cases.json
references/templates.json
scripts/install_check.py
scripts/synthesize_prompt.py
scripts/library_query.py
scripts/library_add.py
scripts/library_common.py
tests/
```

几个核心文件：

- `SKILL.md` 是 Agent 真正会读的工作规则。
- `references/prompt_cases.json` 是冷启动提示词案例库，共 503 条。
- `references/templates.json` 保存分类、风格、场景和模板线索。
- `scripts/synthesize_prompt.py` 负责分析任务、检索参考、抽取基因、合成新提示词。
- `scripts/library_query.py` 负责分层浏览参考库标签和提示词。
- `scripts/library_add.py` 负责把用户确认过的新提示词加入本地参考库。
- `scripts/install_check.py` 负责探测当前环境有没有可用的生图能力。

自迭代产生的数据会写到：

```text
references/user_prompt_library.json
```

这个文件默认被 `.gitignore` 忽略。  
也就是说，仓库里的冷启动库保持不变，你自己的好结果会留在本地。

---

## 安装方式

在支持 `SKILL.md` / Agent Skills 结构的 Agent 里直接说：

```text
帮我安装这个 skill：https://github.com/Stormycry-cryp/Grompt
```

如果你的 Agent 能自动安装，它应该会自己 clone 到对应目录。  
如果要手动安装，常见目录如下：

| Agent | 常见安装目录 |
|---|---|
| Codex | `~/.codex/skills/grompt` |
| Claude Code | `~/.claude/skills/grompt` |
| OpenCode | `~/.config/opencode/skills/grompt` |
| OpenClaw | `~/.openclaw/skills/grompt` |
| 其他 Agent | 放到它能扫描 `SKILL.md` 的 skills 目录 |

macOS / Linux 示例：

```bash
git clone https://github.com/Stormycry-cryp/Grompt.git
mkdir -p ~/.codex/skills
cp -R Grompt ~/.codex/skills/grompt
```

Windows PowerShell 示例：

```powershell
git clone https://github.com/Stormycry-cryp/Grompt.git
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse -Force .\Grompt "$env:USERPROFILE\.codex\skills\grompt"
```

如果你用的不是 Codex，把上面的 `.codex\skills` 换成对应 Agent 的 skills 目录即可。

---

## 怎么用

第一次使用时，可以直接跟 Agent 说：

```text
用 Grompt 给我做一张酸奶新品海报，中文主标题可读，画面要干净高级。如果不能生图，就先给我提示词。
```

Agent 应该先检测生图能力：

```bash
python <grompt-skill-folder>/scripts/install_check.py
```

如果检测到可用 provider，就继续生成图片。  
如果检测不到，它应该主动问你要不要提供生图 provider，并说明最好是 GPT Image 2 或兼容 GPT Image 2 的 provider。

如果你不想提供 provider，也可以继续让它只产出提示词：

```text
不用生图，先给我最终 prompt。
```

手动运行提示词合成：

```bash
python <grompt-skill-folder>/scripts/synthesize_prompt.py \
  --task "做一张城市生命系统信息图，要求信息结构清楚，中文标签可读，竖版" \
  --count 5 \
  --format markdown
```

---

## 分层查参考库

`Grompt` 不鼓励 Agent 一上来读取整个提示词库。

它应该渐进式查看：

1. 先看有哪些标签类型。
2. 再看某几个标签类型下有哪些具体标签。
3. 再看具体标签下面有哪些提示词摘要。
4. 最后只打开最相关的少数提示词。

对应命令：

```bash
python <grompt-skill-folder>/scripts/library_query.py --level types
```

```bash
python <grompt-skill-folder>/scripts/library_query.py \
  --level tags \
  --tag-type category
```

```bash
python <grompt-skill-folder>/scripts/library_query.py \
  --level prompts \
  --tag-type category \
  --tag "Charts & Infographics" \
  --limit 5
```

这样做的目的很朴素：  
**先看地图，再进房间，不要一上来把整栋楼搬进上下文。**

---

## 自迭代参考库

每次完成提示词或生图后，Agent 都应该问一句：

```text
这次结果要加入 Grompt 参考库吗？
```

只有用户明确同意，才写入本地参考库。

写入示例：

```bash
python <grompt-skill-folder>/scripts/library_add.py \
  --title "夜航计划音乐节海报" \
  --prompt "$FINAL_PROMPT" \
  --category "Posters & Typography" \
  --style "Poster" \
  --scene "Music" \
  --task "做一张赛博朋克音乐节海报" \
  --source "user-confirmed"
```

这部分是 `Grompt` 的长期价值：  
冷启动库负责一开始能用，你确认过的结果负责越用越贴近你自己的审美和任务类型。

---

## 生图 provider 规则

`Grompt` 优先推荐 GPT Image 2，或者兼容 GPT Image 2 行为的 provider。

原因很简单：这个 skill 的冷启动库来自 GPT Image 2 相关提示词案例，参考案例的写法、结构和约束都更贴近 GPT Image 2 的行为。

如果没有可用 provider：

- Agent 必须说明当前环境没有检测到生图能力。
- Agent 应该主动询问用户是否提供 provider。
- Agent 应该说明最好是 GPT Image 2。
- 如果用户不提供，Agent 也可以只交付提示词。

prompt-only 是正常完成路径，不是失败。

---

## Skill 规则

`Grompt` 的核心规则写在 [SKILL.md](./SKILL.md)。

几个关键点：

- skill 注册名是 `grompt`，用户可见名是 `Grompt`。
- 它是给所有 Agent / 系统用的，不绑定 Codex 路径。
- 所有脚本都可以通过 `<grompt-skill-folder>` 或 `GROMPT_DIR` 定位。
- 不能跳过参考检索直接编 prompt。
- 每次任务要选 3-5 个参考提示词。
- 要同时做视觉基因提取和提示词结构提取。
- 上游冷启动库保持不可变。
- 用户确认后的新提示词写入本地 `references/user_prompt_library.json`。
- 没有 provider 时要诚实说明，并进入 prompt-only 模式。

---

## 验证

运行测试：

```bash
python3 -m unittest discover -s tests -v
```

预期结果：

```text
Ran 7 tests
OK
```

如果你本地有 skill validator，也可以运行：

```bash
python3 /path/to/skill-creator/scripts/quick_validate.py /absolute/path/to/grompt
```

---

## 数据说明

冷启动语料来自 [`freestylefly/awesome-gpt-image-2`](https://github.com/freestylefly/awesome-gpt-image-2)，采集时对应 commit：

```text
5ffa75c6e22e804b54a462841dc3d7035d8584ed
```

打包时观察到的事实：

- 浅克隆 checkout 大小：`292M`
- `.git` 大小：`141M`
- 克隆后文件数：`621`
- 已索引提示词案例：`503`
- 图片目录案例图：`506`
- 生成提示词数据缺失案例 ID：`12`, `169`, `170`

这些数据只是说明冷启动库来源和整理过程。  
`Grompt` 不会把用户自己的提示词回写到上游库，也不会把本地自迭代数据提交到仓库。

---

## 适合谁

适合：

- 经常让 Agent 写生图 prompt 的人
- 想让 prompt 有参考依据，而不是凭空编的人
- 想做海报、信息图、产品图、角色图、场景图、封面图的人
- 想沉淀自己审美和高质量结果的人
- 没有固定生图 provider，但也想先稳定产出 prompt 的人
- 想让不同 Agent 都能复用同一套提示词工作流的人

不适合：

- 只想要一个静态提示词合集的人
- 不希望 Agent 做参考检索和分析的人
- 需要云端多人同步提示词库的人
- 需要保证所有模型都按同一方式理解 prompt 的人

---

## 致谢

特别感谢 [`freestylefly/awesome-gpt-image-2`](https://github.com/freestylefly/awesome-gpt-image-2)。

`Grompt` 的冷启动提示词数据库来自这个项目：初始案例、分类、风格、场景和模板参考，都让 `Grompt` 在还没有任何用户本地案例时就可以开始工作。

`Grompt` 是在这个公开提示词库之上做的一层 Agent 工作流、分层检索和提示词合成系统。  
上游语料保持不可变，用户确认后的新提示词会单独保存在本地参考库里。

---

## License

MIT
