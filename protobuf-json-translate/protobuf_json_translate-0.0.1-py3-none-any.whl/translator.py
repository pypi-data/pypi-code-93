from google.protobuf.json_format import Parse, MessageToJson



class Translator:
    def protobuf_to_json(self,protoFileLocation,protoMessageLocationInFile,protobufDataToBeTranslated,displayEnabled=False):
        eval("exec('import {}_pb2')".format(protoFileLocation))
        skeletonTranslator = eval("{}_pb2.{}()".format(protoFileLocation, protoMessageLocationInFile))
        skeletonTranslator.ParseFromString(protobufDataToBeTranslated)
        skeletonTranslator = MessageToJson(skeletonTranslator)
        if displayEnabled:
            print(skeletonTranslator)
        return skeletonTranslator
