# Zsh 插件目录

## 说明

此目录用于存放独立的 zsh 插件，不依赖 oh-my-zsh。

## 安装插件

### 方法 1：使用 git clone（推荐）

```bash
# 创建插件目录（如果不存在）
mkdir -p ~/.config/zsh/plugins

# 安装 zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-autosuggestions ~/.config/zsh/plugins/zsh-autosuggestions

# 安装 zsh-syntax-highlighting
git clone https://github.com/zsh-users/zsh-syntax-highlighting ~/.config/zsh/plugins/zsh-syntax-highlighting
```

### 方法 2：手动下载

1. 下载插件压缩包
2. 解压到 `~/.config/zsh/plugins/` 目录
3. 确保插件目录结构正确

## 插件目录结构

插件应该按照以下结构组织：

```
plugins/
├── zsh-autosuggestions/
│   └── zsh-autosuggestions.zsh
└── zsh-syntax-highlighting/
    └── zsh-syntax-highlighting.zsh
```

或者：

```
plugins/
├── zsh-autosuggestions/
│   └── zsh-autosuggestions.plugin.zsh
└── zsh-syntax-highlighting/
    └── zsh-syntax-highlighting.plugin.zsh
```

## 支持的插件格式

插件加载器会自动尝试以下路径：

1. `plugins/<插件名>/<插件名>.plugin.zsh`
2. `plugins/<插件名>/<插件名>.zsh`
3. `plugins/<插件名>.zsh`
4. 对于特定插件（zsh-autosuggestions, zsh-syntax-highlighting），会尝试 `plugins/<插件名>/<插件名>.zsh`

## 常用插件

### zsh-autosuggestions
自动建议插件，根据历史记录提供命令建议。

```bash
git clone https://github.com/zsh-users/zsh-autosuggestions ~/.config/zsh/plugins/zsh-autosuggestions
```

### zsh-syntax-highlighting
语法高亮插件，实时高亮命令。

```bash
git clone https://github.com/zsh-users/zsh-syntax-highlighting ~/.config/zsh/plugins/zsh-syntax-highlighting
```

**注意**：zsh-syntax-highlighting 必须在最后加载，配置文件已经处理了这一点。

## 使用 dotbot 管理

如果你使用 dotbot 管理配置文件，可以将插件目录添加到 dotbot 配置中，这样插件也会被版本控制管理。

## 手动加载插件

如果你想手动加载某个插件，可以在配置文件中使用：

```zsh
load_plugin "your-plugin-name"
```

或者批量加载：

```zsh
load_plugins "plugin1" "plugin2" "plugin3"
```

