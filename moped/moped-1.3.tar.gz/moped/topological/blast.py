"""NCBI Blast interface."""


import functools
import io
import multiprocessing
import pathlib
import subprocess
import sys
from collections.abc import Iterable

import pandas as pd

from ..utils import get_temporary_directory

TEMP_DIR = get_temporary_directory(subdirectory="blast")


def _generate_blast_database(genome_file):
    """Generate a blast database from a given nucleotide fasta file.

    The generates files are stored in a temporary directory.

    Attributes
    ----------
    genome_file: fasta file
        Nucleotide fasta file
    """
    subprocess.run(
        [
            "makeblastdb",
            "-in",
            genome_file,
            "-parse_seqids",
            "-blastdb_version",
            "5",
            "-dbtype",
            "nucl",
            "-out",
            TEMP_DIR / genome_file.stem,
        ]
    )


def _unify_inputs(sequences, tempfiles):
    """Unify the different inputs for the blast method.

    Will create temporary files, if sequences is not a file

    Attributes
    ----------
    sequences: str, Iterable(str), file_path
        Inputs
    tempfiles: list
        list to keep track of all created files

    Returns
    -------
    file: pathlib.Path
    """
    if isinstance(sequences, str):
        if sequences.startswith(">"):
            file = TEMP_DIR / "blast_input.fasta"
            with open(file, "w+") as f:
                f.write(sequences)
            tempfiles.append(file)
        else:
            file = pathlib.Path(sequences)
    elif isinstance(sequences, Iterable):
        file = TEMP_DIR / "blast_input.fasta"
        with open(file, "w+") as f:
            for sequence in sequences:
                f.write(sequence + "\n")
        tempfiles.append(file)
    elif isinstance(sequences, pathlib.Path):
        file = sequences
    else:
        raise TypeError(f"Unsupported type {type(sequences)}")
    return file


def _split_input_files(file_path, n_cores, temporary_files):
    """Split the input file into multiple files to enable multiprocessing with blast.

    Attributes
    ----------
    file_path
        Path to the input file
    n_cores: int
        Number of cores (or processes) to be generated
    temporary_files:
        list to keep track of all created files

    Returns
    -------
    files: list(str)
        A list of all the file names
    """
    with open(file_path, "r") as fp:
        file = fp.read().strip().split("\n")
    files = []
    for i in range(n_cores):
        file_name = TEMP_DIR / f"blast_input_{i}.fasta"
        files.append(file_name)
        temporary_files.append(file_name)
        with open(file_name, "w+") as fp:
            fp.write(
                "\n".join(
                    [
                        "\n".join(i)
                        for i in zip(
                            file[0 + 2 * i :: 2 * n_cores],
                            file[1 + 2 * i :: 2 * n_cores],
                        )
                    ]
                )
            )
    return files


def _run_blast_process(query_file_path, database_name):
    """Run blast software (helper function).

    Attributes
    ----------
    query_file_path: str or pathlib.Path
        Path of the query file

    Returns
    -------
    matches: str
        Outputs the matches in a tsv table format as a multiline-string
    """
    out = subprocess.run(
        [
            "tblastn",
            "-db",
            TEMP_DIR / database_name,
            "-query",
            query_file_path,
            "-outfmt",
            "6 qseqid sseqid evalue pident qcovs",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if out.returncode != 0:
        raise ValueError(f"Process failed: {out.stderr.decode('utf-8')}")
    return out.stdout.decode("utf-8")


def _read_blast_results(results):
    """Transform blast csv result to pandas df."""
    results = pd.read_csv(
        io.StringIO(results),
        sep="\t",
        header=None,
        names=["Monomer", "qseqid", "evalue", "pident", "qcovs"],
    )
    # Only keep results with lowest e-value
    results = results.sort_values(by=["Monomer", "evalue"])
    results = results.set_index("Monomer", drop=True)
    results = results[~results.index.duplicated(keep="first")]
    return results


def blast(sequences, genome_file, multiple_cores=True):
    """Blast protein sequences against a genome.

    If multiple matches for a monomer are found, only the one
    with the lowest e-value is returned.

    Attributes
    ----------
    sequences: str, Iterable(str), file_path
        Input protein sequences
    genome_file: file
        Nucleotide fasta file
    multiple_cores: bool
        Whether to utilize multiprocessing. On Windows this is always disabled

    Returns
    -------
    matches: pandas.DataFrame
        The matches sorted by their monomer ID
    """
    temporary_files = []
    genome_file = pathlib.Path(genome_file)

    _generate_blast_database(genome_file=genome_file)
    file_path = _unify_inputs(sequences, temporary_files)
    partial_blast = functools.partial(_run_blast_process, **{"database_name": genome_file.stem})

    if not multiple_cores or sys.platform in ["win32", "cygwin"]:
        results = partial_blast(file_path)
    else:
        n_cores = multiprocessing.cpu_count()
        files = _split_input_files(file_path, n_cores, temporary_files)
        pool = multiprocessing.Pool(n_cores)
        results = "\n".join(pool.map(partial_blast, files))
        pool.close()
    results = _read_blast_results(results=results)

    # Delete temporary files
    for file in temporary_files:
        file.unlink()
    return results


def filter_blast_results(
    blast_monomers,
    max_evalue,
    min_coverage,
    min_pident,
    prefix_remove,
    suffix_remove,
):
    """Filter the blast results to remove matches that do not match the quality criteria.

    Also optionally removes a prefix and suffix (given as regular expressions).

    For explanations for the quality criteria please consult the NCBI blast
    manual.

    Attributes
    ----------
    blast_monomers: pandas.DataFrame
        A dataframe obtained by the blast function,
        which carries the match names as the index
    max_evalue: float
        Upper boundary for accepted Expect value
    min_coverage: float
        Lower boundary for accepted Query Coverage Per Subject
    min_pident: float
        Lower boundary for accepted Percentage of identical matches
    prefix_remove: raw_string
        Regular expression for a prefix to be removed ('^' is added automatically)
    suffix_remove: raw_string
        Regular expression for a suffix to be removed ('$' is added automatically)

    Returns
    -------
    blast_monomers: set(str)
        Set of all monomer ids, that match the criteria
    """
    fltr = (
        (blast_monomers["evalue"] < max_evalue)
        & (blast_monomers["qcovs"] > min_coverage)
        & (blast_monomers["pident"] > min_pident)
    )

    results = blast_monomers[fltr].index
    if prefix_remove is not None:
        results = results.str.replace(f"^{prefix_remove}", "", regex=True)
    if suffix_remove is not None:
        results = results.str.replace(f"{suffix_remove}$", "", regex=True)
    return set(results)
