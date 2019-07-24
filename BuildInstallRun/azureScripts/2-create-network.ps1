. "$PSScriptRoot\login.ps1"

Function createNSG($NsgName,  $addRules)
{
    $NSG = Get-AzNetworkSecurityGroup -ResourceGroupName $RESOURCEGROUP_NAME `
                                 -Name $NsgName -ErrorAction SilentlyContinue
    if (-not $NSG)
    {
        Write-Host -ForegroundColor Yellow "creating a new NSG '$NsgName' ... "
        if ($addRules)
        {

            Write-Host -ForegroundColor Yellow "creating new rule for '$NsgName' ... "
            $rules = @()

            $httpRule = New-AzNetworkSecurityRuleConfig -Name $HTTP_NSG_RULE `
                -Description "Allow HTTP" -Access Allow `
                -Protocol Tcp -Direction Inbound -Priority 1010 `
                -SourceAddressPrefix Internet -SourcePortRange * `
                -DestinationAddressPrefix * -DestinationPortRange 80

            $httpsRule = New-AzNetworkSecurityRuleConfig -Name $HTTPS_NSG_RULE `
                -Description "Allow HTTPS" -Access Allow `
                -Protocol Tcp -Direction Inbound -Priority 1020 `
                -SourceAddressPrefix Internet -SourcePortRange * `
                -DestinationAddressPrefix * -DestinationPortRange 443

            $rules += $httpRule 
            $rules += $httpsRule 
            
            $NSG = New-AzNetworkSecurityGroup -ResourceGroupName $RESOURCEGROUP_NAME `
                -Location $LOCATION `
                -Name $NsgName `
                -SecurityRules $rules
        }
        else
        {
            Write-Host -ForegroundColor DarkYellow "Adding precreated NSG '$NsgName' ... "
            $NSG = New-AzNetworkSecurityGroup -ResourceGroupName $RESOURCEGROUP_NAME `
                    -Location $LOCATION `
                    -Name $NsgName
        }
    }
    else
    {
        Write-Host -ForegroundColor Green ("Already exists - '$NsgName'")
    }
    return $NSG
}

Function createSubNet($SubnetName, $virtualNetwork, $AddresPrefix)
{
    $Subnet = Get-AzVirtualNetworkSubnetConfig -Name $SubnetName `
            -VirtualNetwork $virtualNetwork -ErrorAction SilentlyContinue
    if (-not $Subnet)
    {
        Write-Host -ForegroundColor Yellow "creating a new subnet '$SubnetName'... "
        $Subnet = Add-AzVirtualNetworkSubnetConfig -Name $SubnetName `
                -AddressPrefix $AddresPrefix -VirtualNetwork $virtualNetwork
    }
    else
    {
        Write-Host -ForegroundColor Green ("Already exists - '$SubnetName'")
    }
    return $Subnet
}



$VnetAddressPrefix = "10.0.0.0/16"
$SubnetAddresPrefix = "10.0.1.0/24"


$virtualNetwork  = Get-AzVirtualNetwork -Name $VIRTUALNETWORKNAME `
        -ResourceGroupName $RESOURCEGROUP_NAME -ErrorAction SilentlyContinue 
if (-not $virtualNetwork)
{
    Write-Host -ForegroundColor Yellow "create a new VNET ... ";
    $virtualNetwork = New-AzVirtualNetwork `
                        -ResourceGroupName $RESOURCEGROUP_NAME `
                        -Location $LOCATION -Name $VIRTUALNETWORKNAME `
                        -AddressPrefix $VnetAddressPrefix
}
else
{
     Write-Host -ForegroundColor Green ("Already exists - '$VIRTUALNETWORKNAME'")
}

if ($virtualNetwork)
{
    # create the subnets
    $frontEndSubnet = createSubNet -SubnetName $SUBNET_NAME `
                -virtualNetwork $virtualNetwork `
                -AddresPrefix $SubnetAddresPrefix 

    # check if subnets exists
    if (-not $frontEndSubnet)
    {
        if (-not $frontEndSubnet)
        {
            Write-Host -ForegroundColor Red "Error! SUB-VNET '$SUBNET_NAME' not found"
        }
    }
    else
    {
        # both subnets exist now; save status ; 
        $dummy = Set-AzVirtualNetwork -VirtualNetwork $virtualNetwork 

        # lets update with NSGS
        $frontendNSG = createNSG -NsgName $NSG_NAME -addRules $true


        if ($frontendNSG)
        {
            $dummy = Set-AzVirtualNetworkSubnetConfig -Name $SUBNET_NAME `
                -VirtualNetwork $virtualNetwork -NetworkSecurityGroup $frontEndNSG `
                -AddressPrefix $SubnetAddresPrefix 
        }
        else
        {
            Write-Host -ForegroundColor Red "Error! NSG '$SUBNET_NAME' not found"
        }
        $dummy =  Set-AzVirtualNetwork -VirtualNetwork $virtualNetwork
    }
}
else
{
    Write-Host -ForegroundColor Red "Error! VNET '$VIRTUALNETWORKNAME' not found"
}

