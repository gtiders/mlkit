# PowerShell

```pwsh
# 允许 Windows 执行任何脚本（用户级别 bypass）: Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser
# PowerShell Profile Configuration
# 模块化设计：通过加载模块来配置 PowerShell

# 获取配置文件所在目录
$ProfileDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ConfigDir = Join-Path $ProfileDir "config"

# 加载配置模块
# 只需要一行就可以加载整个模块
. (Join-Path $ConfigDir "editor.ps1")      # 编辑器配置
. (Join-Path $ConfigDir "environment.ps1") # 环境变量配置
. (Join-Path $ConfigDir "functions.ps1")   # 自定义函数
. (Join-Path $ConfigDir "tools.ps1")       # 工具自动加载

# 如果需要禁用某个模块，只需要注释掉对应的行即可
# 例如：不加载 starship 和 pixi，注释掉 tools.ps1
# . (Join-Path $ConfigDir "tools.ps1")
```

## 模块化设计说明

PowerShell 配置文件采用模块化设计，将不同功能的配置拆分为独立的模块文件，便于管理和维护。

## 目录结构

```md
powershell/
├── Microsoft.PowerShell_profile.ps1  # 主配置文件（只负责加载模块）
└── config/                           # 配置模块目录
    ├── editor.ps1                    # 编辑器配置
    ├── environment.ps1               # 环境变量和 PATH 配置
    ├── functions.ps1                 # 自定义函数
    └── tools.ps1                      # 工具自动加载（starship, pixi）
```

## 模块说明

### editor.ps1

- 设置默认编辑器（优先 helix/hx，然后是 nvim/vim）
- 创建 `edit` 别名

### environment.ps1

- 设置 uv 环境代理（清华源）
- 添加 PATH 路径：
  - `~/.local/bin`
  - `~/.pixi/bin`
  - `~/.cargo/bin`
  - scoop 的 git bin 路径（用于 yazi）

### functions.ps1

- `yy` - 使用 yazi 打开当前目录
- `vpn-proxy` - 设置代理（默认端口 7897）
- `no-proxy` - 清除代理设置

### tools.ps1

- 自动检测并加载 starship 提示符
- 自动检测并加载 pixi 补全（如果支持）

## 使用方法

### 加载所有模块

主配置文件会自动加载所有模块，无需额外操作。

### 禁用某个模块

在主配置文件 `Microsoft.PowerShell_profile.ps1` 中注释掉对应的加载行：

```powershell
# 禁用工具自动加载模块
# . (Join-Path $ConfigDir "tools.ps1")
```

### 添加新模块

1. 在 `config/` 目录下创建新的 `.ps1` 文件
2. 在主配置文件中添加加载语句：

```powershell
. (Join-Path $ConfigDir "your-module.ps1")
```

## 优势

1. **模块化**：每个模块独立，职责清晰
2. **可维护**：修改某个功能只需要编辑对应的模块文件
3. **可扩展**：轻松添加新模块，不影响现有配置
4. **可禁用**：通过注释即可禁用某个模块，无需删除代码
