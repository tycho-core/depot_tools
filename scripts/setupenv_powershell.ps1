$script_dir = $PSScriptRoot
$hub_dir = Join-Path $script_dir "\..\"
Write-Output $hub_dir

function RunApp
{
    param([string]$Script, [string]$Params)
    echo $args
    echo "c:\python27\python.exe" $hub_dir$Script $Params
    & "c:\python27\python.exe" $hub_dir$Script $Params
}

function TyWorkspaceF { RunApp -script "tyworkspace.py" -params $args }
function TyCreateF { RunApp -script "tycreate.py" -params $args }
function TyHubF { RunApp -script "tyhub.py" -params $args }
function TyFormatF { RunApp -script "tyformat.py" -params $args }
function TyInitF { RunApp -script "tyinit.py" -params $args }

Set-Alias tycreate TyCreateF
Set-Alias tyhub TyHubF
Set-Alias tyworkspace TyWorkspaceF
Set-Alias tyformat TyFormatF
Set-Alias tyinit TyInitF
