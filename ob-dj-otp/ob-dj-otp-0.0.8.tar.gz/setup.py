from setuptools import setup

version = "0.0.8"

setup(
    install_requires=["django", "celery", "djangorestframework",],
    # TODO: https://github.com/obytes/ob-dj-otp/issues/3
    packages=[
        "ob_dj_otp.apis",
        "ob_dj_otp.apis.otp",
        "ob_dj_otp.core",
        "ob_dj_otp.core.otp",
        "ob_dj_otp.core.otp.migrations",
        "ob_dj_otp.core.otp.providers",
    ],
    tests_require=["pytest"],
)
