# -*- coding: utf-8 -*-


import base64
from phcli.ph_aws.ph_s3 import PhS3
from phcli.ph_aws.ph_sts import PhSts
from phcli.ph_storage import static as st


class PhS3Storage:

    __phsts = PhSts().assume_role(
        base64.b64decode(st.ASSUME_ROLE_ARN).decode(),
        st.ASSUME_ROLE_EXTERNAL_ID,
    )
    __phs3 = PhS3(phsts=__phsts)

    def upload(self, file, bucket_name, object_name):
        self.__phs3.upload(file, bucket_name, object_name)
