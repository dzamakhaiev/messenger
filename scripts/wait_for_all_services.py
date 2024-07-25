import add_messenger_to_sys_path
import docker
from docker.models.containers import Container
from docker.errors import DockerException
from logger.logger import Logger


listener_logger = Logger('docker_handler')


def is_docker_running():
    try:
        listener_logger.info('Check that docker is running.')
        docker.from_env()
        listener_logger.info('Docker is running.')
        return True

    except DockerException as e:
        listener_logger.error(e)
        return False


def get_all_containers(partial_name='ci'):
    listener_logger.info(f'Get all running containers with partial name "{partial_name}"')
    if is_docker_running():

        docker_handler = docker.from_env()
        containers = docker_handler.containers.list()
        containers = [container for container in containers if partial_name in container.name]
        listener_logger.debug(f'Running containers found: {len(containers)}')
        return containers

    return []


def get_containers_logs(containers: list[Container]):
    containers_logs = {}

    for container in containers:
        containers_logs[container.name] = str(container.logs(), encoding='utf-8', errors='ignore')

    return containers_logs


if __name__ == '__main__':
    running_containers = get_all_containers()
    running_containers_logs = get_containers_logs(running_containers)
