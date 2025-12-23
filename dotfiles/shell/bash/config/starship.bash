#!/bin/bash
# Starship 提示符配置模块
# 提供 starship 检测和初始化功能

# 初始化 starship
_init_starship() {
    # 检测 starship 命令是否存在
    if ! command -v starship &> /dev/null; then
        echo "提示: starship 未安装"
        echo "安装方法："
        echo "  curl -sS https://starship.rs/install.sh | sh"
        echo "  或者使用包管理器："
        echo "  - macOS: brew install starship"
        echo "  - Ubuntu/Debian: sudo apt install starship"
        echo "  - Arch: sudo pacman -S starship"
        echo "  - Fedora: sudo dnf install starship"
        return 1
    fi
    
    # 初始化 starship
    eval "$(starship init bash)"
    return 0
}

# 自动初始化
_init_starship

