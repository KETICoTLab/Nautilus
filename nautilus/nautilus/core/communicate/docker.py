import docker
from docker.errors import NotFound, APIError

def exec_command_in_container(container_name: str, command: str) -> str:
    """
    docker-compose로 띄운 컨테이너에서 명령어 실행

    :param container_name: docker-compose로 실행된 컨테이너 이름
    :param command: 실행할 bash 명령어 (str)
    :return: 출력 결과 (str)
    """
    client = docker.from_env()
    try:
        container = client.containers.get(container_name)
        print(f"📦 Executing in container: {container.name} -> {command}")
        exec_log = container.exec_run(cmd=["/bin/bash", "-c", command], stdout=True, stderr=True)
        output = exec_log.output.decode('utf-8')
        print("✅ Command executed.")
        return output
    except NotFound:
        return f"❌ Container '{container_name}' not found."
    except APIError as e:
        return f"❌ Docker API error: {e.explanation}"
    except Exception as e:
        return f"❌ General error: {str(e)}"
