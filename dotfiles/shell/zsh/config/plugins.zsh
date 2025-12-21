# 插件加载模块
# 独立的插件系统，不依赖 oh-my-zsh

# 插件目录（固定为 ~/.config/zsh/plugins）
ZSH_PLUGINS_DIR="${HOME}/.config/zsh/plugins"

# 加载插件函数
# 用法: load_plugin <插件名>
load_plugin() {
    local plugin_name="$1"
    local plugin_file=""
    
    # 尝试多种可能的插件文件路径
    # 1. 插件目录/插件名/插件名.plugin.zsh
    plugin_file="${ZSH_PLUGINS_DIR}/${plugin_name}/${plugin_name}.plugin.zsh"
    if [[ -f "$plugin_file" ]]; then
        source "$plugin_file"
        return 0
    fi
    
    # 2. 插件目录/插件名/插件名.zsh
    plugin_file="${ZSH_PLUGINS_DIR}/${plugin_name}/${plugin_name}.zsh"
    if [[ -f "$plugin_file" ]]; then
        source "$plugin_file"
        return 0
    fi
    
    # 3. 插件目录/插件名.zsh
    plugin_file="${ZSH_PLUGINS_DIR}/${plugin_name}.zsh"
    if [[ -f "$plugin_file" ]]; then
        source "$plugin_file"
        return 0
    fi
    
    # 4. 插件目录/插件名/插件名.zsh (zsh-autosuggestions 和 zsh-syntax-highlighting 的特殊情况)
    if [[ "$plugin_name" == "zsh-autosuggestions" ]]; then
        plugin_file="${ZSH_PLUGINS_DIR}/${plugin_name}/zsh-autosuggestions.zsh"
        if [[ -f "$plugin_file" ]]; then
            source "$plugin_file"
            return 0
        fi
    fi
    
    if [[ "$plugin_name" == "zsh-syntax-highlighting" ]]; then
        plugin_file="${ZSH_PLUGINS_DIR}/${plugin_name}/zsh-syntax-highlighting.zsh"
        if [[ -f "$plugin_file" ]]; then
            source "$plugin_file"
            return 0
        fi
    fi
    
    echo "Warning: Plugin '${plugin_name}' not found in ${ZSH_PLUGINS_DIR}" >&2
    return 1
}

# 批量加载插件
# 用法: load_plugins <插件1> <插件2> ...
load_plugins() {
    for plugin in "$@"; do
        load_plugin "$plugin"
    done
}

# 自动加载常用插件（如果存在）
# zsh-autosuggestions - 自动建议
load_plugin "zsh-autosuggestions" 2>/dev/null

# zsh-syntax-highlighting - 语法高亮（必须在最后加载）
load_plugin "zsh-syntax-highlighting" 2>/dev/null

