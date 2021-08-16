from phcli.ph_aws.ph_sts import PhSts
from phcli.ph_aws.ph_s3 import PhS3
from phcli.ph_storage.model.local_storage import PhLocalStorage
from phcli.ph_storage.model.hdfs_storage import PhHdfsStorage

phsts = PhSts()
phsts = phsts.assume_role('arn:aws-cn:iam::444603803904:role/Ph-Cli-Lmd', 'Ph-Cli-Lmd')

phs3 = PhS3(phsts=phsts)


def test_ph_clean_logs_remove_local_file():
    ins = PhLocalStorage()
    assert ins.remove("/Users/qianpeng/Desktop/test.txt") is True


def test_ph_clean_logs_exec():
    from phcli.ph_storage.model.local_storage import PhLocalStorage
    from phcli.ph_storage.model.s3_storage import PhS3Storage
    ins = PhHdfsStorage(PhLocalStorage(), PhS3Storage())
    assert ins.back_up('["hdfs://backup:8020/common/public/cpa/0.0.4/YEAR=2015.0/MONTH=2.0"]') is True
