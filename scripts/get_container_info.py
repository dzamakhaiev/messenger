import os
import docker
from docker.errors import NotFound, DockerException
from logger.logger import Logger


docker_logger = Logger('docker_handler')


def get_container_host(container_name: str):
    docker_logger.info('Try to get docker container network info.')

    # Check ENV variables
    run_inside_docker = int(os.environ.get('RUN_INSIDE_DOCKER', 0))
    ci_run = int(os.environ.get('CI_RUN', 0))
    docker_logger.info(f'Run inside docker: {run_inside_docker}\n'
                       f'Continuous Integration: {ci_run}\n')
    if docker_is_running():
        docker_handler = docker.from_env()
    else:
        return

    if docker_handler.ping():
        docker_logger.info('Docker is running.')
    else:
        docker_logger.info('Docker is not running.')
        return

    # Get container network settings
    if container_is_running(container_name):
        container = docker_handler.containers.get(container_name)
        container_info = container.attrs
        networks = container_info.get('NetworkSettings').get('Networks')
        docker_logger.debug(f'Networks found:\n"{networks}"')

    else:
        return

    # Define container hostname for prod network
    if networks.get('backend-prod') and run_inside_docker and ci_run:
        docker_logger.info(f'Container "{container_name}" is in prod network.')
        return container_name

    # Define container hostname for ci network
    elif networks.get('backend-ci') and run_inside_docker and ci_run:
        docker_logger.info(f'Container "{container_name}" is in ci network.')
        return container_name

    # Define container hostname for default bridge network
    elif networks.get('bridge') and run_inside_docker and ci_run:
        docker_logger.info(f'Container "{container_name}" is outside prod and ci networks.')
        network = networks.get('bridge')
        docker_logger.debug(f'Network: "{network}"')
        return network.get('IPAddress')

    else:
        docker_logger.info(f'Container "{container_name}" is running locally.')
        return 'localhost'


def docker_is_running():
    try:
        docker_handler = docker.from_env()
        return docker_handler.ping()
    except DockerException as e:
        docker_logger.error(f'Cannot connect with Docker: {e}')
        return False


def container_is_running(container_name: str):
    if docker_is_running():

        docker_handler = docker.from_env()
        try:
            docker_logger.info(f'Container "{container_name}" is running.')
            docker_handler.containers.get(container_name)
            return True

        except NotFound:
            docker_logger.info(f'Container "{container_name}" is not running.')
            return False

    return False


if __name__ == '__main__':
    get_container_host('rabbitmq')
