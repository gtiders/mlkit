# 环境变量配置模块

# PATH 配置
# 添加 ~/.local/bin 和 ~/bin 到 PATH
if [[ -d "$HOME/.local/bin" ]]; then
    export PATH="$HOME/.local/bin:$PATH"
fi

if [[ -d "$HOME/bin" ]]; then
    export PATH="$HOME/bin:$PATH"
fi

# 添加 pixi 的环境变量
if [[ -d "$HOME/.pixi/bin" ]]; then
    export PATH="$HOME/.pixi/bin:$PATH"
fi

# 添加 cargo 的环境变量
if [[ -d "$HOME/.cargo/bin" ]]; then
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Linux 下添加 brew 的软件路径
if [[ "$OSTYPE" == "linux-gnu"* ]] && [[ -d "/home/linuxbrew/.linuxbrew/bin" ]]; then
    export PATH="/home/linuxbrew/.linuxbrew/bin:$PATH"
fi

# 设置 uv 的环境代理（清华源）
export UV_DEFAULT_INDEX="https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple"
export PIP_INDEX_URL="https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple"
export PIP_TRUSTED_HOST="mirrors.tuna.tsinghua.edu.cn"

# 语言环境
export LANG=en_US.UTF-8

