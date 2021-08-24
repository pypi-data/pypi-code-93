from pyfiglet import figlet_format
from typing import List
from colorama import Fore, Style
import calendar
from random import shuffle
import textwrap as tr
import sys
import logging
from sylo.models import Durations, Config
from sylo.utils import get_today, get_weekday, strike


logger = logging.getLogger(__name__)


config = Config()


class Display:
    def __init__(
        self,
        durations: Durations,
        theme_color: str = config.theme_color,
        pom_name: str = config.pom_name,
    ):
        self.theme_color = theme_color
        self.simple_colors = config.fewer_colors
        self.theme = self.color_map(theme_color)
        self.pom_name = pom_name
        self.durations = durations

    def col(self, string: str, color: str = "grey"):
        if color:
            return f"{self.color_map(color)}{string}{Style.RESET_ALL}"
        else:
            return f"{self.theme}{string}{Style.RESET_ALL}"

    def print_poms(self, pom: int):
        return f"{self.col('(' + str(pom) + ' ' + self.add_plurality(self.pom_name) + ')', 'lmagenta')}"

    def print_age(self, age: int):
        if age > 7:
            return f"{self.col('(' + str(age) + ' days old)', 'red')}"
        elif 4 <= age <= 6:
            return f"{self.col('(' + str(age) + ' days old)', 'red')}"
        else:
            return ""

    def print_timer(self, mode: str, timer_val: int, tasks: List = None):
        if mode == "work":
            self.print_header_small()
            print(
                self.col(
                    f"Tasks for {calendar.day_name[get_weekday()]} {get_today()}",
                    "lblue",
                )
            )
            print(self.col("-----------------------------------------", "lblue"))
            self.print_tasks(tasks)
            print(
                f"\n{self.col('Press')} {self.col('Ctrl-C', 'yellow')} "
                f"{self.col('to stop timer early.')}"
                "\n"
                f"\n{self.col('WORK', 'red')} "
                f"{self.col('for')} {self.col(str(timer_val), 'yellow')} {self.col('minutes')}"
            )
        else:
            self.print_header_small()
            print(
                self.col(f"{calendar.day_name[get_weekday()]} {get_today()}", "lblue")
            )
            print(self.col("-----------------------------------------", "lblue"))
            print(
                f"\n{self.col('Press')} {self.col('Ctrl-C', 'yellow')} "
                f"{self.col('to stop timer early.')}"
                f"\n{self.col('REST', 'green')} "
                f"for {self.col(str(timer_val), 'yellow')} minutes"
            )

    def print_summary_and_quit(self):
        sys.stdout.write("\033[K")
        print(
            f"{self.col('Press')} "
            f"{self.col('ENTER', 'yellow')}"
            f"{self.col('to stop timer.')}",
        )

    def print_insights(self):
        print(
            f"\nTotal {self.col(self.add_plurality(self.pom_name), 'lmagenta')} today:{self.fix_indent()}      "
            f"{self.col(str(int(self.durations.poms)), 'yellow')} "
            f"{self.add_plurality(self.pom_name)}"
            f"\nTotal {self.col('Work', 'red')} today:           "
            f"{self.col(str(int(self.durations.total_work_mins)), 'yellow')} minutes"
            f"\nTotal {self.col('Rest', 'green')} today:           "
            f"{self.col(str(int(self.durations.total_rest_mins)), 'yellow')} minutes\n"
            f"\n{self.col('Press')} "
            f"{self.col('ENTER', 'yellow')} "
            f"{self.col('to return to main menu.')}"
        )

    def print_bar_header(self):
        print(f"{self.col('Daily work/rest minutes, for the past fortnight', 'lblue')}")

    def print_busy_days_header(self):
        print("\n")
        print(f"{self.col('Ways of working', 'lblue')}")

    def print_heat_header(self):
        print(f"{self.col(f'{self.add_plurality(self.pom_name)} heatmap', 'lblue')}")

    def print_today_totals_header(self):
        print("\n")
        print(f"{self.col(f'Totals for today', 'lblue')}")

    def print_busy_days(self, created_at_day: str, completed_at_day: str):
        print(
            "\n"
            + tr.fill(
                f"Your favourite day for opening new tasks is "
                f"{self.col(created_at_day, 'lred')},"
                f" while {self.col(self.add_plurality(completed_at_day),'lgreen')} "
                f"are your busiest days for closing them.\n",
                75,
            )
        )

    def cursor(self):
        return self.col(">> ", "yellow")

    def print_options(self):
        print(
            f"\n"
            f"{self.col('Additional commands;')}"
            f"\n{self.col('S', 'yellow')}{self.col('       --    Swap upcoming timer')}"
            f"\n{self.col('T', 'yellow')}{self.col('       --    Show task view')}"
            f"\n{self.col('I', 'yellow')}{self.col('       --    Show insights view')}"
            f"\n{self.col('Q', 'yellow')}{self.col('       --    Quit')}"
        )

    def print_offer_options(self):
        print(
            f"\n{self.col('Press')} {self.col('H', 'yellow')} {self.col('for Help.')}"
        )

    def print_add_task_or_quit(self):
        print("\n")
        print(
            f"{self.col('ENTER', 'yellow')} "
            f"{self.col('to go back')} "
            f"\n{self.col('N', 'yellow')} "
            f"{self.col('to add a new task')}"
            f"\n{self.col('C', 'yellow')} "
            f"{self.col('to complete a task')}"
            f"\n{self.col('M', 'yellow')} "
            f"{self.col('to move a task to today')}"
            f"\n{self.col('D', 'yellow')} "
            f"{self.col('to delete a task')}"
            f"\n{self.col('L', 'yellow')} "
            f"{self.col('to lump all incomplete tasks to today')}\n"
        )

    def print_new_task(self):
        print(f"{self.col('Input a new task')}")

    def print_edit_task(self):
        print("\n")
        print(f"{self.col('Pick a task to complete/put back')}")

    def print_remove_task(self):
        print("\n")
        print(f"{self.col('Pick a task to DELETE')}")

    def fix_indent(self):
        num = len("pomodoro") - len(self.pom_name)
        fix_str = ""
        for no in range(0, num):
            fix_str += " "
        return fix_str

    def print_splash(self, mode: str, tasks: List):
        print(
            self.col(
                f"TODAY: {calendar.day_name[get_weekday()].upper()} {get_today()} "
                f"------------------",
                "lblue",
            )
        )
        print("\n")
        self.print_tasks(tasks)

    def print_splash_prompt(self, mode: str):
        print(
            f"{self.col('Press')} "
            f"{self.col('ENTER', 'yellow')} "
            f"{self.col('to start the')} "
            f"{self.col(mode.upper(), self._set_mode_color(mode, self.durations))} "
            f"{self.col('timer.')}"
        )

    def print_splash_variants(
        self,
        mode: str,
        is_options: bool = None,
        is_tasks: bool = None,
        tasks: List = None,
    ):
        logger.info(f"Splash. is_options: {is_options} is_tasks: {is_tasks}")
        self.print_header_small()
        self.print_splash(mode, tasks)
        if is_options is True and is_tasks is False:
            self.print_options()
            self.print_splash_prompt(mode)
        elif is_options is False and is_tasks is True:
            self.print_tasks(tasks)
            self.print_offer_options()
            self.print_splash_prompt(mode)
        elif is_options is True and is_tasks is True:
            self.print_tasks(tasks)
            self.print_options()
            self.print_splash_prompt(mode)
        else:
            self.print_offer_options()
            self.print_splash_prompt(mode)

    def print_tasks(self, tasks: List = None):
        logger.info(tasks)
        complete_tasks = "\n".join(
            "".join(
                map(
                    str,
                    f"{self.col('->', 'lblue')} "
                    f"{self.trim_string(strike(t[2]),65)}",
                )
            )
            for t in tasks
            if t[4] == True
        )
        incomplete_tasks = "\n".join(
            "".join(
                map(
                    str,
                    f"{self.col('->', 'lblue')} "
                    f"{self.print_poms(t[3])}{self.print_age(t[5])}: "
                    f"{tr.fill(self.col(t[2],'white'), 45)}",
                )
            )
            for t in tasks
            if t[4] == False
        )
        if complete_tasks:
            print(complete_tasks)
        if incomplete_tasks:
            print(incomplete_tasks)

    def print_tasks_with_id(self, tasks: List = None):
        complete_tasks = "\n".join(
            "".join(
                map(
                    str,
                    f"{self.col('->', 'lblue')} {self.col(t[0], 'yellow')}  "
                    f"{self.print_poms(t[3])}: "
                    f"{self.trim_string(strike(t[2]),65)}",
                )
            )
            for t in tasks
            if t[4] == True
        )
        incomplete_tasks = "\n".join(
            "".join(
                map(
                    str,
                    f"{self.col('->', 'lblue')} {self.col(t[0], 'yellow')}  "
                    f"{self.print_poms(t[3])}{self.print_age(t[5])}: "
                    f"{tr.fill(t[2], 45)}",
                )
            )
            for t in tasks
            if t[4] == False
        )
        if complete_tasks:
            print(complete_tasks)
        if incomplete_tasks:
            print(incomplete_tasks)

    def print_header_small(self):
        if self.theme_color != "rainbow":
            print(
                self.col(
                    self.ascii_header(string="SYLO", font="alligator", width=60),
                    self.theme_color,
                )
            )
        else:
            if int(self.simple_colors) == 1:
                colors = ["lred", "yellow", "lgreen", "lblue", "lmagenta"]
            else:
                colors = [
                    "lred",
                    "lyellow",
                    "yellow",
                    "lgreen",
                    "lblue",
                    "lmagenta",
                    "magenta",
                ]
            shuffle(colors)

            # This nasty work-around is because using ascii_header prints each letter to a new row.
            # Forced to add E501 and W291 to flake8 config so remove them if a better solution is found for this.

            print(
                f"""      {self.col('::::::::', colors[0])}  {self.col(':::   :::', colors[1])} {self.col(':::', colors[2])}        {self.col('::::::::', colors[3])} 
    {self.col(':+:    :+:', colors[0])} {self.col(':+:   :+:', colors[1])} {self.col(':+:', colors[2])}       {self.col(':+:    :+:', colors[3])} 
   {self.col('+:+', colors[0])}         {self.col('+:+ +:+', colors[1])}  {self.col('+:+', colors[2])}       {self.col('+:+    +:+', colors[3])}  
  {self.col('+#++:++#++', colors[0])}   {self.col('+#++:', colors[1])}   {self.col('+#+', colors[2])}       {self.col('+#+    +:+', colors[3])}   
        {self.col('+#+', colors[0])}    {self.col('+#+', colors[1])}    {self.col('+#+', colors[2])}       {self.col('+#+    +#+', colors[3])}    
{self.col('#+#    #+#', colors[0])}    {self.col('#+#', colors[1])}    {self.col('#+#', colors[2])}       {self.col('#+#    #+#', colors[3])}     
{self.col('########', colors[0])}     {self.col('###', colors[1])}    {self.col('##########', colors[2])} {self.col('########', colors[3])}                      
"""
            )

    @staticmethod
    def color_map(color: str):
        colors = {
            "red": Fore.RED,
            "lred": Fore.LIGHTRED_EX,
            "blue": Fore.BLUE,
            "lblue": Fore.LIGHTBLUE_EX,
            "green": Fore.GREEN,
            "lgreen": Fore.LIGHTGREEN_EX,
            "yellow": Fore.YELLOW,
            "lyellow": Fore.LIGHTYELLOW_EX,
            "magenta": Fore.MAGENTA,
            "white": Fore.WHITE,
            "black": Fore.BLACK,
            "cyan": Fore.CYAN,
            "lcyan": Fore.LIGHTCYAN_EX,
            "grey": Fore.LIGHTBLACK_EX,
            "lmagenta": Fore.LIGHTMAGENTA_EX,
            "rainbow": Fore.WHITE,  # Set temporarily to white, set in print_header_small
        }
        return colors[color]

    @staticmethod
    def ascii_header(string: str, font: str, width: int):
        return figlet_format(string, font=font, width=width)

    @staticmethod
    def _set_mode_color(mode: str, durations: Durations):
        if mode == "rest":
            return durations.rest.bar_color
        else:
            return durations.work.bar_color

    @staticmethod
    def add_plurality(string: str):
        if string[-1] == "s":
            return string
        else:
            return string + "s"

    @staticmethod
    def trim_string(string: str, max_len: int) -> str:
        return string[:max_len] + ".." if len(string) > max_len else string
