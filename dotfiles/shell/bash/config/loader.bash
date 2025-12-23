#!/bin/bash
# Bash 配置模块加载器
# 简洁高效的模块管理系统

# 获取配置目录（当前文件所在目录）
BASH_CONFIG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 已加载的模块列表
declare -A _loaded_modules

# 加载模块
# 用法: load_module <模块名>
load_module() {
    local module_name="$1"
    
    # 检查是否已加载
    if [[ -n "${_loaded_modules[$module_name]}" ]]; then
        return 0
    fi
    
    local module_file="${BASH_CONFIG_DIR}/${module_name}.bash"
    
    if [[ -f "$module_file" ]]; then
        source "$module_file"
        _loaded_modules[$module_name]=1
        return 0
    else
        echo "警告: 模块 '${module_name}' 未找到: ${module_file}" >&2
        return 1
    fi
}

# 卸载模块（通过取消定义相关函数和变量）
# 用法: unload_module <模块名>
unload_module() {
    local module_name="$1"
    unset "_loaded_modules[$module_name]"
    # 注意：bash 无法真正"卸载"已 source 的文件，这里只是标记
    echo "模块 '${module_name}' 已标记为卸载（需要重启 shell 才能完全卸载）"
}


# 列出所有可用模块
list_modules() {
    echo "可用模块:"
    for file in "${BASH_CONFIG_DIR}"/*.bash; do
        if [[ -f "$file" ]]; then
            local name=$(basename "$file" .bash)
            if [[ "$name" != "loader" ]]; then
                local status="未加载"
                [[ -n "${_loaded_modules[$name]}" ]] && status="已加载"
                echo "  - $name ($status)"
            fi
        fi
    done
}

