# team-skills · 团队智能体技能

本目录存放团队版智能体技能的源码，随 vault 走 Git 版本管理，**本机不直接运行**——先复制到个人 skills 目录再使用。

## 技能清单

| 技能 | 职责 | 形态 |
| --- | --- | --- |
| `zotero-team-fetcher` | 从 Zotero 群组库只读抓条目/分类/附件 | SKILL.md + Python 脚本 |
| `vault-qa` | 文献库规范巡检（frontmatter/命名/查重） | SKILL.md + Python 脚本 |
| `team-digest` | 生成团队周报到 `08_Daily` | SKILL.md（流程型，无脚本） |

脚本均为 Python 3.9+ 纯标准库，无第三方依赖；对 Zotero 只读。

## 安装（每个成员本机一次）

前置：已完成 `CONTRIBUTING.md` 第二节（vault 已 clone、`config/.env` 已填写）。

PowerShell：

```powershell
$src = "E:\TeamVault\team-skills"
$dst = "$env:USERPROFILE\.zcode\skills"
Copy-Item "$src\zotero-team-fetcher" $dst -Recurse -Force
Copy-Item "$src\vault-qa" $dst -Recurse -Force
Copy-Item "$src\team-digest" $dst -Recurse -Force
```

安装后重启 agent 会话（或重新加载 skills）即可按名称调用。

## 更新

技能随 vault 更新（`skill:` 前缀提交）。成员 `git pull` 后重新执行上面的复制命令即可。

## 注意

- `config/.env` 不随 Git 分发，每台机器单独填写。
- 脚本对 `zotero.sqlite` / `storage` 严格只读，这是 `AGENTS.md` 规定的铁律；发现任何技能试图写入请立即停止并上报。
