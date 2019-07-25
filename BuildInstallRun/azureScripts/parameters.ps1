$RESOURCEGROUP_NAME="ComputerVisionProject"
$LOCATION="North Europe"
$SUBSCRIPTION_ID="ba1d4485-2ac1-4c28-be39-56e5a0f0185c"
$TENANT="ninadkanthihotmail054.onmicrosoft.com"

$DNSNAME = "computer-vision-proj"
$FQDN="$DNSNAME.northeurope.cloudapp.azure.com"

$VERSION="-v1"

$PUBLIC_IP_NAME="ComputerVisionProj_PublicIp$VERSION"
$DNS_PREFIX="ninadkanthi$VERSION"

$VIRTUALNETWORKNAME = "ComputerVisionProj-VNET"
$SUBNET_NAME = "ComputerVisionProj-VNET-Subnet"
$NSG_NAME = "ComputerVisionProj-VNET-NSG"

$HTTP_NSG_RULE = "http_nsg_rule"
$HTTPS_NSG_RULE = "https_nsg_rule"
$HTTPS_NSG_5002_RULE = "https_nsg_5002_rule"
$HTTPS_NSG_5555_RULE = "https_nsg_5555_rule"
$SSH_NSG_RULE = "ssh_nsg_rule"


$VIRTUAL_MACHINE_NAME="linuxDockerContainer"
$NETWORK_INTERFACE_NAME = "NetworkInterfaceLinuxDocker1"

$WEBUSERNAME = "ninadk"














