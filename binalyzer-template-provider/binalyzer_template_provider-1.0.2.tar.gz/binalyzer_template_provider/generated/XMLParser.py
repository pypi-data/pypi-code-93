# Generated from resources/XMLParser.g4 by ANTLR 4.8
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\33")
        buf.write("\u0088\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r\3\2")
        buf.write("\5\2\34\n\2\3\2\7\2\37\n\2\f\2\16\2\"\13\2\3\2\3\2\7\2")
        buf.write("&\n\2\f\2\16\2)\13\2\3\3\3\3\7\3-\n\3\f\3\16\3\60\13\3")
        buf.write("\3\3\3\3\3\4\5\4\65\n\4\3\4\3\4\3\4\3\4\3\4\5\4<\n\4\3")
        buf.write("\4\5\4?\n\4\7\4A\n\4\f\4\16\4D\13\4\3\5\3\5\3\6\3\6\3")
        buf.write("\6\7\6K\n\6\f\6\16\6N\13\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6")
        buf.write("\3\6\3\6\3\6\7\6Z\n\6\f\6\16\6]\13\6\3\6\5\6`\n\6\3\7")
        buf.write("\3\7\3\b\3\b\3\b\3\b\5\bh\n\b\3\t\3\t\3\t\3\t\3\n\3\n")
        buf.write("\3\n\3\n\3\n\3\n\3\13\3\13\3\13\5\13w\n\13\3\13\3\13\3")
        buf.write("\13\3\13\5\13}\n\13\7\13\177\n\13\f\13\16\13\u0082\13")
        buf.write("\13\3\f\3\f\3\r\3\r\3\r\2\2\16\2\4\6\b\n\f\16\20\22\24")
        buf.write("\26\30\2\5\3\2\6\7\4\2\b\b\13\13\5\2\3\3\b\b\33\33\2\u008d")
        buf.write("\2\33\3\2\2\2\4*\3\2\2\2\6\64\3\2\2\2\bE\3\2\2\2\n_\3")
        buf.write("\2\2\2\fa\3\2\2\2\16c\3\2\2\2\20i\3\2\2\2\22m\3\2\2\2")
        buf.write("\24s\3\2\2\2\26\u0083\3\2\2\2\30\u0085\3\2\2\2\32\34\5")
        buf.write("\4\3\2\33\32\3\2\2\2\33\34\3\2\2\2\34 \3\2\2\2\35\37\5")
        buf.write("\30\r\2\36\35\3\2\2\2\37\"\3\2\2\2 \36\3\2\2\2 !\3\2\2")
        buf.write("\2!#\3\2\2\2\" \3\2\2\2#\'\5\n\6\2$&\5\30\r\2%$\3\2\2")
        buf.write("\2&)\3\2\2\2\'%\3\2\2\2\'(\3\2\2\2(\3\3\2\2\2)\'\3\2\2")
        buf.write("\2*.\7\n\2\2+-\5\16\b\2,+\3\2\2\2-\60\3\2\2\2.,\3\2\2")
        buf.write("\2./\3\2\2\2/\61\3\2\2\2\60.\3\2\2\2\61\62\7\r\2\2\62")
        buf.write("\5\3\2\2\2\63\65\5\b\5\2\64\63\3\2\2\2\64\65\3\2\2\2\65")
        buf.write("B\3\2\2\2\66<\5\n\6\2\67<\5\f\7\28<\7\4\2\29<\7\33\2\2")
        buf.write(":<\7\3\2\2;\66\3\2\2\2;\67\3\2\2\2;8\3\2\2\2;9\3\2\2\2")
        buf.write(";:\3\2\2\2<>\3\2\2\2=?\5\26\f\2>=\3\2\2\2>?\3\2\2\2?A")
        buf.write("\3\2\2\2@;\3\2\2\2AD\3\2\2\2B@\3\2\2\2BC\3\2\2\2C\7\3")
        buf.write("\2\2\2DB\3\2\2\2EF\5\26\f\2F\t\3\2\2\2GH\7\t\2\2HL\7\21")
        buf.write("\2\2IK\5\16\b\2JI\3\2\2\2KN\3\2\2\2LJ\3\2\2\2LM\3\2\2")
        buf.write("\2MO\3\2\2\2NL\3\2\2\2OP\7\f\2\2PQ\5\6\4\2QR\7\t\2\2R")
        buf.write("S\7\17\2\2ST\7\21\2\2TU\7\f\2\2U`\3\2\2\2VW\7\t\2\2W[")
        buf.write("\7\21\2\2XZ\5\16\b\2YX\3\2\2\2Z]\3\2\2\2[Y\3\2\2\2[\\")
        buf.write("\3\2\2\2\\^\3\2\2\2][\3\2\2\2^`\7\16\2\2_G\3\2\2\2_V\3")
        buf.write("\2\2\2`\13\3\2\2\2ab\t\2\2\2b\r\3\2\2\2cd\7\21\2\2dg\7")
        buf.write("\20\2\2eh\5\20\t\2fh\5\22\n\2ge\3\2\2\2gf\3\2\2\2h\17")
        buf.write("\3\2\2\2ij\7\23\2\2jk\7\21\2\2kl\7\23\2\2l\21\3\2\2\2")
        buf.write("mn\7\23\2\2no\7\24\2\2op\5\24\13\2pq\7\25\2\2qr\7\23\2")
        buf.write("\2r\23\3\2\2\2sv\7\27\2\2tu\7\31\2\2uw\7\27\2\2vt\3\2")
        buf.write("\2\2vw\3\2\2\2w\u0080\3\2\2\2xy\7\30\2\2y|\7\27\2\2z{")
        buf.write("\7\31\2\2{}\7\27\2\2|z\3\2\2\2|}\3\2\2\2}\177\3\2\2\2")
        buf.write("~x\3\2\2\2\177\u0082\3\2\2\2\u0080~\3\2\2\2\u0080\u0081")
        buf.write("\3\2\2\2\u0081\25\3\2\2\2\u0082\u0080\3\2\2\2\u0083\u0084")
        buf.write("\t\3\2\2\u0084\27\3\2\2\2\u0085\u0086\t\4\2\2\u0086\31")
        buf.write("\3\2\2\2\21\33 \'.\64;>BL[_gv|\u0080")
        return buf.getvalue()


class XMLParser ( Parser ):

    grammarFileName = "XMLParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "'<'", "<INVALID>", 
                     "<INVALID>", "'>'", "<INVALID>", "'/>'", "'/'", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'\"'", "'{'", "'}'", "'.'", 
                     "<INVALID>", "','" ]

    symbolicNames = [ "<INVALID>", "COMMENT", "CDATA", "DTD", "EntityRef", 
                      "CharRef", "SEA_WS", "OPEN", "XMLDeclOpen", "TEXT", 
                      "CLOSE", "SPECIAL_CLOSE", "SLASH_CLOSE", "SLASH", 
                      "EQUALS", "Name", "S", "DOUBLE_QUOTES", "BRACKET_OPEN", 
                      "BRACKET_CLOSE", "BRACKET_DOT", "BRACKET_NAME", "BRACKET_COMMA", 
                      "BRACKET_EQUAL", "BRACKET_WS", "PI" ]

    RULE_document = 0
    RULE_prolog = 1
    RULE_content = 2
    RULE_text = 3
    RULE_element = 4
    RULE_reference = 5
    RULE_attribute = 6
    RULE_value = 7
    RULE_binding = 8
    RULE_sequence = 9
    RULE_chardata = 10
    RULE_misc = 11

    ruleNames =  [ "document", "prolog", "content", "text", "element", "reference", 
                   "attribute", "value", "binding", "sequence", "chardata", 
                   "misc" ]

    EOF = Token.EOF
    COMMENT=1
    CDATA=2
    DTD=3
    EntityRef=4
    CharRef=5
    SEA_WS=6
    OPEN=7
    XMLDeclOpen=8
    TEXT=9
    CLOSE=10
    SPECIAL_CLOSE=11
    SLASH_CLOSE=12
    SLASH=13
    EQUALS=14
    Name=15
    S=16
    DOUBLE_QUOTES=17
    BRACKET_OPEN=18
    BRACKET_CLOSE=19
    BRACKET_DOT=20
    BRACKET_NAME=21
    BRACKET_COMMA=22
    BRACKET_EQUAL=23
    BRACKET_WS=24
    PI=25

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.8")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class DocumentContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def element(self):
            return self.getTypedRuleContext(XMLParser.ElementContext,0)


        def prolog(self):
            return self.getTypedRuleContext(XMLParser.PrologContext,0)


        def misc(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(XMLParser.MiscContext)
            else:
                return self.getTypedRuleContext(XMLParser.MiscContext,i)


        def getRuleIndex(self):
            return XMLParser.RULE_document

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDocument" ):
                listener.enterDocument(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDocument" ):
                listener.exitDocument(self)




    def document(self):

        localctx = XMLParser.DocumentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_document)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 25
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==XMLParser.XMLDeclOpen:
                self.state = 24
                self.prolog()


            self.state = 30
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << XMLParser.COMMENT) | (1 << XMLParser.SEA_WS) | (1 << XMLParser.PI))) != 0):
                self.state = 27
                self.misc()
                self.state = 32
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 33
            self.element()
            self.state = 37
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << XMLParser.COMMENT) | (1 << XMLParser.SEA_WS) | (1 << XMLParser.PI))) != 0):
                self.state = 34
                self.misc()
                self.state = 39
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PrologContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def XMLDeclOpen(self):
            return self.getToken(XMLParser.XMLDeclOpen, 0)

        def SPECIAL_CLOSE(self):
            return self.getToken(XMLParser.SPECIAL_CLOSE, 0)

        def attribute(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(XMLParser.AttributeContext)
            else:
                return self.getTypedRuleContext(XMLParser.AttributeContext,i)


        def getRuleIndex(self):
            return XMLParser.RULE_prolog

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProlog" ):
                listener.enterProlog(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProlog" ):
                listener.exitProlog(self)




    def prolog(self):

        localctx = XMLParser.PrologContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_prolog)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 40
            self.match(XMLParser.XMLDeclOpen)
            self.state = 44
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==XMLParser.Name:
                self.state = 41
                self.attribute()
                self.state = 46
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 47
            self.match(XMLParser.SPECIAL_CLOSE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ContentContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def text(self):
            return self.getTypedRuleContext(XMLParser.TextContext,0)


        def element(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(XMLParser.ElementContext)
            else:
                return self.getTypedRuleContext(XMLParser.ElementContext,i)


        def reference(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(XMLParser.ReferenceContext)
            else:
                return self.getTypedRuleContext(XMLParser.ReferenceContext,i)


        def CDATA(self, i:int=None):
            if i is None:
                return self.getTokens(XMLParser.CDATA)
            else:
                return self.getToken(XMLParser.CDATA, i)

        def PI(self, i:int=None):
            if i is None:
                return self.getTokens(XMLParser.PI)
            else:
                return self.getToken(XMLParser.PI, i)

        def COMMENT(self, i:int=None):
            if i is None:
                return self.getTokens(XMLParser.COMMENT)
            else:
                return self.getToken(XMLParser.COMMENT, i)

        def chardata(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(XMLParser.ChardataContext)
            else:
                return self.getTypedRuleContext(XMLParser.ChardataContext,i)


        def getRuleIndex(self):
            return XMLParser.RULE_content

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterContent" ):
                listener.enterContent(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitContent" ):
                listener.exitContent(self)




    def content(self):

        localctx = XMLParser.ContentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_content)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 50
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==XMLParser.SEA_WS or _la==XMLParser.TEXT:
                self.state = 49
                self.text()


            self.state = 64
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,7,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 57
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [XMLParser.OPEN]:
                        self.state = 52
                        self.element()
                        pass
                    elif token in [XMLParser.EntityRef, XMLParser.CharRef]:
                        self.state = 53
                        self.reference()
                        pass
                    elif token in [XMLParser.CDATA]:
                        self.state = 54
                        self.match(XMLParser.CDATA)
                        pass
                    elif token in [XMLParser.PI]:
                        self.state = 55
                        self.match(XMLParser.PI)
                        pass
                    elif token in [XMLParser.COMMENT]:
                        self.state = 56
                        self.match(XMLParser.COMMENT)
                        pass
                    else:
                        raise NoViableAltException(self)

                    self.state = 60
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if _la==XMLParser.SEA_WS or _la==XMLParser.TEXT:
                        self.state = 59
                        self.chardata()

             
                self.state = 66
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,7,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TextContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def chardata(self):
            return self.getTypedRuleContext(XMLParser.ChardataContext,0)


        def getRuleIndex(self):
            return XMLParser.RULE_text

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterText" ):
                listener.enterText(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitText" ):
                listener.exitText(self)




    def text(self):

        localctx = XMLParser.TextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_text)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 67
            self.chardata()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ElementContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def OPEN(self, i:int=None):
            if i is None:
                return self.getTokens(XMLParser.OPEN)
            else:
                return self.getToken(XMLParser.OPEN, i)

        def Name(self, i:int=None):
            if i is None:
                return self.getTokens(XMLParser.Name)
            else:
                return self.getToken(XMLParser.Name, i)

        def CLOSE(self, i:int=None):
            if i is None:
                return self.getTokens(XMLParser.CLOSE)
            else:
                return self.getToken(XMLParser.CLOSE, i)

        def content(self):
            return self.getTypedRuleContext(XMLParser.ContentContext,0)


        def SLASH(self):
            return self.getToken(XMLParser.SLASH, 0)

        def attribute(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(XMLParser.AttributeContext)
            else:
                return self.getTypedRuleContext(XMLParser.AttributeContext,i)


        def SLASH_CLOSE(self):
            return self.getToken(XMLParser.SLASH_CLOSE, 0)

        def getRuleIndex(self):
            return XMLParser.RULE_element

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterElement" ):
                listener.enterElement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitElement" ):
                listener.exitElement(self)




    def element(self):

        localctx = XMLParser.ElementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_element)
        self._la = 0 # Token type
        try:
            self.state = 93
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,10,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 69
                self.match(XMLParser.OPEN)
                self.state = 70
                self.match(XMLParser.Name)
                self.state = 74
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==XMLParser.Name:
                    self.state = 71
                    self.attribute()
                    self.state = 76
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 77
                self.match(XMLParser.CLOSE)
                self.state = 78
                self.content()
                self.state = 79
                self.match(XMLParser.OPEN)
                self.state = 80
                self.match(XMLParser.SLASH)
                self.state = 81
                self.match(XMLParser.Name)
                self.state = 82
                self.match(XMLParser.CLOSE)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 84
                self.match(XMLParser.OPEN)
                self.state = 85
                self.match(XMLParser.Name)
                self.state = 89
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==XMLParser.Name:
                    self.state = 86
                    self.attribute()
                    self.state = 91
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 92
                self.match(XMLParser.SLASH_CLOSE)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ReferenceContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EntityRef(self):
            return self.getToken(XMLParser.EntityRef, 0)

        def CharRef(self):
            return self.getToken(XMLParser.CharRef, 0)

        def getRuleIndex(self):
            return XMLParser.RULE_reference

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterReference" ):
                listener.enterReference(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitReference" ):
                listener.exitReference(self)




    def reference(self):

        localctx = XMLParser.ReferenceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_reference)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 95
            _la = self._input.LA(1)
            if not(_la==XMLParser.EntityRef or _la==XMLParser.CharRef):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AttributeContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Name(self):
            return self.getToken(XMLParser.Name, 0)

        def EQUALS(self):
            return self.getToken(XMLParser.EQUALS, 0)

        def value(self):
            return self.getTypedRuleContext(XMLParser.ValueContext,0)


        def binding(self):
            return self.getTypedRuleContext(XMLParser.BindingContext,0)


        def getRuleIndex(self):
            return XMLParser.RULE_attribute

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAttribute" ):
                listener.enterAttribute(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAttribute" ):
                listener.exitAttribute(self)




    def attribute(self):

        localctx = XMLParser.AttributeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_attribute)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 97
            self.match(XMLParser.Name)
            self.state = 98
            self.match(XMLParser.EQUALS)
            self.state = 101
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,11,self._ctx)
            if la_ == 1:
                self.state = 99
                self.value()
                pass

            elif la_ == 2:
                self.state = 100
                self.binding()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ValueContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DOUBLE_QUOTES(self, i:int=None):
            if i is None:
                return self.getTokens(XMLParser.DOUBLE_QUOTES)
            else:
                return self.getToken(XMLParser.DOUBLE_QUOTES, i)

        def Name(self):
            return self.getToken(XMLParser.Name, 0)

        def getRuleIndex(self):
            return XMLParser.RULE_value

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValue" ):
                listener.enterValue(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValue" ):
                listener.exitValue(self)




    def value(self):

        localctx = XMLParser.ValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_value)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 103
            self.match(XMLParser.DOUBLE_QUOTES)
            self.state = 104
            self.match(XMLParser.Name)
            self.state = 105
            self.match(XMLParser.DOUBLE_QUOTES)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BindingContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DOUBLE_QUOTES(self, i:int=None):
            if i is None:
                return self.getTokens(XMLParser.DOUBLE_QUOTES)
            else:
                return self.getToken(XMLParser.DOUBLE_QUOTES, i)

        def BRACKET_OPEN(self):
            return self.getToken(XMLParser.BRACKET_OPEN, 0)

        def sequence(self):
            return self.getTypedRuleContext(XMLParser.SequenceContext,0)


        def BRACKET_CLOSE(self):
            return self.getToken(XMLParser.BRACKET_CLOSE, 0)

        def getRuleIndex(self):
            return XMLParser.RULE_binding

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBinding" ):
                listener.enterBinding(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBinding" ):
                listener.exitBinding(self)




    def binding(self):

        localctx = XMLParser.BindingContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_binding)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 107
            self.match(XMLParser.DOUBLE_QUOTES)
            self.state = 108
            self.match(XMLParser.BRACKET_OPEN)
            self.state = 109
            self.sequence()
            self.state = 110
            self.match(XMLParser.BRACKET_CLOSE)
            self.state = 111
            self.match(XMLParser.DOUBLE_QUOTES)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SequenceContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def BRACKET_NAME(self, i:int=None):
            if i is None:
                return self.getTokens(XMLParser.BRACKET_NAME)
            else:
                return self.getToken(XMLParser.BRACKET_NAME, i)

        def BRACKET_EQUAL(self, i:int=None):
            if i is None:
                return self.getTokens(XMLParser.BRACKET_EQUAL)
            else:
                return self.getToken(XMLParser.BRACKET_EQUAL, i)

        def BRACKET_COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(XMLParser.BRACKET_COMMA)
            else:
                return self.getToken(XMLParser.BRACKET_COMMA, i)

        def getRuleIndex(self):
            return XMLParser.RULE_sequence

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSequence" ):
                listener.enterSequence(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSequence" ):
                listener.exitSequence(self)




    def sequence(self):

        localctx = XMLParser.SequenceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_sequence)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 113
            self.match(XMLParser.BRACKET_NAME)
            self.state = 116
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==XMLParser.BRACKET_EQUAL:
                self.state = 114
                self.match(XMLParser.BRACKET_EQUAL)
                self.state = 115
                self.match(XMLParser.BRACKET_NAME)


            self.state = 126
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==XMLParser.BRACKET_COMMA:
                self.state = 118
                self.match(XMLParser.BRACKET_COMMA)
                self.state = 119
                self.match(XMLParser.BRACKET_NAME)
                self.state = 122
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==XMLParser.BRACKET_EQUAL:
                    self.state = 120
                    self.match(XMLParser.BRACKET_EQUAL)
                    self.state = 121
                    self.match(XMLParser.BRACKET_NAME)


                self.state = 128
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ChardataContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TEXT(self):
            return self.getToken(XMLParser.TEXT, 0)

        def SEA_WS(self):
            return self.getToken(XMLParser.SEA_WS, 0)

        def getRuleIndex(self):
            return XMLParser.RULE_chardata

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterChardata" ):
                listener.enterChardata(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitChardata" ):
                listener.exitChardata(self)




    def chardata(self):

        localctx = XMLParser.ChardataContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_chardata)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 129
            _la = self._input.LA(1)
            if not(_la==XMLParser.SEA_WS or _la==XMLParser.TEXT):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MiscContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COMMENT(self):
            return self.getToken(XMLParser.COMMENT, 0)

        def PI(self):
            return self.getToken(XMLParser.PI, 0)

        def SEA_WS(self):
            return self.getToken(XMLParser.SEA_WS, 0)

        def getRuleIndex(self):
            return XMLParser.RULE_misc

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMisc" ):
                listener.enterMisc(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMisc" ):
                listener.exitMisc(self)




    def misc(self):

        localctx = XMLParser.MiscContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_misc)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 131
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << XMLParser.COMMENT) | (1 << XMLParser.SEA_WS) | (1 << XMLParser.PI))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





