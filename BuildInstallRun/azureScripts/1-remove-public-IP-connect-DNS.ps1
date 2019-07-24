. "$PSScriptRoot\login.ps1"

$publicIp = Get-AzPublicIpAddress `
    -Name $PUBLIC_IP_NAME `
    -ResourceGroupName $RESOURCEGROUP_NAME `
    -ErrorAction SilentlyContinue

if ($publicIp)
{
    Remove-AzPublicIpAddress `
        -Name $PUBLIC_IP_NAME `
        -ResourceGroupName $RESOURCEGROUP_NAME 
}


