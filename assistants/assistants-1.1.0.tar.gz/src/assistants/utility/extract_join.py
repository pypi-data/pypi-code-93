from pathlib import Path


def join_extracts(root_path: Path, region: str, folder: str) -> None:
    training_folder = "Raw Extracts - Trng"
    partial_extracts_path = root_path / region / training_folder / folder
    output_file = partial_extracts_path.parent.joinpath(f"Region Training Report (Beta) - {region} - {folder}.csv")

    headers_written = False
    with open(output_file, "w", encoding="utf-8") as target_file:
        for filename in partial_extracts_path.glob("*.csv"):
            with open(filename, "r", encoding="utf-8-sig") as f:
                if headers_written:
                    next(f)  # skip header line 1 (Textbox77)
                    next(f)  # skip header line 2 (Date: ...)
                    next(f)  # skip header line 3 (<blank>)
                    next(f)  # skip header line 4 (Col headers)
                else:
                    for _ in range(4):
                        target_file.write(next(f))
                headers_written = True
                for line in f:
                    if line != "\n":
                        target_file.write(line)


if __name__ == "__main__":
    join_extracts(
        root_path=Path(r"A:\OneDrive\OneDrive - Central Yorkshire Scouts\National\Compliance Reporting"),
        # region="East Midlands",
        region="North East",
        # region="South East",
        folder="2021-02-01",
    )
