
import os

from ...util.config import SurfingConfigurator

from .fin_quality_factors import GrossMarginFactor, ReturnOnAssetsFactor, ReturnOnEquityFactor, TurnoverRateOfFAFactor, MixFinQualityFactor
from .growth_factors import IncomeGrowthFactor, NetProfitOfNonRecurringGoLFactor, OperationalCashFlowFactor, MixGrowthFactor
from .leverage_factors import FloatRatioFactor, StockDebtRatioFactor, CashFlowRatioFactor, MixLeverageFactor
from .liquidity_factors import Turnover30DFactor, Turnover60DFactor, Turnover90DFactor, MixLiquidityFactor
from .momentum_factors import AdjMomentum3MFactor, AdjMomentum6MFactor, AdjMomentum12MFactor, MixMomentumFactor
from .scale_factors import MarketValueFloatedFactor
from .tech_factors import ReverseFactor, BiasFactor, RSIFactor, MixTechFactor
from .value_factors import NAToMVFactor, NPToMVFactor, SPSToPFactor, DividendYieldFactor, EBITDAToMVFactor, EBITDAToEVFactor, MixValueFactor
from .volatility_factors import BetaSSEIFactor, Vol250DFactor, ResidualVolSSEIFactor, MixVolatilityFactor
from .fund_basic_factors import FundInfo, InMarketFundInfo, CloseFundInfo, FilteredFundInfoI, TradingDay, IndexInfo, FundManagerInfo, \
                                FundConvInfo, FundBenchmarkInfo, FilteredFundInfoWhole, ActiveFundInfo, IndexCloseDaily, IndexRetDaily, \
                                IndexRetWeekly, IndexRetMonthly, FundNavDaily, FundRetDaily, FundSize, FundSizeCombine, FundCompanyHold, \
                                FundRetDailyModify, FundRetWeeklyModify, FundRetMonthlyModify, FundNavDailyModify, FundInfoAsset, \
                                FundNavWeeklyModify, FundNavMonthlyModify, Macroeco, FundBenchmarkRet, FundBenchmarkPrice, FundPersonalHold
from .fund_derived_factors import TradeYear, FeeRate, AlphaBetaDaily3yI, AlphaDaily3yI, BetaDaily3yI, TrackerrDaily3yI, InfoRatioDaily3yI, \
                                  MddDaily3y, TreynorDaily3yI, DownriskDaily3y, RetOverPeriodDaily3y, AnnualRetDaily3y, AnnualVolDaily3y, \
                                  SharpeDaily3y, AlphaBetaDaily1yI, AlphaDaily1yI, BetaDaily1yI, TrackerrDaily1yI, InfoRatioDaily1yI, \
                                  MddDaily1y, TreynorDaily1yI, DownriskDaily1y, RetOverPeriodDaily1y, AnnualRetDaily1y, AnnualVolDaily1y, \
                                  SharpeDaily1y, AnnualRetDailyHistory, AnnualVolDailyHistory, AnnualRetMonthlyHalfY, AnnualVolMonthlyHalfY, \
                                  SharpeMonthlyHalfY, ContinueRegValue, TotalRetDailyHistory, MddDailyHistory, RecentMonthRet, DownsideStdDailyHistory, \
                                  FundClAlphaBetaHistoryWeekly, FundClAlphaHistoryWeekly, FundClBetaHistoryWeekly, FundClAlphaBeta1YWeekly, FundClAlpha1YWeekly, \
                                  FundClBeta1YWeekly, AlphaMdd3yI, WinRateMonthlyI, WinRateMonthlyTop50, WinRateMonthlyTop75, \
                                  ManagerIndex, ManagerBestFund, ManagerIndexRetDaily, ManagerIndexWeekly, ManagerIndexRetWeekly, \
                                  ManagerIndexMonthly, ManagerIndexRetMonthly, MngAnnualRetDailyHistory, MngAnnualRetDaily1Y, MngAnnualRetDaily3Y, \
                                  MngTotalRetDailyHistory, MngMddDailyHistory, MngAnnualVolDailyHistory, MngDownsideStdDailyHistory, MngDownsideStdMonthlyHistory, \
                                  MngFundTypeTradingDays, MngClAlphaBetaWeekly1Y, MngClAlphaWeekly1Y, MngClBetaWeekly1Y, MngClAlphaBetaWeeklyHistory, \
                                  MngClAlphaWeeklyHistory, MngClBetaWeeklyHistory, MngFundSize

from .fund_derived_score import MngScoreV1, FundMngScoreV1, RetAbilityFundScore, RiskAbilityFundScore, StableAbility, SelectTimeAbility, SelectStockAbility 

conf = SurfingConfigurator().get_aws_settings()
# 在to_parquet/read_parquet中通过storage_options传递如下参数的方法不好用，这里直接设置环境变量
os.environ['AWS_ACCESS_KEY_ID'] = conf.aws_access_key_id
os.environ['AWS_SECRET_ACCESS_KEY'] = conf.aws_secret_access_key
os.environ['AWS_DEFAULT_REGION'] = conf.region_name


for obj in (GrossMarginFactor, ReturnOnAssetsFactor, ReturnOnEquityFactor, TurnoverRateOfFAFactor, MixFinQualityFactor,
            IncomeGrowthFactor, NetProfitOfNonRecurringGoLFactor, OperationalCashFlowFactor, MixGrowthFactor,
            FloatRatioFactor, StockDebtRatioFactor, CashFlowRatioFactor, MixLeverageFactor,
            Turnover30DFactor, Turnover60DFactor, Turnover90DFactor, MixLiquidityFactor,
            AdjMomentum3MFactor, AdjMomentum6MFactor, AdjMomentum12MFactor, MixMomentumFactor,
            MarketValueFloatedFactor,
            ReverseFactor, BiasFactor, RSIFactor, MixTechFactor,
            NAToMVFactor, NPToMVFactor, SPSToPFactor, DividendYieldFactor, EBITDAToMVFactor, EBITDAToEVFactor, MixValueFactor,
            BetaSSEIFactor, Vol250DFactor, ResidualVolSSEIFactor, MixVolatilityFactor):
    obj().register()

fund_basic_factor = [FundInfo, InMarketFundInfo, CloseFundInfo, FilteredFundInfoI, TradingDay, IndexInfo, FundManagerInfo,
                     FundConvInfo, FundBenchmarkInfo, FilteredFundInfoWhole, ActiveFundInfo, IndexCloseDaily, IndexRetDaily,
                     IndexRetWeekly, IndexRetMonthly, FundNavDaily, FundRetDaily, FundSize, FundSizeCombine, FundCompanyHold,
                     FundRetDailyModify, FundInfoAsset, FundRetWeeklyModify, FundRetMonthlyModify, FundNavDailyModify,
                     FundNavWeeklyModify, FundNavMonthlyModify, Macroeco, FundBenchmarkRet, FundBenchmarkPrice, FundPersonalHold]

fund_derived_factor = [TradeYear, FeeRate, AlphaBetaDaily3yI, AlphaDaily3yI, BetaDaily3yI, TrackerrDaily3yI, InfoRatioDaily3yI,
                       MddDaily3y, TreynorDaily3yI, DownriskDaily3y, RetOverPeriodDaily3y, AnnualRetDaily3y, AnnualVolDaily3y,
                       SharpeDaily3y, AlphaBetaDaily1yI, AlphaDaily1yI, BetaDaily1yI, TrackerrDaily1yI, InfoRatioDaily1yI,
                       MddDaily1y, TreynorDaily1yI, DownriskDaily1y, RetOverPeriodDaily1y, AnnualRetDaily1y, AnnualVolDaily1y,
                       SharpeDaily1y, AnnualRetDailyHistory, AnnualVolDailyHistory, AnnualRetMonthlyHalfY, AnnualVolMonthlyHalfY,
                       SharpeMonthlyHalfY, ContinueRegValue, TotalRetDailyHistory, MddDailyHistory, RecentMonthRet, DownsideStdDailyHistory,
                       FundClAlphaBetaHistoryWeekly, FundClAlphaHistoryWeekly, FundClBetaHistoryWeekly, FundClAlphaBeta1YWeekly, FundClAlpha1YWeekly,
                       FundClBeta1YWeekly, ManagerIndex, ManagerBestFund, ManagerIndexRetDaily, ManagerIndexWeekly, ManagerIndexRetWeekly,
                       ManagerIndexMonthly, ManagerIndexRetMonthly, MngAnnualRetDailyHistory, MngAnnualRetDaily1Y, MngAnnualRetDaily3Y,
                       MngTotalRetDailyHistory, MngMddDailyHistory, MngAnnualVolDailyHistory, MngDownsideStdDailyHistory, MngDownsideStdMonthlyHistory,
                       MngFundTypeTradingDays, MngClAlphaBetaWeekly1Y, MngClAlphaWeekly1Y, MngClBetaWeekly1Y, MngClAlphaBetaWeeklyHistory,
                       MngClAlphaWeeklyHistory, MngClBetaWeeklyHistory, MngFundSize, AlphaMdd3yI, WinRateMonthlyI, WinRateMonthlyTop50, WinRateMonthlyTop75]

fund_derived_score = [MngScoreV1,FundMngScoreV1, RetAbilityFundScore, RiskAbilityFundScore, StableAbility, SelectTimeAbility, SelectStockAbility ]

fund_append_update_factor = [AlphaBetaDaily3yI, TrackerrDaily3yI, AlphaBetaDaily1yI, TrackerrDaily1yI, FundClAlphaBetaHistoryWeekly, FundClAlphaBeta1YWeekly,
                             ManagerIndex, MngClAlphaBetaWeekly1Y, MngClAlphaBetaWeeklyHistory, MngScoreV1]