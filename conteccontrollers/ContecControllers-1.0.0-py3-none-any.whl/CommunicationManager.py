from .Conductor import Conductor
from typing import Callable
from pymodbus.client.sync import ModbusTcpClient
import asyncio
from queue import Queue
from pymodbus.exceptions import ModbusIOException
import time
from .ITracer import ConsoleTracer, ITracer

class TaskToExecute:
    def __init__(self, functionToPerforme: Callable[[], any]):
        self.__FunctionToPerforme = functionToPerforme
        self.__TaskToComplete = asyncio.Future()

    @property
    def FunctionToPerforme(self) -> Callable[[], any]:
        return self.__FunctionToPerforme

    @property
    def TaskToComplete(self) -> asyncio.Future:
        return self.__TaskToComplete

class CommunicationManager:
    _tracer: ITracer
    _pendingTasks = Queue
    _controllersIp: str
    _controllersPort: int
    _modbusTcpClient: ModbusTcpClient
    _conductor: Conductor
    _workerTask: asyncio.Task
    _currentExecutingTask: TaskToExecute

    def __init__(self, tracer: ITracer, controllersIp: str, controllersPort: int) -> None:
        self._tracer = tracer
        self.__IsConnected = False
        self._controllersIp = controllersIp
        self._controllersPort = controllersPort
        self._modbusTcpClient = ModbusTcpClient(self._controllersIp, self._controllersPort)
        self._conductor = Conductor()
        self._pendingTasks = Queue()
        self._currentExecutingTask = None
    
    @property
    def IsConnected(self)-> bool:
        return self.__IsConnected

    def StartListening(self) -> None:
        self._workerTask = asyncio.create_task(self._ExecutePendingCommand())

    async def ReadInputRegistersAsync(self, slaveAddress: int, startAddress: int, numberOfPoints: int) -> list[int]:
        result = [None]
        func = lambda: self._ReadInputRegisters(slaveAddress, startAddress, numberOfPoints, result)
        taskToExecute = TaskToExecute(func)
        self._pendingTasks.put(taskToExecute)
        await taskToExecute.TaskToComplete
        return result[0]
    
    async def WriteSingleRegisterAsync(self, slaveAddress, regAddress, newRegValue) -> None:
        func = lambda: self._WriteSingleRegisterAsync(slaveAddress, regAddress, newRegValue)
        taskToExecute = TaskToExecute(func)
        self._pendingTasks.put(taskToExecute)
        await taskToExecute.TaskToComplete

    async def CloseAsync(self) -> None:
        self._workerTask.cancel()
        cancelMessage: str = "Communication closed"
        while not self._pendingTasks.empty:
            taskToExecute: TaskToExecute = self._pendingTasks.get()
            taskToExecute.TaskToComplete.cancel(cancelMessage)
        
        if self._currentExecutingTask != None:
            self._currentExecutingTask.TaskToComplete.cancel(cancelMessage)

    def _ReadInputRegisters(self, slaveAddress: int, startAddress: int, numberOfPoints: int, result: list) -> None:
        res = self._modbusTcpClient.read_holding_registers(startAddress, numberOfPoints, unit=(slaveAddress + 1))
        if type(res) is ModbusIOException:
            raise res
        result[0] = res.registers

    def _WriteSingleRegisterAsync(self, slaveAddress, regAddress, newRegValue) -> None:
        res = self._modbusTcpClient.write_register(regAddress, newRegValue, unit=(slaveAddress + 1))
        if type(res) is ModbusIOException:
            raise res

    async def _ExecutePendingCommand(self) -> None:
        while True:
            try:
                await asyncio.sleep(0.03) # 30 ms
                ticket = self._conductor.TryObtainTicket()
                if ticket == None:
                    return
                with ticket:
                    self._currentExecutingTask: TaskToExecute = self._pendingTasks.get_nowait()
                    if self._currentExecutingTask == None:
                        continue
                    while not self._modbusTcpClient.is_socket_open():
                        self.__IsConnected = False
                        if self.IsClosed():
                            return
                        if not self._modbusTcpClient.connect():
                            self._tracer.TraceError("Failed to connect to Contec controllers")
                            await asyncio.sleep(1)
                        else:
                            self._tracer.TraceInformation("connected to Contec controllers")

                    self.__IsConnected = True
                    try:
                        self._currentExecutingTask.FunctionToPerforme()
                        self._currentExecutingTask.TaskToComplete.set_result(True)
                    except Exception as e:
                        self._tracer.TraceError(f"Task failed with exception: {e}")
                        self._pendingTasks.put(self._currentExecutingTask)
                    finally:
                        self._currentExecutingTask = None
            except Exception as e:
                pass
    
    def IsClosed(self):
        ticket = self._conductor.TryObtainTicket()
        if ticket == None:
            return True
        with ticket:
            return False

async def Main():
    communicationManager = CommunicationManager(ConsoleTracer(), '127.0.0.1', 1234)
    communicationManager.StartListening()
    for i in range(1000):
        await communicationManager.WriteSingleRegisterAsync(1, 26, i % 10)
        res = await communicationManager.ReadInputRegistersAsync(1, 26, 3)
        print(f"got result {i} - {res}")
        time.sleep(1)
    await communicationManager.CloseAsync()
    print("Done")
    await asyncio.sleep(5)
    print("Done5")

if __name__ == "__main__":
    asyncio.run(Main())