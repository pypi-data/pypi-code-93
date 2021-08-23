
from ._common import *

# ***************************************************************************************

# namespace
class _rules:

    # Keywords
    keyword = lex2.Rule(
        "KEYWORD",
        '|'.join([
            "alignas",
            "alignof",
            "and",
            "and_eq",
            "asm",
            "auto",
            "bitand",
            "bitor",
            "bool",
            "break",
            "case",
            "catch",
            "char",
            "char8_t"
            "char18_t"
            "char32_t",
            "class",
            "compl",
            "const",
            "const_cast",
            "constexpr",
            "continue",
            "decltype",
            "default",
            "delete",
            "do",
            "double",
            "dynamic_cast",
            "else",
            "enum",
            "explicit",
            "extern",
            "false",
            "float",
            "for",
            "friend",
            "goto",
            "if",
            "inline",
            "int",
            "long",
            "mutable",
            "namespace",
            "new",
            "noexcept",
            "not",
            "not_eq",
            "nullptr",
            "operator",
            "or",
            "or_eq",
            "private",
            "protected",
            "public",
            "register",
            "reinterpret_cast",
            "return",
            "short",
            "signed",
            "sizeof",
            "static",
            "static_assert",
            "static_cast",
            "struct",
            "switch",
            "template",
            "this",
            "thread_local",
            "throw",
            "true",
            "try",
            "typedef",
            "typeid",
            "typename",
            "union",
            "unsigned",
            "using",
            "virtual",
            "void",
            "volatile",
            "wchar_t",
            "while",
            "xor",
            "xor_eq"
        ])
    )

    # Identifiers
    identifier = lex2.Rule(
        "IDENTIFIER",
        r"[a-zA-Z_][a-zA-Z0-9_]*"
    )

    # Comments
    sl_comment = lex2.predefs.SinglelineComment(r"\/\/")
    ml_comment = lex2.predefs. MultilineComment(r"\/\*", r"\*\/")

    # Float
    float_number = lex2.Rule(
        "FLOAT",
        r"([1-9][0-9]*|0)\.[0-9]+"
    )

    # Integers
    oct_integer = lex2.Rule(
        "OCTAL_INTEGER",
        r"[-]?0[0-7]+"
    )
    hex_integer = lex2.Rule(
        "HEXADECIMAL_INTEGER",
        r"[-]?0[xX][0-9a-fA-F]+"
    )
    bin_integer = lex2.Rule(
        "DECIMAL_INTEGER",
        r"[-]?[0-9]+"
    )
    dec_integer = lex2.Rule(
        "DECIMAL_INTEGER",
        r"[-]?0[bB][01]+"
    )

    # Characters and Strings
    char = lex2.Rule(
        "CHARACTER",
        r"'\\?.'"
    )
    string = lex2.Rule(
        "STRING",
        # r"\"[^\"\\\\]*(\\\\.[^\"\\\\]*)*\""
        r"(\/\/.*|\/\*[\s\S]*?\*\/|(?:u8?|U|L)?'(?:\\(?:['\"?\\abfnrtv]|[0-7]{1,3}|x[0-9a-fA-F]{1,2}|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8})|[^'\\\r\n])+')|(?:u8?|U|L)?\"(?:\\(?:['\"?\\abfnrtv]|[0-7]{1,3}|x[0-9a-fA-F]{1,2}|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8})|[^\"\\\r\n])*\"|(?:u8?|U|L)?R\"([^ ()\\\t\x0B\r\n]*)\([\s\S]*?\)\2"
    )

    # Operators
    operator = lex2.Rule(
        "OPERATOR",
        '|'.join([
            r"::",
            r"\.",
            r"->",
            r"<",
            r">",
            r"=",
            r"\+",
            r"-",
            r"\*",
            r"\/",
            r"\+=",
            r"-=",
            r"\*=",
            r"\/=",
            r"%=",
            r"&",
            r"==",
            r"!=",
            r"&&",
            r"\|\|",
            r"<<=",
            r">>=",
            r"&=",
            r"\|=",
            r"\^=",
            r"\+\+",
            r"--",
            r"\|",
            r"\^",
            r"\!",
            r"%",
            r"<<",
            r">>",
            r"<=",
            r">=",
            r"~",
        ])
    )

    # Punctors
    punctor = lex2.Rule(
        "PUNCTORS",
        '|'.join([
            r"\(",
            r"\)",
            r";",
            r",",
            r"\{",
            r"\}",
            r":",
            r"\[",
            r"\]",
            r"<",
            r">",
            r"\?",
            r"\/",
            r"#",
        ])
    )

    # # Preprocessor Keywords
    preprocessor_macro = lex2.Rule(
        "PREPROCESSOR_MACRO",
        r"(?m)#(?:.*\\\r?\n)*.*"
    )


    RULESET = [
        sl_comment,
        ml_comment,
        operator,
        keyword,
        preprocessor_macro,
        float_number,
        hex_integer,
        bin_integer,
        oct_integer,
        dec_integer,
        punctor,
        identifier,
        char,
        string,
    ]


class Test_CppTokenization (unittest.TestCase):

  # --- UNIT TESTS --- #

    def test_CppTokenization_01(self):

        self.options = lex2.opts.LexerOptions()
        self.options.idReturns[lex2.predefs.comment.id] = True
        # self.options.idReturns[_rules.operator.id] = True
        # self.options.idReturns[_rules.punctor.id] = True
        # self.options.idReturns[_rules.string.id] = True

        # Setup
        lexer = lex2.MakeLexer(
            ruleset=_rules.RULESET,
            options=self.options
        )
        lexer.Open(
            # DIR_OF(__file__) / "data/json_single.hpp",
            r"D:\Programming\C-CPP\CppUtils\audio\old2\AudioBuffer.hpp",
            encoding="UTF-8",
            bufferSize=256
            # convertLineEndings=True
        )

        lexer = lex2.lexer.ProfilerLexer(lexer=lexer)

        # Token matching tests
        token: lex2.Token

        while(1):

            try: token = lexer.GetNextToken()
            except lex2.excs.EndOfData:
                break

            # info = [
            #     token.id,
            #     token.data,
            #     "ln: {}".format(token.position.ln +1),
            #     "col: {}".format(token.position.col+1),
            # ]
            # print("{: <20} {: <20} {: <10} {: <10}".format(*info))

        lexer.ShowReport()



        return
