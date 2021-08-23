import logging
import uuid
from pathlib import Path
from IPython.display import display
import ipywidgets as widgets
import clease_gui as gui
import json

__all__ = ['MCRunDashboard']

logger = logging.getLogger(__name__)
gui.register_logger(logger)


class MCRunDashboard(gui.BaseDashboard):
    def initialize(self):
        s = "Export MC run data to JSON file for further analysis, "
        s += "or load MC run data from file."
        html = f"<h1 style='font-size:15px'> {s} </h1>"
        self.description = widgets.HTML(html)
        self.filename_widget = widgets.Text(description='Filename:',
                                            value='clease_mc.json',
                                            **self.DEFAULT_STYLE_KWARGS)

        self.mode_widget = widgets.Dropdown(
            description='MC mode:',
            options=[
                ('Canonical', 'canonical'),
            ],
            **self.DEFAULT_STYLE_KWARGS,
        )
        self.save_button = widgets.Button(description='Export data')
        self.save_button.on_click(self._on_save_click)

        self.append_widget = widgets.Checkbox(
            description='Append data in save/load?',
            value=True,
            **self.DEFAULT_STYLE_KWARGS)

        self.load_data_button = widgets.Button(description='Load Data')
        self.load_data_button.on_click(self._on_load_click)

    def display(self):
        hbox = widgets.HBox(children=[self.save_button, self.load_data_button])
        display(
            self.description,
            self.mode_widget,
            self.filename_widget,
            self.append_widget,
            hbox,
        )

    def get_filename(self):
        cwd = self.get_cwd()
        return cwd / self.filename_widget.value

    @property
    def mc_mode(self):
        return self.mode_widget.value

    def get_data(self):
        """Retrieve the MC run data from the app data"""
        mode = self.mc_mode
        if mode == 'canonical':
            key = self.KEYS.CANONICAL_MC_DATA
        else:
            raise ValueError(f'Unknown mode: {mode}')

        try:
            return list(self.app_data[key])
        except KeyError:
            raise KeyError('No data found. Did you run the MC yet?')

    def set_data(self, data, append=False) -> None:
        """Set the data of the currently active MC mode. If append=False, it will
        override any existing runs, and otherwise it will only append runs which
        aren't already in the list, i.e. the UUID does not exist in the list."""
        # We shouldn't have UUID collisions, but just in case we made a mistake.
        assert len({get_uuid_from_run(run)
                    for run in data
                    }) == len(data), "Not all runs have unique ID's"
        mode = self.mc_mode
        if mode == 'canonical':
            key = self.KEYS.CANONICAL_MC_DATA
        else:
            raise ValueError(f'Unknown mode: {mode}')

        if append:
            all_data = self.app_data.get(key, [])
            # Iterate through incoming new data, only append the runs which are new
            uids = {get_uuid_from_run(run) for run in all_data}
            for run in data:
                new_id = get_uuid_from_run(run)
                if new_id in uids:
                    # We already have this run
                    continue
                all_data.append(run)
        else:
            # Just override all the data
            all_data = data
        self.app_data[key] = all_data
        logger.debug('Updated MC data for mode: %s', mode)

    def save_data(self, filename):
        data = self.get_data()
        data = self.append_data(data, filename)
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

    @gui.update_statusbar
    @gui.utils.disable_cls_widget('save_button')
    def _on_save_click(self, b):
        try:
            fname = self.get_filename()
            logger.info('Exporting data to file: %s', fname)
            self.save_data(fname)
        except Exception as exc:
            self.log_error(logger, exc)

    def append_data(self, data, filename):
        if not self.append_widget.value:
            return data
        if not Path(filename).is_file():
            return data

        logger.info('Found existing data file. Appending current data.')
        # Read the data, and append ours
        with open(filename) as file:
            existing_data = json.load(file)

        if not isinstance(existing_data, list):
            raise TypeError((f'Loaded data from file "{filename}", '
                             'which was not of the expected type.'
                             f'Got {type(existing_data)}, expected list'))

        runs_to_save = set(get_uuid_from_run(run) for run in data)
        # figure out what data we already saved
        for run in existing_data:
            uid = get_uuid_from_run(run)
            # Remove the ID from the set if it exists
            # since we already have it
            runs_to_save.discard(uid)

        # Figure out runs to save
        data = [run for run in data if get_uuid_from_run(run) in runs_to_save]

        data = existing_data + data
        return data

    def load_data(self, filename):
        with open(filename) as file:
            data = json.load(file)

        self.set_data(data, append=self.append_widget.value)

    @gui.update_statusbar
    @gui.utils.disable_cls_widget('load_data_button')
    def _on_load_click(self, b):
        try:
            fname = self.get_filename()
            logger.info('Loading data from file: %s', fname)
            self.load_data(fname)
        except Exception as exc:
            self.log_error(logger, exc)
        logger.info('Data loaded succesfully.')


def get_uuid_from_run(run):
    meta = run.get('meta', {})
    uid = meta.get('run_id', None)
    if uid is not None:
        uid = uuid.UUID(uid)
    return uid
