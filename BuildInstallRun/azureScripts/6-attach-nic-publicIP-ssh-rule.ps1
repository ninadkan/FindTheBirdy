. "$PSScriptRoot\login.ps1"

# VM needs to be stopped before executing this script

Function createAttach_PublicIP_NIC($IpAddressName, `
                        $nicName                
                        )
{
    #create a temporary public IP address
    $IP = Get-AzPublicIpAddress `
        -Name $IpAddressName `
        -ResourceGroupName $RESOURCEGROUP_NAME `
        -ErrorAction SilentlyContinue

    if (-not $IP)
    {
        Write-Host -ForegroundColor Yellow `
            "create a new static IP address '$IpAddressName'... "
        $IP = New-AzPublicIpAddress  `
                            -Name $IpAddressName `
                            -ResourceGroupName $RESOURCEGROUP_NAME `
                            -AllocationMethod Static `
                            -Location $LOCATION `
                            -Sku "Standard"
    }
        
    
    $nic = Get-AzNetworkInterface `
            -Name $nicName `
            -ResourceGroupName $RESOURCEGROUP_NAME `
               
    if ($nic)
    {
        Write-Host -ForegroundColor Green `
            "Attaching the created public IP to NIC '$nicName'... "
        $d =Set-AzNetworkInterfaceIpConfig `
            -Name $nic.IpConfigurations[0].Name `
            -NetworkInterface $nic `
            -Subnet $nic.IpConfigurations[0].Subnet `
            -PrivateIpAddress $nic.IpConfigurations[0].PrivateIpAddress `
            -Primary `
            -PublicIpAddress $IP 
         $d = Set-AzNetworkInterface -NetworkInterface $nic
    }
    $ipAddress = $IP.IpAddress
    Write-Host -ForegroundColor Cyan "IP address = '$ipAddress', NIC = '$nicName'"
}


Function openRDPPortForNSGs($NsgName)
{
    $NSG = Get-AzNetworkSecurityGroup `
        -ResourceGroupName $RESOURCEGROUP_NAME `
        -Name $NsgName
    if ($NSG)
    {
        Write-Host -ForegroundColor Green "creating new rule for '$NsgName' ... "

        $existingRules = $NSG.SecurityRules
        $ruleExist = $false

        ForEach ($existingrule in $existingRules) { 
            Write-Host $existingrule.Name
            If ($existingrule.Name.StartsWith($SSH_NSG_RULE))
            {
               $ruleExist = $true
               break 
            } 
        }

        if (-not $ruleExist)
        {
            # Add rdpRule to the collection
            $d= Add-AzNetworkSecurityRuleConfig `
                -Access Allow `
                -Direction Inbound `
                -Priority 1050 `
                -Name $SSH_NSG_RULE `
                -NetworkSecurityGroup $NSG `
                -Protocol Tcp `
                -SourcePortRange * `
                -DestinationPortRange 22 `
                -SourceAddressPrefix * `
                -DestinationAddressPrefix *
            $d = Set-AzNetworkSecurityGroup -NetworkSecurityGroup $NSG
        }
        else
        {
            Write-Warning ("NSG '$NsgName' already contains rule - '$SSH_NSG_RULE' ")
        }
    }
    else
    {
        Write-Warning ("NSG Does not exist - '$NsgName'")
    }
    return $NSG
}

createAttach_PublicIP_NIC `
    -IpAddressName $PUBLIC_IP_NAME `
    -nicName $NETWORK_INTERFACE_NAME
  
openRDPPortForNSGs -NsgName $NSG_NAME





