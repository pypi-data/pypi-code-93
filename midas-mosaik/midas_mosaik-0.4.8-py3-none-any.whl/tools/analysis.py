import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def analyze(
    name,
    db_path="midasmv_der",
    output_path="_outputs",
    db_style="mosaik",
    sim_keys=["Powergrid-0"],
):
    mosaik_style = db_style.lower() == "mosaik"
    data = load_db(db_path, mosaik_style)

    os.makedirs(output_path, exist_ok=True)
    for sim_key in sim_keys:
        analyze_grid(
            data[sim_key], f"{name}_{sim_key}", output_path, mosaik_style
        )

    if not mosaik_style:
        data.close()


def load_db(filename, mosaik_style):
    if mosaik_style:
        data = dict()
        with h5py.File(filename, "r") as data_file:

            for tsd in data_file["Series"]:
                sid, eid = tsd.split(".")
                data.setdefault(sid, dict())
                data[sid].setdefault(eid, dict())
                for attr in data_file["Series"][tsd]:
                    data[sid][eid][attr] = np.array(
                        data_file["Series"][tsd][attr]
                    )

        return data
    else:
        return pd.HDFStore(filename)
        # with h5py.File(filename, "r") as data_file:
        #     print(data_file)
        # data = pd.read_hdf(filename)
        # print(data)


def analyze_storages(data, report_file, name, output_path):

    p_mws = np.array([data[key]["p_mw"] for key in data])
    total_p = p_mws.sum(axis=0)
    q_mvars = np.array([data[key]["q_mvar"] for key in data])
    total_q = q_mvars.sum(axis=0)

    annual_p = np.sort(total_p)[::-1]
    annual_q = np.sort(total_q)[::-1]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    ax1.plot(total_p)
    ax1.set_title("Aggregated Storage active power")
    ax1.set_xlabel("time (15 minute steps)")
    ax1.set_ylabel("MW")
    ax2.plot(annual_p)
    ax2.set_title("Annual curve Storage active power")
    ax2.set_xlabel("time (15 minute steps)")
    ax2.set_ylabel("MW")
    plt.savefig(
        os.path.join(output_path, f"{name}_aggr_storage_p.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    ax1.plot(total_q)
    ax1.set_title("Aggregated Storage reactive power")
    ax1.set_xlabel("time (15 minute steps)")
    ax1.set_ylabel("MVAr")
    ax2.plot(annual_q)
    ax2.set_title("Annual curve Storage reactive power")
    ax2.set_xlabel("time (15 minute steps)")
    ax2.set_ylabel("MVAr")

    plt.savefig(
        os.path.join(output_path, f"{name}_aggr_storage_q.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()
    report_file.write(
        "[Storage p_MW] \n"
        f"Max: {np.max(total_p):.3f} MW, Min: {np.min(total_p):.3f} MW\n"
        f"Average: {np.mean(total_p):.3f} MW, Sum: {np.sum(total_p):.3f} MW"
        f"\nAnnual active energy: {np.sum(total_p) / 4:.3f} MWh/a\n"
    )

    report_file.write(
        "[Storage q_MVAr] \n"
        f"Max: {np.max(total_q):.3f} MVAr, Min: {np.min(total_q):.3f} MVAr\n"
        f"Average: {np.mean(total_q):.3f} MVAr, Sum: {np.sum(total_q):.3f} MVAr"
        f"\nAnnual reactive energy: {np.sum(total_q) / 4:.3f} MVArh/a\n"
    )
    total_s = np.sqrt(
        np.square(np.sum(total_p) * 0.25) + np.square(np.sum(total_q) * 0.25)
    )
    report_file.write(
        "[Storage s_MVA] \n"
        f"Annual apparent energy supply: {total_s:.3f} MVAh/a\n"
    )


def analyze_grid(data, name, output_path, mosaik_style):
    report_file = open(os.path.join(output_path, f"{name}_report.txt"), "w")
    if not mosaik_style:
        new_data = dict()
        for key, vals in data.items():
            eid, attr = key.split(".")
            new_data.setdefault(eid, dict())
            new_data[eid][attr] = np.array(vals)
        data = new_data
    bus_data = {key: val for key, val in data.items() if "bus" in key}
    analyze_buses(bus_data, report_file, name, output_path)

    load_data = {key: val for key, val in data.items() if "load" in key}
    analyze_loads(load_data, report_file, name, output_path)

    sgen_data = {key: val for key, val in data.items() if "sgen" in key}
    analyze_sgens(sgen_data, report_file, name, output_path)

    line_data = {key: val for key, val in data.items() if "line" in key}
    analyze_line(line_data, report_file, name, output_path)

    storage_data = {key: val for key, val in data.items() if "storage" in key}
    if storage_data:
        analyze_storages(storage_data, report_file, name, output_path)

    report_file.close()


def analyze_buses(data, report_file, name, output_path):
    num_buses = len(data)

    vm_pus = np.array([data[key]["vm_pu"] for key in data])

    data["bus_avg"] = {"vm_pu": vm_pus.mean(axis=0)}

    for key, vals in data.items():

        vm_pus = np.array(vals["vm_pu"])

        annual = np.sort(vm_pus)[::-1]
        too_high10 = (annual > 1.1).sum()
        too_high4 = (annual > 1.04).sum()
        too_low10 = (annual < 0.9).sum()
        too_low4 = (annual < 0.96).sum()

        if too_high10 > 0:
            report_file.write(f"[{key}] {too_high10} values > 1.1\n")
        if too_low10 > 0:
            report_file.write(f"[{key}] {too_low10} values < 0.9\n")
        if too_high4 > 0:
            report_file.write(f"[{key}] {too_high4} values > 1.04\n")
        if too_low4 > 0:
            report_file.write(f"[{key}] {too_low4} values < 0.96\n")

        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        ax.plot(annual)
        ax.axhline(y=1.1, color="red")
        ax.axhline(y=1.04, linestyle="--", color="red")
        ax.axhline(y=0.96, linestyle="--", color="red")
        ax.axhline(y=0.9, color="red")
        ax.set_title(f"{key}")
        ax.set_ylabel("voltage magnitude p.u.")
        ax.set_xlabel("time (15 minute steps)")
        plt.savefig(
            os.path.join(output_path, f"{name}_{key}_vmpu_annual.png"),
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()


def analyze_loads(data, report_file, name, output_path):
    p_mws = np.array([data[key]["p_mw"] for key in data])
    total_p = p_mws.sum(axis=0)
    q_mvars = np.array([data[key]["q_mvar"] for key in data])
    total_q = q_mvars.sum(axis=0)

    annual_p = np.sort(total_p)[::-1]
    annual_q = np.sort(total_q)[::-1]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    ax1.plot(total_p)
    ax1.set_title("Aggregated load active power")
    ax1.set_xlabel("time (15 minute steps)")
    ax1.set_ylabel("MW")

    ax2.plot(annual_p)
    ax2.set_title("Annual curve load active power")
    ax2.set_xlabel("time (15 minute steps)")
    ax2.set_ylabel("MW")
    plt.savefig(
        os.path.join(output_path, f"{name}_aggr_load_p.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    ax1.plot(total_q)
    ax1.set_title("Aggregated load reactive power")
    ax1.set_xlabel("time (15 minute steps)")
    ax1.set_ylabel("MVAr")

    ax2.plot(annual_q)
    ax2.set_title("Annual curve load reactive power")
    ax2.set_xlabel("time (15 minute steps)")
    ax2.set_ylabel("MVAr")
    plt.savefig(
        os.path.join(output_path, f"{name}_aggr_load_q.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()
    report_file.write(
        "[Load p_MW] \n"
        f"Max: {np.max(total_p):.3f} MW, Min: {np.min(total_p):.3f} MW\n"
        f"Average: {np.mean(total_p):.3f} MW, Sum: {np.sum(total_p):.3f} MW"
        f"\nAnnual active energy: {np.sum(total_p) / 4:.3f} MWh/a\n"
    )

    report_file.write(
        "[Load q_MVAr] \n"
        f"Max: {np.max(total_q):.3f} MVAr, Min: {np.min(total_q):.3f} MVAr\n"
        f"Average: {np.mean(total_q):.3f} MVAr, Sum: {np.sum(total_q):.3f} MVAr"
        f"\nAnnual reactive energy: {np.sum(total_q) / 4:.3f} MVArh/a\n"
    )
    total_s = np.sqrt(
        np.square(np.sum(total_p) * 0.25) + np.square(np.sum(total_q) * 0.25)
    )
    report_file.write(
        "[Load s_MVA] \n"
        f"Annual apparent energy demand: {total_s:.3f} MVAh/a\n"
    )


def analyze_sgens(data, report_file, name, output_path):
    p_mws = np.array([data[key]["p_mw"] for key in data])
    total_p = p_mws.sum(axis=0)
    q_mvars = np.array([data[key]["q_mvar"] for key in data])
    total_q = q_mvars.sum(axis=0)

    annual_p = np.sort(total_p)[::-1]
    annual_q = np.sort(total_q)[::-1]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    ax1.plot(total_p)
    ax1.set_title("Aggregated sgen active power")
    ax1.set_xlabel("time (15 minute steps)")
    ax1.set_ylabel("MW")
    ax2.plot(annual_p)
    ax2.set_title("Annual curve sgen active power")
    ax2.set_xlabel("time (15 minute steps)")
    ax2.set_ylabel("MW")
    plt.savefig(
        os.path.join(output_path, f"{name}_aggr_sgen_p.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    ax1.plot(total_q)
    ax1.set_title("Aggregated sgen reactive power")
    ax1.set_xlabel("time (15 minute steps)")
    ax1.set_ylabel("MVAr")
    ax2.plot(annual_q)
    ax2.set_title("Annual curve sgen reactive power")
    ax2.set_xlabel("time (15 minute steps)")
    ax2.set_ylabel("MVAr")

    plt.savefig(
        os.path.join(output_path, f"{name}_aggr_sgen_q.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()
    report_file.write(
        "[Sgen p_MW] \n"
        f"Max: {np.max(total_p):.3f} MW, Min: {np.min(total_p):.3f} MW\n"
        f"Average: {np.mean(total_p):.3f} MW, Sum: {np.sum(total_p):.3f} MW"
        f"\nAnnual active energy: {np.sum(total_p) / 4:.3f} MWh/a\n"
    )

    report_file.write(
        "[Sgen q_MVAr] \n"
        f"Max: {np.max(total_q):.3f} MVAr, Min: {np.min(total_q):.3f} MVAr\n"
        f"Average: {np.mean(total_q):.3f} MVAr, Sum: {np.sum(total_q):.3f} MVAr"
        f"\nAnnual reactive energy: {np.sum(total_q) / 4:.3f} MVArh/a\n"
    )
    total_s = np.sqrt(
        np.square(np.sum(total_p) * 0.25) + np.square(np.sum(total_q) * 0.25)
    )
    report_file.write(
        "[Sgen s_MVA] \n"
        f"Annual apparent energy supply: {total_s:.3f} MVAh/a\n"
    )


def analyze_line(data, report_file, name, output_path):
    load_percent = np.array([data[key]["loading_percent"] for key in data])

    data["line_avg"] = {"loading_percent": load_percent.mean(axis=0)}

    for key, vals in data.items():
        load_percent = np.array(vals["loading_percent"])

        annual = np.sort(load_percent)[::-1]
        too_high10 = (annual > 120).sum()
        too_high4 = (annual > 60).sum()

        if too_high10 > 0:
            report_file.write(f"[{key}] {too_high10} values > 120\n")
        if too_high4 > 0:
            report_file.write(f"[{key}] {too_high4} values > 60\n")

        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        ax.plot(annual)
        ax.axhline(y=120, color="red")
        ax.axhline(y=60, linestyle="--", color="red")
        ax.set_title(f"{key}")
        ax.set_ylabel("Line load percentage")
        ax.set_xlabel("time (15 minute steps)")
        plt.savefig(
            os.path.join(
                output_path, f"{name}_{key}_load_percentage_annual.png"
            ),
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()


if __name__ == "__main__":
    # analyze(
    #     name="midaslv",
    #     db_path="_outputs/midaslv.hdf5",
    #     db_style="mosaik",
    # )
    analyze(
        name="midasmv_der",
        db_path="_outputs/midasmv_der.hdf5",
        db_style="midas",
    )
