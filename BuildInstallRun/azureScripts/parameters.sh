#!/bin/bash
export RESOURCEGROUP_NAME='ComputerVisionProject'
export LOCATION='North Europe'
export SUBSCRIPTION_ID='ba1d4485-2ac1-4c28-be39-56e5a0f0185c'
export TENANT='ninadkanthihotmail054.onmicrosoft.com'

export DNSNAME='computer-vision-proj'
export FQDN='export DNSNAME.northeurope.cloudapp.azure.com'

export VERSION='-v1'

export PUBLIC_IP_NAME='ComputerVisionProj_PublicIpexport$VERSION'
export DNS_PREFIX='ninadkanthiexport$VERSION'

export VIRTUALNETWORKNAME='ComputerVisionProj-VNET'
export SUBNET_NAME='ComputerVisionProj-VNET-Subnet'
export NSG_NAME='ComputerVisionProj-VNET-NSG'

export HTTP_NSG_RULE='http_nsg_rule'
export HTTPS_NSG_RULE='https_nsg_rule'
export SSH_NSG_RULE='ssh_nsg_rule'

export VIRTUAL_MACHINE_NAME='linuxDockerContainer'
export NETWORK_INTERFACE_NAME='NetworkInterfaceLinuxDocker1'

export WEBUSERNAME='ninadk'