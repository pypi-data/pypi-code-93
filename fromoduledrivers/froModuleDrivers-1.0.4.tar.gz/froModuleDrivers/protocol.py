# -*- encoding=utf-8 -*-

ProtocolDefine = {
    # protocolName: {
    #     "request":{
    #         orderName:{
    #             "cmd": bytes[]
    #             "args": [
    #                 {
    #                     "argName": nameStr,
    #                     "index": 3,
    #                     "length": 1
    #                 }
    #                 ...
    #             ]
    #         }
    #     },
    #     "responsePattern": rb'\xa0\x0b([\s\S]+)\x0d\x0a',
    #     "response": {
    #         orderCode: {
    #         orderName: nameStr,
    #         dataDefine: [
    #             {
    #                 fieldName: nameStr,
    #                 length: int
    #             },
    #             '''
    #         ]
    #     }
    # }
    "K210": {
        "request": {
            "查询固件版本": {
                "cmd": b"\xA0\x02\xD1\x0D\x0A",
                "args": []
            },

            "转向点设置": {
                "cmd": b"\xA0\x02\xC5\x00\x00\x00\x00\x00\x00\x0D\x0A",
                "args": [
                    {
                        "argName": "左转数量",
                        "index": 3,
                        "length": 1
                     },
                    {
                        "argName": "左转卡位高位",
                        "index": 4,
                        "length": "左转数量"
                    },
                    {
                        "argName": "左转卡位低位",
                        "index": 5,
                        "length": "左转数量"
                    },
                    {
                        "argName": "右转数量",
                        "index": 6,
                        "length": 1
                     },
                    {
                        "argName": "右转卡位高位",
                        "index": 7,
                        "length": "右转数量"
                    },
                    {
                        "argName": "右转卡位低位",
                        "index": 8,
                        "length": "右转数量"
                    },
                ]
            },


            "读寄存器-缓冲区": {
                "cmd": b"\xA0\x02\xF2\x00\x00\x00\x00\x0D\x0A",
                "args": [
                    {
                        "argName": "起始寄存器地址",
                        "index": 3,
                        "length": 2
                     },
                    {
                        "argName": "寄存器长度",
                        "index": 5,
                        "length": 2
                    }
                ]
            },
            "读寄存器-底层板": {
                "cmd": b"\xA0\x02\xF3\x00\x00\x00\x00\x0D\x0A",
                "args": [
                    {
                        "argName": "起始寄存器地址",
                        "index": 3,
                        "length": 2
                    },
                    {
                        "argName": "寄存器长度",
                        "index": 5,
                        "length": 2
                    }
                ]
            },
            "写寄存器": {
                # A0 02	F1	X1 X2	X3 X4	X5	XN …	0D 0A 不定长的数据占一位
                "cmd": b"\xA0\x02\xF1\x00\x00\x00\x00\x00\x00\x0D\x0A",
                "args": [
                    {
                        "argName": "起始寄存器地址",
                        "index": 3,
                        "length": 2
                    },
                    {
                        "argName": "寄存器长度",
                        "index": 5,
                        "length": 2
                    },
                    {
                        "argName": "数据长度",
                        "index": 7,
                        "length": 1
                    },
                    {
                        "argName": "写数据",
                        "index": 8,
                        "length": "数据长度"
                    }
                ]
            },
            "前进/启动": {
                "cmd": b"\xA0\x02\x01\x0D\x0A",
                "args": []
            },
            "停车": {
                "cmd": b"\xA0\x02\x02\x0D\x0A",
                "args": []
            },
        },
        "responsePattern": rb'\xa0\x0b([\s\S]+)\x0d\x0a',
        "response": {
            0xD1: {
                "orderName": "查询固件版本",
                "dataDefine": [
                    {
                        "fieldName": "版本号",
                        "length": 3
                    }
                ]
            },
            0xF2: {
                "orderName": "读寄存器-缓冲区",
                "dataDefine": [
                    {
                        "fieldName": "起始寄存器地址",
                        "length": 2
                    },
                    {
                        "fieldName": "寄存器长度",
                        "length": 2
                    },
                    {
                        "fieldName": "寄存器数据长度",
                        "length": 1
                    },
                    {
                        "fieldName": "寄存器数据",
                        "length": "寄存器数据长度"   # 若是变量，则之前必然出现过，否则逻辑上就无法解析。因此这里用fieldName字符串表示变量
                    }
                ]
            },
            0xF3: {
                "orderName": "读寄存器-底层板",
                "dataDefine": [
                    {
                        "fieldName": "起始寄存器地址",
                        "length": 2
                    },
                    {
                        "fieldName": "寄存器长度",
                        "length": 2
                    },
                    {
                        "fieldName": "寄存器数据长度",
                        "length": 1
                    },
                    {
                        "fieldName": "寄存器数据",
                        "length": "寄存器数据长度"   # 若是变量，则之前必然出现过，否则逻辑上就无法解析。因此这里用fieldName字符串表示变量
                    }
                ]
            },
            0xF1: {
                "orderName": "写寄存器",
                "dataDefine": [
                    {
                        "fieldName": "起始寄存器地址",
                        "length": 2
                    },
                    {
                        "fieldName": "寄存器长度",
                        "length": 2
                    },
                    {
                        "fieldName": "寄存器数据长度",
                        "length": 1
                    },
                    {
                        "fieldName": "寄存器数据",
                        "length": "寄存器数据长度"   # 若是变量，则之前必然出现过，否则逻辑上就无法解析。因此这里用fieldName字符串表示变量
                    }
                ]
            },
            0x01: {
                "orderName": "前进/启动",
                "dataDefine": []
            },
            0x02: {
                "orderName": "停车",
                "dataDefine": []
            },
            0xC5: {
                "orderName": "转向点设置",
                "dataDefine": [
                    {
                        "fieldName": "左转数量",
                        "length": 1
                    },
                    {
                        "fieldName": "左转卡位高位",
                        "length": "左转数量"
                    },
                    {
                        "fieldName": "左转卡位低位",
                        "length": "左转数量"
                    },
                    {
                        "fieldName": "右转数量",
                        "length": 1
                    },
                    {
                        "fieldName": "右转卡位高位",
                        "length": "右转数量"
                    },
                    {
                        "fieldName": "右转卡位低位",
                        "length": "右转数量"
                    }
                ]
            }
        }
    },

    "K12": {
        "request": {
            "03号查询指令": {
                "cmd": b"\x00\x03\x00\x00\x00\x00\x00\x00",
                "args": [
                    {
                        "argName": "主/从机号",
                        "index": 0,
                        "length": 1
                    },
                    {
                        "argName": "地址位",
                        "index": 2,
                        "length": 2
                    },
                    {
                        "argName": "地址长度",
                        "index": 4,
                        "length": 2
                    },
                    {
                        "argName": "CRC校验",
                        "index": 6,
                        "length": 2
                    }
                ]
            },
            "10号写指令": {
                "cmd": b"\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00",
                "args": [
                    {
                        "argName": "主/从机号",
                        "index": 0,
                        "length": 1
                    },
                    {
                        "argName": "地址位",
                        "index": 2,
                        "length": 2
                    },
                    {
                        "argName": "地址长度",
                        "index": 4,
                        "length": 2
                    },
                    {
                        "argName": "数据长度",
                        "index": 6,
                        "length": 1
                    },
                    {
                        "argName": "数据",
                        "index": 7,
                        "length": "数据长度"
                    },
                    {
                        "argName": "CRC校验",
                        "index": 8,
                        "length": 2
                    }
                ]
            }
        },
        "responsePattern": rb'([\s\S][\x03\x10\x83\x90][\s\S]+)',
        "response": {
            0x03: {
                "orderName": "03号查询指令",
                "dataDefine": [
                    {
                        "fieldName": "主机号",
                        "length": 1
                    },
                    {
                        "fieldName": "指令号",
                        "length": 1
                    },
                    {
                        "fieldName": "设备号",
                        "length": 2
                    },
                    {
                        "fieldName": "数据长度",
                        "length": 1
                    },
                    {
                        "fieldName": "数据",
                        "length": "数据长度"
                    },
                    {
                        "fieldName": "CRC校验",
                        "length": 2
                    }
                ]
            },
            0x10: {
                "orderName": "10号写指令",
                "dataDefine": [
                    {
                        "fieldName": "主/从机号",
                        "length": 1
                    },
                    {
                        "fieldName": "指令号",
                        "length": 1
                    },
                    {
                        "fieldName": "设备号",
                        "length": 2
                    },
                    {
                        "fieldName": "地址长度",
                        "length": 2
                    },
                    {
                        "fieldName": "数据长度",
                        "length": 1
                    },
                    {
                        "fieldName": "数据",
                        "length": "数据长度"
                    },
                    {
                        "fieldName": "CRC校验",
                        "length": 2
                    }
                ]
            },
            0x83: {
                "orderName": "03号错误指令",
                "dataDefine": [
                    {
                        "fieldName": "主/从机号",
                        "length": 1
                    },
                    {
                        "fieldName": "指令号",
                        "length": 1
                    },
                    {
                        "fieldName": "错误码",
                        "length": 1
                    },
                    {
                        "fieldName": "CRC校验",
                        "length": 2
                    }
                ]
            },
            0x90: {
                "orderName": "10号错误指令",
                "dataDefine": [
                    {
                        "fieldName": "主/从机号",
                        "length": 1
                    },
                    {
                        "fieldName": "指令号",
                        "length": 1
                    },
                    {
                        "fieldName": "错误码",
                        "length": 1
                    },
                    {
                        "fieldName": "CRC校验",
                        "length": 2
                    }
                ]
            }
        }
    }
}