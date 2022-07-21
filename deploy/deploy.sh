#!/bin/bash
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../" && pwd)/"
echo "${BASE_DIR}"

# load the prod-env file
if [ -f .env ]; then
    # Load Environment Variables
    export $(echo $(cat .env | sed 's/#.*//g'| xargs) | envsubst)
fi

echo -e "\033[0;32mUploading files\033[0m"
if [[ ! -z "${DEPLOY_HOST}" ]]; then
    rsync --info=progress2 --human-readable --exclude=app_data/ --exclude=.mypy_cache/ -ar ${BASE_DIR} ${DEPLOY_HOST}:${DEPLOY_PATH}/bookkeeper
fi

function remote_command(){
    ssh ${DEPLOY_HOST} "cd ${DEPLOY_PATH}/bookkeeper && ${1}"
}

remote_command "docker-compose --env-file=.env --file=deploy/docker-compose.yml down"
remote_command "docker-compose --env-file=.env --file=deploy/docker-compose.yml build"
remote_command "docker-compose --env-file=.env --file=deploy/docker-compose.yml up -d"
