# my-zsh-config

```bash
# 获取配置文件所在目录
# 配置文件目录固定为 ~/.config/zsh/config
ZSH_CONFIG_DIR="${HOME}/.config/zsh/config"

# 加载模块加载器
source "${ZSH_CONFIG_DIR}/loader.zsh"

# 加载配置模块
# 只需要一行就可以加载整个模块
load_module "options"      # Zsh 选项配置
load_module "environment"  # 环境变量配置
load_module "history"       # 历史记录配置
load_module "completion"    # 补全配置
load_module "editor"        # 编辑器配置
load_module "functions"     # 自定义函数
load_module "prompt"        # 提示符配置
load_module "plugins"       # 插件加载

# 如果需要禁用某个模块，只需要注释掉对应的行即可
# 例如：不加载插件，注释掉 plugins
# load_module "plugins"
```
