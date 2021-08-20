#from api.API import Transaction, TransactionId
from pycs.api.API import Transaction, TransactionId
import sys
from pycs.keys import Keys
from pycs.clientex import ClientEx
import base58check
#import keys
#from .api.API import Transaction, TransactionId
#from .keys import Keys
#from .clientex import ClientEx



class Connector(object):
    def __init__(self, address):
        self.ip = address

    def TransactionGet(self,PoolSeq, Index):
        """Description of TransactionGet

            Parameters:
            PoolSeq (int): BlockNumber
            Index (int): Transaction number in that block

            Returns:
            Object:TransactionGetResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).TransactionGet(TransactionId(poolSeq=PoolSeq, index=Index))
        except Exception as e:
            raise e
    
    def WalletGetBalance(self,PubKey):
        """Description of WalletGetBalance

            Parameters:
            PubKey (string): Base58 PublicKey

            Returns:
            Object:WalletGetBalanceResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).WalletGetBalance(base58check.b58decode(PubKey))
        except Exception as e:
            raise e
    
    def WalletTransactionsCountGet(self,PubKey):
        """Description of WalletTransactionsCountGet

            Parameters:
            PubKey (string): Base58 PublicKey

            Returns:
            Object:WalletTransactionsCountGetResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).WalletTransactionsCountGet(base58check.b58decode(PubKey))
        except Exception as e:
            raise e

    def WalletDataGet(self,PubKey):
        """Description of WalletDataGet

            Parameters:
            PubKey (string): Base58 PublicKey

            Returns:
            Object:WalletDataGetResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).WalletDataGet(base58check.b58decode(PubKey))
        except Exception as e:
            raise e

    def StatsGet(self):
        """Description of StatsGet
            NOT IMPLEMENTED YET
            Returns:
            Object:StatsGetResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).StatsGet()
        except Exception as e:
            raise e

    def TransactionsGet(self,PubKey,Offset=0, Index=10):
        """Description of TransactionsGet

            Parameters:
            PoolSeq (int): BlockNumber
            Index (int): Transaction number in that block

            Returns:
            Object:TransactionsGetResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).TransactionsGet(base58check.b58decode(PubKey),Offset,Index)
        except Exception as e:
            raise e
    def DeploySmart(self,smcode,PublicKey,PrivateKey,Target):
        """Description of SendTransaction

            Parameters:
            Integeral (int): Amount before the .
            fraction (int): Amount after the .
            fee (int): Amount fee as maximum
            PublicKey (string): PublicKey 
            PrivateKey (string): PrivateKey
            Target (string): Target Address
            UserData(byte[]) Optional
            TxsID(int) Optional
            Transaction(Transaction) Optional
            Returns:
            Object:TransactionFlowResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        keys_ = Keys(PublicKey,PrivateKey,Target)
        return ClientEx(self.ip.split(':')).deploy_smart_contract("",1.0,keys_)
    def SendTransaction(self,Integeral,fraction,fee,PublicKey,PrivateKey,Target,UserData=None,TxsID=0,Transaction = None):
        """Description of SendTransaction

            Parameters:
            Integeral (int): Amount before the .
            fraction (int): Amount after the .
            fee (int): Amount fee as maximum
            PublicKey (string): PublicKey 
            PrivateKey (string): PrivateKey
            Target (string): Target Address
            UserData(byte[]) Optional
            TxsID(int) Optional
            Transaction(Transaction) Optional
            Returns:
            Object:TransactionFlowResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            keys_ = Keys(PublicKey,PrivateKey,Target)
            if(TxsID == 0):
                TxsID = ClientEx(self.ip.split(':')).WalletTransactionsCountGet(keys_.public_key_bytes).lastTransactionInnerId + 1
            return ClientEx(self.ip.split(':')).transfer_coins(Integeral,fraction,fee,keys_,UserData,TxsID,Transaction)
        except Exception as e:
            raise e

    def SyncState(self):
        """Description of SyncState
            Returns:
            Object:SyncStateResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).SyncState()
        except Exception as e:
            raise e

    def ActualFeeGet(self,TransactionSize):
        """Description of SyncState

            Parameters:
            TransactionSize (int): TransactionSize

            Returns:
            Object:ActualFeeGetResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).ActualFeeGet(TransactionSize)
        except Exception as e:
            raise e

    def WalletIdGet(self,Address):
        """Description of WalletIdGet

            Parameters:
            Address (string): Address of Wallet

            Returns:
            Object:WalletIdGetResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).WalletIdGet(base58check.b58decode(Address))
        except Exception as e:
            raise e

    def TransactionsListGet(self, OffSet=0, Limit=10):
        """Description of TransactionsListGet

            Parameters:
            OffSet (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:TransactionsGetResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).TransactionsListGet(OffSet,Limit)
        except Exception as e:
            raise e

    def PoolListGetStable(self, Sequence=0, Limit=10):
        """Description of PoolListGetStable

            Parameters:
            Sequence (int): Sequence/block number
            Limit (int): Limit Amount per request

            Returns:
            Object:PoolListGetResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).PoolListGetStable(Sequence,Limit)
        except Exception as e:
            raise e

    def PoolListGet(self, Offset=0, Limit=10):
        """Description of PoolListGet

            Parameters:
            Offset (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:PoolListGetResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).PoolListGet(Offset,Limit)
        except Exception as e:
            raise e

    def PoolInfoGet(self, Offset=0, Limit=10):
        """Description of PoolInfoGet

            Parameters:
            Offset (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:PoolInfoGetResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).PoolInfoGet(Offset,Limit)
        except Exception as e:
            raise e

    def PoolTransactionsGet(self, Sequence, Offset=0, Limit=10):
        """Description of PoolTransactionsGet

            Parameters:
            Offset (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:PoolTransactionsGetResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).PoolTransactionsGet(Sequence,Offset,Limit)
        except Exception as e:
            raise e

    def SmartContractGet(self, Address):
        """Description of PoolTransactionsGet

            Parameters:
            Offset (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:PoolTransactionsGetResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).SmartContractGet(base58check.b58decode(Address))
        except Exception as e:
            raise e

    def SmartContractsListGet(self, Deployer, Offset=0, Limit=10):
        """Description of SmartContractsListGet

            Parameters:
            Offset (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:SmartContractsListGetResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).SmartContractsListGet(base58check.b58decode(Deployer),Offset,Limit)
        except Exception as e:
            raise e
    
    def TransactionsStateGet(self, Address, Id):
        """Description of TransactionsStateGet

            Parameters:
            Offset (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:TransactionsStateGetResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).TransactionsStateGet(base58check.b58decode(Address),Id)
        except Exception as e:
            raise e

    def ContractAllMethodsGet(self, byteCodeObjects):
        """Description of ContractAllMethodsGet

            Parameters:
            Offset (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:ContractAllMethodsGetResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).ContractAllMethodsGet(byteCodeObjects)
        except Exception as e:
            raise e

    def SmartMethodParamsGet(self, Address, Id):
        """Description of SmartMethodParamsGet

            Parameters:
            Offset (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:SmartMethodParamsGetResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).SmartMethodParamsGet(base58check.b58decode(Address), Id)
        except Exception as e:
            raise e
    
    def SmartContractDataGet(self, Address):
        """Description of SmartContractDataGet

            Parameters:
            Offset (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:SmartContractDataResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).SmartContractDataGet(base58check.b58decode(Address))
        except Exception as e:
            raise e

    def SmartContractCompile(self, SCcode):
        """Description of SmartContractCompile

            Parameters:
            Offset (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:SmartContractCompileResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).SmartContractCompile(SCcode)
        except Exception as e:
            raise e

    def TokenBalancesGet(self, Address):
        """Description of TokenBalancesGet

            Parameters:
            Offset (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:TokenBalancesResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).TokenBalancesGet(base58check.b58decode(Address))
        except Exception as e:
            raise e

    def TokenTransfersGet(self, Token, Offset=0, Limit=0):
        """Description of TokenTransfersGet

            Parameters:
            Offset (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:TokenTransfersResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).TokenTransfersGet(base58check.b58decode(Token), Offset, Limit)
        except Exception as e:
            raise e

    def TokenTransferGet(self, Token, TxsID):
        """Description of TokenTransferGet

            Parameters:
            Offset (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:TokenTransfersResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).TokenTransferGet(base58check.b58decode(Token), TxsID)
        except Exception as e:
            raise e
        
    def TokenTransfersListGet(self, Offset=0, Limit=0):
        """Description of TokenTransfersListGet

            Parameters:
            Offset (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:TokenTransfersResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).TokenTransfersListGet(Offset,Limit)
        except Exception as e:
            raise e

    def TokenWalletTransfersGet(self, Token, Address, Offset=0, Limit=0):
        """Description of TokenWalletTransfersGet

            Parameters:
            Offset (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:TokenTransfersResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).TokenWalletTransfersGet(base58check.b58decode(Token),base58check.b58decode(Address),Offset,Limit)
        except Exception as e:
            raise e

    def TokenInfoGet(self, Token):
        """Description of TokenInfoGet

            Parameters:
            Offset (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:TokenInfoResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).TokenInfoGet(base58check.b58decode(Token))
        except Exception as e:
            raise e

    def TokenHoldersGet(self, Token, Order, Desc, Offset=0, Limit=0):
        """Description of TokenHoldersGet

            Parameters:
            Offset (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:TokenHoldersResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).TokenHoldersGet(base58check.b58decode(Token), Order, Desc, Offset, Limit)
        except Exception as e:
            raise e

    def TokensListGet(self, Order, Filters, Desc, Offset=0, Limit=10):
        """Description of TokensListGet

            Parameters:
            Offset (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:TokensListResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).TokensListGet(Order, Filters, Desc, Offset,Limit)
        except Exception as e:
            raise e

    def WalletsGet(self, OrdCol, Desc, Offset=0, Limit=10):
        """Description of WalletsGet

            Parameters:
            Offset (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:WalletsGetResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).WalletsGet(OrdCol, Desc, Offset,Limit)
        except Exception as e:
            raise e

    def TrustedGet(self, Page):
        """Description of WalletsGet

            Parameters:
            Offset (int): Offset number
            Limit (int): Limit Amount per request

            Returns:
            Object:TrustedGetResult

            Detailed Documentation

            https://centr.gitbook.io/netcs/
            """
        try: 
            return ClientEx(self.ip.split(':')).TrustedGet(Page)
        except Exception as e:
            raise e



        

        
