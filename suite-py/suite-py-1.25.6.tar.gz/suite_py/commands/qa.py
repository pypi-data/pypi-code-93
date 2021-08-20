# -*- coding: utf-8 -*-

import sys
import json
import copy
import re

from rich.table import Table
from rich.console import Console
from suite_py.lib import logger
from suite_py.lib.handler import prompt_utils
from suite_py.lib.handler.qainit_handler import QainitHandler
from suite_py.lib.handler import git_handler as git
from suite_py.lib.handler.git_handler import GitHandler
from suite_py.lib.handler.youtrack_handler import YoutrackHandler


class QA:
    def __init__(self, action, project, config, tokens, flags=None):
        self._action = action
        self._project = project
        self._flags = flags
        self._config = config
        self._tokens = tokens
        self._git = GitHandler(project, config)
        self._qainit = QainitHandler(project, config, tokens)
        self._youtrack = YoutrackHandler(config, tokens)

    def run(self):
        if self._action == "list":
            self._list()
        elif self._action == "create":
            self._create()
        elif self._action == "update":
            self._update()
        elif self._action == "delete":
            self._delete()
        elif self._action == "freeze":
            self._freeze()
        elif self._action == "unfreeze":
            self._unfreeze()
        elif self._action == "check":
            self._check()
        elif self._action == "describe":
            self._describe()
        elif self._action == "update-quota":
            self._update_quota()

    def _check(self):
        logger.info(
            "Checking configuration. If there is an issue, check ~/.suite_py/config.yml file and execute: suite-py login"
        )

        self._qainit.user_info()

    def _create_instance_table(self):
        instance_table = Table()
        instance_table.add_column("Name", style="purple")
        instance_table.add_column("Hash", style="green")
        instance_table.add_column("Card", style="white")
        instance_table.add_column("Created by", style="white")
        instance_table.add_column("Updated by", style="white")
        instance_table.add_column("Deleted by", style="white")
        instance_table.add_column("Status", style="white")

        return instance_table

    def _insert_instance_record(self, table, qa):
        table.add_row(
            qa["name"],
            qa["hash"],
            qa["card"],
            qa.get("created", {}).get("github_username", "/")
            if qa["created"] is not None
            else "/",
            qa.get("updated", {}).get("github_username", "/")
            if qa["updated"] is not None
            else "/",
            qa.get("deleted", {}).get("github_username", "/")
            if qa["deleted"] is not None
            else "/",
            qa["status"],
        )

    def _list(self):
        # init empty table with column (useful for reset)
        empty_table = self._create_instance_table()
        table = copy.deepcopy(empty_table)
        console = Console()

        # execute query with pagination and filtering
        page_number = 1
        while True:
            r = self._qainit.list(
                self._flags,
                page=page_number,
                page_size=self._config.qainit["table_size"],
            )
            response = r.json()
            qa_list = response["list"]
            for qa in qa_list:
                self._insert_instance_record(table, qa)

            console.print(table)

            # break conditions
            if response["page_number"] >= response["total_pages"]:
                break
            if not prompt_utils.ask_confirm(
                f"I found {response['total_entries']} results. Do you want to load a few more?",
                False,
            ):
                break
            page_number += 1
            # table reset
            table = copy.deepcopy(empty_table)

    def _describe(self):
        qa_hash = self._flags["hash"]
        jsonify = self._flags["json"]

        r = self._qainit.describe(qa_hash)
        if jsonify:
            print(json.dumps(r, sort_keys=True, indent=2))
        else:
            # RESOURCES TABLE
            table = Table()
            table.add_column("Microservice", style="purple", no_wrap=True)
            table.add_column("Drone build")
            table.add_column("Branch", style="white")
            table.add_column("Status", style="white")

            # INSTANCE TABLE
            instance_table = self._create_instance_table()

            self._insert_instance_record(instance_table, r["list"])

            # DNS TABLE
            dns_table = Table()
            dns_table.add_column("Name", style="purple", no_wrap=True)
            dns_table.add_column("Record", style="green")

            console = Console()

            try:
                resources_list = sorted(r["list"]["resources"], key=lambda k: k["name"])
                for resource in resources_list:
                    if (
                        resource["type"] == "microservice"
                        or "service" in resource["name"]
                    ) and resource["dns"]:
                        for key, value in resource["dns"].items():
                            dns_table.add_row(key, value)
                    if resource["type"] == "microservice":
                        drone_url = (
                            "[blue][u]"
                            + "https://drone-1.prima.it/primait/"
                            + resource["name"]
                            + "/"
                            + resource["promoted_build"]
                            + "[/u][/blue]"
                        )
                        table.add_row(
                            resource["name"],
                            drone_url,
                            resource["ref"]
                            if resource["ref"] == "master"
                            else f"[green]{resource['ref']}[/green]",
                            resource["status"],
                        )

                console.print(instance_table)
                console.print(dns_table)
                console.print(table)
            except TypeError:
                logger.error("Wrong hash")

    def _delete(self):
        self._qainit.delete(self._flags["hash"])

    def _freeze(self):
        self._qainit.freeze(self._flags["hash"])

    def _unfreeze(self):
        self._qainit.unfreeze(self._flags["hash"])

    def _create(self):
        user = self._qainit.user_info()

        if not user["quota"]["remaining"] > 0:
            logger.error("There's no remaining quota for you.")
            sys.exit("-1")

        if "staging" in self._qainit.url:
            qa_default_name = (
                f"staging_{git.get_username()}_{self._git.current_branch_name()}"
            )
        else:
            qa_default_name = f"{git.get_username()}_{self._git.current_branch_name()}"

        qa_name = prompt_utils.ask_questions_input(
            "Choose the QA name: ", default_text=qa_default_name
        )

        card_match = re.match(r"[^\/]*_(?P<name>[A-Z]+-\d+)\/", qa_name)
        default_card_name = (
            card_match["name"] if card_match else self._config.user["default_slug"]
        )

        qa_card = prompt_utils.ask_questions_input(
            "Youtrack issue ID: ", default_text=default_card_name
        )

        if qa_card != "":
            try:
                self._youtrack.get_issue(qa_card)
            except Exception:
                logger.error("invalid Youtrack issue ID")
                sys.exit(-1)

        self._qainit.create(qa_name, qa_card, self._flags["services"])

    def _update(self):
        self._qainit.update(self._flags["hash"], self._flags["services"])

    def _update_quota(self):
        username = prompt_utils.ask_questions_input("Insert GitHub username: ")
        quota = prompt_utils.ask_questions_input("Insert new quota value: ")

        self._qainit.update_user_quota(username, quota)
