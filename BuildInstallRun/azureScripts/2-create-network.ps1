. "$PSScriptRoot\login.ps1"

Function createNSG($NsgName,  $addRules)
{
    $NSG = Get-AzureRMNetworkSecurityGroup -ResourceGroupName $RESOURCEGROUP_NAME `
                                 -Name $NsgName -ErrorAction SilentlyContinue
    if (-not $NSG)
    {
        Write-Host -ForegroundColor Yellow "creating a new NSG '$NsgName' ... "
        if ($addRules)
        {

            Write-Host -ForegroundColor Yellow "creating new rule for '$NsgName' ... "
            $rules = @()

            $httpRule = New-AzureRMNetworkSecurityRuleConfig -Name $HTTP_NSG_RULE `
                -Description "Allow HTTP" -Access Allow `
                -Protocol Tcp -Direction Inbound -Priority 1010 `
                -SourceAddressPrefix Internet -SourcePortRange * `
                -DestinationAddressPrefix * -DestinationPortRange 80

            $httpsRule = New-AzureRMNetworkSecurityRuleConfig -Name $HTTPS_NSG_RULE `
                -Description "Allow HTTPS" -Access Allow `
                -Protocol Tcp -Direction Inbound -Priority 1020 `
                -SourceAddressPrefix Internet -SourcePortRange * `
                -DestinationAddressPrefix * -DestinationPortRange 443


            $httpsRule5002 = New-AzureRMNetworkSecurityRuleConfig -Name $HTTPS_NSG_5002_RULE `
                -Description "Allow HTTPS" -Access Allow `
                -Protocol Tcp -Direction Inbound -Priority 1030 `
                -SourceAddressPrefix Internet -SourcePortRange * `
                -DestinationAddressPrefix * -DestinationPortRange 5002

            $httpsRule5555 = New-AzureRMNetworkSecurityRuleConfig -Name $HTTPS_NSG_5555_RULE `
                -Description "Allow HTTPS" -Access Allow `
                -Protocol Tcp -Direction Inbound -Priority 1030 `
                -SourceAddressPrefix Internet -SourcePortRange * `
                -DestinationAddressPrefix * -DestinationPortRange 5555

            $rules += $httpRule 
            $rules += $httpsRule 
            $rules += $httpsRule5002
            $rules += $httpsRule5555 
             
            
            $NSG = New-AzureRMNetworkSecurityGroup -ResourceGroupName $RESOURCEGROUP_NAME `
                -Location $LOCATION `
                -Name $NsgName `
                -SecurityRules $rules
        }
        else
        {
            Write-Host -ForegroundColor DarkYellow "Adding precreated NSG '$NsgName' ... "
            $NSG = New-AzureRMNetworkSecurityGroup -ResourceGroupName $RESOURCEGROUP_NAME `
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
    $Subnet = Get-AzureRMVirtualNetworkSubnetConfig -Name $SubnetName `
            -VirtualNetwork $virtualNetwork -ErrorAction SilentlyContinue
    if (-not $Subnet)
    {
        Write-Host -ForegroundColor Yellow "creating a new subnet '$SubnetName'... "
        $Subnet = Add-AzureRMVirtualNetworkSubnetConfig -Name $SubnetName `
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


$virtualNetwork  = Get-AzureRMVirtualNetwork -Name $VIRTUALNETWORKNAME `
        -ResourceGroupName $RESOURCEGROUP_NAME -ErrorAction SilentlyContinue 
if (-not $virtualNetwork)
{
    Write-Host -ForegroundColor Yellow "create a new VNET ... ";
    $virtualNetwork = New-AzureRMVirtualNetwork `
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
        $dummy = Set-AzureRMVirtualNetwork -VirtualNetwork $virtualNetwork 

        # lets update with NSGS
        $frontendNSG = createNSG -NsgName $NSG_NAME -addRules $true


        if ($frontendNSG)
        {
            $dummy = Set-AzureRMVirtualNetworkSubnetConfig -Name $SUBNET_NAME `
                -VirtualNetwork $virtualNetwork -NetworkSecurityGroup $frontEndNSG `
                -AddressPrefix $SubnetAddresPrefix 
        }
        else
        {
            Write-Host -ForegroundColor Red "Error! NSG '$SUBNET_NAME' not found"
        }
        $dummy =  Set-AzureRMVirtualNetwork -VirtualNetwork $virtualNetwork
    }
}
else
{
    Write-Host -ForegroundColor Red "Error! VNET '$VIRTUALNETWORKNAME' not found"
}

