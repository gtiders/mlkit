<#
.SYNOPSIS
    Installs all fonts from a directory (recursively) for the current user.
    
.DESCRIPTION
    Scans the specified SourcePath for .ttf, .otf, and .ttc files, copies them 
    to the user's local font directory, and registers them in the HKCU registry.
    No Administrator privileges are required.

.PARAMETER SourcePath
    The directory to scan for fonts. Defaults to the current directory.

.EXAMPLE
    .\install_fonts.ps1
    Installs fonts from the current folder.

.EXAMPLE
    .\install_fonts.ps1 -SourcePath "C:\Downloads\Fonts"
    Installs fonts from C:\Downloads\Fonts and its subfolders.
#>

param (
    [string]$SourcePath = "."
)

try {
    $SourcePath = Resolve-Path $SourcePath -ErrorAction Stop
}
catch {
    Write-Error "Source path does not exist: $SourcePath"
    exit 1
}

# Standard User Font Path (Windows 10/11)
$TargetDir = "$env:LOCALAPPDATA\Microsoft\Windows\Fonts"
$RegistryKey = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"

# Ensure target directory exists
if (-not (Test-Path $TargetDir)) {
    Write-Host "Creating user font directory..."
    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
}

Write-Host "Scanning for fonts in: $SourcePath"
$Fonts = Get-ChildItem -Path $SourcePath -Recurse -Include "*.ttf", "*.otf", "*.ttc"

if ($Fonts.Count -eq 0) {
    Write-Warning "No font files found."
    exit
}

foreach ($Font in $Fonts) {
    try {
        $TargetFile = Join-Path $TargetDir $Font.Name
        
        Write-Host "Installing: $($Font.Name)" -ForegroundColor Cyan
        
        # 1. Copy the file
        Copy-Item -Path $Font.FullName -Destination $TargetFile -Force -ErrorAction Stop
        
        # 2. Register in Registry
        # We append "(TrueType)" as per convention to ensure compatibility, 
        # though modern Windows is flexible. Using the filename as the key ensures uniqueness.
        $RegValueName = $Font.Name + " (TrueType)"
        
        Set-ItemProperty -Path $RegistryKey -Name $RegValueName -Value $TargetFile -ErrorAction Stop
    }
    catch {
        if ($_.Exception -is [System.IO.IOException]) {
            Write-Warning "Skipped '$($Font.Name)': File is currently in use or locked."
        }
        else {
            Write-Error "Failed to install $($Font.Name): $_"
        }
    }
}

Write-Host "`nInstallation Complete!" -ForegroundColor Green
Write-Host "You may need to restart running applications to see the new fonts." -ForegroundColor Gray
