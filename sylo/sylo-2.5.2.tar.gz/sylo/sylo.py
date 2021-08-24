#!/usr/bin/env python
import sys
import logging
import time
import simpleaudio
import csv
from beepy import beep
from tqdm import tqdm
from colorama import Fore
from typing import List
from time import sleep
from sylo.models import (
    Durations,
    Database,
    Config,
    ConfigFile,
)
from sylo.definitions import (
    INPUT_OPTIONS,
    COUNTDOWN_INCREMENTS,
    METRICS_BAR,
    METRICS_HEAT,
    HOME_DIR_CREATE,
    FORTNIGHT_AGO,
    ONE_YEAR_AGO,
    SYLO_HOME,
    INSIGHTS_FILE_SESSIONS,
    INSIGHTS_FILE_POMS,
)
from sylo.utils import (
    clear_screen,
    mins_to_secs,
    flip_mode,
    get_input,
    run_subprocess,
    check_for_dir,
    get_today,
    generate_date_range,
    valid_input,
)
from sylo.display import Display


logger = logging.getLogger(__name__)
is_speed_mode = False
timer_mode = "work"
database = Database()
initial_boot_flag = False


class Timer:
    def __init__(
        self,
        mode: str,
        durations: Durations,
        increments: int,
        config: Config,
        display: Display,
    ):
        self.durations = durations
        self.config = config
        self.mode: str = mode
        self.increments = increments
        self.mins_passed = 0
        self.tasks = database.select(
            f"SELECT"
            f'"id",'
            f'"assigned_date",'
            f'"description",'
            f'"effort",'
            f'"complete",'
            f"CAST(ROUND(JULIANDAY('now') - JULIANDAY(\"created_at\"),0) as integer) as age "
            f"FROM tasks WHERE \"assigned_date\" = '{get_today()}' "
            f";"
        )
        self.display = display

        if self.mode == "work":
            self.mins = self.durations.work.mins
            self.secs = self.durations.work.secs
            self.bar_color = self.durations.work.bar_color
        else:
            self.mins = self.durations.rest.mins
            self.secs = self.durations.rest.secs
            self.bar_color = self.durations.rest.bar_color

    def _start_timer(self):
        timer_iterator = tqdm(
            total=self.secs,
            position=0,
            leave=False,
            desc=self.display.print_timer(self.mode, self.mins, self.tasks),
            unit=" seconds",
            bar_format="{l_bar}%s{bar}%s{r_bar}"
            % (
                self.display.color_map(self.bar_color),
                Fore.RESET,
            ),
            smoothing=True,
            ncols=70,
        )
        try:
            while self.secs > 0:
                time.sleep(1)
                self.secs -= self.increments
                timer_iterator.update(self.increments)
                if self.secs % 60 == 0:
                    self.mins_passed += 1
                    logger.debug(f"{self.mode} Timer loop: secs remaining: {self.secs}")

        except KeyboardInterrupt:
            print("\nQuitting early..")
            logger.info(f"Ctrl-C quit with {self.secs} remaining")
            timer_iterator.close()
            return False, self.mins_passed
            pass
        logger.info(f"{self.mode} timer loop finished")
        timer_iterator.close()
        return True, self.mins_passed

    def start_countdown(self):
        logger.info(f"{self.mode} timer started")
        complete, mins_passed = self._start_timer()
        return complete, mins_passed


class Sound:
    def __init__(self, audio_path: str = "dummy"):
        self.sound_file = audio_path
        self.beep_needed = False
        self.initialised_file = None

    def initialise(self):
        logger.info(f"Initialising audio: {self.sound_file}")
        try:
            self.initialised_file = simpleaudio.WaveObject.from_wave_file(
                self.sound_file
            )
            logger.info(f"Custom audio successfully initialised: {self.sound_file}")
        except FileNotFoundError:
            logger.info(f"Custom audio not found: {self.sound_file}")
            self.beep_needed = True
        except AttributeError:
            logger.info(f"Custom audio not found: {self.sound_file}")
            self.beep_needed = True

    def play_sound(self):
        if self.beep_needed is False:
            play_obj = self.initialised_file.play()
            logger.info("Played audio file")
            play_obj.wait_done()
            logger.info("Waiting audio file")

        else:
            logger.info("Playing beep")
            beep("ready")


class Insights:
    def __init__(self, display: Display):
        self.data_file = INSIGHTS_FILE_SESSIONS
        self.poms_file = INSIGHTS_FILE_POMS
        self.heatmap_start_date = ONE_YEAR_AGO
        self.bar_start_date = FORTNIGHT_AGO
        self.display = display

    def save_files(self):
        csv_writer = csv.writer(open(self.data_file, "w"))
        data = database.select(
            f""
            f"SELECT * "
            f"FROM sessions "
            f"WHERE session_date >= {self.bar_start_date}"
        )
        logger.info(data)
        for row in data:
            csv_writer.writerow(row)

        csv_writer = csv.writer(open(self.poms_file, "w"))
        data = database.select(
            f""
            f"SELECT * "
            f"FROM poms "
            f"WHERE poms_date >= {self.heatmap_start_date}"
        )
        logger.info(data)
        for row in data:
            csv_writer.writerow(row)

    def print_bar(self):
        global initial_boot_flag
        self.display.print_bar_header()
        if initial_boot_flag is False:
            logger.info(f"Running ${self._bar_chart()}")
            run_subprocess(self._bar_chart())
        else:
            print("No data available, complete some segments and check later.")

    def print_heat(self):
        logger.info(f"Running ${self._heat_map()}")
        self.display.print_heat_header()
        run_subprocess(self._heat_map())

    def _bar_chart(self):
        return METRICS_BAR % (self.data_file, self.bar_start_date)

    def _heat_map(self):
        return METRICS_HEAT % (self.heatmap_start_date, self.poms_file)

    def print_busy_days(self):
        query = (
            ""
            "SELECT "
            "case cast (strftime('%w', {}) as integer)"
            "when 0 then 'Sunday'"
            "when 1 then 'Monday'"
            "when 2 then 'Tuesday'"
            "when 3 then 'Wednesday'"
            "when 4 then 'Thursday'"
            "when 5 then 'Friday'"
            "when 6 then 'Saturday'"
            "else 'No day' end as dayofweek,"
            "count(*) "
            "FROM tasks "
            "GROUP BY 1 "
            "ORDER BY 2 desc "
            "LIMIT 1"
        )
        busiest_day_created = database.select(query.format("created_at"))
        busiest_day_completed = database.select(query.format("completed_at"))
        self.display.print_busy_days_header()
        try:
            self.display.print_busy_days(
                busiest_day_created[0][0], busiest_day_completed[0][0]
            )
        except IndexError:
            print("\nTry using SYLO for a while for your working patterns to generate.")


class Task:
    def __init__(self):
        self.description = None
        self.date = get_today()
        self.complete = 0
        self.effort = 1

    def write_task_to_db(self):
        database.execute(
            f"INSERT INTO tasks ("
            f'"created_at", '
            f'"assigned_date", '
            f'"description", '
            f'"effort", '
            f'"complete", '
            f'"number_of_times_moved"'
            f") VALUES("
            f'"{self.date}",'
            f'"{self.date}",'
            f'"{self.description}",'
            f'"{self.effort}",'
            f'"{self.complete}",'
            f"0);"
        )


class Sylo:
    def __init__(
        self,
        durations: Durations,
        sound_obj: any,
        mode: str,
        show_options: bool = False,
        show_tasks: bool = False,
        tasks: List = None,
        tasks_date: str = None,
        speed_mode: bool = is_speed_mode,
        config: Config = None,
        display: Display = None,
    ):
        self.durations = durations
        self.sound_obj = sound_obj
        self.mode = mode
        self.show_options = show_options
        self.show_tasks = show_tasks
        self.tasks = tasks
        self.tasks_date = tasks_date
        self.speed_mode = speed_mode
        self.increments = 1
        self.config = config
        self.display = display

    def on_boot(self):
        clear_screen()
        if self.speed_mode is True:
            self.increments = 30
        else:
            self.increments = COUNTDOWN_INCREMENTS
        logger.debug(f"Running in {self.increments} second increments")

    def splash(self):
        self.display.print_splash_variants(
            mode=self.mode,
            is_options=self.show_options,
            is_tasks=self.show_tasks,
            tasks=self.tasks,
        )

    def show_task(self, dates, with_id: bool = False):
        for date in dates:
            print(
                self.display.col(f"--------------------------------- {date}", "lblue")
            )
            self.tasks = database.select(
                f"SELECT"
                f'"id",'
                f'"assigned_date",'
                f'"description",'
                f'"effort",'
                f'"complete",'
                f"CAST(ROUND(JULIANDAY('now') - JULIANDAY(\"created_at\"),0) as integer) as age "
                f"FROM tasks WHERE \"assigned_date\" = '{date}'"
                f";"
            )
            if with_id is False:
                self.display.print_tasks(self.tasks)
            else:
                self.display.print_tasks_with_id(self.tasks)
            logger.info(f"Tasks: {self.tasks}")

    def task_menu_new(self, dates: List):
        task = Task()
        self.display.print_new_task()
        task.description = input(self.display.col("Description >> ", "yellow"))
        task.effort = input(
            self.display.col(
                f"Effort (in"
                f" {self.display.add_plurality(self.display.pom_name)}) >> ",
                "yellow",
            )
        )
        while task.effort.isnumeric() is False:
            print(self.display.col("MUST BE NUMERIC", "red"))
            sleep(1)
            self.task_menu(dates)
        task.write_task_to_db()
        self.task_menu(dates)

    def task_menu_close(self, dates: List, task_ids: List[tuple]):
        clear_screen()
        self.display.print_header_small()
        self.show_task(dates, True)
        self.display.print_edit_task()
        comp_input = input(self.display.col("Task id >> ", "yellow"))
        while valid_input(comp_input, task_ids) is False:
            print(self.display.col("NOT A VALID ID", "red"))
            sleep(1)
            self.task_menu(dates)
        database.execute(
            f"UPDATE tasks SET "
            f'"complete" = '
            f'CASE WHEN "complete" = False THEN True ELSE False END, '
            f'"completed_at" = "{get_today()}"'
            f' WHERE "id" = {comp_input};'
        )
        self.task_menu(dates)

    def task_menu_move(self, dates: List, task_ids: List[tuple]):
        clear_screen()
        self.display.print_header_small()
        self.show_task(dates, True)
        self.display.print_edit_task()
        comp_input = input(self.display.col("Task id >> ", "yellow"))
        while valid_input(comp_input, task_ids) is False:
            print(self.display.col("NOT A VALID ID", "red"))
            sleep(1)
            self.task_menu(dates)
        database.execute(
            f"UPDATE tasks SET "
            f"\"assigned_date\" = '{get_today()}',"
            f'"number_of_times_moved" = "number_of_times_moved" + 1'
            f' WHERE "id" = {comp_input};'
        )
        self.task_menu(dates)

    def task_menu_move_all(self, dates: List):
        clear_screen()
        self.display.print_header_small()
        self.show_task(dates, True)
        self.display.print_edit_task()
        print(self.display.col("MOVED ANY OPEN TASKS TO TODAY", "red"))
        sleep(1)
        database.execute(
            f"UPDATE tasks SET "
            f"\"assigned_date\" = '{get_today()}',"
            f'"number_of_times_moved" = "number_of_times_moved" + 1'
            f' WHERE "complete" = False;'
        )
        self.task_menu(dates)

    def task_menu_delete(self, dates: List, task_ids: List[tuple]):
        clear_screen()
        self.display.print_header_small()
        self.show_task(dates, True)
        self.display.print_remove_task()
        comp_input = input(self.display.col("Task id >> ", "yellow"))
        while valid_input(comp_input, task_ids) is False:
            print(self.display.col("NOT A VALID ID", "red"))
            sleep(1)
            self.task_menu(dates)
        database.execute(f"DELETE FROM tasks" f' WHERE "id" = {comp_input};')
        self.task_menu(dates)

    def task_menu(self, dates: List):
        clear_screen()
        all_tasks = self.tasks = database.select(
            f"SELECT"
            f'"id"'
            f'FROM tasks WHERE "assigned_date" '
            f">= (SELECT DATETIME({(get_today())}, '-7 day'))"
            f";"
        )
        all_task_ids = [i[0] for i in all_tasks]
        self.display.print_header_small()
        print(self.display.col("ADD/REMOVE/MOVE TASKS ----------------------", "lblue"))
        print("\n")
        self.show_task(dates)
        self.display.print_add_task_or_quit()
        usr_input = input(self.display.cursor())
        while valid_input(usr_input, INPUT_OPTIONS["task_menu"]) is False:
            self.task_menu(dates)
        if usr_input == "":
            self.home_loop()
        while usr_input.lower() == "n":
            self.task_menu_new(dates)
        while usr_input.lower() == "c":
            self.task_menu_close(dates, all_task_ids)
        while usr_input.lower() == "m":
            self.task_menu_move(dates, all_task_ids)
        while usr_input.lower() == "l":
            self.task_menu_move_all(dates)
        while usr_input.lower() == "d":
            self.task_menu_delete(dates, all_task_ids)

    def switch_modes(self):
        logger.info("Switch requested")
        self.mode = flip_mode(self.mode)
        self.home_loop()

    def show_help_menu(self):
        logger.info("Help requested")
        self.show_options ^= True
        self.home_loop()

    def show_insights_menu(self):
        clear_screen()
        metrics = Insights(self.display)
        metrics.save_files()
        self.display.print_header_small()
        print(self.display.col("INSIGHTS -----------------------------------", "lblue"))

        print("\n")
        metrics.print_bar()
        metrics.print_heat()
        metrics.print_busy_days()
        self.display.print_today_totals_header()
        self.display.print_insights()
        input(self.display.cursor())
        self.home_loop()

    def timer_loop(self, timer: Timer):
        clear_screen()
        global initial_boot_flag
        logger.info("User pressed ENTER")
        if self.mode == "rest":
            complete, secs_passed = timer.start_countdown()
            if complete is True:
                self.sound_obj.play_sound()
                self.durations.total_rest_mins += secs_passed
                self.mode = flip_mode(self.mode)
            else:
                self.durations.total_rest_mins += secs_passed
            database.execute(
                'INSERT INTO sessions ("session_date", "time_worked", "time_rested")'
                f"VALUES ('{get_today()}',"
                f"'{self.durations.total_work_mins}', "
                f"'{self.durations.total_rest_mins}')"
                'ON CONFLICT ("session_date") DO UPDATE SET '
                '("time_worked", "time_rested") = (excluded."time_worked", excluded."time_rested")'
            )
            clear_screen()
        else:
            complete, secs_passed = timer.start_countdown()
            if complete is True:
                self.sound_obj.play_sound()
                self.durations.total_work_mins += self.durations.work.mins
                self.durations.poms += 1
                self.mode = flip_mode(self.mode)
            else:
                self.durations.total_work_mins += secs_passed
            database.execute(
                'INSERT INTO sessions ("session_date", "time_worked", "time_rested")'
                f"VALUES ('{get_today()}',"
                f"'{self.durations.total_work_mins}', "
                f"'{self.durations.total_rest_mins}')"
                'ON CONFLICT ("session_date") DO UPDATE SET '
                '("time_worked", "time_rested") = (excluded."time_worked", excluded."time_rested")'
            )
            database.execute(
                'INSERT INTO poms ("poms_date", "poms")'
                f"VALUES ('{get_today()}',"
                f"'{self.durations.poms}')"
                'ON CONFLICT ("poms_date") DO UPDATE SET '
                '"poms" = excluded."poms"'
            )
            clear_screen()
        logger.info("Durations model set")
        logger.info(f"Work time: {self.durations.total_work_mins}")
        logger.info(f"Work time: {self.durations.total_rest_mins}")
        initial_boot_flag = False
        self.home_loop()

    @staticmethod
    def quit_app():
        logger.info("Quit requested")
        clear_screen()
        sys.exit()

    def home_loop(self):
        self.on_boot()
        timer = Timer(
            mode=self.mode,
            durations=self.durations,
            config=self.config,
            increments=self.increments,
            display=self.display,
        )
        self.splash()
        response = get_input(self.display.cursor())
        logger.info(f"User response: {response}")
        while valid_input(response, INPUT_OPTIONS["home"]) is False:
            self.show_options = True
            logger.info(f"Rejected user response of {response}")
            self.home_loop()
        while response.lower() == "q":
            self.quit_app()
        while response.lower() == "i":
            self.show_insights_menu()
        while response.lower() == "s":
            self.switch_modes()
        while response.lower() == "h":
            self.show_help_menu()
        while response.lower() == "t":
            self.task_menu(generate_date_range(get_today(), 7))
        while response == "":
            self.timer_loop(timer)


def virgin_boostrap():
    global initial_boot_flag
    initial_boot_flag = True
    logger.info("First boot")
    run_subprocess(HOME_DIR_CREATE)


def config_allocation(args, config, durations: Durations, display: Display):
    config_file = ConfigFile()
    config_file.set_config(config, durations)
    logger.info(config.theme_color)
    if args.theme:
        config.theme_color = args.theme
    logger.info(config.theme_color)
    display.theme_color = config.theme_color
    display.theme = display.color_map(config.theme_color)
    display.pom_name = config.pom_name
    display.simple_colors = config.fewer_colors
    logger.info(display.theme)
    if args.audio_file:
        config.audio_file = args.audio_file
    if args.work_time:
        durations.work.mins = args.work_time
        durations.work.secs = mins_to_secs(args.work_time)
    if args.rest_time:
        durations.rest.mins = args.rest_time
        durations.rest.secs = mins_to_secs(args.rest_time)


def run(args, config):
    global is_speed_mode, timer_mode

    durations_data = Durations()
    display = Display(durations=durations_data)
    config_allocation(args, config, durations_data, display)
    sound = Sound(config.audio_file)
    sound.initialise()

    if check_for_dir(SYLO_HOME) is False:
        virgin_boostrap()
    clear_screen()
    database.bootstrap_on_first_boot()
    database.initial_data_load(durations_data)

    logger.info("Durations model set")
    logger.info(f"Work time:    {durations_data.work.mins}")
    logger.info(f"Work time:    {durations_data.work.secs}")
    logger.info(f"Work time:    {durations_data.rest.mins}")
    logger.info(f"Work time:    {durations_data.rest.secs}")
    logger.info(f"Sound file:   {sound.sound_file}")

    if args.speed_mode is True:
        is_speed_mode = True
    logger.info(f"Speed mode set to {is_speed_mode}")

    sylo = Sylo(
        durations=durations_data,
        sound_obj=sound,
        mode=timer_mode,
        speed_mode=is_speed_mode,
        tasks=database.select(
            f"SELECT"
            f'"id",'
            f'"assigned_date",'
            f'"description",'
            f'"effort",'
            f'"complete",'
            f"CAST(ROUND(JULIANDAY('now') - JULIANDAY(\"created_at\"),0) as integer) as age "
            f"FROM tasks WHERE \"assigned_date\" = '{get_today()}' "
            f";"
        ),
        config=config,
        display=display,
    )
    sylo.home_loop()
