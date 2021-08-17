import sqlite3
import os
import pandas as pd
import numpy as np
from sensiml.datasegments import DataSegments, DataSegment
import uuid
from collections import OrderedDict


class DCLProject:
    def __init__(self):
        self._path = None
        self._conn = None
        self._tables = None
        self._verbose = False

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, value):
        if isinstance(value, bool):
            self._verbose = value
        else:
            print("verbose must be either True or False.")

    @property
    def data_dir(self):

        if self._path is None:
            raise Exception("Path is not set!")

        return os.path.join(self._path, "data")

    def _set_table_list(self):
        cursorObj = self._conn.cursor()

        cursorObj.execute('SELECT name from sqlite_master where type= "table"')

        self._tables = [x[0] for x in cursorObj.fetchall()]

    def create_connection(self, db_file):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        self._path = os.path.dirname(db_file)
        if not os.path.exists(db_file):
            print("database file not found at {}".format(db_file))
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Exception as e:
            print(e)
            raise e

        self._conn = conn
        self._set_table_list()

    def _execute_query(self, query, header=None):

        cur = self._conn.cursor()

        if self.verbose:
            print(query)

        cur.execute(query)

        if header is None:
            header = [x[0] for x in cur.description]

        rows = cur.fetchall()

        results = []
        for row in rows:
            results.append(row)

        df = pd.DataFrame(results, columns=header)

        if "uuid" in header:
            df["uuid"] = df["uuid"].apply(lambda x: uuid.UUID(bytes=x) if x else None)

        if "local_status" in header:
            local_status = {
                0: "To Add",
                1: "To Update",
                "Synced": "Synced",
                2: "To Delete",
                None: "Synced",
            }
            df["local_status"] = (
                df["local_status"].fillna("Synced").apply(lambda x: local_status[x])
            )

        return df

    def _list_table_raw(self, tablename):

        if tablename not in self._tables:
            print("Table is not part of the database.")
            return None

        query = "SELECT * FROM {tablename} ".format(tablename=tablename)

        return self._execute_query(query)

    def _list_table(self, tablename, fields, fk_fields=None, query_filter=None):

        if tablename not in self._tables:
            print("Table is not part of the database.")
            return None

        select_fields = ", ".join(
            ["{}.{}".format(tablename, field) for field in fields]
        )

        if fk_fields:
            select_fields += ", " + ", ".join(
                [
                    "{}.name".format(fk_table)
                    if fk_table != "LabelValue"
                    else "{}.value".format(fk_table)
                    for fk_table in fk_fields.keys()
                ]
            )

        query_select = "SELECT {select_fields} FROM {tablename} ".format(
            select_fields=select_fields, tablename=tablename
        )

        query_join = ""

        if fk_fields:
            join_fields = []
            for fk_table, fk_field in fk_fields.items():
                join_fields.append(
                    "JOIN {fk_table} ON {fk_table}.id = {tablename}.{fk_field} ".format(
                        fk_table=fk_table, tablename=tablename, fk_field=fk_field
                    )
                )
            query_join += " ".join(join_fields)

        header = None

        if query_filter:
            query_where = (
                query_filter  # + "AND {}.local_status != 2 ".format(tablename)
            )
        else:
            query_where = ""  # "WHERE {}.local_status != 2 ".format(tablename)

        if fk_fields:
            header = fields + list(fk_fields.values())

        return self._execute_query(query_select + query_join + query_where, header)

    def list_captures(self):
        fields = [
            "uuid",
            "name",
            "file_size",
            "number_samples",
            "set_sample_rate",
            "created_at",
            "local_status",
            "last_modified",
        ]

        fk_fields = OrderedDict([("CaptureConfiguration", "capture_configuration")])

        return self._list_table("Capture", fields=fields, fk_fields=fk_fields)

    def list_sessions(self):
        fields = [
            "name",
            "parameters",
            "custom",
            "preprocess",
            "created_at",
            "local_status",
            "last_modified",
        ]

        fk_fields = OrderedDict([])

        return self._list_table("Segmenter", fields, fk_fields)

    def list_capture_segments(self, capture=None, session=None):

        query_filter = ""

        if capture and session:
            query_filter = 'WHERE Capture.name="{}" '.format(
                capture
            ) + 'AND Segmenter.name = "{0}" '.format(session)

        elif capture:
            query_filter = 'WHERE Capture.name="{}" '.format(capture)
        elif session:
            query_filter += 'WHERE Segmenter.name = "{0}" '.format(session)

        fields = [
            "uuid",
            "capture_sample_sequence_start",
            "capture_sample_sequence_end",
            "local_status",
            "created_at",
            "last_modified",
        ]

        fk_fields = OrderedDict(
            [
                ("Segmenter", "segmenter"),
                ("Capture", "capture"),
                ("LabelValue", "label_value"),
            ]
        )

        return self._list_table("CaptureLabelValue", fields, fk_fields, query_filter)

    def get_capture_segments(self, capture, session):
        """
        Returns a DataSegment object of the specified capture and session


        Args:
            capture_name (str): name of capture
            session (str):  name of session where the labels are
            recognized (Dataframe): results from recognize signal on this capture
            class_map (dict): The class map describing how to map the labels to integer values
            groups (dict): a dict of key value pairs where the key is the original label the value is the label it was should be renamed to

        """

        labels = self.list_capture_segments(capture=capture, session=session)

        # TODO: read wave file if file is .wav
        tmp_df = pd.read_csv(os.path.join(self.data_dir, capture), index_col="sequence")

        M = DataSegments()

        for index, label in enumerate(
            labels[
                ["capture_sample_sequence_start", "capture_sample_sequence_end", "uuid"]
            ].values
        ):
            M[label[2]] = DataSegment(
                tmp_df.loc[label[0] : label[1]],
                metadata={"segment": index, "capture": capture},
            )

        return M

    def get_capture(self, capture_name):
        """
        Returns the capture as a dataframe

        Args:
            capture_name (str): name of capture

        """

        # TODO: read wave file if file is .wav
        tmp_df = pd.read_csv(
            os.path.join(self.data_dir, capture_name), index_col="sequence"
        )

        return tmp_df

    def plot_segment_labels(
        self,
        capture_name,
        session,
        recognized=None,
        class_map=None,
        groups=None,
        figsize=(24, 6),
        style="x",
        ms=2,
    ):
        """
        Creates a plot of the labels and raw signal data for a capture and session. 
        Will also overlay the results of recognize signal for the capture file and model. 


        Args:
            capture_name (str): name of capture
            session (str):  name of session where the labels are
            recognized (Dataframe): results from recognize signal on this capture
            class_map (dict): The class map describing how to map the labels to 
             integer values
            groups (dict): a dict of key value pairs where the key is the original
              label the value is the label it was should be renamed to
        """

        segments = self.list_capture_segments(capture_name, session)
        capture = self.get_capture(capture_name)

        if groups:
            segments["label_value"] = segments["label_value"].apply(
                lambda x: x if x not in groups else groups[x]
            )

        if class_map is None:
            class_map = {
                label: index
                for index, label in enumerate(segments.label_value.unique())
            }

        M = {k: np.zeros(len(capture)) - 1 for k in segments.label_value.unique()}
        M["Unknown"] = np.zeros(len(capture))

        for index, seg in segments.iterrows():
            M[seg["label_value"]][
                seg["capture_sample_sequence_start"] : seg[
                    "capture_sample_sequence_end"
                ]
            ] = class_map[seg["label_value"]]
            M["Unknown"][
                seg["capture_sample_sequence_start"] : seg[
                    "capture_sample_sequence_end"
                ]
            ] = -1

        ytick_values = [0] + sorted(list(class_map.values()))
        r_class_map = {v: k for k, v in class_map.items()}
        r_class_map[0] = "Unknown"
        ytick_labels = [r_class_map[x] for x in ytick_values]

        ax = pd.DataFrame(M).plot(
            ylim=(-0.5, len(M) + 1),
            figsize=figsize,
            style=style,
            ms=ms,
            yticks=ytick_values,
        )
        ax.set_yticklabels(ytick_labels)

        if recognized is not None:
            recognized["classification_step"] = (
                recognized["SegmentStart"] + recognized["SegmentLength"] / 2
            )
            recognized.plot(
                y="Classification", x="classification_step", ax=ax, style="-x"
            )

        capture.reset_index(drop=True).plot(figsize=figsize)
