# Zsh 配置模块加载器
# 提供模块加载功能，类似于 PowerShell 的模块系统

# 配置目录（如果未设置，则使用当前文件所在目录）
# 注意：ZSH_CONFIG_DIR 应该在加载此文件前设置
if [[ -z "$ZSH_CONFIG_DIR" ]]; then
    # 如果未设置，假设当前文件在 config 目录下
    ZSH_CONFIG_DIR="${0:a:h}"
fi

# 模块加载函数
# 用法: load_module <模块名>
# 示例: load_module editor
load_module() {
    local module_name="$1"
    local module_file="${ZSH_CONFIG_DIR}/${module_name}.zsh"
    
    if [[ -f "$module_file" ]]; then
        source "$module_file"
        return 0
    else
        echo "Warning: Module '${module_name}' not found at ${module_file}" >&2
        return 1
    fi
}

# 批量加载模块
# 用法: load_modules <模块1> <模块2> ...
# 示例: load_modules editor environment history
load_modules() {
    for module in "$@"; do
        load_module "$module"
    done
}

# 检查模块是否存在
# 用法: module_exists <模块名>
module_exists() {
    local module_name="$1"
    local module_file="${ZSH_CONFIG_DIR}/${module_name}.zsh"
    [[ -f "$module_file" ]]
}

