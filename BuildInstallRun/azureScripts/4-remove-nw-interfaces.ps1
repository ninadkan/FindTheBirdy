. "$PSScriptRoot\login.ps1"


Function removeNetworkInterface($networkInterfaceName )
{
    $nwInterface = Get-AzureRMNetworkInterface `
        -Name $networkInterfaceName `
        -ResourceGroupName $RESOURCEGROUP_NAME `
        -ErrorAction SilentlyContinue
    if ($nwInterface)
    {
        Write-Warning  "Removing '$networkInterfaceName'"
        Remove-AzureRMNetworkInterface `
            -Name $networkInterfaceName `
            -ResourceGroupName $RESOURCEGROUP_NAME `
            -Force
    }
    else
    {
        Write-Warning "Not Found '$networkInterfaceName'"
    }
}


# remove the network interfaces
removeNetworkInterface -networkInterfaceName $NETWORK_INTERFACE_NAME

