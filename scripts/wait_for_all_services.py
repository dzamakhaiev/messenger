"""
That module checks all containers for 'ready to work' state.
"""
from time import sleep
import add_messenger_to_sys_path
import docker
from docker.models.containers import Container
from docker.errors import DockerException
from logger.logger import Logger


listener_logger = Logger('docker_handler')
TIMEOUT = 60
READY_TO_WORK_MARKERS = {
    'nginx-ci': ['start worker processes', 'start worker process'],
    'rabbitmq-ci': ['Ready to start client connection listeners', 'Time to start RabbitMQ:1'],
    'postgres-ci': ['PostgreSQL init process complete; ready for start up.',
                    'database system is ready to accept connections'],
    'listener-ci': ['PostgreSQL connection established.', 'SQLite in-memory connection opened.',
                    'RabbitMQ connection established.', 'Service logger started.'],
    'sender-ci': ['Sender logger started.', 'Service logger started.', 'RabbitMQ connection established.',
                  'SQLite in-memory connection opened.', 'PostgreSQL connection established.']}


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
        containers_logs[container.name] = str(container.logs(), encoding='utf-8', errors='ignore').split('\n')

    return containers_logs


def check_containers_logs_for_markers(containers_logs: dict):
    listener_logger.info('Check containers logs for markers.')
    containers_statuses = {}

    for container_name, container_logs in containers_logs.items():
        listener_logger.debug(f'Container "{container_name}" log length: {len(container_logs)}')

        # Copy markers to remove found markers from log
        container_markers = READY_TO_WORK_MARKERS[container_name][:]

        # Check all markers starting from the end of log
        for log_line in container_logs[::-1]:
            preliminary_flags = []

            if container_markers:
                for log_marker in container_markers:

                    if log_marker in log_line:
                        listener_logger.debug(f'Log marker "{log_marker}" found in "{container_name}" log.')
                        preliminary_flags.append(True)
                        container_markers.remove(log_marker)

            else:
                if all(preliminary_flags):
                    listener_logger.debug(f'All markers are found for "{container_name}".')
                    containers_statuses[container_name] = True
                else:
                    listener_logger.debug(f'Not all markers are found for "{container_name}".')
                    containers_statuses[container_name] = False

    listener_logger.info('Check containers logs completed.')
    return containers_statuses


if __name__ == '__main__':
    running_containers = get_all_containers()
    running_containers_logs = get_containers_logs(running_containers)
    statuses = check_containers_logs_for_markers(running_containers_logs)
    print(statuses)
