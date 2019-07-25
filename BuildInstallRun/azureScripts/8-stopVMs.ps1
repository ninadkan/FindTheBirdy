. "$PSScriptRoot\login.ps1"

Function stopLinuxVM($VMName)
{
    $vm = Get-AzureRMVM –Name $VMName `
        –ResourceGroupName $RESOURCEGROUP_NAME `
        -ErrorAction SilentlyContinue
    if ($vm)
    { 
        Stop-AzureRMVM `
            -Name $VMName `
            -ResourceGroupName $RESOURCEGROUP_NAME
    }
    else
    {
        Write-Warning "VM not found for removing '$VMName'"
    }
}


stopLinuxVM -VMName $VIRTUAL_MACHINE_NAME


