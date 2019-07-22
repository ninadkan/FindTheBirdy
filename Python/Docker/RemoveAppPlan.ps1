. "$PSScriptRoot\login.ps1"
#. "$PSScriptRoot\parameters.ps1"

$resource = Get-AzResource -ResourceGroupName $RESOURCEGROUP_NAME -Name $APP_SERVICE_PLAN_NAME -ResourceType microsoft.web/serverfarms -ErrorAction Continue

if ($resource)
{

    $appSrvPlan = Get-AzWebApp -ResourceGroupName $RESOURCEGROUP_NAME -Name $APP_SERVICE_WEB_APP_NAME -Location $LOCATION -AppServicePlan $resource -ErrorAction Continue
    if ($appSrvPlan)
    {
        Write-Host -ForegroundColor DarkRed -Object "Removing Web App {$APP_SERVICE_WEB_APP_NAME}"
        $appSrvPlan = Remove-AzWebApp -ResourceGroupName $RESOURCEGROUP_NAME -Name $APP_SERVICE_WEB_APP_NAME -AppServicePlan  $APP_SERVICE_WEB_APP_NAME
    }

    Write-Host -ForegroundColor DarkRed -Object "Removing App Service plan {$APP_SERVICE_PLAN_NAME}"
    $resource = Remove-AzResource -ResourceGroupName $RESOURCEGROUP_NAME -Name $APP_SERVICE_PLAN_NAME -ResourceType microsoft.web/serverfarms
}


