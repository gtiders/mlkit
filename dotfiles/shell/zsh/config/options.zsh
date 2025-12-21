# Zsh 选项配置模块

# 目录选项
setopt auto_cd                    # 自动 cd 到目录
setopt auto_pushd                 # 自动推送目录到目录栈
setopt pushd_ignore_dups           # 忽略重复的目录栈条目
setopt cdable_vars                # 允许 cd 到变量名

# 通配符选项
setopt extended_glob              # 启用扩展通配符
setopt glob_dots                  # 匹配隐藏文件

# 输入/输出选项
setopt correct                     # 自动纠正命令拼写
setopt correct_all                 # 纠正所有参数
setopt no_beep                     # 禁用 beep 声

# 作业控制选项
setopt no_hup                      # 后台作业在 shell 退出时不挂起
setopt no_check_jobs               # 不检查后台作业

# 其他选项
setopt interactive_comments        # 允许在交互式 shell 中使用注释

