# 编辑器配置模块

# 设置默认编辑器（优先使用 helix/hx，然后是 nvim/vim）
if command -v hx >/dev/null 2>&1; then
    export EDITOR='hx'
elif command -v helix >/dev/null 2>&1; then
    export EDITOR='helix'
elif command -v nvim >/dev/null 2>&1; then
    export EDITOR='nvim'
elif command -v vim >/dev/null 2>&1; then
    export EDITOR='vim'
elif command -v vi >/dev/null 2>&1; then
    export EDITOR='vi'
fi

# 创建 edit 别名
alias edit="$EDITOR"

