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


docker_logger = Logger('docker_handler')
TIMEOUT = 90
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
        docker_logger.info('Check that docker is running.')
        docker.from_env()
        docker_logger.info('Docker is running.')
        return True

    except DockerException as e:
        docker_logger.error(e)
        return False


def get_all_containers(partial_name='ci'):
    docker_logger.info(f'Get all running containers with partial name "{partial_name}"')
    if is_docker_running():

        docker_handler = docker.from_env()
        containers = docker_handler.containers.list()
        containers = [container for container in containers if partial_name in container.name]
        docker_logger.debug(f'Running containers found: {len(containers)}')
        docker_logger.debug(f'Running containers: {[container.name for container in containers]}')
        return containers

    return []


def get_containers_logs(containers: list[Container]):
    containers_logs = {}

    for container in containers:
        containers_logs[container.name] = str(container.logs(), encoding='utf-8', errors='ignore').split('\n')

    return containers_logs


def check_containers_logs_for_markers(containers_logs: dict):
    docker_logger.info('Checking container logs for specific markers.')
    containers_statuses = {}

    for container_name, container_logs in containers_logs.items():
        docker_logger.debug(f'Container "{container_name}" log length: {len(container_logs)}')

        # Copy markers to remove found markers from log
        container_markers = READY_TO_WORK_MARKERS[container_name][:]

        # Check all markers starting from the end of log
        for log_line in container_logs[::-1]:
            preliminary_flags = []

            if container_markers:
                for log_marker in container_markers:

                    # If marker has found in log, delete marker from the list
                    if log_marker in log_line:
                        docker_logger.debug(f'Log marker "{log_marker}" found in "{container_name}" log.')
                        preliminary_flags.append(True)
                        container_markers.remove(log_marker)

            else:
                if all(preliminary_flags):
                    docker_logger.debug(f'All markers are found for "{container_name}".')
                    containers_statuses[container_name] = True
                    break
                else:
                    docker_logger.debug(f'Not all markers are found for "{container_name}".')
                    containers_statuses[container_name] = False

    docker_logger.info('Check containers logs completed.')
    return containers_statuses


def main_loop():
    docker_logger.info('Check containers logs for "ready to work" markers.')
    time_spent = 0
    statuses = {}
    running_containers = []
    running_containers_logs = {}

    while time_spent <= TIMEOUT:
        docker_logger.info('Start new check in loop.')
        running_containers = get_all_containers()
        running_containers_logs = get_containers_logs(running_containers)
        statuses = check_containers_logs_for_markers(running_containers_logs)

        if len(statuses) == len(READY_TO_WORK_MARKERS) and all(statuses.values()):
            docker_logger.info('All containers are ready to work.')
            docker_logger.info(f'Time spent: {time_spent} seconds.')
            break

        elif len(statuses) == len(READY_TO_WORK_MARKERS) and not all(statuses.values()):
            docker_logger.debug('Not all containers are ready to work.')
            time_spent += SLEEP_INTERVAL
            sleep(SLEEP_INTERVAL)

        else:
            docker_logger.debug(f'Not all containers are running:\n{statuses}')
            time_spent += SLEEP_INTERVAL
            sleep(SLEEP_INTERVAL)

    else:
        docker_logger.error(f'Script could not found all "ready to work" '
                            f'markers during {TIMEOUT} seconds.')

        failed_list = [container_name for container_name, status in statuses.items()
                       if status is False]
        not_working_containers = {name: logs for name, logs in running_containers_logs.items()
                                  if name in failed_list}

        docker_logger.info(f'Running containers: {[container.name for container in running_containers]}')
        docker_logger.info(f'Not working containers are: {not_working_containers}')
        for name, logs in not_working_containers.items():
            logs = '\n'.join([line for line in logs])
            docker_logger.info(f'Container "{name}" logs:\n{logs}')

        sys.exit(1)


if __name__ == '__main__':
    main_loop()
