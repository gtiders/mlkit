#!/bin/bash
# FZF 配置模块
# 提供 fzf 配置、ctrl+r 历史搜索和 tab 补全功能

# 获取 fzf-tab-completion 目录（config 的同级别目录）
# BASH_CONFIG_DIR 由 loader.bash 定义
FZF_TAB_COMPLETION_DIR="$(dirname "$BASH_CONFIG_DIR")/fzf-tab-completion"
FZF_TAB_COMPLETION_REPO="https://github.com/lincheney/fzf-tab-completion.git"

# 初始化 fzf
_init_fzf() {
    # 检测 fzf 命令是否可用
    if ! command -v fzf &> /dev/null; then
        echo "提示: fzf 未安装，跳过 fzf 配置"
        return 1
    fi
    
    # Set up fzf key bindings and fuzzy completion
    eval "$(fzf --bash)"
    
    # 设置默认选项
    export FZF_DEFAULT_OPTS='--height 40% --layout=reverse --border'
    export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git 2>/dev/null || find . -type f 2>/dev/null'
    export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
    
    # 配置 ctrl+r 历史搜索功能
    if command -v rg &> /dev/null; then
        # 使用 ripgrep 进行内容搜索预览
        export FZF_CTRL_R_OPTS='--preview "echo {}" --preview-window down:3:hidden:wrap --bind "?:toggle-preview"'
    else
        # 基本的历史搜索配置
        export FZF_CTRL_R_OPTS=''
    fi
    
    return 0
}

# 安装/更新 fzf-tab-completion
# 用法: fzf_tab_install [update|remove]
fzf_tab_install() {
    local action="${1:-install}"
    
    if [[ "$action" == "update" ]] || [[ "$action" == "install" ]]; then
        echo "正在处理 fzf-tab-completion..."
        
        if [[ -d "$FZF_TAB_COMPLETION_DIR" ]]; then
            if [[ "$action" == "update" ]]; then
                echo "更新 fzf-tab-completion..."
                # 临时恢复 .git 目录进行更新
                if [[ -d "${FZF_TAB_COMPLETION_DIR}/.git" ]] || [[ -f "${FZF_TAB_COMPLETION_DIR}/.git" ]]; then
                    (cd "$FZF_TAB_COMPLETION_DIR" && git pull 2>/dev/null || echo "更新失败，请手动检查")
                else
                    # 如果没有 .git，重新克隆
                    rm -rf "$FZF_TAB_COMPLETION_DIR"
                    git clone "$FZF_TAB_COMPLETION_REPO" "$FZF_TAB_COMPLETION_DIR" 2>/dev/null || {
                        echo "克隆失败，请检查网络连接和 git 是否已安装"
                        return 1
                    }
                fi
                # 更新后删除 git 相关文件
                _remove_git_files
            else
                echo "fzf-tab-completion 已存在，使用 'fzf_tab_install update' 来更新"
            fi
        else
            echo "克隆 fzf-tab-completion 仓库..."
            git clone "$FZF_TAB_COMPLETION_REPO" "$FZF_TAB_COMPLETION_DIR" 2>/dev/null || {
                echo "克隆失败，请检查网络连接和 git 是否已安装"
                return 1
            }
            # 克隆后删除 git 相关文件
            _remove_git_files
        fi
        
        # 加载 bash 补全
        _load_fzf_tab_completion
    elif [[ "$action" == "remove" ]]; then
        if [[ -d "$FZF_TAB_COMPLETION_DIR" ]]; then
            rm -rf "$FZF_TAB_COMPLETION_DIR"
            echo "fzf-tab-completion 已删除"
        else
            echo "fzf-tab-completion 不存在"
        fi
    else
        echo "用法: fzf_tab_install [install|update|remove]"
    fi
}

# 删除 git 相关文件，使其不识别为 git 子仓库
_remove_git_files() {
    if [[ -d "$FZF_TAB_COMPLETION_DIR" ]]; then
        echo "删除 git 相关文件..."
        rm -rf "${FZF_TAB_COMPLETION_DIR}/.git"
        rm -f "${FZF_TAB_COMPLETION_DIR}/.gitignore"
        rm -f "${FZF_TAB_COMPLETION_DIR}/.gitattributes"
        echo "git 相关文件已删除"
    fi
}

# 加载 fzf-tab-completion
_load_fzf_tab_completion() {
    local completion_file="${FZF_TAB_COMPLETION_DIR}/bash/fzf-bash-completion.sh"
    
    if [[ -f "$completion_file" ]]; then
        source "$completion_file"
        # 绑定 tab 键到 fzf_bash_completion
        bind -x '"\t": fzf_bash_completion' 2>/dev/null
        return 0
    else
        echo "警告: 未找到 fzf-bash-completion.sh: ${completion_file}" >&2
        return 1
    fi
}

# 自动初始化和安装
if _init_fzf; then
    # 如果 fzf 可用，检查并安装 fzf-tab-completion
    if [[ ! -d "$FZF_TAB_COMPLETION_DIR" ]]; then
        # 自动安装（静默模式，不输出信息）
        fzf_tab_install install >/dev/null 2>&1
    fi
    
    # 如果目录存在，尝试加载
    if [[ -d "$FZF_TAB_COMPLETION_DIR" ]]; then
        _load_fzf_tab_completion 2>/dev/null
    fi
fi
