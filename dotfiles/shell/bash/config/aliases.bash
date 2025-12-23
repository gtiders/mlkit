#!/bin/bash
# 别名配置模块

# 常用命令别名
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

# 如果系统有这些命令，添加别名
command -v vim &> /dev/null && alias vi='vim'
command -v nvim &> /dev/null && alias vim='nvim'
command -v rg &> /dev/null && alias grep='rg'
command -v bat &> /dev/null && alias cat='bat'
command -v exa &> /dev/null && alias ls='exa'
command -v fzf &> /dev/null && alias fzf='fzf --height 40% --layout=reverse --border'
command -v helix &> /dev/null && alias hx='helix'
