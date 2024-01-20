import os
import docker
import logging
import requests
from typing import List

client = docker.from_env()

logger = logging.getLogger(__name__)

# the philosophy of this module is that, for now we will only support
# one geth container running at a time for simplicity, for a single version
# multiple geth containers can be unstable and unpredictable for now

# and right now, we will only be supporting linux/unix systems for simplicity

def map_architecture(architecture: str):
    architecture_mapping = {
        "x86_64": "amd64",
        "armv7l": "arm",
        "arm64": "arm64",
        "aarch64": "arm64",
        "amd64": "amd64"
    }

    if architecture not in architecture_mapping:
        raise ValueError(f"Unknown architecture: {architecture}")
    
    return architecture_mapping[architecture]

# returns the latest version of geth
def verify_and_get_tag(docker_install_version=None) -> str:
    # if docker_install_version="latest", return latest tag

    GITHUB_API = "https://api.github.com/repos/ethereum/go-ethereum/"

    if docker_install_version is None:
        docker_install_version = "latest"
    else:
        docker_install_version = f"{docker_install_version}"

    RELEASES_API = GITHUB_API + "releases/"

    release_url = f"{RELEASES_API}{docker_install_version}"

    r = requests.get(release_url)
    if r.status_code == 404:
        raise ValueError(f"Unable to find docker install version: {docker_install_version} from URL: {release_url}")
    elif r.status_code != 200:
        raise ValueError(f"Unexpected status code while checking for geth versions: {r.status_code}")
    
    release_data = r.json()
    if docker_install_version == "latest":
        docker_install_version = release_data.get("tag_name")
        commit_tag = release_data.get("target_commitish")

    if docker_install_version is None or commit_tag is None:
        raise ValueError(f"Unable to find docker install version/commit tag: {docker_install_version}/{commit_tag}")
   
    # detect arm or amd64
    arc = os.uname().machine
    architecture = map_architecture(arc)

    # check if image ethereum/client-go:{docker_install_version}-{architecture} exists
    repository = "ethereum/client-go"
    tag = f"{docker_install_version}-{architecture}"

    # check if tag exists on docker hub
    image_url = f"https://hub.docker.com/v2/repositories/{repository}/tags/{tag}"
    r = requests.head(image_url)
    if r.status_code != 200:
        raise ValueError(f"Unable to find docker image {tag} from URL: {image_url}")
    
    total_image_tag = f"{repository}:{tag}"

    return total_image_tag

# return image tag (useful for external use)
# just in case, "latest" was given
def image_fix(docker_install_version=None, docker_image_tag=None) -> str:
    # check all folders initialised in ~/.py-geth that start with "v"
    path = os.path.join(os.path.expanduser("~"), ".py-geth")
    if os.path.exists(path):
        listed = os.listdir(path)
        for folder in listed:
            if folder.startswith("v"):
                if docker_install_version is None:
                    # use the first folder
                    docker_install_version = folder
                    architecture = map_architecture(os.uname().machine)
                    docker_image_tag = f"ethereum/client-go:{docker_install_version}-{architecture}"
                    # found_locally = True
                    break

    tag = docker_image_tag
    if tag is None:
        # get the latest version of geth
        tag = verify_and_get_tag(docker_install_version=docker_install_version)
    
    # check if image exists
    try:
        client.images.get(tag)
        logger.info(f"Image already exists: {tag}")
    except docker.errors.ImageNotFound:
        logger.info(f"Pulling image: {tag}")
        try:
            client.images.pull(tag)
        except docker.errors.APIError as e:
            raise ValueError(f"Unable to pull image: {tag}") from e

    # create folder with geth version in ~/.py-geth
    geth_version = tag.split(":")[1]
    ethereum_path = os.path.join(os.path.expanduser("~"), ".py-geth", geth_version, ".ethereum")
    
    if not os.path.exists(ethereum_path):
        os.makedirs(ethereum_path)
    
    return tag

def stop_container(container: docker.models.containers.Container):
    container.stop()
    container.remove()

# returns a list of all containers using image_name
def image_to_containers(image_name: str) -> List[docker.models.containers.Container]:
    if image_name == "latest":
        image_name = verify_and_get_tag()

    try:
        client.images.get(image_name)
    except docker.errors.ImageNotFound:
        return []
    
    containers = client.containers.list(
        all=True, 
        filters={
            "ancestor": image_name,
        }
    )

    if len(containers) == 0:
        return []
    else:
        return containers

def fix_containers(image_name: str):
    containers = image_to_containers(image_name)
    for container in containers:
        container.stop()
        container.remove()

# image must be existing
# this function assumes that image_name has
# the version number in it as it's tag
def start_container(image_name: str, commands: List[str] = []):
    # check if image exists
    try:
        client.images.get(image_name)
    except docker.errors.ImageNotFound as e:
        raise ValueError("Image not found") from e
    
    image_version_with_arc = image_name.split(":")[1]
    image_version = image_version_with_arc.split("-")[0]

    ethereum_path = os.path.join(os.path.expanduser("~"), ".py-geth", image_version, ".ethereum")

    if not os.path.exists(ethereum_path):
        os.makedirs(ethereum_path)
    
    fix_containers(image_name)

    # build container with image_name
    # and mount ethereum_path to /root/.ethereum
    container = client.containers.run(
        image_name, 
        detach=True, 
        volumes={
            ethereum_path: {
                "bind": "/root/.ethereum", 
                "mode": "rw"
            }
        },
        command=" ".join(commands)
    )

    return container
