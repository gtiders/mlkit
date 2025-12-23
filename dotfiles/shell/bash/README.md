# Bash 配置系统

简洁高效的模块化 bash 配置管理系统。

## 目录结构

```
bash/
├── config/          # 配置模块目录
│   ├── loader.bash  # 模块加载器（核心）
│   ├── fzf.bash     # FZF 配置模块
│   ├── starship.bash # Starship 提示符模块
│   ├── aliases.bash # 别名配置
│   └── functions.bash # 自定义函数
└── plugins/         # 插件目录
```

## 使用方法

### 在 .bashrc 中加载

```bash
# 加载 bash 配置系统
BASH_CONFIG_DIR="${HOME}/software/mlkit/dotfiles/shell/bash/config"
if [[ -f "${BASH_CONFIG_DIR}/loader.bash" ]]; then
    source "${BASH_CONFIG_DIR}/loader.bash"
    
    # 加载需要的模块
    load_module aliases      # 别名
    load_module functions    # 自定义函数
    load_module fzf          # FZF 配置
    load_module starship     # Starship 提示符
fi
```
```

### 模块管理

```bash
# 加载模块
load_module <模块名>

# 列出所有可用模块
list_modules

# 加载插件
load_plugin <插件名>
```

### FZF 模块使用

```bash
# 安装/拉取 fzf-tab-completion
fzf_tab_install

# 更新 fzf-tab-completion
fzf_tab_install update

# 删除 fzf-tab-completion
fzf_tab_install remove
```

### Starship 模块

Starship 模块会自动检测 starship 是否已安装：
- 如果已安装，自动初始化 starship 提示符
- 如果未安装，会显示安装提示信息

安装 starship：
```bash
curl -sS https://starship.rs/install.sh | sh
```

## 创建新模块

1. 在 `config/` 目录下创建 `<模块名>.bash` 文件
2. 在 `.bashrc` 中添加 `load_module <模块名>`
3. 如需卸载，注释掉对应的 `load_module` 行即可

## 特点

- ✅ 简洁明了，易于理解
- ✅ 模块化设计，方便管理
- ✅ 支持动态加载和卸载
- ✅ 自动检测已加载模块，避免重复加载
- ✅ 内置 FZF 配置和安装工具

