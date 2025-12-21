# 历史记录配置模块

# 历史记录大小
HISTSIZE=100000
SAVEHIST=100000
HISTFILE="${HOME}/.zsh_history"

# 历史记录选项
setopt hist_ignore_all_dups      # 忽略重复的历史记录
setopt hist_ignore_space          # 忽略以空格开头的命令
setopt hist_verify                # 执行历史命令前先显示
setopt share_history              # 在多个 shell 会话间共享历史
setopt append_history             # 追加而不是覆盖历史文件
setopt inc_append_history         # 立即追加历史记录
setopt extended_history           # 记录时间戳和持续时间

