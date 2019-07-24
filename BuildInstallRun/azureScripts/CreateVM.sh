#!/bin/bash
source ./login.sh
az.cmd vm create \
    --resource-group $RESOURCEGROUP_NAME \
    --name $VIRTUAL_MACHINE_NAME \
    --image UbuntuLTS \
    --admin-username $WEBUSERNAME \
    --generate-ssh-keys \
    --nics $NETWORK_INTERFACE_NAME \
    --custom-data cloud-init.txt

        if [ $? -eq 0 ];
        then
            echo "VM creation Successful"
        else
            echo "VM creation Unsuccessul"
        fi
