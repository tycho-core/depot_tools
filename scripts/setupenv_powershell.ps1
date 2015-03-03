function Get-ScriptDirectory
{
    $Invocation = (Get-Variable MyInvocation -Scope 1).Value;
    if($Invocation.PSScriptRoot)
    {
        $Invocation.PSScriptRoot;
    }
    Elseif($Invocation.MyCommand.Path)
    {
        Split-Path $Invocation.MyCommand.Path
    }
    else
    {
        $Invocation.InvocationName.Substring(0,$Invocation.InvocationName.LastIndexOf("\"));
    }
}

$script_dir = Get-ScriptDirectory
$hub_dir = Join-Path $script_dir "\..\"
Write-Output $hub_dir
Set-Alias tycreate "$hub_dir\tycreate.py"
Set-Alias tyhub "$hub_dir\tyhub.py"
Set-Alias tyworkspace "$hub_dir\tyworkspace.py"
Set-Alias tyformat "$hub_dir\tyformat.py"
Set-Alias tyinit "$hub_dir\tyinit.py"
