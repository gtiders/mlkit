# 自定义函数模块

# 使用 yazi 打开当前目录的函数
function yy {
    param([string[]]$Args)
    
    $tmpFile = New-TemporaryFile
    $tmpPath = $tmpFile.FullName
    Remove-Item $tmpFile
    
    # 运行 yazi 并保存当前目录到临时文件
    yazi @Args --cwd-file $tmpPath
    
    if (Test-Path $tmpPath) {
        $cwd = Get-Content $tmpPath -Raw
        $cwd = $cwd.Trim()
        if ($cwd -and $cwd -ne $PWD.Path) {
            Set-Location $cwd
        }
        Remove-Item $tmpPath -ErrorAction SilentlyContinue
    }
}

# 设置代理的函数（只接受端口号）
function vpn-proxy {
    param(
        [string]$Port = "7897"
    )
    
    $host = "127.0.0.1"
    $proxyUrl = "http://${host}:${Port}"
    
    $env:http_proxy = $proxyUrl
    $env:https_proxy = $proxyUrl
    $env:HTTP_PROXY = $proxyUrl
    $env:HTTPS_PROXY = $proxyUrl
    
    Write-Host "代理已设置为: $proxyUrl" -ForegroundColor Green
}

# 清除代理的函数
function no-proxy {
    Remove-Item Env:\http_proxy -ErrorAction SilentlyContinue
    Remove-Item Env:\https_proxy -ErrorAction SilentlyContinue
    Remove-Item Env:\HTTP_PROXY -ErrorAction SilentlyContinue
    Remove-Item Env:\HTTPS_PROXY -ErrorAction SilentlyContinue
    
    Write-Host "代理已清除" -ForegroundColor Green
}

