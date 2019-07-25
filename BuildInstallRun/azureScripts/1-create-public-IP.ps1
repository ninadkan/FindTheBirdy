. "$PSScriptRoot\login.ps1"


$publicIp = Get-AzPublicIpAddress `
    -Name $PUBLIC_IP_NAME `
    -ResourceGroupName $RESOURCEGROUP_NAME `
    -ErrorAction SilentlyContinue

if (!$publicIp)
{
    Write-Host -ForegroundColor Yellow "create a new static IP address ... ";
    $publicIp = New-AzPublicIpAddress  -Name $PUBLIC_IP_NAME `
        -ResourceGroupName $RESOURCEGROUP_NAME -AllocationMethod Static `
        -DomainNameLabel $DNSNAME -Location $LOCATION -Sku "Standard"
}
else
{
    $addr = $publicIp.IpAddress
    Write-Host -ForegroundColor Green "static IP address already exists = '$addr'";
}









