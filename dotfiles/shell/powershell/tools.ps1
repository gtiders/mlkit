# 工具自动加载模块
# 检测并自动加载 starship、pixi 等工具

# 检测 starship 是否可用并设置自动加载
function Setup-Starship {
    $starshipCmd = Get-Command starship -ErrorAction SilentlyContinue
    if (-not $starshipCmd) {
        Write-Host "starship not found, skipping starship setup" -ForegroundColor Yellow
        return
    }
    
    # PowerShell 中 starship 的初始化方式
    $starshipInit = starship init powershell
    if ($starshipInit) {
        Invoke-Expression $starshipInit
    }
}

# 检测 pixi 是否可用并设置自动加载
function Setup-Pixi {
    $pixiCmd = Get-Command pixi -ErrorAction SilentlyContinue
    if (-not $pixiCmd) {
        Write-Host "pixi not found, skipping pixi setup" -ForegroundColor Yellow
        return
    }
    
    # pixi completion for PowerShell
    # 注意：pixi 可能不支持 PowerShell 的自动补全，这里先跳过
    # 如果需要，可以手动添加补全脚本
}

# 执行自动加载设置
Setup-Pixi
Setup-Starship

