#!/bin/bash

echo remove containers
(cd "$DOCKER_PATH" && docker-compose down)

