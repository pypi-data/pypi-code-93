from json import dump
from io import StringIO
from typing import List
from pandas import read_csv


def convert(filenames: List[str]) -> None:
    """convert files from csv to json

    Args:
        filenames (List[str]): list of filenames with path; each path must be a string
    """
    if not type(filenames) == list:
        filenames = [filenames]

    for filename in filenames:
        # split the file based on dashes; use two dashes since negative numbers also contain dashes
        with open(filename, "r") as infile:
            data = list(
                filter(None, infile.read().split("--"))
            )  # remove all empty splits
            data = list(
                filter(lambda x: x != "\t", data)
            )  # remove all splits with only tabs ("\t")

        sample_info = list(
            filter(None, data[1].strip("$").split("\n"))
        )  # second item in list contains sample information
        # assemble the dictionary
        sample_dict = {}
        for item in sample_info:
            intensity = item.strip("$").split(":", 1)
            sample_dict[intensity[0]] = intensity[1]

        if "No data" in data[-1]:
            print("blank file")
            continue
        else:
            print(sample_dict)

        # read the last item of the data list as a dataframe
        dataFrame = read_csv(
            StringIO(data[-1]), delimiter="\t", names=["254", "280", "320", "FC"]
        )

        # expected format for each column is one of the following:
        # <intensity,time> or <intensity>

        # if <intensity>
        sample_dict["time"] = [i / 10 for i in range(0, dataFrame.shape[0])]

        # Kept just in case
        # sample_dict["time"] = [round(float(x.split(",")[1]) * 60, 1) for x in df["254"].to_list()]
        # get time from splitting one column of dataframe and taking the second value in each cell then multiply it by 60 to convert it to seconds

        sample_dict["intensities"] = {}  # initialize intensities

        if dataFrame.dtypes[0] == "float64":
            for col in dataFrame.columns:
                sample_dict["intensities"][col] = [
                    float(x) for x in dataFrame[col].to_list()
                ]
        else:
            for col in dataFrame.columns:
                sample_dict["intensities"][col] = [
                    float(x.split(",")[0]) for x in dataFrame[col].to_list()
                ]

        # write to a json file
        with open(filename.replace(".csv", ".json"), "w") as outfile:
            dump(sample_dict, outfile)
