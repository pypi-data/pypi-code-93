# coding: utf-8

###############################################################
#
#   STANDARD IMPORTS
#

import enum


###############################################################
#
#   REFINITIV IMPORTS
#

###############################################################
#
#   LOCAL IMPORTS
#

###############################################################
#
#   CLASSES
#


@enum.unique
class SearchViews(enum.Enum):
    """ define all possible views """

    BondFutOptQuotes = "BondFutOptQuotes"
    CdsInstruments = "CdsInstruments"
    CdsQuotes = "CdsQuotes"
    CmoInstruments = "CmoInstruments"
    CmoQuotes = "CmoQuotes"
    CommodityQuotes = "CommodityQuotes"
    DealsMergersAndAcquisitions = "DealsMergersAndAcquisitions"
    DerivativeInstruments = "DerivativeInstruments"
    DerivativeQuotes = "DerivativeQuotes"
    EquityDerivativeInstruments = "EquityDerivativeInstruments"
    EquityDerivativeQuotes = "EquityDerivativeQuotes"
    EquityInstruments = "EquityInstruments"
    EquityQuotes = "EquityQuotes"
    FixedIncomeInstruments = "FixedIncomeInstruments"
    FixedIncomeQuotes = "FixedIncomeQuotes"
    FundQuotes = "FundQuotes"
    GovCorpInstruments = "GovCorpInstruments"
    GovCorpQuotes = "GovCorpQuotes"
    IndexInstruments = "IndexInstruments"
    IndexQuotes = "IndexQuotes"
    IndicatorQuotes = "IndicatorQuotes"
    Instruments = "Instruments"
    IRDQuotes = "IRDQuotes"
    LoanInstruments = "LoanInstruments"
    LoanQuotes = "LoanQuotes"
    MoneyQuotes = "MoneyQuotes"
    MortgageInstruments = "MortgageInstruments"
    MortQuotes = "MortQuotes"
    MunicipalInstruments = "MunicipalInstruments"
    MunicipalQuotes = "MunicipalQuotes"
    Organisations = "Organisations"
    People = "People"
    PhysicalAssets = "PhysicalAssets"
    Quotes = "Quotes"
    QuotesAndSTIRs = "QuotesAndSTIRs"
    SearchAll = "SearchAll"
    STIRs = "STIRs"
    VesselPhysicalAssets = "VesselPhysicalAssets"
    YieldCurveContQuotes = "YieldCurveContQuotes"
