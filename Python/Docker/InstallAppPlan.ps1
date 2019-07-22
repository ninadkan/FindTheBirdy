. "$PSScriptRoot\login.ps1"
#. "$PSScriptRoot\parameters.ps1"

#az login
#az account set -s ba1d4485-2ac1-4c28-be39-56e5a0f0185c
#az appservice plan show --name $APP_SERVICE_PLAN_NAME --resource-group $RESOURCEGROUP_NAME --output json
#az appservice plan list --resource-group $RESOURCEGROUP_NAME

$resource = Get-AzResource -ResourceGroupName $RESOURCEGROUP_NAME -Name $APP_SERVICE_PLAN_NAME -ResourceType microsoft.web/serverfarms -ErrorAction Continue
if (!$resource)
{
    Write-Host -ForegroundColor DarkRed -Object "Creating App Service plan {$APP_SERVICE_PLAN_NAME}"
    $resource = New-AzResource -ResourceGroupName $RESOURCEGROUP_NAME -ResourceName $APP_SERVICE_PLAN_NAME -Location $LOCATION -ResourceType microsoft.web/serverfarms -Kind linux -Sku @{name="S1";tier="Standard"; size="S1"; family="S"; capacity="1"}
}

if ($resource)
{
    Write-Host -ForegroundColor Green -Object "App Service plan Available {$APP_SERVICE_PLAN_NAME}"
    $appSrvPlan = Get-AzWebApp -Name $APP_SERVICE_WEB_APP_NAME -Location $LOCATION -ResourceGroupName $RESOURCEGROUP_NAME -ErrorAction Continue
    if (!$appSrvPlan)
    {
        Write-Host -ForegroundColor DarkRed -Object "Creating Web App {$APP_SERVICE_PLAN_NAME}"
        $appSrvPlan = New-AzWebApp -ResourceGroupName $RESOURCEGROUP_NAME -Name $APP_SERVICE_WEB_APP_NAME -AppServicePlan  $APP_SERVICE_WEB_APP_NAME
    }    
}

#New-AzureRmResource -ResourceGroupName <ResourceGroupName> -Location <Location> -ResourceType microsoft.web/serverfarms -ResourceName <YourPlanName> -kind linux -Properties @{reserved="true"} -Sku @{name="S1";tier="Standard"; size="S1"; family="S"; capacity="1"} -Force
#New-AzureRmWebApp -ResourceGroupName <ResourceGroupName> -Name <YourAppName> -AppServicePlan <YourPlanName>



#if ($appSrvPlan)
#{
#    $wepApp = Get-AzWebApp -Name $APP_SERVICE_WEB_APP_NAME -ResourceGroupName $RESOURCEGROUP_NAME
#    if (!$wepApp)
#    {
#        $wepApp = New-AzWebApp -Name $APP_SERVICE_WEB_APP_NAME -ResourceGroupName $RESOURCEGROUP_NAME -Location $LOCATION -AppServicePlan $appSrvPlan -EnableContainerContinuousDeployment compose 
#        
#    }
#}


#Function uploadImage($LocalDockerImageName)
#{
#    $fullName = $FQN_CONTAINER_REGISTRY_NAME + "/" + $LocalDockerImageName
#    Write-Host $fullName
#    docker tag $LocalDockerImageName $fullName
#    docker push $fullName
#}


#if ($registry)
#{
#    $creds = Get-AzContainerRegistryCredential -Registry $registry
#    $creds.Password | docker login $registry.LoginServer -u $creds.Username --password-stdin
#    
#    uploadImage -LocalDockerImageName $DOCKER_IMAGE_PYTHON_API
#    uploadImage -LocalDockerImageName $DOCKER_IMAGE_PYTHON_MESSAGINGAPI
#    uploadImage -LocalDockerImageName $DOCKER_IMAGE_WEB
#    uploadImage -LocalDockerImageName $DOCKER_IMAGE_PYTHON_CORE
#}
