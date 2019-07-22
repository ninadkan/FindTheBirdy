. "$PSScriptRoot\login.ps1"

$registry = Get-AzContainerRegistry -ResourceGroupName $RESOURCEGROUP_NAME -Name $CONTAINER_REGISTRY_NAME
if (!$registry){
    $registry = New-AzContainerRegistry -ResourceGroupName $RESOURCEGROUP_NAME -Name $CONTAINER_REGISTRY_NAME -EnableAdminUser -Sku Standard
}


Function uploadImage($LocalDockerImageName)
{
    $fullName = $FQN_CONTAINER_REGISTRY_NAME + "/" + $LocalDockerImageName
    Write-Host $fullName
    docker tag $LocalDockerImageName $fullName
    docker push $fullName
}


if ($registry)
{
    $creds = Get-AzContainerRegistryCredential -Registry $registry
    $creds.Password | docker login $registry.LoginServer -u $creds.Username --password-stdin
    
    uploadImage -LocalDockerImageName $DOCKER_IMAGE_PYTHON_API
    uploadImage -LocalDockerImageName $DOCKER_IMAGE_PYTHON_MESSAGINGAPI
    uploadImage -LocalDockerImageName $DOCKER_IMAGE_WEB
    uploadImage -LocalDockerImageName $DOCKER_IMAGE_PYTHON_CORE
}

