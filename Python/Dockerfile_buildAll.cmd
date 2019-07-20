docker stop $(docker ps -aq)
docker rm $(docker ps -aq)

call Dockerfile_build_messaging_api.cmd
call Dockerfile_build_api.cmd
call Dockerfile_build_core.cmd
