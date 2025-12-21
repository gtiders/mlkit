# 补全配置模块

# 启用补全系统
autoload -Uz compinit

# 检查补全转储文件是否需要更新（每天检查一次）
if [[ -n "${ZSH_COMPDUMP}"(#qN.mh+24) ]]; then
    compinit -d "${ZSH_COMPDUMP}"
else
    compinit -C -d "${ZSH_COMPDUMP}"
fi

# 补全选项
setopt auto_menu                  # 自动显示补全菜单
setopt complete_in_word           # 在单词中间补全
setopt always_to_end              # 补全后光标移到末尾

# 补全样式
zstyle ':completion:*' menu select                    # 使用菜单选择
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'  # 不区分大小写
zstyle ':completion:*' list-colors ''                 # 使用默认颜色
zstyle ':completion:*' special-dirs true              # 补全特殊目录
zstyle ':completion:*' rehash true                    # 自动重新哈希

# 缓存补全结果以提高性能
zstyle ':completion:*' use-cache yes
zstyle ':completion:*' cache-path "${HOME}/.cache/zsh/cache"

