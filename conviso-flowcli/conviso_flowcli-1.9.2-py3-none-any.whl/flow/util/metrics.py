from convisoappsec.flow.source_code_scanner import SCC
import docker

def project_metrics(source_code_dir):
    try:
        scanner = SCC(source_code_dir)
        scanner.scan()
        return {
            'total_lines': scanner.total_source_code_lines
        }
    except docker.errors.APIError:
        return None

