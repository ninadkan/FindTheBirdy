. "$PSScriptRoot\login.ps1"



Function createVM($nwInterfaceName, $VMName)
    # $nwInterfaceName : The interface name that the 
    # created VM will be attached to
    # $VMName : Name of the VM that that is being created. 
{

    $vm = Get-AzVM -Name $VMName `
        -ResourceGroupName $RESOURCEGROUP_NAME `
        -ErrorAction SilentlyContinue
    if (-not $vm)
    { 
 
        $securePassword = ConvertTo-SecureString ' ' `
            -AsPlainText -Force
        $cred = New-Object `
            System.Management.Automation.PSCredential ($WEBUSERNAME, `
                        $securePassword)

        $nwInterface = Get-AzNetworkInterface `
            -Name $nwInterfaceName `
            -ResourceGroupName $RESOURCEGROUP_NAME


        $vmConfig = New-AzVMConfig -VMName $VMName `
            -VMSize Standard_B1s `
          | Set-AzVMOperatingSystem -Linux `
           -ComputerName $VMName `
           -Credential $cred `
           -DisablePasswordAuthentication `
         | Set-AzVMSourceImage -PublisherName Canonical `
           -Offer UbuntuServer `
           -Skus 16.04-LTS `
           -Version latest `
         | Add-AzVMNetworkInterface -Id $nwInterface.Id `
            -Primary 
        

        $sshPublicKey = cat ./keys/id_rsa.pub 
        Write-Verbose $sshPublicKey
        $keypath=  "/home/" + $WEBUSERNAME + "/.ssh/authorized_keys"
        
        $dummy = Add-AzVMSshPublicKey -VM $vmconfig -KeyData $sshPublicKey -Path $keypath
        $dummy = New-AzVM -VM $vmConfig -ResourceGroupName $RESOURCEGROUP_NAME -Location $LOCATION
    }
    else
    {
        Write-Warning "VM alerady existing - '$VMName'"
    }
}


createVM -nwInterfaceName $NETWORK_INTERFACE_NAME `
    -VMName $VIRTUAL_MACHINE_NAME




