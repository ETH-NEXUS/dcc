# Docker Compose Command-Wrapper (DCC)

The `docker compose` command wrapper is a shortcut for the command `docker compose`. On top of that it supports using different `docker-compose.yml` files depending on the `DCC_ENV` variable.

It will wrap the docker compose command like this:

```bash
docker compose -f docker-compose.yml -f docker-compose.${DCC_ENV}.yml $@
```

`$@`: these are all additional parameters you provide the `dcc` command. For example, assuming the `DCC_ENV` variable is `dev`, if you type

```bash
dcc up -d
```

the following command will be executed:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

You can use all `docker compose` command line arguments documented in the [official documentation](https://docs.docker.com/compose/reference/), except the [special commands](#special-commands) described below.

It also reads the `.env` file every time the command is run and, if you are working in a git repository, it sets some `git` related environment variables such as

- `GIT_VERSION=$(git describe --always)`
- `GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD`)
- `GIT_LASTCOMMITDATE=$(git log -1 --format=%cI)`
- `GIT_COMMITHASH=$(git rev-parse HEAD)`

## Special commands

To shorthand often used commands the following shorthands are available:

- `ls`: lists all containers on the system with their status
- `rm`: removes all containers on the system
- `lg`: follow log files
- `po`: lists the exposed ports of all running containers
- `rp`: lists the restart policy of all containers
- `mt`: show mounts
- `sh`: opens an interactive shell (bash) at a certain container
- `clean`: cleans the docker environment

## Installation

```bash
curl -Ls https://raw.githubusercontent.com/ETH-NEXUS/dcc/main/setup.sh | sh
```
