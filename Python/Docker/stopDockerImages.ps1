. "$PSScriptRoot\login.ps1"

$registry = Get-AzContainerRegistry -ResourceGroupName $RESOURCEGROUP_NAME -Name $CONTAINER_REGISTRY_NAME

Function stopImage($LocalDockerImageName)
{
    $fullName = $FQN_CONTAINER_REGISTRY_NAME + "/" + $LocalDockerImageName
    Write-Host $fullName
    docker stop $fullName
}

if ($registry)
{
    $creds = Get-AzContainerRegistryCredential -Registry $registry
    $creds.Password | docker login $registry.LoginServer -u $creds.Username --password-stdin

    
    stopImage -LocalDockerImageName $DOCKER_IMAGE_PYTHON_API
    stopImage -LocalDockerImageName $DOCKER_IMAGE_PYTHON_MESSAGINGAPI
    stopImage -LocalDockerImageName $DOCKER_IMAGE_WEB
    stopImage -LocalDockerImageName $DOCKER_IMAGE_PYTHON_CORE
}

