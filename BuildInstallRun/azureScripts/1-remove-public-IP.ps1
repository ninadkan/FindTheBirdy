. "$PSScriptRoot\login.ps1"

$publicIp = Get-AzureRMPublicIpAddress `
    -Name $PUBLIC_IP_NAME `
    -ResourceGroupName $RESOURCEGROUP_NAME `
    -ErrorAction SilentlyContinue

if ($publicIp)
{
    Remove-AzureRMPublicIpAddress `
        -Name $PUBLIC_IP_NAME `
        -ResourceGroupName $RESOURCEGROUP_NAME -Force
}


