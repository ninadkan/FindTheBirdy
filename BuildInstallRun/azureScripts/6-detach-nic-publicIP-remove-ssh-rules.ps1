. "$PSScriptRoot\login.ps1"

function detachIPAddressFromNIC($nicName)
{
    $nic = Get-AzureRMNetworkInterface `
            -Name $nicName `
            -ResourceGroupName $RESOURCEGROUP_NAME `
            -ErrorAction SilentlyContinue

    if ($nic)
    {
       Set-AzureRMNetworkInterfaceIpConfig `
            -Name $nic.IpConfigurations[0].Name `
            -NetworkInterface $nic `
            -Subnet $nic.IpConfigurations[0].Subnet `
            -PrivateIpAddress $nic.IpConfigurations[0].PrivateIpAddress `
            -Primary 
        #$nic.Primary = $false
        Set-AzureRMNetworkInterface -NetworkInterface $nic
    }
    else
    {
        Write-Warning "Nic not found - '$nicName'"
    }
}


Function closeRDPPortForNSGs($NsgName)
{
    $NSG = Get-AzureRMNetworkSecurityGroup -ResourceGroupName $RESOURCEGROUP_NAME `
                                 -Name $NsgName -ErrorAction SilentlyContinue
    if ($NSG)
    {
        Write-Host -ForegroundColor Green "removing rule for '$NsgName' ... "
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

        if ($ruleExist)
        {
            Remove-AzureRMNetworkSecurityRuleConfig `
                -Name $SSH_NSG_RULE -NetworkSecurityGroup $NSG
            Set-AzureRMNetworkSecurityGroup `
                -NetworkSecurityGroup $NSG
        }
        else
        {
            Write-Warning ("NSG '$NsgName' Does not contain rule - '$rdpSecurityRuleName' ")
        }
    }
    else
    {
        Write-Warning ("NSG Does not exist - '$NsgName'")
    }
    return $NSG
}

# close RDP security gap
closeRDPPortForNSGs -NsgName $NSG_NAME


# detach IP Address from NIC
detachIPAddressFromNIC `
    -nicName $NETWORK_INTERFACE_NAME



