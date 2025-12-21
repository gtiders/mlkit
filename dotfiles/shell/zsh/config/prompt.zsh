# 提示符配置模块

# 检测 starship 是否可用并设置自动加载
if command -v starship >/dev/null 2>&1; then
    eval "$(starship init zsh)"
else
    # 如果没有 starship，使用 robbyrussell 风格的提示符
    autoload -Uz vcs_info
    precmd() { vcs_info }
    
    # Git 信息格式
    zstyle ':vcs_info:git:*' formats 'git:(%b)'
    zstyle ':vcs_info:git:*' actionformats 'git:(%b|%a)'
    
    # Git 状态检查函数
    git_prompt_info() {
        local ref dirty
        if [[ -n $(git rev-parse --git-dir 2>/dev/null) ]]; then
            ref=$(git symbolic-ref HEAD 2>/dev/null) || ref="$(git rev-parse --short HEAD 2>/dev/null)"
            ref=${ref#refs/heads/}
            
            if [[ -n $(git status --porcelain 2>/dev/null) ]]; then
                dirty=" %F{yellow}✗%f"
            else
                dirty=""
            fi
            
            echo "%F{blue}git:(%F{red}${ref}%F{blue})${dirty}%f"
        fi
    }
    
    setopt PROMPT_SUBST
    
    # robbyrussell 风格的提示符
    # 绿色箭头表示上一条命令成功，红色表示失败
    PROMPT='%(?:%F{green}➜%f :%F{red}➜%f ) %F{cyan}%c%f $(git_prompt_info)'
fi

