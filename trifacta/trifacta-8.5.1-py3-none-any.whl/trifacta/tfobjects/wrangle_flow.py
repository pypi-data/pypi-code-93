import os
import webbrowser
from time import sleep
from collections import OrderedDict

import numpy as np
import pandas as pd
from tqdm.auto import tqdm

from trifacta.constants import PrintFormatting, Recipe
from trifacta.util import tfrequests, tf_alias_naming_util
from trifacta.util.tfAPIs import upload_dataset_to_flow, get_user_and_aws_config, get_flow_nodes, get_python_code
from trifacta.util.tffiles import downloadGet


class WrangleFlow:
    """
    This is the class we use to capture state of a flow
    """

    def __init__(
            self,
            flow_id,
            flow_name
    ):
        self.user, self.conf, self.awsConfig = get_user_and_aws_config()
        self.flow_id = flow_id
        self.flow_name = flow_name
        self.recipe_dict = OrderedDict()
        self.recipe_name_to_output_id = {}  # dictionary of recipeName : id pairs
        self.cache = {}
        self.aliases = list()
        self.verbose = True
        self.__alias_util = tf_alias_naming_util.AliasNamingUtil()
        self.__sync_flow_state()

    def add_datasets(self, *datasets, progress_bar=None):
        if len(datasets) == 0:
            return
        data_alias_tuple_list = self._sanitize_data_alias(*datasets)
        self.aliases.extend([data_alias_tuple[1] for data_alias_tuple in data_alias_tuple_list])

        if progress_bar is None:
            progress_bar = tqdm(total=100)
        single_step_progress = (progress_bar.total - progress_bar.n) // len(data_alias_tuple_list)

        for num, data_alias_tuple in enumerate(data_alias_tuple_list, start=1):
            progress_bar.set_description(f'Uploading dataset {num}/{len(data_alias_tuple_list)}')
            recipe = upload_dataset_to_flow(data_alias_tuple, self.flow_id)
            self.recipe_dict[recipe.name] = recipe
            progress_bar.update(single_step_progress)
        progress_bar.set_description("All datasets added")
        progress_bar.n = 100
        progress_bar.refresh()

    def open(self, do_not_open=False, recipe_name=None):
        if recipe_name is None:
            url = f"{self.conf['endpoint']}/flows/{self.flow_id}"
        else:
            ooId = self.recipe_dict[recipe_name].id
            url = f"{self.conf['endpoint']}/data/{str(self.flow_id)}/{str(ooId)}?minimalView=true"

        # assume that opening the flow requires us to invalidate the result cache
        self.cache = {}
        if not do_not_open:
            print("Opening " + url)
            webbrowser.open_new(url)
        return url

    def run_job(self, pbar=None, execution='photon', recipe_name=None):
        # run the flow, return the jobGroup object. this is a blocking call.
        # as a side-effect, cache the outputObjectId, jobGroup and outputUrl
        # We repeatedly increment the pbar by 10% of the remainder as we poll.
        # If the pbar is passed in, the caller is then responsible
        # to complete and close the bar.
        if recipe_name is None:
            recipe_name = list(self.recipe_dict.keys())[0]
        if execution not in ['photon', 'emrSpark']:
            execution = 'photon'  # set it to default engine
        print(f'Running job for recipe {recipe_name} on execution engine {execution}.')

        close_pbar = False
        if not pbar:
            close_pbar = True
            pbar = tqdm(total=100)

        if recipe_name not in self.recipe_name_to_output_id:
            try:
                self.recipe_name_to_output_id[recipe_name] = self._create_output_object_id(recipe_name=recipe_name,
                                                                                           execution=execution)
            except:
                print(f"cannot create new outputObject for recipe {recipe_name}")
                return None

        if pbar:
            pbar.set_description("starting flow")
            # increment by 10% of the remainder
            pbar.update((pbar.total - pbar.n) / 10)
        jobGroup = self._run_flow(recipe_name=recipe_name, execution=execution)
        self._cache_put("jobGroup", recipe_name, jobGroup)

        if pbar:
            pbar.set_description("transforming and profiling data")
            # increment by 10% of the remainder
            pbar.update((pbar.total - pbar.n) / 10)
        url = f"/v4/jobgroups/{jobGroup['id']}/status"
        resp = None
        while resp is None or resp.json() != "Complete":
            resp = tfrequests.get(url)
            if resp.json() != "Complete":
                sleep(1)
                if pbar and pbar.n < (pbar.total - 1):
                    # increment by 10% of the remainder
                    pbar.update((pbar.total - pbar.n) / 10)

        self._cache_put("outputUrl", recipe_name, self._getOutputUrl(recipe_name))

        if close_pbar:
            pbar.update(pbar.total - pbar.n)
            pbar.close()
        return jobGroup

    def profile(self, recipe_name=None):
        if recipe_name is None:
            recipe_name = list(self.recipe_dict.keys())[0]
        if self._cache_get("prof", recipe_name):
            return self._cache_get("prof", recipe_name)

        jobGroup = self._cache_get("jobGroup", recipe_name)
        if jobGroup is None:
            jobGroup = self.run_job(recipe_name=recipe_name)
        if jobGroup is None:  # error
            return None

        url = f"/v4/jobgroups/{jobGroup['id']}/profile"
        resp = tfrequests.get(url)

        self._cache_put("prof", recipe_name, resp.json())
        return self._cache_get("prof", recipe_name)

    def dq_bars(self, show_types=True, recipe_name=None):
        if recipe_name is None:
            recipe_name = list(self.recipe_dict.keys())[0]
        hist = self.profile(recipe_name)["profilerTypeCheckHistograms"]
        if show_types:
            types = self.col_types(recipe_name)
            rows = [
                {
                    **{"column": f"{h} ({t})"},
                    **{cat["key"]: cat["count"] for cat in hist[h]},
                }
                for h, t in zip(hist, types["type"])
            ]
        else:
            rows = [
                {**{"column": h}, **{cat["key"]: cat["count"] for cat in hist[h]}}
                for h in hist
            ]
        df = pd.DataFrame(columns=["column", "VALID", "INVALID", "EMPTY"])
        df = pd.DataFrame(rows)
        df = df.reindex(columns=["column", "VALID", "INVALID", "EMPTY"]).set_index(
            "column"
        )
        df = df.replace(np.nan, 0)
        return df

    def col_types(self, recipe_name=None):
        if recipe_name is None:
            recipe_name = list(self.recipe_dict.keys())[0]
        return pd.DataFrame(
            [(k, v[0]) for (k, v) in self.profile(recipe_name)["columnTypes"].items()],
            columns=["name", "type"],
        )

    def recipe_names(self):
        return [r.name for r in list(self.recipe_dict.values())]

    def _numeric_bars_df(self, col, name):
        # min = col['min']
        # max = col['max']
        # roundMin = col['roundMin']
        # roundMax = col['roundMax']
        # quartiles = col['quartiles']
        df = (
            pd.DataFrame(col["buckets"])
                .rename(columns={"pos": name, "b": "count"})
                .set_index(name)
        )
        return df

    def _categorical_bars_df(self, col, name):
        # k = col['k']
        # c = col['c']
        # ub = col['ub']
        df = pd.DataFrame(col["topk"]).rename(columns={"key": name}).set_index(name)
        return df

    def _bars_df(self, col, name):
        if "buckets" in col:
            df = self._numeric_bars_df(col, name)
        elif "topk" in col:
            df = self._categorical_bars_df(col, name)
        else:
            raise (
                TypeError(f"neither buckets not topk given for bar chart in {name}!")
            )
        return df

    def bars_df_list(self, recipe_name=None):
        if recipe_name is None:
            recipe_name = list(self.recipe_dict.keys())[0]
        hist = self.profile(recipe_name)["profilerValidValueHistograms"]
        return [self._bars_df(hist[col], col) for col in hist]

    def _numeric_summary_df(self, col, name, recipe_name=None):
        if recipe_name is None:
            recipe_name = list(self.recipe_dict.keys())[0]
        schema = col.keys() - ["buckets", "quartiles"]
        row = {"column": name, "type": self.profile(recipe_name)["columnTypes"][name]}
        row.update({k: col[k] for k in schema})
        row.update(col["quartiles"])
        return row

    def _categorical_summary_df(self, col, name, recipe_name=None):
        if recipe_name is None:
            recipe_name = list(self.recipe_dict.keys())[0]
        schema = col.keys() - ["topk"]
        row = {"column": name, "type": self.profile(recipe_name)["columnTypes"][name]}
        row.update({k: col[k] for k in schema})
        return row

    def summary(self, recipe_name=None):
        if recipe_name is None:
            recipe_name = list(self.recipe_dict.keys())[0]
        hist = self.profile(recipe_name)["profilerValidValueHistograms"]
        data = []
        for col in hist:
            if "buckets" in hist[col]:
                data.append(self._numeric_summary_df(hist[col], col, recipe_name))
            elif "topk" in hist[col]:
                data.append(self._categorical_summary_df(hist[col], col, recipe_name))
            else:
                raise (
                    TypeError(f"neither buckets not topk given for summary of {col}!")
                )
        df = pd.DataFrame(data).set_index("column")
        return df

    def pdf_profile(self, filename=None, recipe_name=None):
        if recipe_name is None:
            recipe_name = list(self.recipe_dict.keys())[0]
        if self._cache_get("pdfProf", recipe_name):
            return self._cache_get("pdfProf", recipe_name)
        jobGroup = None
        if self._cache_get("jobGroup", recipe_name) is None:
            jobGroup = self.run_job(recipe_name=recipe_name)
        if jobGroup is None:  # error
            return None

        jobGroup = self._cache_get("jobGroup", recipe_name)
        url = f"/v4/jobgroups/{jobGroup['id']}/pdfResults"
        resp = None
        # poll until job completes, sleeping between polls
        while resp is None or resp.status_code == 404:
            resp = tfrequests.raw_get(url)
            if resp.status_code == 404:
                sleep(1)
        self._cache_put("pdfProf", recipe_name, resp)
        if filename:
            with open(filename, "wb") as fd:
                for chunk in resp.iter_content(chunk_size=128):
                    fd.write(chunk)
        return resp

    def output(self, filename=None, noDf=False, recipe_name=None):
        if recipe_name is None:
            recipe_name = list(self.recipe_dict.keys())[0]
        if (filename is None) and (noDf == False) and not (self._cache_get("outDf", recipe_name) is None):
            return self._cache_get("outDf", recipe_name)
        if not self._cache_get("jobGroup", recipe_name):
            self.run_job(recipe_name=recipe_name)
        result = downloadGet(self._cache_get("outputUrl", recipe_name), filename)
        if not noDf:
            df = pd.read_csv(result)
            self._cache_put("outDf", recipe_name, df)
        if not filename:
            # clean up tempfile created by downloadGet
            os.remove(result)
        return df

    def _tf_cleanup(self):
        # garbage collect state in Trifacta
        # first the flow; presumably this cascades delete to
        # OutputObject, writeSettings, and recipes
        tfrequests.delete(f"/v4/flows/{self.flow_id}")

    def open_profile(self, recipe_name=None):
        if recipe_name is None:
            recipe_name = list(self.recipe_dict.keys())[0]
        if self._cache_get('jobGroup', recipe_name) is None:
            jobGroup = self.run_job(recipe_name=recipe_name)
            if jobGroup is None:  # error
                return None
        url = (
                str(self.conf["endpoint"])
                + "/jobs/"
                + str(self._cache_get('jobGroup', recipe_name)['id'])
                + "?activeTab=profile"
        )
        print("Opening " + url)
        webbrowser.open_new(url)
        return url

    def get_pandas(self, add_to_next_cell=False, recipe_name=None):
        if recipe_name is None:
            recipe_name = list(self.recipe_dict.keys())[0]
        if recipe_name not in self.recipe_name_to_output_id:
            self.recipe_name_to_output_id[recipe_name] = self._create_output_object_id(recipe_name=recipe_name)

        python_code = get_python_code(self.recipe_name_to_output_id[recipe_name])
        if add_to_next_cell:
            self._add_source_to_next_notebook_cell(python_code)
        else:
            return python_code

    @staticmethod
    def _add_source_to_next_notebook_cell(contents):
        from IPython.core.getipython import get_ipython
        shell = get_ipython()
        shell.set_next_input(contents, replace=False)

    # def __del__(self):
    #     self._tf_cleanup()

    def _sanitize_data_alias(self, *args):
        data_alias_tuple_list = list()
        print('Registering aliases for input dataframes as per their input order.')
        for data in args:
            if isinstance(data, pd.DataFrame):
                generated_alias = self.__alias_util.get_valid_alias_name()
                data_alias_tuple_list.append((data, generated_alias))
                if self.verbose:
                    print(f'Alias not found, '
                          f'new alias assigned : {PrintFormatting.GREEN}{generated_alias}{PrintFormatting.END}')
            elif isinstance(data, tuple):
                if isinstance(data[1], str) and isinstance(data[0], pd.DataFrame):
                    generated_alias = self.__alias_util.get_valid_alias_name(data[1])
                    data_alias_tuple_list.append((data[0], generated_alias))
                    if generated_alias != data[1] and self.verbose:
                        print(
                            f'Alias conflict, new alias : {PrintFormatting.GREEN}{generated_alias}{PrintFormatting.END}')
                    elif self.verbose:
                        print(f'Alias registered : {PrintFormatting.GREEN}{generated_alias}{PrintFormatting.END}')
                elif isinstance(data[0], str) and isinstance(data[1], pd.DataFrame):
                    generated_alias = self.__alias_util.get_valid_alias_name(data[0])
                    data_alias_tuple_list.append((data[1], generated_alias))
                    if generated_alias != data[0] and self.verbose:
                        print(f'Alias conflict, '
                              f'new alias : {PrintFormatting.GREEN}{generated_alias}{PrintFormatting.END}')
                    elif self.verbose:
                        print(f'Alias registered : {PrintFormatting.GREEN}{generated_alias}{PrintFormatting.END}')
            else:
                print('Provide dataset with valid format, '
                      'dataframe or (dataframe, alias_name) or (alias_name, dataframe)')
        return data_alias_tuple_list

    def _cache_get(self, k, i):
        if (k, i) in self.cache:
            return self.cache[(k, i)]
        else:
            return None

    def _cache_put(self, k, i, v):
        self.cache[(k, i)] = v

    def _create_output_object_id(self, recipe_name, execution='photon'):
        if recipe_name is None:
            recipe_name = list(self.recipe_dict.keys())[0]
        recipe = self.recipe_dict[recipe_name]

        # make sure there's no outputObject for this recipeName already;
        # if so, raise an error.
        the_url = f"/v4/wrangledDatasets/{recipe.id}?embed=outputObjects"
        fn = tfrequests.get(the_url).json()
        if fn['outputObjects']['data']:
            return fn['outputObjects']['data'][0]['id']
        # assert (len(fn['outputObjects']['data']) == 0)

        # create an output object
        payload = {
            "profiler": True,
            "execution": execution,
            "flowNodeId": recipe.id,
            "isAdhoc": True,
        }

        oObj = tfrequests.post(url="/v4/outputObjects/", json=payload).json()
        awsConfig = self.awsConfig

        # establish write settings
        payload = {
            "action": "create",
            "format": "csv",
            "compression": "none",
            "header": True,
            "asSingleFile": True,
            "suffix": "_increment",
            "outputObjectId": oObj["id"],
        }
        if awsConfig:
            payload.update(
                {
                    "path": "s3://"
                            + awsConfig["defaultBucket"]
                            + self.user["outputHomeDir"]
                            + "/"
                            + self.flow_name
                            + ".csv"
                }
            )
        else:
            payload.update(
                {
                    "path": "file://"
                            + self.user["outputHomeDir"]
                            + "/"
                            + self.flow_name
                            + ".csv"
                }
            )

        wsObj = tfrequests.post(url="/v4/writeSettings", json=payload)

        return oObj["id"]

    def _run_recipe(self, recipe, execution='photon'):
        payload = {
            "wrangledDataset": {"id": recipe.id},
            "overrides": {
                "execution": execution,
                "profiler": True,
            },
            # "ranfrom": "ui",
            # "testMode": False,
            # "isCanceled": False
        }
        if not self.awsConfig:
            payload["overrides"].update({"execution": "photon"})
        jobGroup = tfrequests.post(url="/v4/jobGroups/", json=payload).json()
        return jobGroup

    def _run_flow(self, recipe_name=None, execution='photon'):
        if recipe_name is None:
            recipe_name = list(self.recipe_dict.keys())[0]
        return self._run_recipe(self.recipe_dict[recipe_name], execution=execution)

    def _getOutputUrl(self, recipe_name=None):
        if recipe_name is None:
            recipe_name = list(self.recipe_dict.keys())[0]

        # Assumes there is only one filewriter for this jobGroup,
        # and only one scriptResult for this filewriter!
        outs = tfrequests.get(
            f"/v4/jobGroups/{self._cache_get('jobGroup', recipe_name)['id']}?embed=jobs.scriptResults"
        ).json()["jobs"]["data"]
        fw = list(filter(lambda x: x["jobType"] == "filewriter", outs))
        if len(fw) > 1:
            raise (Exception("ambiguous output; multiple filewriters for job!"))
        sr = fw[0]["scriptResults"]["data"]
        if len(sr) > 1:
            raise (Exception("ambiguous output; multiple scriptResults for job!"))
        sr0 = sr[0]
        srId = sr0["id"]
        return f"/v4/scriptResults/{srId}/download"

    def __sync_flow_state(self):
        self.recipe_dict = OrderedDict()
        flow_nodes = get_flow_nodes(self.flow_id)
        for flow_node in flow_nodes:
            if flow_node['wrangled']:
                self.recipe_dict[flow_node['recipe']['name']] = Recipe(flow_node['recipe']['name'], flow_node['id'])
        self.__alias_util.init_alias_names(*list(self.recipe_dict.keys()))
