import pathlib
import unittest
from tempfile import TemporaryDirectory
from textwrap import wrap

from moped import Model, Reaction
from moped.topological.blast import (
    _generate_blast_database,
    _read_blast_results,
    _run_blast_process,
    _split_input_files,
    _unify_inputs,
    blast,
    filter_blast_results,
)
from moped.utils import get_temporary_directory

import pandas as pd


def write_fasta(filename, headers, sequences):
    with open(f"{filename}.fasta", "w+") as f:
        for header, sequence in zip(headers, sequences):
            f.write(">" + header + "\n")
            for i in wrap(sequence, width=70):
                f.write(i + "\n")


def create_test_db(directory, sequences):
    # This table incomplete, but that doesn't matter for the
    # tests
    table = {
        "I": "ATT",
        "M": "ATG",
        "T": "ACT",
        "N": "AAT",
        "K": "AAG",
        "S": "TCT",
        "R": "CGT",
        "L": "TTG",
        "P": "CCT",
        "H": "CAT",
        "Q": "CAG",
        "V": "GTT",
        "A": "GCT",
        "D": "GAT",
        "E": "GAG",
        "G": "GGT",
        "F": "TTT",
        "Y": "TAT",
        "C": "TGT",
        "W": "TGG",
    }
    # Those are meaningless, just randomly created

    genome = ""
    for sequence in sequences.values():
        genome += "".join([table[i] for i in sequence])
    write_fasta(directory / "testgenome", ["ORGANISM"], [genome])
    return directory / "testgenome.fasta"


def clean_directory(directory):
    for i in directory.iterdir():
        i.unlink()


def create_toy_model(reactions):
    m = Model()
    m.add_reactions(reactions=reactions)
    return m.copy()


SEQUENCES = {
    "MONOMER-1": "FWSMKYRLADFSIEELHAYNLKSAAYLINA",
    "MONOMER-2": "VYLFINYSTECCEWDVSCWPWHNYSACSTG",
}

REACTIONS = (
    Reaction(
        id="RXN1",
        sequences={"MONOMER-1": SEQUENCES["MONOMER-1"]},
        monomers={"ENZRXN-1": {"MONOMER-1"}},
    ),
    Reaction(
        id="RXN2",
        sequences={
            "MONOMER-1": SEQUENCES["MONOMER-1"],
            "MONOMER-2": SEQUENCES["MONOMER-2"],
        },
        monomers={"ENZRXN-1": {"MONOMER-1", "MONOMER-2"}},
    ),
    Reaction(
        id="RXN3",
        sequences={
            "MONOMER-1": SEQUENCES["MONOMER-1"],
            "MONOMER-2": SEQUENCES["MONOMER-2"],
            "MONOMER-3": "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMM",
        },
        monomers={"ENZRXN-1": {"MONOMER-1", "MONOMER-2", "MONOMER-3"}},
    ),
)

TEST_DIR = get_temporary_directory(subdirectory="tests")
BLAST_DIR = get_temporary_directory(subdirectory="blast")
GENOME_FILE = create_test_db(directory=TEST_DIR, sequences=SEQUENCES)


class BlastIsolationTests(unittest.TestCase):
    def test_generate_blast_database(self):
        _generate_blast_database(genome_file=GENOME_FILE)
        files = set([i.name for i in BLAST_DIR.iterdir()])
        expected_files = {
            "testgenome.ntf",
            "testgenome.nin",
            "testgenome.nhr",
            "testgenome.not",
            "testgenome.nos",
            "testgenome.nsq",
            "testgenome.nto",
            "testgenome.nog",
            "testgenome.ndb",
        }
        self.assertEqual(files, expected_files)
        clean_directory(directory=BLAST_DIR)

    def test_unify_inputs_str(self):
        sequences = "".join([f">{k}\n{v}\n" for k, v in SEQUENCES.items()])
        file = _unify_inputs(sequences=sequences, tempfiles=[])

        self.assertEqual(file, get_temporary_directory(subdirectory="blast") / "blast_input.fasta")
        with open(file, "r") as f:
            self.assertEquals(
                f.readlines(),
                [
                    ">MONOMER-1\n",
                    "FWSMKYRLADFSIEELHAYNLKSAAYLINA\n",
                    ">MONOMER-2\n",
                    "VYLFINYSTECCEWDVSCWPWHNYSACSTG\n",
                ],
            )
        clean_directory(directory=BLAST_DIR)

    def test_unify_inputs_iterable(self):
        sequences = [f">{k}\n{v}" for k, v in SEQUENCES.items()]
        file = _unify_inputs(sequences=sequences, tempfiles=[])

        self.assertEqual(file, get_temporary_directory(subdirectory="blast") / "blast_input.fasta")

        with open(file, "r") as f:
            self.assertEquals(
                f.readlines(),
                [
                    ">MONOMER-1\n",
                    "FWSMKYRLADFSIEELHAYNLKSAAYLINA\n",
                    ">MONOMER-2\n",
                    "VYLFINYSTECCEWDVSCWPWHNYSACSTG\n",
                ],
            )
        clean_directory(directory=BLAST_DIR)

    def test_split_input_files_same_number(self):
        content = [
            ">MONOMER-1\n",
            "111111\n",
            ">MONOMER-2\n",
            "222222\n",
            ">MONOMER-3\n",
            "333333\n",
            ">MONOMER-4\n",
            "444444\n",
        ]
        with TemporaryDirectory() as tmp_dir:
            tmp_dir = pathlib.Path(tmp_dir)
            file = tmp_dir / "test.fasta"

            with open(file, "w+") as f:
                f.writelines(content)
            _split_input_files(file_path=file, n_cores=4, temporary_files=[])
            files = sorted(i for i in BLAST_DIR.iterdir())
            self.assertEqual(
                [i.name for i in files],
                [
                    "blast_input_0.fasta",
                    "blast_input_1.fasta",
                    "blast_input_2.fasta",
                    "blast_input_3.fasta",
                ],
            )
            file_contents = []
            for file in files:
                with open(file, "r") as f:
                    file_contents.append(f.readlines())
                    file.unlink()
            self.assertEqual(
                file_contents,
                [
                    [">MONOMER-1\n", "111111"],
                    [">MONOMER-2\n", "222222"],
                    [">MONOMER-3\n", "333333"],
                    [">MONOMER-4\n", "444444"],
                ],
            )
        clean_directory(directory=BLAST_DIR)

    def test_split_input_files_different_number(self):
        content = [
            ">MONOMER-1\n",
            "111111\n",
            ">MONOMER-2\n",
            "222222\n",
            ">MONOMER-3\n",
            "333333\n",
            ">MONOMER-4\n",
            "444444\n",
        ]
        with TemporaryDirectory() as tmp_dir:
            tmp_dir = pathlib.Path(tmp_dir)
            file = tmp_dir / "test.fasta"

            with open(file, "w+") as f:
                f.writelines(content)
            _split_input_files(file_path=file, n_cores=2, temporary_files=[])
            files = sorted(i for i in BLAST_DIR.iterdir())
            self.assertEqual(
                [i.name for i in files],
                ["blast_input_0.fasta", "blast_input_1.fasta"],
            )
            file_contents = []
            for file in files:
                with open(file, "r") as f:
                    file_contents.append(f.readlines())
                    file.unlink()
            self.assertEqual(
                file_contents,
                [
                    [">MONOMER-1\n", "111111\n", ">MONOMER-3\n", "333333"],
                    [">MONOMER-2\n", "222222\n", ">MONOMER-4\n", "444444"],
                ],
            )
        clean_directory(directory=BLAST_DIR)

    def test_unify_inputs_pathlib_file(self):
        content = [
            ">MONOMER-1\n",
            "FWSMKYRLADFSIEELHAYNLKSAAYLINA\n",
            ">MONOMER-2\n",
            "VYLFINYSTECCEWDVSCWPWHNYSACSTG\n",
        ]
        with TemporaryDirectory() as temp_dir:
            temp_dir = pathlib.Path(temp_dir)
            with open(temp_dir / "test.fasta", "w+") as f:
                for i in content:
                    f.write(i)

            file = _unify_inputs(sequences=temp_dir / "test.fasta", tempfiles=[])
            self.assertEqual(file, temp_dir / "test.fasta")
            with open(file, "r") as f:
                self.assertEqual(
                    f.readlines(),
                    [
                        ">MONOMER-1\n",
                        "FWSMKYRLADFSIEELHAYNLKSAAYLINA\n",
                        ">MONOMER-2\n",
                        "VYLFINYSTECCEWDVSCWPWHNYSACSTG\n",
                    ],
                )

    def test_unify_inputs_file(self):
        content = [
            ">MONOMER-1\n",
            "FWSMKYRLADFSIEELHAYNLKSAAYLINA\n",
            ">MONOMER-2\n",
            "VYLFINYSTECCEWDVSCWPWHNYSACSTG\n",
        ]
        with TemporaryDirectory() as temp_dir:
            temp_dir = pathlib.Path(temp_dir)
            with open(temp_dir / "test.fasta", "w+") as f:
                for i in content:
                    f.write(i)

            file = _unify_inputs(sequences=str(temp_dir / "test.fasta"), tempfiles=[])
            self.assertEqual(file, temp_dir / "test.fasta")
            with open(file, "r") as f:
                self.assertEqual(
                    f.readlines(),
                    [
                        ">MONOMER-1\n",
                        "FWSMKYRLADFSIEELHAYNLKSAAYLINA\n",
                        ">MONOMER-2\n",
                        "VYLFINYSTECCEWDVSCWPWHNYSACSTG\n",
                    ],
                )

    def test_unify_inputs_fail_on_unsupported_type(self):
        with self.assertRaises(TypeError):
            _unify_inputs(1, [])

    def test_run_blast_process(self):
        _generate_blast_database(genome_file=GENOME_FILE)
        sequences = [f">{k}\n{v}" for k, v in SEQUENCES.items()]
        file = _unify_inputs(sequences=sequences, tempfiles=[])

        results = _run_blast_process(query_file_path=file, database_name=GENOME_FILE.stem)
        df = _read_blast_results(results)
        self.assertEqual(list(df.index), ["MONOMER-1", "MONOMER-2"])
        self.assertEqual(list(df.columns), ["qseqid", "evalue", "pident", "qcovs"])
        clean_directory(directory=BLAST_DIR)

    def test_run_blast_process_fail_on_wrong_name(self):
        _generate_blast_database(genome_file=GENOME_FILE)
        sequences = [f">{k}\n{v}" for k, v in SEQUENCES.items()]
        file = _unify_inputs(sequences=sequences, tempfiles=[])
        with self.assertRaises(ValueError):
            _run_blast_process(query_file_path=file, database_name="WRONG_NAME")
        clean_directory(directory=BLAST_DIR)

    def test_blast(self):
        sequences = [f">{k}\n{v}" for k, v in SEQUENCES.items()]
        # multiprocessing
        df = blast(sequences=sequences, genome_file=GENOME_FILE, multiple_cores=True)
        self.assertEqual(list(df.index), ["MONOMER-1", "MONOMER-2"])
        self.assertEqual(list(df.columns), ["qseqid", "evalue", "pident", "qcovs"])
        clean_directory(directory=BLAST_DIR)

        # No multiprocessing
        df = blast(sequences=sequences, genome_file=GENOME_FILE, multiple_cores=False)
        self.assertEqual(list(df.index), ["MONOMER-1", "MONOMER-2"])
        self.assertEqual(list(df.columns), ["qseqid", "evalue", "pident", "qcovs"])
        clean_directory(directory=BLAST_DIR)

    def test_filter_blast_results(self):
        df = pd.DataFrame(
            {
                "qseqid": {"MONOMER-1": "ORGANISM", "MONOMER-2": "ORGANISM"},
                "evalue": {"MONOMER-1": 1e-20, "MONOMER-2": 1e-4},
                "pident": {"MONOMER-1": 100, "MONOMER-2": 50},
                "qcovs": {"MONOMER-1": 100, "MONOMER-2": 50},
            }
        )
        self.assertEqual(
            filter_blast_results(
                blast_monomers=df,
                max_evalue=1,
                min_coverage=0,
                min_pident=0,
                prefix_remove=None,
                suffix_remove=None,
            ),
            {"MONOMER-1", "MONOMER-2"},
        )

        self.assertEqual(
            filter_blast_results(
                blast_monomers=df,
                max_evalue=1,
                min_coverage=51,
                min_pident=0,
                prefix_remove=None,
                suffix_remove=None,
            ),
            {"MONOMER-1"},
        )

        self.assertEqual(
            filter_blast_results(
                blast_monomers=df,
                max_evalue=1,
                min_coverage=0,
                min_pident=51,
                prefix_remove=None,
                suffix_remove=None,
            ),
            {"MONOMER-1"},
        )

    def test_filter_blast_results_prefix_suffix(self):
        df = pd.DataFrame(
            {
                "qseqid": {
                    "|PREFIX|MONOMER-1|SUFFIX|": "ORGANISM",
                    "|PREFIX|MONOMER-2|SUFFIX|": "ORGANISM",
                },
                "evalue": {
                    "|PREFIX|MONOMER-1|SUFFIX|": 1e-20,
                    "|PREFIX|MONOMER-2|SUFFIX|": 1e-4,
                },
                "pident": {
                    "|PREFIX|MONOMER-1|SUFFIX|": 100,
                    "|PREFIX|MONOMER-2|SUFFIX|": 50,
                },
                "qcovs": {
                    "|PREFIX|MONOMER-1|SUFFIX|": 100,
                    "|PREFIX|MONOMER-2|SUFFIX|": 50,
                },
            }
        )

        self.assertEqual(
            filter_blast_results(
                blast_monomers=df,
                max_evalue=1,
                min_coverage=0,
                min_pident=0,
                prefix_remove=r"\|PREFIX\|",
                suffix_remove=r"\|SUFFIX\|",
            ),
            {"MONOMER-1", "MONOMER-2"},
        )


class BlastModelTests(unittest.TestCase):
    def test_get_monomer_sequences(self):
        m = create_toy_model(reactions=REACTIONS)
        seqs = m.get_monomer_sequences(reaction_ids=["RXN1", "RXN2", "RXN3"])
        expected = {
            ">gnl|META|MONOMER-1\nFWSMKYRLADFSIEELHAYNLKSAAYLINA",
            ">gnl|META|MONOMER-2\nVYLFINYSTECCEWDVSCWPWHNYSACSTG",
            ">gnl|META|MONOMER-3\nMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM",
        }
        self.assertEqual(seqs, expected)
        clean_directory(directory=BLAST_DIR)

    def test_get_all_monomer_sequences(self):
        m = create_toy_model(reactions=REACTIONS)
        seqs = m.get_all_monomer_sequences()
        expected = {
            ">gnl|META|MONOMER-1\nFWSMKYRLADFSIEELHAYNLKSAAYLINA",
            ">gnl|META|MONOMER-2\nVYLFINYSTECCEWDVSCWPWHNYSACSTG",
            ">gnl|META|MONOMER-3\nMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM",
        }
        self.assertEqual(seqs, expected)
        clean_directory(directory=BLAST_DIR)

    def test_blast_sequences(self):
        m = create_toy_model(reactions=REACTIONS)
        df = m.blast_sequences(
            sequences=m.get_monomer_sequences(reaction_ids=["RXN1"]),
            genome_file=GENOME_FILE,
        )
        self.assertEqual(list(df.columns), ["qseqid", "evalue", "pident", "qcovs"])
        self.assertEqual(list(df.index), ["gnl|META|MONOMER-1"])
        clean_directory(directory=BLAST_DIR)

    def test_blast_sequences_fail_on_missing_genome(self):
        m = create_toy_model(reactions=REACTIONS)
        with self.assertRaises(FileNotFoundError):
            m.blast_sequences(
                sequences=m.get_monomer_sequences(reaction_ids=["RXN1"]),
                genome_file="garbage",
            )

    def test_blast_reactions(self):
        m = create_toy_model(reactions=REACTIONS)
        df = m.blast_reactions(reaction_ids=["RXN1"], genome_file=GENOME_FILE)
        self.assertEqual(list(df.columns), ["qseqid", "evalue", "pident", "qcovs"])
        self.assertEqual(list(df.index), ["gnl|META|MONOMER-1"])
        clean_directory(directory=BLAST_DIR)

    def test_blast_all_reactions(self):
        m = create_toy_model(reactions=REACTIONS)
        df = m.blast_all_reactions(genome_file=GENOME_FILE)
        self.assertEqual(list(df.columns), ["qseqid", "evalue", "pident", "qcovs"])
        self.assertEqual(set(df.index), {"gnl|META|MONOMER-1", "gnl|META|MONOMER-2"})
        clean_directory(directory=BLAST_DIR)

    def test_get_reactions_from_blast_result(self):
        m = create_toy_model(reactions=REACTIONS)
        df = m.blast_all_reactions(genome_file=GENOME_FILE)
        filtered_blast_results = filter_blast_results(
            blast_monomers=df,
            max_evalue=1e-6,
            min_coverage=85,
            min_pident=85,
            prefix_remove=r"gnl\|.*?\|",
            suffix_remove=None,
        )
        self.assertEqual(
            m._get_reactions_from_blast_results(
                filtered_blast_monomers=filtered_blast_results,
                require_all_complex_monomers=True,
            ),
            {"RXN1", "RXN2"},
        )
        self.assertEqual(
            m._get_reactions_from_blast_results(
                filtered_blast_monomers=filtered_blast_results,
                require_all_complex_monomers=False,
            ),
            {"RXN1", "RXN2", "RXN3"},
        )
        clean_directory(directory=BLAST_DIR)

    def test_create_submodel_from_blast_monomers(self):
        m = create_toy_model(reactions=REACTIONS)
        df = m.blast_all_reactions(genome_file=GENOME_FILE)
        sm1 = m.create_submodel_from_blast_monomers(blast_monomers=df, require_all_complex_monomers=True)
        sm2 = m.create_submodel_from_blast_monomers(blast_monomers=df, require_all_complex_monomers=False)
        self.assertEqual(sorted(sm1.reactions), ["RXN1", "RXN2"])
        self.assertEqual(sorted(sm2.reactions), ["RXN1", "RXN2", "RXN3"])
        clean_directory(directory=BLAST_DIR)

    def test_create_submodel_from_sequences(self):
        m = create_toy_model(reactions=REACTIONS)
        sequences = sorted(m.get_all_monomer_sequences())

        sm1 = m.create_submodel_from_sequences(
            sequences=sequences,
            genome_file=GENOME_FILE,
            name="results",
            cache_blast_results=True,
            require_all_complex_monomers=True,
        )
        sm2 = m.create_submodel_from_sequences(
            sequences=sequences,
            genome_file=GENOME_FILE,
            name="results",
            cache_blast_results=True,
            require_all_complex_monomers=False,
        )
        self.assertEqual(list(sm1.reactions), ["RXN1", "RXN2"])
        self.assertEqual(list(sm2.reactions), ["RXN1", "RXN2", "RXN3"])
        clean_directory(directory=BLAST_DIR)

    def test_create_submodel_from_sequences_fail_on_missing_cache(self):
        m = create_toy_model(reactions=REACTIONS)
        sequences = sorted(m.get_all_monomer_sequences())

        with self.assertRaises(ValueError):
            m.create_submodel_from_sequences(
                sequences=sequences,
                genome_file=GENOME_FILE,
                name=None,
                cache_blast_results=True,
            )

    def test_create_submodel_from_genome(self):
        m = create_toy_model(reactions=REACTIONS)
        sm = m.create_submodel_from_genome(genome_file=GENOME_FILE, require_all_complex_monomers=True)
        self.assertEqual(list(sm.reactions), ["RXN1", "RXN2"])

        sm = m.create_submodel_from_genome(genome_file=GENOME_FILE, require_all_complex_monomers=False)
        self.assertEqual(list(sm.reactions), ["RXN1", "RXN2", "RXN3"])
        clean_directory(directory=BLAST_DIR)
