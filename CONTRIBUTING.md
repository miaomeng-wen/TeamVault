# 成员上手指南（CONTRIBUTING）

目标：30 分钟内完成全部安装，开始正常读写团队知识库。遇到问题先看文末"常见问题"，再在群里问。

## 一、安装基础软件（一次性）

1. **Obsidian**：<https://obsidian.md/download>，默认安装。
2. **Git**：<https://git-scm.com/download/win>，安装时全部默认选项。
3. **Zotero 7**：<https://www.zotero.org/download/>，默认安装。

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
  - Commit Message：`vault backup: {{date}}`

配置完手动点一次 "Commit-and-sync" 确认能通。

### 3. 加入 Zotero 群组库

1. 注册/登录 <https://www.zotero.org>，接受管理员发来的群组邀请邮件（或点邀请链接）。
2. 本机 Zotero → 编辑 → 设置 → 同步 → 登录同一账号 → 勾选 "同步群组库"。
3. 点右上角同步按钮，等待群组库条目/PDF 同步完成。

### 4. 配置本机密钥

```bat
copy config\.env.example config\.env
notepad config\.env
```

填写 `ZOTERO_GROUP_ID`（群组页 URL 中的数字）和 `ZOTERO_API_KEY`（在 <https://www.zotero.org/settings/keys/new> 创建，只需群组库 Read 权限）。`.env` 不会提交进 Git。

## 三、日常使用

### 认领并精读一篇论文

1. 打开 `04_Tables/待认领清单.md`，挑一篇无人认领的论文。
2. 让你的智能体执行 `zotero-team-fetcher` 抓取该条目 → 按模板生成 `02_Literature` 笔记，frontmatter 填你的 ID（`assignee`）和 `reading_status: reading`。
3. 精读、补全证据与页码跳转，完成后改 `reading_status: finished`。
4. 提交：让 agent 提交，或手动 `git add -A && git commit -m "notes: Khan_2025_xxx" && git push`。

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

### 创建 Zotero 群组库

1. <https://www.zotero.org/groups/> → Create New Group → 类型选 Private。
2. Members 页邀请成员（权限给 Read）。
3. 把原有个别库条目批量导入群组（Zotero 里全选 → 右键 → Add to Collection，先在群组库建好同名分类）。
4. 生成 API Key 并分发给成员各自填入自己的 `config/.env`（不要在群里发明文）。

## 五、常见问题

- **推送被拒 / 冲突**：先 `git pull --rebase`，解决冲突后 `git push`；看板类文件（04_Tables）冲突时随便取一边——它们是自动生成的，拉平后刷新即可。
- **看板不刷新**：确认 Dataview 插件已启用；`Ctrl+P → Reload app without saving`。
- **Zotero 同步空间满了**：免费版群组库 300MB。方案：PDF 放团队网盘/NAS，群组库只留元数据；或升级 Zotero Storage。
- **智能体没反应**：确认 `team-skills` 里的技能已安装到本机 skills 目录（见 `team-skills/README.md`），且 `config/.env` 已填写。
- **我不小心改坏了 04_Tables**：`git checkout -- 04_Tables/` 恢复即可。
