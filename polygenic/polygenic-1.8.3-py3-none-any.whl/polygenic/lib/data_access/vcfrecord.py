import logging
from typing import List
from typing import Dict
from polygenic.lib.polygenic_exception import PolygenicException

logger = logging.getLogger('description_language.' + __name__)

class VcfRecord(object):
    def __init__(self, vcf_line:str, sample_names:List[str] = []):
        super().__init__()
        self.line = vcf_line

    def get_alt(self) -> List[str]:
        #try:
        return self.line.split("\t")[4].split(",")
        #except:
        #    raise PolygenicException("No alt allele in line: " + str(line))

    def get_ref(self) -> str:
        return self.line.split("\t")[3]

    def get_info(self) -> str:
        return self.line.split("\t")[7]

    def get_format(self) -> str:
        return self.line.split("\t")[8]

    def is_imputed(self) -> bool:
        return self.get_format().find("DS") != -1

    def get_info_field(self, name) -> str:
        for field in self.get_info().split(";"):
            field_name = field.split("=")[0]
            if field_name == name:
                return field.split("=")[1]

    def get_af_by_pop(self, population_name) -> Dict[str, float]:
        af = {}
        counter = 0
        sumfreq = 0
        for allele in self.get_alt():
            #print(population_name)
            #print(self.get_info())
            freq = float(self.get_info_field(population_name).split(",")[counter])
            sumfreq = sumfreq + freq
            af[allele] = freq
            counter = counter + 1
        af[self.get_ref()] = 1 - freq
        return af