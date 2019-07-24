#!/bin/bash
source ./parameters.sh
LoggedIn=$(az.cmd account show --query 'id')
if [ $LoggedIn ];
    then 
        echo "User already logged in"
        echo $LoggedIn 
        pwd
    else
        echo "Need to login again"
        az.cmd login
        if [ $? -eq 0 ];
        then
            echo "Login Successful"
        else
            echo "Login Unsuccessul"
        fi
fi 
echo $WEBUSERNAME
Date