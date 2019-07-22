. "$PSScriptRoot\login.ps1"



$registry = Get-AzContainerRegistry -ResourceGroupName $RESOURCEGROUP_NAME -Name $CONTAINER_REGISTRY_NAME
if (!$registry){
    $registry = New-AzContainerRegistry -ResourceGroupName $RESOURCEGROUP_NAME -Name $CONTAINER_REGISTRY_NAME -EnableAdminUser -Sku Standard
}


Function runImage($LocalDockerImageName)
{
    $fullName = $FQN_CONTAINER_REGISTRY_NAME + "/" + $LocalDockerImageName
    Write-Host $fullName
    docker run $fullName
}

if ($registry)
{
    $creds = Get-AzContainerRegistryCredential -Registry $registry
    $creds.Password | docker login $registry.LoginServer -u $creds.Username --password-stdin

    
    runImage -LocalDockerImageName $DOCKER_IMAGE_PYTHON_API
    runImage -LocalDockerImageName $DOCKER_IMAGE_PYTHON_MESSAGINGAPI
    runImage -LocalDockerImageName $DOCKER_IMAGE_WEB
    #runImage -LocalDockerImageName $DOCKER_IMAGE_PYTHON_CORE
}


