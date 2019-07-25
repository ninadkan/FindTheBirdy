. "$PSScriptRoot\login.ps1"$

Function createNetworkInterface($networkInterfaceName, # name of NIC
                                $Subnet, # Subnet where the NIC will be plugged in
                                $NsgGroup) # NSG where the created NIC will be placed nder
                                
{
    $nwInterface = Get-AzureRMNetworkInterface `
        -Name $networkInterfaceName `
        -ResourceGroupName $RESOURCEGROUP_NAME `
        -ErrorAction SilentlyContinue
    if (-not $nwInterface)
    {
        Write-Host  `
            -ForegroundColor Yellow  `
            "Creating Network Interface '$networkInterfaceName'"
            # create NIC with Subnet + NSG
        $nwInterface = New-AzureRMNetworkInterface `
            -Name $networkInterfaceName `
            -ResourceGroupName $RESOURCEGROUP_NAME `
            -Location $LOCATION `
            -SubnetId $Subnet.Id `
            -NetworkSecurityGroupId $NsgGroup.Id `
            -EnableIPForwarding 
    }
    else
    {
        write-host -ForegroundColor Green ("Network Interface '$networkInterfaceName' already exists")
    }

    $nwInterface.Primary = $true
    $dummy = Set-AzureRMNetworkInterface -NetworkInterface $nwInterface

    return $nwInterface
}

$virtualNetwork  = Get-AzureRMVirtualNetwork `
    -Name $VIRTUALNETWORKNAME `
    -ResourceGroupName $RESOURCEGROUP_NAME `
    -ErrorAction Stop

$Subnet = Get-AzureRMVirtualNetworkSubnetConfig `
    -Name $SUBNET_NAME `
    -VirtualNetwork $virtualNetwork `
    -ErrorAction Stop

$NSG = Get-AzureRMNetworkSecurityGroup `
    -ResourceGroupName $RESOURCEGROUP_NAME `
    -Name $NSG_NAME `
    -ErrorAction Stop

createNetworkInterface -networkInterfaceName $NETWORK_INTERFACE_NAME -Subnet $Subnet -NsgGroup $NSG














