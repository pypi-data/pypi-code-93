from pathlib import Path
from enum import Enum
from .html_page_util import HtmlDoc
from ...scan.io import mmd
from sys import stderr

__all__ = ["QADocSink", "DocSink"]

class BaseDocSink:
    def __init__(self, date, src_dir, src_file, verbose=True):
        self._verbose = verbose
        self.date = date
        self.src_file = src_file
        self.src_filepath = (src_dir / src_file).resolve()

    qa_pair = False
    nest_qa_pair_as_summary = False

    @property
    def target(self):
        return Path(self.src_file).stem # i.e. strip .mmd file extension

    def emit(self, target_dir):
        self.transform()
        # dumb approach, but do it for now
        date_subpath = Path(*self.date)
        emit_dir = target_dir / date_subpath
        if not emit_dir.exists():
            emit_dir.mkdir(parents=True)
        emit_path = emit_dir / self.target
        if self._verbose:
            print(f"Emitting --> {emit_path}", file=stderr)
        with open(emit_path, "w") as f:
            f.write(self.output)
        return emit_path

    def transform(self):
        src = mmd(self.src_filepath)
        listparseconfig={"listclass": "auto", "strict_list_breaks": False}
        src = mmd(self.src_filepath, listparseconfig)
        file_depth = 4 # len(["wire", "yy", "mm", "dd"])
        self.html_doc = HtmlDoc(
            src,
            depth_from_root=file_depth,
            qa_pair=self.qa_pair,
            nested_qa_summary=self.nest_qa_pair_as_summary,
        )
        self.transform_hook()
        self.output = self.html_doc.as_str()

    def transform_hook(self):
        """
        Extensible hook for subclasses to intervene in `transform`.
        """
        pass

class QADocSink(BaseDocSink):
    """
    Shallow subclass of BaseDocSink but pairing up Q&A
    """
    qa_pair = True

class RadioTranscriptDocSink(BaseDocSink):
    """
    Unchanged from BaseDocSink but will probably modify to suit radio.
    """
    pass


class RadioTranscriptSummariesDocSink(RadioTranscriptDocSink):
    """
    Summary version of `RadioTranscriptDocSink`, Q&A pairs are transformed
    to become summary and details elements.
    """
    qa_pair = True
    nest_qa_pair_as_summary = True # Q & A will become summary & details
    #def transform_hook(self):
    #    # Manually surround pairs of nodes as summary/details
    #    qa_pair_idx_dict = {}
    #    for i, b in enumerate(self.html_doc.doc.blocks):
    #        qa_pair_idx_block_dict = {}
    #        for j, n in enumerate(b.nodes):
    #            if hasattr(n, "paired_to"):
    #                aired_bl_no, paired_line_no = n.paired_to
    #                qa_pair_idx_block_dict[j] = paired_line_no
    #        qa_pair_idx_dict[i] = qa_pair_idx_block_dict
    #    #print(qa_pair_idx_dict)


class DocSink(Enum):
    qa = QADocSink
    speech = QADocSink # TODO: change
    slides = QADocSink # TODO: change
    roundtable = QADocSink # TODO: change
    radio_transcript = RadioTranscriptDocSink
    radio_transcript_summaries = RadioTranscriptSummariesDocSink
