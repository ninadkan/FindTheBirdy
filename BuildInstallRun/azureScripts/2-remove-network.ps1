. "$PSScriptRoot\login.ps1"

Function removeNSG($NsgName)
{
    $NSG = Get-AzureRMNetworkSecurityGroup `
            -ResourceGroupName $RESOURCEGROUP_NAME `
            -Name $NsgName -ErrorAction SilentlyContinue
    if ($NSG)
    {
        #remove the NSG from the attached Subnet first
         $NSG = Remove-AzureRMNetworkSecurityGroup `
            -ResourceGroupName $RESOURCEGROUP_NAME -Name $NsgName -Force
    }
    else
    {
        Write-Warning "Not found '$NsgName' for Removal"
    }
}

Function removeSubNet($SubnetName, $virtualNetwork)
{
    $Subnet = Get-AzureRMVirtualNetworkSubnetConfig -Name $SubnetName `
        -VirtualNetwork $virtualNetwork -ErrorAction SilentlyContinue
    if ($Subnet)
    {
        $Subnet = Remove-AzureRMVirtualNetworkSubnetConfig -Name $SubnetName `
        -VirtualNetwork $virtualNetwork
        $virtualNetwork | Set-AzureRMVirtualNetwork
    }
    else
    {
        Write-Warning "Not found '$SubnetName' for Removal"
    }
    return $Subnet
}


$virtualNetwork  = Get-AzureRMVirtualNetwork -Name $VIRTUALNETWORKNAME `
        -ResourceGroupName $RESOURCEGROUP_NAME `
        -ErrorAction SilentlyContinue
if ($virtualNetwork)
{

    removeSubNet -SubnetName $SUBNET_NAME `
        -virtualNetwork $virtualNetwork
  
    Remove-AzureRMVirtualNetwork -ResourceGroupName $RESOURCEGROUP_NAME `
        -Name $VIRTUALNETWORKNAME -Force
}
else
{
    Write-Warning "Not found '$VIRTUALNETWORKNAME' for Removal"
}

removeNsg -NsgName $NSG_NAME




