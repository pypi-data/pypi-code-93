import logging
import pathlib
from typing import Dict
from typing import List
from typing import Union
from polygenic.lib import mobigen_utils
from polygenic.lib.data_access.dto import SnpData
from polygenic.lib.data_access.dto import SnpDataManySamples
from polygenic.lib.data_access.vcfrecord import VcfRecord

# rsidx
import os
from gzip import open as gzopen
import rsidx
import sqlite3

logger = logging.getLogger('description_language.' + __name__)

class VcfAccessor(object):
    def __init__(self, vcf_path:str):
        super().__init__()
        self.path = vcf_path
        if not os.path.exists(self.path + '.idx.db'):
            with sqlite3.connect(self.path + '.idx.db') as dbconn, gzopen(self.path, 'rt') as vcffh:
                rsidx.index.index(dbconn, vcffh)
        self.sample_names = self.get_sample_names()
        self.__data: Dict[str, Dict[str:SnpData]] = {}  # dictionary rsid:{sample_name:ModelSnpData}

    def get_sample_names(self) -> List[str]:
        logger.info('Getting sample names')
        sample_names_for_all_files = []
        with gzopen(self.path) as vcf_file:
            for line in vcf_file:
                line = line.decode("utf-8")
                if line.find("#CHROM") != -1:
                    break
        if line.find('FORMAT') == -1:
            return None
        samples_string = line.split('FORMAT')[1].strip()
        sample_names_for_all_files.append(samples_string.split())
        assert all(sample_names == sample_names_for_all_files[-1] for sample_names in sample_names_for_all_files[:-1])
        return sample_names_for_all_files[-1]

    def __get_data_for_given_rsid(self, rsid, imputed:bool = False) -> Dict[str, SnpData]:
        line = self.__get_vcf_line_for_rsid(rsid)
        if not line:
            logger.debug(f'No line for rsid {rsid} found')
            raise DataNotPresentError
        if VcfRecord(line).is_imputed() == imputed:
            data = mobigen_utils.get_genotypes(line, self.sample_names)
            self.__data[rsid] = {sample_name: SnpData(data.ref, data.alts, genotype) for sample_name, genotype in data.genotypes.items()}
        else:
            raise DataNotPresentError
        return self.__data[rsid]

    def __get_record_for_rsid(self, rsid) -> VcfRecord:
        return VcfRecord(self.__get_vcf_line_for_rsid(rsid), self.sample_names)

    def get_af_by_pop(self, rsid:str, population_name:str) -> Dict[str, float]:
        return self.__get_record_for_rsid(rsid).get_af_by_pop(population_name)


    def get_data_for_sample(self, sample_name:str, rsid:str, imputed:bool = False) -> SnpData:
        try:
            return self.__data[rsid][sample_name]
        except KeyError:
            try:
                return self.__get_data_for_given_rsid(rsid, imputed)[sample_name]
            except DataNotPresentError:
                return None

    def __get_vcf_line_for_rsid(self, rsid:str) -> Union[None, str]:
        try:
            with sqlite3.connect(self.path + '.idx.db') as dbconn:
                for line in rsidx.search.search([rsid], dbconn, self.path):
                    return line
        except KeyError:
            print("Record " + str(rsid) + " not found")
            raise DataNotPresentError
        raise DataNotPresentError

    def get_allele_freq_from_db(rsid: str, population_name: str):
        record = self.__get_record_for_rsid(rsid)
        ref_allele = record.get_ref()
        alt_allele = record.get_alt()
        alt_allele_freq = record.get_af_by_pop(population_name)
        if not len(alt_allele) == 1:
            logger.info(
                f'{rsid} is multiallelic but only two alleles are provided. Only {ref_allele} and {alt_allele} were considered')
        return {alt_allele: alt_allele_freq, ref_allele: 1 - alt_allele_freq}

class DataNotPresentError(RuntimeError):
    pass

def path_to_fname_stem(path:str) -> str:
    return pathlib.PurePath(path).name.split('.')[0]