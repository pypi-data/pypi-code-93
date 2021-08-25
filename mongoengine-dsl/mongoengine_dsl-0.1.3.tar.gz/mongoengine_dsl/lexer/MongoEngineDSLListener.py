# Generated from mongoengine_dsl/lexer/MongoEngineDSL.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .MongoEngineDSLParser import MongoEngineDSLParser
else:
    from MongoEngineDSLParser import MongoEngineDSLParser

# This class defines a complete listener for a parse tree produced by MongoEngineDSLParser.
class MongoEngineDSLListener(ParseTreeListener):

    # Enter a parse tree produced by MongoEngineDSLParser#process.
    def enterProcess(self, ctx:MongoEngineDSLParser.ProcessContext):
        pass

    # Exit a parse tree produced by MongoEngineDSLParser#process.
    def exitProcess(self, ctx:MongoEngineDSLParser.ProcessContext):
        pass


    # Enter a parse tree produced by MongoEngineDSLParser#BracketExpression.
    def enterBracketExpression(self, ctx:MongoEngineDSLParser.BracketExpressionContext):
        pass

    # Exit a parse tree produced by MongoEngineDSLParser#BracketExpression.
    def exitBracketExpression(self, ctx:MongoEngineDSLParser.BracketExpressionContext):
        pass


    # Enter a parse tree produced by MongoEngineDSLParser#AndExpression.
    def enterAndExpression(self, ctx:MongoEngineDSLParser.AndExpressionContext):
        pass

    # Exit a parse tree produced by MongoEngineDSLParser#AndExpression.
    def exitAndExpression(self, ctx:MongoEngineDSLParser.AndExpressionContext):
        pass


    # Enter a parse tree produced by MongoEngineDSLParser#FilterExpression.
    def enterFilterExpression(self, ctx:MongoEngineDSLParser.FilterExpressionContext):
        pass

    # Exit a parse tree produced by MongoEngineDSLParser#FilterExpression.
    def exitFilterExpression(self, ctx:MongoEngineDSLParser.FilterExpressionContext):
        pass


    # Enter a parse tree produced by MongoEngineDSLParser#OrExpression.
    def enterOrExpression(self, ctx:MongoEngineDSLParser.OrExpressionContext):
        pass

    # Exit a parse tree produced by MongoEngineDSLParser#OrExpression.
    def exitOrExpression(self, ctx:MongoEngineDSLParser.OrExpressionContext):
        pass


    # Enter a parse tree produced by MongoEngineDSLParser#filterexpr.
    def enterFilterexpr(self, ctx:MongoEngineDSLParser.FilterexprContext):
        pass

    # Exit a parse tree produced by MongoEngineDSLParser#filterexpr.
    def exitFilterexpr(self, ctx:MongoEngineDSLParser.FilterexprContext):
        pass


    # Enter a parse tree produced by MongoEngineDSLParser#field.
    def enterField(self, ctx:MongoEngineDSLParser.FieldContext):
        pass

    # Exit a parse tree produced by MongoEngineDSLParser#field.
    def exitField(self, ctx:MongoEngineDSLParser.FieldContext):
        pass


    # Enter a parse tree produced by MongoEngineDSLParser#operator.
    def enterOperator(self, ctx:MongoEngineDSLParser.OperatorContext):
        pass

    # Exit a parse tree produced by MongoEngineDSLParser#operator.
    def exitOperator(self, ctx:MongoEngineDSLParser.OperatorContext):
        pass


    # Enter a parse tree produced by MongoEngineDSLParser#BooleanValue.
    def enterBooleanValue(self, ctx:MongoEngineDSLParser.BooleanValueContext):
        pass

    # Exit a parse tree produced by MongoEngineDSLParser#BooleanValue.
    def exitBooleanValue(self, ctx:MongoEngineDSLParser.BooleanValueContext):
        pass


    # Enter a parse tree produced by MongoEngineDSLParser#IntegerValue.
    def enterIntegerValue(self, ctx:MongoEngineDSLParser.IntegerValueContext):
        pass

    # Exit a parse tree produced by MongoEngineDSLParser#IntegerValue.
    def exitIntegerValue(self, ctx:MongoEngineDSLParser.IntegerValueContext):
        pass


    # Enter a parse tree produced by MongoEngineDSLParser#DoubleValue.
    def enterDoubleValue(self, ctx:MongoEngineDSLParser.DoubleValueContext):
        pass

    # Exit a parse tree produced by MongoEngineDSLParser#DoubleValue.
    def exitDoubleValue(self, ctx:MongoEngineDSLParser.DoubleValueContext):
        pass


    # Enter a parse tree produced by MongoEngineDSLParser#QuoteStringValue.
    def enterQuoteStringValue(self, ctx:MongoEngineDSLParser.QuoteStringValueContext):
        pass

    # Exit a parse tree produced by MongoEngineDSLParser#QuoteStringValue.
    def exitQuoteStringValue(self, ctx:MongoEngineDSLParser.QuoteStringValueContext):
        pass


    # Enter a parse tree produced by MongoEngineDSLParser#WildcardValue.
    def enterWildcardValue(self, ctx:MongoEngineDSLParser.WildcardValueContext):
        pass

    # Exit a parse tree produced by MongoEngineDSLParser#WildcardValue.
    def exitWildcardValue(self, ctx:MongoEngineDSLParser.WildcardValueContext):
        pass


    # Enter a parse tree produced by MongoEngineDSLParser#DeniedValue.
    def enterDeniedValue(self, ctx:MongoEngineDSLParser.DeniedValueContext):
        pass

    # Exit a parse tree produced by MongoEngineDSLParser#DeniedValue.
    def exitDeniedValue(self, ctx:MongoEngineDSLParser.DeniedValueContext):
        pass


    # Enter a parse tree produced by MongoEngineDSLParser#TokenValue.
    def enterTokenValue(self, ctx:MongoEngineDSLParser.TokenValueContext):
        pass

    # Exit a parse tree produced by MongoEngineDSLParser#TokenValue.
    def exitTokenValue(self, ctx:MongoEngineDSLParser.TokenValueContext):
        pass


    # Enter a parse tree produced by MongoEngineDSLParser#ArrayValue.
    def enterArrayValue(self, ctx:MongoEngineDSLParser.ArrayValueContext):
        pass

    # Exit a parse tree produced by MongoEngineDSLParser#ArrayValue.
    def exitArrayValue(self, ctx:MongoEngineDSLParser.ArrayValueContext):
        pass



del MongoEngineDSLParser