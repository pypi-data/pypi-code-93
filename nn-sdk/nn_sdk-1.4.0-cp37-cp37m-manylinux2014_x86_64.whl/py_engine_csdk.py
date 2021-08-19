# -*- coding: UTF-8 -*-
import sys
from nn_sdk.engine_csdk import sdk_new,sdk_delete,sdk_process

# 支持 的 c库 函数
# typedef long long SDK_HANDLE_CC;
# int sdk_init_cc();
# int sdk_uninit_cc();
# SDK_HANDLE_CC sdk_new_cc(const char* json);
# int sdk_delete_cc(SDK_HANDLE_CC handle);
# int sdk_process_cc(SDK_HANDLE_CC handle, void** final_result, int net_stage, int input_num, ...);

class csdk_object:
    def __init__(self,conf):
        self.instance = None
        self.instance = sdk_new(conf)
        print("csdk_object create ", self.instance)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb is None:
            self.close()
        else:
            print("[Exit %s]: Exited with exception raised." % self.instance)

    def valid(self):
        return self.instance and self.instance > 0
    def close(self):
        if self.instance and self.instance > 0:
            print('csdk_object destroy',self.instance)
            code = sdk_delete(self.instance)
            self.instance = 0
    '''
        stage 推理子图id
        input 为该子图的输入,支持多输入。
    '''
    def process(self,stage:int,*input):
        code, result = sdk_process(self.instance,stage, *input)
        return code,result