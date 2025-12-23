#!/bin/bash
# 自定义函数模块

function yy() {
	local tmp="$(mktemp -t "yazi-cwd.XXXXXX")" cwd
	yazi "$@" --cwd-file="$tmp"
	IFS= read -r -d '' cwd < "$tmp"
	[ -n "$cwd" ] && [ "$cwd" != "$PWD" ] && builtin cd -- "$cwd"
	rm -f -- "$tmp"
}

# 智能解压函数（类似 oh-my-zsh 的 extract）
# 用法: extract <压缩文件>
extract() {
    local file="$1"
    
    # 检查参数
    if [[ -z "$file" ]]; then
        echo "用法: extract <压缩文件>" >&2
        return 1
    fi
    
    # 检查文件是否存在
    if [[ ! -f "$file" ]]; then
        echo "错误: 文件 '$file' 不存在" >&2
        return 1
    fi
    
    # 获取文件名（不含路径）和目录
    local name=$(basename "$file")
    local dir="${file%/*}"
    [[ "$dir" == "$file" ]] && dir="."
    
    # 根据文件扩展名选择解压命令
    case "$name" in
        *.tar.bz2|*.tbz2)
            if command -v tar &> /dev/null; then
                tar xvjf "$file" -C "$dir"
            else
                echo "错误: 需要 tar 命令" >&2
                return 1
            fi
            ;;
        *.tar.gz|*.tgz)
            if command -v tar &> /dev/null; then
                tar xvzf "$file" -C "$dir"
            else
                echo "错误: 需要 tar 命令" >&2
                return 1
            fi
            ;;
        *.tar.xz|*.txz)
            if command -v tar &> /dev/null; then
                tar xvJf "$file" -C "$dir"
            else
                echo "错误: 需要 tar 命令" >&2
                return 1
            fi
            ;;
        *.tar.zst|*.tzst)
            if command -v tar &> /dev/null && command -v zstd &> /dev/null; then
                tar --use-compress-program=zstd -xvf "$file" -C "$dir"
            else
                echo "错误: 需要 tar 和 zstd 命令" >&2
                return 1
            fi
            ;;
        *.tar)
            if command -v tar &> /dev/null; then
                tar xvf "$file" -C "$dir"
            else
                echo "错误: 需要 tar 命令" >&2
                return 1
            fi
            ;;
        *.zip|*.ZIP)
            if command -v unzip &> /dev/null; then
                unzip "$file" -d "$dir"
            else
                echo "错误: 需要 unzip 命令" >&2
                return 1
            fi
            ;;
        *.rar|*.RAR)
            if command -v unrar &> /dev/null; then
                unrar x "$file" "$dir"
            elif command -v rar &> /dev/null; then
                rar x "$file" "$dir"
            else
                echo "错误: 需要 unrar 或 rar 命令" >&2
                return 1
            fi
            ;;
        *.7z|*.7Z)
            if command -v 7z &> /dev/null; then
                7z x "$file" -o"$dir"
            elif command -v 7za &> /dev/null; then
                7za x "$file" -o"$dir"
            else
                echo "错误: 需要 7z 或 7za 命令" >&2
                return 1
            fi
            ;;
        *.gz)
            if command -v gunzip &> /dev/null; then
                gunzip "$file"
            else
                echo "错误: 需要 gunzip 命令" >&2
                return 1
            fi
            ;;
        *.bz2)
            if command -v bunzip2 &> /dev/null; then
                bunzip2 "$file"
            else
                echo "错误: 需要 bunzip2 命令" >&2
                return 1
            fi
            ;;
        *.xz)
            if command -v unxz &> /dev/null; then
                unxz "$file"
            else
                echo "错误: 需要 unxz 命令" >&2
                return 1
            fi
            ;;
        *.zst)
            if command -v zstd &> /dev/null; then
                zstd -d "$file"
            else
                echo "错误: 需要 zstd 命令" >&2
                return 1
            fi
            ;;
        *.Z)
            if command -v uncompress &> /dev/null; then
                uncompress "$file"
            else
                echo "错误: 需要 uncompress 命令" >&2
                return 1
            fi
            ;;
        *.lzma)
            if command -v unlzma &> /dev/null; then
                unlzma "$file"
            else
                echo "错误: 需要 unlzma 命令" >&2
                return 1
            fi
            ;;
        *.exe)
            if command -v cabextract &> /dev/null; then
                cabextract "$file"
            else
                echo "错误: 需要 cabextract 命令" >&2
                return 1
            fi
            ;;
        *.deb)
            if command -v dpkg-deb &> /dev/null; then
                dpkg-deb -x "$file" "$dir"
            else
                echo "错误: 需要 dpkg-deb 命令" >&2
                return 1
            fi
            ;;
        *.rpm)
            if command -v rpm2cpio &> /dev/null && command -v cpio &> /dev/null; then
                cd "$dir" && rpm2cpio "$file" | cpio -idmv
            else
                echo "错误: 需要 rpm2cpio 和 cpio 命令" >&2
                return 1
            fi
            ;;
        *)
            echo "错误: 不支持的文件类型: '$name'" >&2
            echo "支持的格式: tar.bz2, tar.gz, tar.xz, tar.zst, tar, zip, rar, 7z, gz, bz2, xz, zst, Z, lzma, exe, deb, rpm" >&2
            return 1
            ;;
    esac
}

