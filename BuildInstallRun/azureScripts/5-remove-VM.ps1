. "$PSScriptRoot\login.ps1"

Function removeLinuxVM($VMName)
{
    $vm = Get-AzureRMVM –Name $VMName `
        –ResourceGroupName $RESOURCEGROUP_NAME `
        -ErrorAction SilentlyContinue
    if ($vm)
    { 
        #Next, we need to get the VM ID. This is required to find the associated boot diagnostics container.
        $azResourceParams = @{
            'ResourceName' = $VMName
            'ResourceType' = 'Microsoft.Compute/virtualMachines'
                'ResourceGroupName' = $RESOURCEGROUP_NAME
        }
        $vmResource = Get-AzureRMResource @azResourceParams
        $vmId = $vmResource.Properties.VmId

        # Remove the boot diagnostics
        removeBootDiagnostics($vm)

        # Remove VM
	    Write-Verbose -Message 'Removing the Azure VM...'
	    $null = $vm | Remove-AzureRMVM -Force
	
        removeOSDisksAndStorage($vm)
    }
    else
    {
        Write-Warning "VM not found for removing '$VMName'"
    }
}



Function removeBootDiagnostics($vm, $vmId)
{
    # Thanks https://4sysops.com/archives/delete-an-azure-vm-with-objects-using-powershell 
    if ($vm.DiagnosticsProfile.bootDiagnostics)
    {
	    Write-Verbose -Message 'Removing boot diagnostics storage container...'
	    $diagSa = [regex]::match($vm.DiagnosticsProfile.bootDiagnostics.storageUri, '^http[s]?://(.+?)\.').groups[1].value
	    if ($vm.Name.Length -gt 9) {
		    $i = 9
	    } else {
		    $i = $vm.Name.Length - 1
	    }

	    $diagContainerName = ('bootdiagnostics-{0}-{1}' -f $vm.Name.ToLower().Substring(0, $i), $vmId)
	    $diagSaRg = (Get-AzureRMStorageAccount | `
            where { $_.StorageAccountName -eq $diagSa }).ResourceGroupName
	    $saParams = @{
		    'ResourceGroupName' = $diagSaRg
		    'Name' = $diagSa
	    }
	    Get-AzureRMStorageAccount @saParams | `
            Get-AzureRMStorageContainer | `
            where { $_.Name-eq $diagContainerName } | `
            Remove-AzureRMStorageContainer -Force
    }
}

Function removeOSDisksAndStorage($vm)
{
    Write-Verbose -Message 'Removing OS disk...'
    $osDiskUri = $vm.StorageProfile.OSDisk.Vhd.Uri
    if ($osDiskUri)
    {
    
        $osDiskContainerName = $osDiskUri.Split('/')[-2]
        ## TODO: Does not account for resouce group 
        $osDiskStorageAcct = Get-AzureRMStorageAccount | where { $_.StorageAccountName -eq $osDiskUri.Split('/')[2].Split('.')[0] }
        $osDiskStorageAcct | Remove-AzureRMStorageBlob -Container $osDiskContainerName -Blob $osDiskUri.Split('/')[-1] -ea Ignore

        #region Remove the status blob
        Write-Verbose -Message 'Removing the OS disk status blob...'
        $osDiskStorageAcct | Get-AzureRMStorageBlob -Container $osDiskContainerName -Blob "$($vm.Name)*.status" | Remove-AzureRMStorageBlob
        #endregion
    }

        ## Remove any other attached disks
    if ($vm.DataDiskNames.Count -gt 0)
    {
	    Write-Verbose -Message 'Removing data disks...'
	    foreach ($uri in $vm.StorageProfile.DataDisks.Vhd.Uri)
	    {
		    $dataDiskStorageAcct = Get-AzureRMStorageAccount -Name $uri.Split('/')[2].Split('.')[0]
		    $dataDiskStorageAcct | Remove-AzureRMStorageBlob -Container $uri.Split('/')[-2] -Blob $uri.Split('/')[-1] -ea Ignore
	    }
    }
}


Function removeManagedDisks()
{
    # Set deleteUnattachedDisks=1 if you want to delete unattached Managed Disks
    # Set deleteUnattachedDisks=0 if you want to see the Id of the unattached Managed Disks
    $deleteUnattachedDisks=1
    $managedDisks = Get-AzureRMDisk
    foreach ($md in $managedDisks) {
        # ManagedBy property stores the Id of the VM to which Managed Disk is attached to
        # If ManagedBy property is $null then it means that the Managed Disk is not attached to a VM
        if($md.ManagedBy -eq $null){
            if($deleteUnattachedDisks -eq 1){
                Write-Host "Deleting unattached Managed Disk with Id: $($md.Id)"
                $md | Remove-AzureRMDisk -Force
                Write-Host "Deleted unattached Managed Disk with Id: $($md.Id) "
            }else{
                $md.Id
            }
        }
     }
}

Function removeUnAttachedUnManagedDisks()
{
    # Set deleteUnattachedVHDs=1 if you want to delete unattached VHDs
    # Set deleteUnattachedVHDs=0 if you want to see the Uri of the unattached VHDs
    $deleteUnattachedVHDs=1
    $storageAccounts = Get-AzureRMStorageAccount
    foreach($storageAccount in $storageAccounts){
        $storageKey = (Get-AzureRMStorageAccountKey -ResourceGroupName $storageAccount.ResourceGroupName -Name $storageAccount.StorageAccountName)[0].Value
        $context = New-AzureRMStorageContext -StorageAccountName $storageAccount.StorageAccountName -StorageAccountKey $storageKey
        $containers = Get-AzureRMStorageContainer -Context $context
        foreach($container in $containers){
            $blobs = Get-AzureRMStorageBlob -Container $container.Name -Context $context
            #Fetch all the Page blobs with extension .vhd as only Page blobs can be attached as disk to Azure VMs
            $blobs | Where-Object {$_.BlobType -eq 'PageBlob' -and $_.Name.EndsWith('.vhd')} | ForEach-Object { 
                #If a Page blob is not attached as disk then LeaseStatus will be unlocked
                if($_.ICloudBlob.Properties.LeaseStatus -eq 'Unlocked'){
                        if($deleteUnattachedVHDs -eq 1){
                            Write-Host "Deleting unattached VHD with Uri: $($_.ICloudBlob.Uri.AbsoluteUri)"
                            $_ | Remove-AzureRMStorageBlob -Force
                            Write-Host "Deleted unattached VHD with Uri: $($_.ICloudBlob.Uri.AbsoluteUri)"
                        }
                        else{
                            $_.ICloudBlob.Uri.AbsoluteUri
                        }
                }
            }
        }
}
}

removeLinuxVM -VMName $VIRTUAL_MACHINE_NAME

# Remove any detached managed and unmanaged disks
removeUnAttachedUnManagedDisks
removeManagedDisks



