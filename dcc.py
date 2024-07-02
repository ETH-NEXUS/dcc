import click
import sh
from sys import argv
from helpers import TableOutput as T, Message as M, Executor as E
import json
from sys import exit
from os.path import isfile, isdir
from os import environ, getcwd
from dotenv import load_dotenv

docker = sh.Command("docker")
bash = sh.Command("bash")


def __bake_command(command_line: str):
    return (command_line).split()


def __handle_output(output: str) -> str:
    # We remove the last \n
    return output.rstrip("\n")


def __containers(filter: str = None):
    _filter = ""
    if filter:
        _filter = f"--filter name={filter}"
    cmd = docker.bake(*__bake_command("ps -a %s --format {{.Names}}" % _filter))
    return __handle_output(cmd()).split("\n")


def __networks():
    cmd = docker.bake(*__bake_command("network ls --format {{.Name}}"))
    return __handle_output(cmd()).split("\n")


def __inspect(filter: str = None):
    inspection = []
    for cont in __containers(filter):
        cmd = docker.bake(*__bake_command("inspect %s" % cont))
        inspection.append(json.loads(__handle_output(cmd()))[0])
    return inspection


def __inspect_networks():
    inspection = []
    for net in __networks():
        cmd = docker.bake(*__bake_command("network inspect %s" % net))
        inspection.append(json.loads(__handle_output(cmd()))[0])
    return inspection


def __inspect_volumes(filter: str = None):
    list_args = ["volume", "list", "--format", "{{ .Name }}"]
    if filter:
        list_args.append("--filter")
        list_args.append(f"name={filter}")
    vols = docker(*list_args).split("\n")[:-1]
    inspection = []
    for vol in vols:
        args = ["volume", "inspect"]
        inspection.append(json.loads(docker(*args, vol))[0])
    return inspection


def __prepare_compose_command(docker_arguments):
    if not isfile("docker-compose.yml"):
        M.error("There is no docker-compose.yml file in this directory!")
        exit(1)
    dcc_env = None
    env = {
        "GIT_VERSION": "?.?.?",
        "GIT_BRANCH": "N/A",
        "GIT_LASTCOMMITDATE": "N/A",
        "GIT_COMMITHASH": "N/A",
        "UID": 0,
        "GID": 0,
        "UNAME": "root",
    }
    if isfile(".env"):
        load_dotenv(".env")
        dcc_env = environ.get("DCC_ENV")
        M.debug(f"Running DCC environment {dcc_env}.")
    else:
        M.warn(f"No .env file found in current directory: {getcwd()}")
    if isdir(".git"):
        if E.success("git rev-parse --is-inside-work-tree"):
            env["GIT_VERSION"] = E.run("git describe --always")
            env["GIT_BRANCH"] = E.run("git rev-parse --abbrev-ref HEAD")
            env["GIT_LASTCOMMITDATE"] = E.run("git log -1 --format=%cI")
            env["GIT_COMMITHASH"] = E.run("git rev-parse HEAD")
        M.debug("Git repository detected.")
    else:
        M.warn("Not a git repository.")

    env["UID"] = E.run("id -u")
    env["GID"] = E.run("id -g")
    env["UNAME"] = E.run("whoami")
    environ.update(env)

    docker_files = ["docker-compose.yml"]
    if dcc_env:
        docker_files.append(f"docker-compose.{dcc_env}.yml")
    if isfile("docker-compose.override.yml"):
        docker_files.append("docker-compose.override.yml")
    command = (
        f"docker compose -f {' -f '.join(docker_files)} {' '.join(docker_arguments)}"
    )
    M.debug(f"Command: {command}")
    return command


def __execute_compose_command(command: str):
    try:
        bash("-c", command, _fg=True)
    except Exception:
        M.error(f"Error executing command '{command}'.")
        # traceback.print_exc()


@click.command()
@click.argument("filter", required=False)
def ls(filter: str = None):
    _filter = ""
    if filter:
        _filter = f"--filter name={filter}"
    cmd = docker.bake(
        *__bake_command(
            "ps -a %s -a --format {{.Names}}#{{.Status}}#{{.Image}}" % _filter
        )
    )
    output = __handle_output(cmd())
    T.out(output, headers=("Name", "Status", "Image"))


@click.command()
@click.argument("filter", required=False)
def rm(filter: str = None):
    for cont in __containers(filter):
        if cont:
            M.info(f"Removing container {cont}...")
            cmd = docker.bake(*__bake_command("rm -f %s" % cont))
            cmd()


@click.command()
@click.argument("args", nargs=-1)
def clean(args: tuple):
    print(E.run(f"docker image prune -f {' '.join(args)}"))
    print(E.run(f"docker image prune -a -f {' '.join(args)}"))
    print(E.run(f"docker container prune -f {' '.join(args)}"))
    print(E.run(f"docker system prune -f {' '.join(args)}"))
    print(E.run(f"docker builder prune -a -f {' '.join(args)}"))


@click.command()
@click.argument("filter", required=False)
def po(filter: str = None):
    output = ""
    for cont in __containers(filter):
        cmd = docker.bake(*__bake_command("port %s" % cont))
        sep = "\n"
        output += f"{cont}#{', '.join(__handle_output(cmd()).split(sep))}\n"
    T.out(__handle_output(output), headers=("Name", "Ports"))


@click.command()
def net():
    for i in __inspect_networks():
        if i["IPAM"]["Config"]:
            M.info(
                f"{i['Name']}: {', '.join(['sn:' + c['Subnet'] + ' gw:' + c['Gateway'] for c in i['IPAM']['Config']])}"
            )
        else:
            M.info(f"{i['Name']}")
        for _, c in i["Containers"].items():
            M.debug(f"   +-- {c['Name']} {c['IPv4Address']}")


@click.command()
@click.argument("filter", required=False)
def rp(filter: str = None):
    output = ""
    for i in __inspect(filter):
        output += (
            f"{i['Name'].lstrip('/')}#{i['HostConfig']['RestartPolicy']['Name']}\n"
        )
    T.out(__handle_output(output), headers=("Name", "Restart"))


@click.command()
@click.argument("filter", required=False)
def mt(filter: str = None):
    for cont in __containers(filter):
        if cont:
            list_args = ["inspect", "--format", "{{ json .Mounts }}", cont]
            vols = json.loads(docker(*list_args))
            rows = []
            for vol in vols:
                rows.append(f"{vol['Type']}#{vol['Source']}#{vol['Destination']}")
            T.out(rows, headers=("Type", "Source", "Destination"))


@click.command()
@click.argument("filter", required=False)
def vol(filter: str = None):
    rows = []
    for i in __inspect_volumes(filter):
        rows.append(
            f"{i['Name']}#{i['CreatedAt']}#{i['Mountpoint']}#{i['Labels']['com.docker.compose.project'] if 'Labels' in i and i['Labels'] and 'com.docker.compose.project' in i['Labels'] else 'Unknown'}"
        )
    T.out(rows, headers=("Name", "CreatedAt", "Mountpoint", "Project"))


@click.command()
@click.argument("container")
def sh(container: str):
    __execute_compose_command(
        __prepare_compose_command(["exec", container, "/usr/bin/env bash"])
    )


@click.command()
@click.argument("container")
def lg(container: str):
    __execute_compose_command(__prepare_compose_command(["logs", "-ft", container]))


def dcc(docker_arguments):
    __execute_compose_command(__prepare_compose_command(docker_arguments))


if __name__ == "__main__":
    if len(argv) < 2:
        M.warn("Please specify a command:")
        M.info(
            """
            - `ls`: lists all containers on the system with their status
            - `rm`: removes all containers on the system
            - `lg`: follow log files
            - `po`: lists the exposed ports of all running containers
            - `net`: show the network infrastructure
            - `rp`: lists the restart policy of all containers
            - `mt`: show mounts
            - `vol`: show volumes
            - `sh`: opens an interactive shell (bash) at a certain container
            - `clean`: cleans the docker environment
            - or any docker compose command: https://docs.docker.com/compose/reference/
            """
        )
        exit(1)

    if argv[1] in globals().keys():
        globals()[argv[1]](argv[2:])
    else:
        dcc(argv[1:])
