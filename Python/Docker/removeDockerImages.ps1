. "$PSScriptRoot\login.ps1"

$registry = Get-AzContainerRegistry -ResourceGroupName $RESOURCEGROUP_NAME -Name $CONTAINER_REGISTRY_NAME
if (!$registry){
    $registry = New-AzContainerRegistry -ResourceGroupName $RESOURCEGROUP_NAME -Name $CONTAINER_REGISTRY_NAME -EnableAdminUser -Sku Standard
}


Function removeImage($LocalDockerImageName)
{
    $fullName = $FQN_CONTAINER_REGISTRY_NAME + "/" + $LocalDockerImageName
    Write-Host $fullName
    docker rmi $fullName
}

if ($registry)
{
    $creds = Get-AzContainerRegistryCredential -Registry $registry
    $creds.Password | docker login $registry.LoginServer -u $creds.Username --password-stdin

    
    removeImage -LocalDockerImageName $DOCKER_IMAGE_PYTHON_API
    removeImage -LocalDockerImageName $DOCKER_IMAGE_PYTHON_MESSAGINGAPI
    removeImage -LocalDockerImageName $DOCKER_IMAGE_WEB
    removeImage -LocalDockerImageName $DOCKER_IMAGE_PYTHON_CORE
}


