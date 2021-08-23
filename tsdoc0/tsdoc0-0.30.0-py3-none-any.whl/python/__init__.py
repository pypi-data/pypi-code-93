from os.path import dirname, join
from textx import language, metamodel_from_file
from textx.metamodel import TextXMetaModel
from tsdoc0.python.activity_header import ActivityHeader
from tsdoc0.python.activity_part import ActivityPart
from tsdoc0.python.answer_abstract import AnswerAbstract
from tsdoc0.python.answer_shape import AnswerShape
from tsdoc0.python.code_refactorable import CodeRefactorable
from tsdoc0.python.code_static import CodeStatic
from tsdoc0.python.comment_abstract import CommentAbstract
from tsdoc0.python.comment_concrete import CommentConcrete
from tsdoc0.python.comment_paragraph import CommentParagraph
from tsdoc0.python.comment_run_your_code import CommentRunYourCode
from tsdoc0.python.comment_section import CommentSection
from tsdoc0.python.comment_sentence import CommentSentence
from tsdoc0.python.comment_turn_in_your_code import CommentTurnInYourCode
from tsdoc0.python.error_type import ErrorType  # noqa :F401
from tsdoc0.python.keywords import Keywords
from tsdoc0.python.model import Model
from tsdoc0.python.solution_code import SolutionCode
from tsdoc0.python.line_blank import LineBlank
from tsdoc0.python.point_tricky import PointTricky
from tsdoc0.python.question_abstract import QuestionAbstract
from tsdoc0.python.question_review import QuestionReview
from tsdoc0.python.question_shape import QuestionShape
from tsdoc0.python.question_structure import QuestionStructure
from tsdoc0.python.question_structure_no import QuestionStructureNo
from tsdoc0.python.segment import Segment  # noqa :F401
from tsdoc0.python.solution_item import SolutionItem
from tsdoc0.python.solution_pseudocode import SolutionPseudocode
from tsdoc0.python.solution_shape import SolutionShape
from tsdoc0.python.vocabulary_term import VocabularyTerm
from tsdoc0.python.vocabulary import Vocabulary
from tsdoc0 import __version__

filename_ext = f".tsdoc{__version__.split('.')[0]}.py"

metamodel: TextXMetaModel = metamodel_from_file(
    join(dirname(__file__), "grammar.tx"),
    classes=[
        ActivityHeader,
        ActivityPart,
        AnswerAbstract,
        AnswerShape,
        CodeRefactorable,
        CodeStatic,
        CommentAbstract,
        CommentConcrete,
        CommentParagraph,
        CommentRunYourCode,
        CommentSection,
        CommentSentence,
        CommentTurnInYourCode,
        Keywords,
        Model,
        SolutionCode,
        LineBlank,
        PointTricky,
        QuestionAbstract,
        QuestionReview,
        QuestionShape,
        QuestionStructure,
        QuestionStructureNo,
        SolutionItem,
        SolutionPseudocode,
        SolutionShape,
        VocabularyTerm,
        Vocabulary,
    ],
    use_regexp_group=True,
)

metamodel.register_obj_processors(
    {
        "QuestionAbstract": QuestionAbstract.process_optional_answer,
        "QuestionShape": QuestionShape.process_optional_answer,
    }
)


@language("TSDoc Python", f"*{filename_ext}")
def register() -> TextXMetaModel:
    "An embedded comment language for TechSmart Python files."
    return metamodel
