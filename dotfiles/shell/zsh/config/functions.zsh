# 自定义函数模块

# 使用 yazi 打开当前目录
yy() {
    local tmp_file=$(mktemp /tmp/yazi-cwd.XXXXXX)
    yazi "$@" --cwd-file "$tmp_file"
    
    if [[ -f "$tmp_file" ]]; then
        local cwd=$(cat "$tmp_file")
        rm -f "$tmp_file"
        
        if [[ -n "$cwd" ]] && [[ "$cwd" != "$PWD" ]]; then
            cd "$cwd"
        fi
    fi
}

# 设置代理的函数（只接受端口号）
vpn-proxy() {
    local port="${1:-7897}"
    local host="127.0.0.1"
    local proxy_url="http://${host}:${port}"
    
    export http_proxy="$proxy_url"
    export https_proxy="$proxy_url"
    export HTTP_PROXY="$proxy_url"
    export HTTPS_PROXY="$proxy_url"
    
    echo "代理已设置为: $proxy_url"
}

# 清除代理的函数
no-proxy() {
    unset http_proxy
    unset https_proxy
    unset HTTP_PROXY
    unset HTTPS_PROXY
    
    echo "代理已清除"
}

# 给 yazi 配置 file.exe 的环境变量（通过 scoop，仅 Windows）
if command -v scoop >/dev/null 2>&1; then
    local scoop_path=$(command -v scoop)
    local scoop_grandparent=$(dirname $(dirname "$scoop_path"))
    local git_bin_path="${scoop_grandparent}/apps/git/current/usr/bin"
    
    if [[ -d "$git_bin_path" ]]; then
        export PATH="${git_bin_path}:$PATH"
    fi
fi

