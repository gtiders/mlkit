# 编辑器配置模块
# 设置默认编辑器（优先使用 helix/hx，然后是 nvim/vim）

function Set-Editor {
    $editors = @('hx', 'helix', 'nvim', 'vim', 'vi', 'code', 'notepad')
    foreach ($editor in $editors) {
        $editorPath = Get-Command $editor -ErrorAction SilentlyContinue
        if ($editorPath) {
            $env:EDITOR = $editor
            Set-Alias -Name edit -Value $editor -ErrorAction SilentlyContinue
            break
        }
    }
}

Set-Editor

