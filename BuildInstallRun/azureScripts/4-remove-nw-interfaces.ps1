. "$PSScriptRoot\login.ps1"


Function removeNetworkInterface($networkInterfaceName )
{
    $nwInterface = Get-AzNetworkInterface `
        -Name $networkInterfaceName `
        -ResourceGroupName $RESOURCEGROUP_NAME `
        -ErrorAction SilentlyContinue
    if ($nwInterface)
    {
        Remove-AzNetworkInterface `
            -Name $networkInterfaceName `
            -ResourceGroupName $RESOURCEGROUP_NAME
    }
    else
    {
        Write-Warning "Not Found '$networkInterfaceName'"
    }
}


# remove the network interfaces
removeNetworkInterface -networkInterfaceName $NETWORK_INTERFACE_NAME

