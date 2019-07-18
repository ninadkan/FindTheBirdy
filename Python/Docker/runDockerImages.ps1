. "$PSScriptRoot\login.ps1"

$registry = Get-AzContainerRegistry -ResourceGroupName $RESOURCEGROUP_NAME -Name $CONTAINER_REGISTRY_NAME

if ($registry)
{
    $creds = Get-AzContainerRegistryCredential -Registry $registry
    $creds.Password | docker login $registry.LoginServer -u $creds.Username --password-stdin
    $fullName = $FQN_CONTAINER_REGISTRY_NAME + "/" + $DOCKER_IMAGE_PYTHON_CORE
    Write-Host $fullName
    docker run $fullName
}

