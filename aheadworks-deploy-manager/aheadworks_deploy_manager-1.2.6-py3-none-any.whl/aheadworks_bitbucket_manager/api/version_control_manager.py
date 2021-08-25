from aheadworks_bitbucket_manager.model.ssh_manager import SshManager
from aheadworks_bitbucket_manager.model.parser.php import Php as PhpParser
import re
import ast
import os


class VersionControlManager:

    def __init__(self):
        self.ssh_manager = SshManager()
        self.php_parser = PhpParser()

    def run_common_app(self, check_containers_arr, up_cmd, host, user):
        command = 'docker ps -q'
        for container_name in check_containers_arr:
            command += ' -f name=' + container_name

        container_ids_arr = self.ssh_manager.run_ssh_command(command, host, user)

        if len(container_ids_arr) != len(check_containers_arr):
            run_result = self.ssh_manager.run_ssh_command(up_cmd, host, user)
            run_result = type(run_result) == list and '\n'.join(run_result)
        else:
            run_result = 'All Common App containers exists'

        return 'run_result:\n' + run_result

    def run_app(
            self,
            path_to_versions,
            path_to_project,
            up_cmd,
            down_exclude_current,
            down_cmd,
            host,
            user
    ):
        """
        :param path_to_versions: path to versions.
        :param path_to_project: path to project folder.
        :param up_cmd: command for run active apps.
        :param down_exclude_current: yes/no, down all app in project.
        :param down_cmd: command for down old apps.
        :param host: host url.
        :param user: host user.
        """
        print('path to versions: ' + path_to_versions)
        print('path to project with releases on server: ' + path_to_project)
        print('run app command: ' + up_cmd)
        print('down all released app in project folder exclude current: ' + down_exclude_current)
        print('kill app command: ' + down_cmd)

        version_config_item_name = ['VERSION', 'SAVE_VERSION']

        save_versions = []
        for var_name in version_config_item_name:
            var_value = self.php_parser.get_variable_from_file(var_name, path_to_versions).strip()
            if var_value:
                save_versions.append(var_value)

        dir_items = self.ssh_manager.run_ssh_command('ls ' + path_to_project, host, user)
        # sort dirs by path by desc
        dir_items = self._sort_versions(dir_items)

        kill_app_paths = []
        run_app_paths = {}
        for item in dir_items:
            item = item.strip()
            item_arr = item.split('-')
            item_arr = len(item_arr) == 1 and item_arr.append('') or item_arr
            item_version, item_build = item_arr[:2]
            if item_version in save_versions and item_version not in run_app_paths:
                run_app_paths[item_version] = item
            else:
                kill_app_paths.append(item)

        run_commands = []
        for key in run_app_paths:
            path_to_project_item = path_to_project + '/' + run_app_paths[key]
            run_commands.append(
                'cd ' + path_to_project_item
                + ' && ' + up_cmd
            )

        run_result = ''
        run_command = ''
        if run_commands:
            run_command = ' && '.join(run_commands)
            run_result = self.ssh_manager.run_ssh_command(run_command, host, user)
            run_result = type(run_result) == list and '\n'.join(run_result)

        # down all app in project
        kill_result = ''
        down_command = ''
        if down_exclude_current == 'yes':
            kill_commands = []
            for item in kill_app_paths:
                path_to_project_item = path_to_project + '/' + item
                kill_commands.append(
                    'cd ' + path_to_project_item + '; '
                    + down_cmd + '; '
                    + 'rm -rf ' + path_to_project_item
                )

            if kill_commands:
                down_command = ' && '.join(kill_commands)
                kill_result = self.ssh_manager.run_ssh_command(down_command, host, user)
                kill_result = type(run_result) == list and '\n'.join(kill_result)

        return '\nrun commands:\n' + str(run_command) \
               + '\n\nkill commands:\n' + str(down_command) \
               + '\n\nrun_result:\n' + str(run_result) \
               + '\n\nkill_result:\n' + str(kill_result)

    def get_version_uid(self, version):
        version_uid = re.sub('[.]', '', version)

        return version_uid

    def get_traefik_version_query(self, path_to_versions):
        magento_version_control = self.php_parser.get_variable_from_file('MAGENTO_VERSION_CONTROL', path_to_versions)
        magento_version_control = magento_version_control \
            .replace('[', '{') \
            .replace(']', '}') \
            .replace('=>', ':') \
            .replace('\n', '')
        magento_version_control = ast.literal_eval(magento_version_control)

        app_curr_full_version = self.php_parser.get_variable_from_file('VERSION', path_to_versions)
        app_curr_major_version = app_curr_full_version.split('.')[0:-1]
        app_curr_major_version.append('*')
        app_curr_major_version = '.'.join(app_curr_major_version)
        app_version_map = [app_curr_full_version, app_curr_major_version]

        query = ''
        for module_version, app_version in magento_version_control.items():
            app_version = list(app_version)[0]
            if app_version in app_version_map:
                query = '&& Query(`version={version:' + module_version + '}`)' \
                        + ' || Query(`ver={ver:' + app_version + '}`)' \
                        + ' || HeadersRegexp(`referer`, `(.*)version=' + module_version + '`)' \
                        + ' || HeadersRegexp(`referer`, `(.*)ver=' + app_version + '`)'

        return query

    # --priority_type low or --priority_type height
    def get_free_priority(self, label_name, priority_type, host, user):
        busy_priority = self.ssh_manager.run_ssh_command(
            'docker ps --format \'{{.Label "' + label_name + '"}}\'',
            host,
            user
        )
        filtered_busy_priority = []
        for item in busy_priority:
            item = item.strip()
            if item:
                try:
                    filtered_busy_priority.append(int(item))
                except:
                    pass

        new_priority = 10
        if priority_type == 'low':
            while True:
                if new_priority not in filtered_busy_priority:
                    break
                new_priority += 1
        elif priority_type == 'height':
            if filtered_busy_priority:
                max_priority = max(filtered_busy_priority)
                new_priority = max_priority + 10

        return new_priority

    def get_free_port(self, host, user):
        busy_ports = self.ssh_manager.run_ssh_command(
            'docker ps --format \'{{.Label "aw.apps.app_port_prefix"}}\'',
            host,
            user
        )
        filtered_busy_ports = []
        for item in busy_ports:
            item = item.strip()
            if item:
                try:
                    filtered_busy_ports.append(int(item))
                except:
                    pass

        new_port = 10
        while True:
            if new_port not in filtered_busy_ports:
                break
            new_port += 1

        return new_port

    def modify_env(self, path, template):
        os.system('touch ' + path)
        with open(template, 'r') as f:
            original_lines = f.readlines()
        modify_lines = list()
        for line in original_lines:
            if line.find('=') != -1:
                split_line = line.split('=')
                param = split_line[0]
                value = split_line[1]
                pattern = "%(.*?)%"
                match_values = re.findall(pattern, value)
                if len(match_values):
                    for match_value in match_values:
                        match_value_arr = match_value.split(':-')
                        match_value_arr = len(match_value_arr) == 1 and match_value_arr.append('') or match_value_arr
                        match_value, match_value_default = match_value_arr[:2]
                        if match_value in os.environ and os.environ[match_value]:
                            line = re.sub(pattern, os.environ[match_value], line)
                        elif match_value_default:
                            if match_value_default[0] == '$':
                                match_value_default_env = match_value_default[1:]
                                if match_value_default_env in os.environ and os.environ[match_value_default_env]:
                                    line = re.sub(pattern, os.environ[match_value_default_env], line)
                                else:
                                    line = ''
                            else:
                                line = re.sub(pattern, match_value_default, line)
                        else:
                            line = ''
            modify_lines.append(line)
        nf = open(path, 'w')
        nf.writelines(item for item in modify_lines)
        nf.close()
        return

    def _sort_versions(self, items):
        versions = []
        build_versions = []
        for item in items:
            if item.find('-') == -1:
                versions.append(item)
            else:
                build_versions.append(item)

        versions = self._sort_version_string(versions)
        build_versions = self._sort_version_string(build_versions)

        return versions + build_versions

    def _sort_version_string(self, items):
        return sorted(items, key=lambda s: list(map(str, s.replace('-', '').replace('.', ''))), reverse=True)
