# Zsh 配置模块

## 模块化设计说明

Zsh 配置文件采用模块化设计，将不同功能的配置拆分为独立的模块文件，便于管理和维护。不再依赖 oh-my-zsh，使用自定义的模块加载系统。

## 目录结构

```md
zsh/
├── zshrc                    # 主配置文件（只负责加载模块）
├── config/                  # 配置模块目录
│   ├── loader.zsh           # 模块加载器（提供 load_module 函数）
│   ├── options.zsh          # Zsh 选项配置
│   ├── environment.zsh       # 环境变量和 PATH 配置
│   ├── history.zsh          # 历史记录配置
│   ├── completion.zsh       # 补全配置
│   ├── editor.zsh           # 编辑器配置
│   ├── functions.zsh       # 自定义函数
│   ├── prompt.zsh           # 提示符配置（支持 starship）
│   └── plugins.zsh           # 插件加载（替代 oh-my-zsh）
└── plugins/                  # 自定义插件目录（可选）
```

## 模块说明

### loader.zsh

- 提供 `load_module` 函数用于加载单个模块
- 提供 `load_modules` 函数用于批量加载模块
- 提供 `module_exists` 函数用于检查模块是否存在

### options.zsh

- 配置 Zsh 的各种选项
- 目录导航选项（auto_cd, auto_pushd）
- 通配符选项（extended_glob）
- 输入/输出选项（correct, no_beep）

### environment.zsh

- 设置 PATH 环境变量
- 添加常用路径（~/.local/bin, ~/.cargo/bin, ~/.pixi/bin）
- 设置 uv 和 pip 的镜像源（清华源）
- 设置语言环境

### history.zsh

- 配置历史记录大小（HISTSIZE, SAVEHIST）
- 设置历史记录选项（忽略重复、共享历史等）

### completion.zsh

- 启用并配置 Zsh 补全系统
- 设置补全样式和选项
- 配置补全缓存以提高性能

### editor.zsh

- 设置默认编辑器（优先 helix/hx，然后是 nvim/vim）
- 创建 `edit` 别名

### functions.zsh

- `yy` - 使用 yazi 打开当前目录
- `vpn-proxy` - 设置代理（默认端口 7897）
- `no-proxy` - 清除代理设置
- 配置 scoop 的 git bin 路径（Windows）

### prompt.zsh

- 自动检测并加载 starship 提示符（如果可用）
- 如果没有 starship，使用简单的自定义提示符（包含 git 分支信息）

### plugins.zsh

- 提供插件加载功能（替代 oh-my-zsh）
- 自动加载 zsh-autosuggestions 和 zsh-syntax-highlighting（如果存在）
- 提供 `load_plugin` 和 `load_plugins` 函数

### 加载所有模块

主配置文件会自动加载所有模块，无需额外操作。

### 禁用某个模块

在主配置文件 `zshrc` 中注释掉对应的加载行：

```zsh
# 禁用插件模块
# load_module "plugins"
```

### 添加新模块

1. 在 `config/` 目录下创建新的 `.zsh` 文件
2. 在主配置文件中添加加载语句：

```zsh
load_module "your-module"
```

### 加载自定义插件

在 `plugins.zsh` 或自定义模块中使用：

```zsh
load_plugin "your-plugin"
```

或者批量加载：

```zsh
load_plugins "plugin1" "plugin2" "plugin3"
```

## 与 oh-my-zsh 的区别

1. **轻量级**：只加载需要的功能，不加载整个框架
2. **模块化**：每个功能独立成模块，易于管理
3. **可定制**：完全控制加载顺序和内容
4. **性能**：启动速度更快，占用资源更少

## 优势

1. **模块化**：每个模块独立，职责清晰
2. **可维护**：修改某个功能只需要编辑对应的模块文件
3. **可扩展**：轻松添加新模块，不影响现有配置
4. **可禁用**：通过注释即可禁用某个模块，无需删除代码
5. **不依赖 oh-my-zsh**：完全独立的配置系统
