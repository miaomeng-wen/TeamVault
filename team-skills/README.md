# team-skills · 团队智能体技能

本目录存放团队版智能体技能的源码，随 vault 走 Git 版本管理，**本机不直接运行**——先复制到个人 skills 目录再使用。

## 技能清单

| 技能 | 职责 | 形态 |
| --- | --- | --- |
| `source-intake` | 从 DOI、URL、PDF 链接或人工元数据创建/补全文献笔记 | SKILL.md（流程型） |
| `vault-qa` | 文献库规范巡检（frontmatter/命名/查重） | SKILL.md + Python 脚本 |
| `team-digest` | 生成团队周报到 `08_Daily` | SKILL.md（流程型，无脚本） |

脚本使用 Python 3.9+ 标准库，无第三方依赖。

## 安装（每个成员本机一次）

前置：已完成 `CONTRIBUTING.md` 第二节（vault 已 clone，团队文件库链接可访问）。

### 技能目录对照

技能必须复制到**你所用 agent 客户端**的用户级技能目录，各客户端路径不同：

| agent 客户端 | 用户级技能目录 |
| --- | --- |
| WorkBuddy AI | `%USERPROFILE%\.workbuddy-ai\skills` |
| Codex | `%USERPROFILE%\.codex\skills` |

不确定就用客户端的技能/插件设置页确认目录位置；换客户端后需重新复制一次。

### 复制命令（PowerShell）

先把 `$dst` 改成本机实际技能目录，再执行：

```powershell
$src = "E:\TeamVault\team-skills"
$dst = "$env:USERPROFILE\.workbuddy-ai\skills"   # 按上表改为你的客户端目录
New-Item -ItemType Directory -Force -Path $dst | Out-Null
Copy-Item "$src\source-intake" $dst -Recurse -Force
Copy-Item "$src\vault-qa" $dst -Recurse -Force
Copy-Item "$src\team-digest" $dst -Recurse -Force
```

安装后重启 agent 会话（或重新加载 skills）即可按名称调用。

## 更新

技能随 vault 更新（`skill:` 前缀提交）。成员 `git pull` 后重新执行上面的复制命令即可。

## 注意

- 核心流程不需要 API Key；未来接入文件服务时，凭据只放各成员本机 `config/.env`。
- `source-intake` 默认不上传、移动或删除团队文件库中的文件。
