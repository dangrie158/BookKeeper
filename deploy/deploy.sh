#!/bin/bash
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../" && pwd)/"
echo "${BASE_DIR}"

set -e
pre-commit run --all-files

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
    ssh ${DEPLOY_HOST} "cd ${DEPLOY_PATH}/bookkeeper && ${@}"
}

function remote_docker_compose(){
    remote_command docker-compose --env-file=.env --file=deploy/docker-compose.yml --project-name=bookkeeper $@
}

remote_docker_compose down
remote_docker_compose build
remote_docker_compose up -d
