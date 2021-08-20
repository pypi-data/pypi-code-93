import hashlib
import math
from struct import pack
import base58check
import ed25519
from thrift.protocol.TBinaryProtocol import TBinaryProtocol
from thrift.transport.TSocket import TSocket
from thrift.transport.TTransport import TMemoryBuffer
from pycs.api.API import Client, Transaction, AmountCommission, SmartContractInvocation, SmartContractDeploy
from pycs.general.ttypes import Amount, ByteCodeObject


class ClientEx:

    def __init__(self, address):
        self.tr = TSocket(address[0], address[1])
        self.protocol = TBinaryProtocol(self.tr)
        self.client = Client(self.protocol)
        self.tr.open()

    def close(self):
        self.tr.close()

    def WalletGetBalance(self, pub_key_bytes):
        return self.client.WalletBalanceGet(pub_key_bytes)

    def WalletTransactionsCountGet(self, pub_key_bytes):
        return self.client.WalletTransactionsCountGet(pub_key_bytes)

    def WalletDataGet(self, pub_key_bytes):
        return self.client.WalletDataGet(pub_key_bytes)

    def StatsGet(self):
        return self.client.StatsGet()

    def TransactionGet(self, transactionid):
        return self.client.TransactionGet(transactionid)    

    def TransactionsGet(self, address,offset,limit):
        return self.client.TransactionsGet(address,offset,limit)

    def SyncState(self):
        return self.client.SyncStateGet()

    def ActualFeeGet(self,transactionsize):
        return self.client.ActualFeeGet(transactionsize)
    
    def WalletIdGet(self,adress):
        return self.client.WalletIdGet(adress)
    
    def TransactionsListGet(self,offset,limit):
        return self.client.TransactionsListGet(offset,limit)

    def PoolListGetStable(self,sequence,limit):
        return self.client.PoolListGetStable(sequence,limit)

    def PoolListGet(self,offset,limit):
        return self.client.PoolListGet(offset,limit)
    
    def PoolInfoGet(self,offset,limit):
        return self.client.PoolInfoGet(offset,limit)

    def PoolTransactionsGet(self,sequence,offset,limit):
        return self.client.PoolTransactionsGet(sequence,offset,limit)

    def SmartContractGet(self,address):
        return self.client.SmartContractGet(address)
    
    def SmartContractsListGet(self,deployer,offset,limit):
        return self.client.SmartContractsListGet(deployer,offset,limit)

    def TransactionsStateGet(self,address,Id):
        return self.client.TransactionsStateGet(address,Id)
    
    def ContractAllMethodsGet(self,bytecodeobjects):
        return self.client.ContractAllMethodsGet(bytecodeobjects)
    
    def SmartMethodParamsGet(self,address,id):
        return self.client.SmartMethodParamsGet(address,id)

    def SmartContractDataGet(self,address):
        return self.client.SmartContractDataGet(address)

    def SmartContractCompile(self,sccode):
        return self.client.SmartContractCompile(sccode)

    def TokenBalancesGet(self,address):
        return self.client.TokenBalancesGet(address)

    def TokenTransfersGet(self,token,offset,limit):
        return self.client.TokenTransfersGet(token,offset,limit)

    def TokenTransferGet(self,token,txsid):
        return self.client.TokenTransferGet(token,txsid)

    def TokenTransfersListGet(self,offset,limit):
        return self.client.TokenTransfersListGet(offset,limit)

    def TokenWalletTransfersGet(self,token,address,offset,limit):
        return self.client.TokenWalletTransfersGet(offset,token,address,offset,limit)

    def TokenInfoGet(self,token):
        return self.client.TokenInfoGet(token)

    def TokenHoldersGet(self,token,order,desc,offset,limit):
        return self.client.TokenHoldersGet(token,order,desc,offset,limit)

    def TokensListGet(self,order,filters,desc,offset,limit):
        return self.client.TokensListGet(offset,limit, order,desc,filters)

    def WalletsGet(self,ordcol,desc,offset,limit):
        return self.client.WalletsGet(offset,limit,ordcol,desc)

    def TrustedGet(self,page):
        return self.client.TrustedGet(page)
    
    def double_to_fee(self,value):
        fee_comission = 0
        a = True
        if value < 0.:
            fee_comission += 32768
        else:
            fee_comission += (32768 if value < 0. else 0)
            value = math.fabs(value)
            expf = (0. if value == 0. else math.log10(value))
            expi = int(expf + 0.5 if expf >= 0. else expf - 0.5)
            value /= math.pow(10, expi)
            if value >= 1.:
                value *= 0.1
                expi += 1
            fee_comission += int(1024*(expi + 18))
            fee_comission += int(value * 1024)
        return fee_comission

    def __fee(self, value):
        sign = 0
        if value < 0.0:
            value = 1
        value = abs(value)
        expf = 0
        if value != 0.0:
            expf = math.log10(value)
        if expf >= 0:
            expf = expf + .5
        else:
            expf = expf - .5
        expi = int(expf)
        value /= math.pow(10, expi)
        if value >= 1.0:
            value *= 0.1
            expi = expi + 1
        exp = expi + 18
        if exp < 0 or exp > 28:
            print('exponent value {0} out of range [0, 28]'.format(exp))
            return -1
        frac = round(value * 1024)
        return sign * 32768 + exp * 1024 + frac

    def transfer_coins(self, integral, fraction, fee, keys, userdata, txsid, txs):
        if(txs != None):
            return self.client.TransactionFlow(txs)
        if(userdata != None):
            return self.client.TransactionFlow(self.create_transaction_userdata(integral, fraction, fee, keys, userdata,txsid))
        else:
            return self.client.TransactionFlow(self.create_transaction(integral, fraction, fee, keys, txsid))

    def create_transaction(self, integral, fraction, fee, keys, txsid):
        tr = Transaction()
        tr.id = txsid
        tr.source = keys.public_key_bytes
        tr.target = keys.target_public_key_bytes
        tr.amount = Amount()
        tr.amount.integral = integral
        tr.amount.fraction = fraction
        tr.currency = 1

        tr.fee = AmountCommission()
        tr.fee.commission = self.__fee(fee)

        serial_transaction = pack('=6s32s32slqhbb',                       # '=' - without alignment'
                                  bytearray(tr.id.to_bytes(6, 'little')), # 6s - 6 byte InnerID (char[] C Type)
                                  tr.source,                              # 32s - 32 byte source public key (char[] C Type)
                                  tr.target,                              # 32s - 32 byte target pyblic key (char[] C Type)
                                  tr.amount.integral,                     # i - 4 byte integer(int C Type)
                                  tr.amount.fraction,                     # q - 8 byte integer(long long C Type)
                                  tr.fee.commission,                      # h - 2 byte integer (short C Type)
                                  tr.currency,                            # b - 1 byte integer (signed char C Type)
                                  0                                       # b - 1 byte userfield_num
        )

        signing_key = ed25519.SigningKey(keys.private_key_bytes)
        sign = signing_key.sign(serial_transaction)
        tr.signature = sign

        return tr

    def create_transaction_userdata(self, integral, fraction, fee, keys,userdata,txsid):
        tr = Transaction()
        tr.id = txsid
        tr.source = keys.public_key_bytes
        tr.target = keys.target_public_key_bytes
        tr.amount = Amount()
        tr.amount.integral = integral
        tr.amount.fraction = fraction
        tr.currency = 1
        tr.userFields =bytearray(userdata,'utf-8')
        tr.fee = AmountCommission()
        tr.fee.commission = self.__fee(fee)

        serial_transaction = pack('=6s32s32slqhbbi',                       # '=' - without alignment'
                                  bytearray(tr.id.to_bytes(6, 'little')), # 6s - 6 byte InnerID (char[] C Type)
                                  tr.source,                              # 32s - 32 byte source public key (char[] C Type)
                                  tr.target,                              # 32s - 32 byte target pyblic key (char[] C Type)
                                  tr.amount.integral,                     # i - 4 byte integer(int C Type)
                                  tr.amount.fraction,                     # q - 8 byte integer(long long C Type)
                                  tr.fee.commission,                      # h - 2 byte integer (short C Type)
                                  tr.currency,                            # b - 1 byte integer (signed char C Type)
                                  1,                                       # b - 1 byte userfield_num
                                  len(tr.userFields)
        )

        full_serial_transaction = serial_transaction + tr.userFields
        
        signing_key = ed25519.SigningKey(keys.private_key_bytes)
        sign = signing_key.sign(full_serial_transaction)
        tr.signature = sign

        return tr

    def deploy_smart_contract(self, code, fee, keys):
        res = self.client.TransactionFlow(self.create_transaction_with_smart_contract(code,fee,keys))
        print(res)

    def createContractAddress(self, source, tId, contract):
        tmpBytes = bytearray()
        tmpBytes.extend(source)
        tmpBytes.extend(tId)
        for a in contract.smartContractDeploy.byteCodeObjects:
            tmpBytes.extend(a.byteCode)
        res = hashlib.blake2s()
        res.update(tmpBytes)
        return res.digest()

    def normalizeCode(self,javaText):
        javaText = javaText.replace('\r', ' ').replace('\t', ' ').replace('{', ' {')
        while '  ' in javaText:
            javaText = javaText.replace('  ', ' ')
        return javaText

    def compile_smart(self,contract_body):
        if self.client == None:
            return None
        res = self.client.SmartContractCompile(contract_body)
        return res   
        
    def create_transaction_with_smart_contract(self, code, fee, keys):
        tr = Transaction()
        contract = SmartContractInvocation()
        contract.smartContractDeploy = SmartContractDeploy()
        if code == "":
            code = 'import com.credits.scapi.annotations.*; import com.credits.scapi.v0.*; public class ' \
                   'MySmartContract extends SmartContract { public MySmartContract() {} public String hello2(String ' \
                   'say) { return \"Hello\" + say; } }';
        contractText = self.normalizeCode(code)
        result = self.compile_smart(contractText)
        contract.smartContractDeploy.byteCodeObjects = result.byteCodeObjects
        tr.smartContract = contract
        tr.smartContract.smartContractDeploy.sourceCode = contractText
        tr.source = keys.public_key_bytes
        w = self.client.WalletTransactionsCountGet(tr.source)
        lastInnerId = bytearray((w.lastTransactionInnerId + 1).to_bytes(6,'little'))
        tr.id = int.from_bytes(lastInnerId,byteorder='little', signed=False)
        tr.target = self.createContractAddress(tr.source, lastInnerId, contract)
        tr.amount = Amount()
        tr.amount.integral = 0
        tr.amount.fraction = 0
        tr.balance = Amount()
        tr.balance.integral = 0
        tr.balance.fraction = 0
        tr.currency = 1
        tr.fee = AmountCommission()
        tr.fee.commission = self.double_to_fee(fee)
        tr.userFields = ""
        ufNum1 = bytearray(b'\x01')
        contract.smartContractDeploy.hashState = ""
        contract.smartContractDeploy.tokenStandard = 0
        contract.method = ""
        contract.params = []
        contract.usedContracts = []
        contract.forgetNewState = False
        transportOut = TMemoryBuffer()
        protocolOut = TBinaryProtocol(transportOut)
        contract.write(protocolOut)
        scBytes = transportOut.getvalue()
        sMap = '=6s32s32slqhb1s4s' + str(len(scBytes)) +'s' #4s' + str(scriptLength) + 's4s' + str(codeNameLength) + 's4s' + str(codeLength) + 's' #len(userField_bytes)
        serial_transaction_for_sign = pack(sMap,  #'=' - without alignment
                            lastInnerId,     #6s - 6 byte InnerID (char[] C Type)
                            tr.source,       #32s - 32 byte source public key (char[] C Type)
                            tr.target,       #32s - 32 byte target pyblic key (char[] C Type)
                            tr.amount.integral, #i - 4 byte integer(int C Type)
                            tr.amount.fraction, #q - 8 byte integer(long long C Type)
                            tr.fee.commission,  #h - 2 byte integer (short C Type)
                            tr.currency,        #b - 1 byte integer (signed char C Type)
                            ufNum1,
                            bytes(len(scBytes).to_bytes(4, byteorder="little")),
                            scBytes
                            )                     
        signing_key = ed25519.SigningKey(keys.private_key_bytes) # Create object for calulate signing
        tr.signature = signing_key.sign(serial_transaction_for_sign)
        return tr

    

    def reverse(self, a):
        a = a.to_bytes(6, 'little')
        a = bytearray(a)
        a.reverse()
        return a

