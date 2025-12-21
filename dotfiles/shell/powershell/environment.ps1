# 环境变量配置模块
# 设置环境变量和 PATH

# 设置 uv 的环境代理（清华源）
$env:UV_DEFAULT_INDEX = "https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple"

# 增加路径到当前会话的 PATH 环境变量（Windows 方式）
function Add-ToPath {
    param([string]$Path)
    if (Test-Path $Path) {
        if ($env:PATH -notlike "*$Path*") {
            $env:PATH = "$Path;$env:PATH"
        }
    }
}

# 增加 Home/.local/bin 到环境变量
$localBinPath = Join-Path $env:USERPROFILE ".local\bin"
Add-ToPath $localBinPath

# 增加 pixi 的环境变量
$pixiBinPath = Join-Path $env:USERPROFILE ".pixi\bin"
Add-ToPath $pixiBinPath

# 增加 cargo 的环境变量
$cargoBinPath = Join-Path $env:USERPROFILE ".cargo\bin"
Add-ToPath $cargoBinPath

# 给 yazi 配置 file.exe 的环境变量（通过 scoop）
$scoopPath = Get-Command scoop -ErrorAction SilentlyContinue
if ($scoopPath) {
    $scoopGrandparent = Split-Path (Split-Path $scoopPath.Source)
    $gitBinPath = Join-Path $scoopGrandparent "apps\git\current\usr\bin"
    Add-ToPath $gitBinPath
}

