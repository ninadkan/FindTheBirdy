﻿. "$PSScriptRoot\login.ps1"

Function startLinuxVM($VMName)
{
    $vm = Get-AzVM –Name $VMName `
        –ResourceGroupName $RESOURCEGROUP_NAME `
        -ErrorAction SilentlyContinue
    if ($vm)
    { 
        Start-AzVM `
            -Name $VMName `
            -ResourceGroupName $RESOURCEGROUP_NAME
        
    }
    else
    {
        Write-Warning "VM not found for removing '$VMName'"
    }
}


startLinuxVM -VMName $VIRTUAL_MACHINE_NAME
