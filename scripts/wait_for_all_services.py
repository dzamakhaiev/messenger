"""
That module checks all containers for 'ready to work' state.
"""
import sys
from time import sleep
import add_messenger_to_sys_path
import docker
from docker.models.containers import Container
from docker.errors import DockerException
from logger.logger import Logger


listener_logger = Logger('docker_handler')
TIMEOUT = 60
SLEEP_INTERVAL = 10
READY_TO_WORK_MARKERS = {
    'nginx-ci': ['start worker processes', 'start worker process'],
    'rabbitmq-ci': ['Ready to start client connection listeners', 'Time to start RabbitMQ:'],
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
        listener_logger.debug(f'Running containers: {[container.name for container in containers]}')
        return containers

    return []


def get_containers_logs(containers: list[Container]):
    containers_logs = {}

    for container in containers:
        containers_logs[container.name] = str(container.logs(), encoding='utf-8', errors='ignore').split('\n')

    return containers_logs


def check_containers_logs_for_markers(containers_logs: dict):
    listener_logger.info('Checking container logs for specific markers.')
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
                    break
                else:
                    listener_logger.debug(f'Not all markers are found for "{container_name}".')
                    containers_statuses[container_name] = False

    listener_logger.info('Check containers logs completed.')
    return containers_statuses


def main_loop():
    listener_logger.info('Check containers logs for "ready to work" markers.')
    time_spent = 0

    while time_spent <= TIMEOUT:
        listener_logger.info('Start new check in loop.')
        running_containers = get_all_containers()
        running_containers_logs = get_containers_logs(running_containers)
        statuses = check_containers_logs_for_markers(running_containers_logs)

        if len(statuses) == len(READY_TO_WORK_MARKERS) and all(statuses.values()):
            listener_logger.info('All containers are ready to work.')
            listener_logger.info(f'Time spent: {time_spent} seconds.')
            break

        elif len(statuses) == len(READY_TO_WORK_MARKERS) and not all(statuses.values()):
            listener_logger.debug('Not all containers are ready to work.')
            time_spent += SLEEP_INTERVAL
            sleep(SLEEP_INTERVAL)

        else:
            listener_logger.debug('Not all containers are running.')
            time_spent += SLEEP_INTERVAL
            sleep(SLEEP_INTERVAL)

    else:
        listener_logger.error(f'Script could not found all "ready to work" '
                              f'markers during {TIMEOUT} seconds.')
        sys.exit(1)


if __name__ == '__main__':
    main_loop()
