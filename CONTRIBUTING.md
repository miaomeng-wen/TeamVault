# 成员上手指南（CONTRIBUTING）

目标：30 分钟内完成全部安装，开始正常读写团队知识库。遇到问题先看文末"常见问题"，再在群里问。

## 一、安装基础软件（一次性）

1. **Obsidian**：<https://obsidian.md/download>，默认安装。
2. **Git**：<https://git-scm.com/download/win>，安装时全部默认选项。

## 二、加入知识库（一次性）

### 1. 克隆仓库并用 Obsidian 打开

```bat
git clone <仓库地址> E:\TeamVault
```

然后在 Obsidian 中：`打开其他仓库 → 打开本地文件夹作为仓库 → 选择 E:\TeamVault`。
信任仓库作者并启用社区插件。

### 2. 安装两个必装插件

Obsidian 设置 → 第三方插件 → 浏览：

- **Dataview**：看板和索引全靠它，装完设置里开启"自动刷新"。
- **Obsidian Git**：自动同步。建议配置：
  - Auto Pull Interval：`15` 分钟
  - Vault Backup Interval（自动 commit+push）：`30` 分钟
  - Commit Message：`vault backup: {{date}}`（自动备份专用前缀，不计入手工提交前缀规范，见 AGENTS.md）

配置完手动点一次 "Commit-and-sync" 确认能通。

### 3. 加入团队文件库

向管理员申请团队文件库权限，并确认：

- 能打开一份测试 PDF；
- 能复制稳定的 HTTPS 分享链接；
- 需要上传资料时拥有对应目录的写权限；
- 本地同步目录不会被提交进 TeamVault 的 Git 仓库。

### 4. 安装团队智能体技能

按 `team-skills/README.md` 把 `source-intake`、`vault-qa`、`team-digest` 安装到本机技能目录，然后重新打开 agent 会话。

## 三、日常使用

### 认领并精读一篇论文

1. 新来源：把 DOI、来源 URL、PDF 链接或书目信息交给 `source-intake`；它会按 `source_id` 查重并创建文献笔记。
2. 已建档来源：打开 `04_Tables/团队任务看板.md` 的"待认领"小节，挑一篇无人认领的笔记。
3. 在 frontmatter 填自己的 `assignee`（建议统一使用真实中文姓名（一人一标识，全库一致）），把 `reading_status` 改为 `reading`。
4. 精读并补全证据、页码和链接；终检通过后改为 `finished`。
5. 运行 `vault-qa`，无 ERR 后提交：`git add -A && git commit -m "notes: Khan_2025_xxx" && git push`。

### 新增 PDF

1. 按团队文件库规范上传 PDF，文件名优先包含 DOI 或 `source_id`。
2. 复制稳定链接到文献笔记的 `pdf_url`。
3. 不把 PDF、数据集等大文件复制进 TeamVault 仓库。

### 只想查资料

直接问智能体，它会检索 `02_Literature` 和 `04_Tables` 回答并给笔记链接；也可以自己用 Obsidian 全文搜索（`Ctrl+Shift+F`）。

## 四、管理员操作（仅首次）

### 创建远程私有仓库

1. GitHub（或 Gitee）→ New repository → Private → 不要初始化 README。
2. 在本目录执行：

```bat
git remote add origin https://github.com/<组织或用户>/<仓库名>.git
git push -u origin main
```

3. 邀请团队成员为仓库协作者（Settings → Collaborators）。
4. 若首次提交的作者信息是占位身份，推送前修正：

```bat
git config user.name  "你的名字"
git config user.email "你的邮箱"
git commit --amend --reset-author --no-edit
```

### 配置团队文件库

1. 使用单位已有的网盘、NAS、对象存储或其他受控文件服务。
2. 至少建立 `papers/` 与 `datasets/` 目录，并按团队角色设置权限。
3. 验证分享链接不会随成员本地同步路径变化。
4. 指定备份负责人、备份频率和恢复抽查周期。
5. 若服务需要 API Key，只放在成员本机 `config/.env`，不得提交或在群里明文分发。

## 五、常见问题

- **推送被拒 / 冲突**：先 `git pull --rebase`，解决冲突后 `git push`；看板类文件（04_Tables）冲突时随便取一边——它们是自动生成的，拉平后刷新即可。
- **看板不刷新**：确认 Dataview 插件已启用；`Ctrl+P → Reload app without saving`。
- **PDF 链接打不开**：先确认已登录团队文件库，再请管理员检查分享范围；不要用成员个人电脑的本地路径代替。
- **来源重复**：不要新建第二篇，按 `source_id` 找到原笔记并补全；无法判断时运行 `vault-qa`。
- **智能体没反应**：确认 `team-skills` 已安装到本机 `.codex/skills` 目录并重新打开会话。
- **我不小心改坏了 04_Tables**：`git checkout -- 04_Tables/` 恢复即可。
