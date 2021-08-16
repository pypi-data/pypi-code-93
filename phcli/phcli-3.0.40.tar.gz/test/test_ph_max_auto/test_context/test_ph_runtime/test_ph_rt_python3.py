import base64

from phcli.ph_max_auto.phcontext.ph_runtime.ph_rt_python3 import PhRTPython3
from phcli.ph_max_auto import define_value as dv
from phcli.ph_aws.ph_s3 import PhS3
from phcli.ph_aws.ph_sts import PhSts


def main():
    print("test_main方法被调用")
    phsts = PhSts().assume_role(
        base64.b64decode(dv.ASSUME_ROLE_ARN).decode(),
        dv.ASSUME_ROLE_EXTERNAL_ID,
    )
    phs3_test = PhS3(phsts=phsts)

    source_path = "./phjobs/a/b"
    target_path = "./phjobs/a/b.ipynb"
    t = PhRTPython3(phs3=phs3_test, group="a", name="b", ide="jupyter")
    t.c9_to_jupyter(source_path, target_path)


if __name__ == '__main__':
    main()
    print("success")
