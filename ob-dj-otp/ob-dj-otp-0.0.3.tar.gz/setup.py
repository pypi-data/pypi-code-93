from setuptools import setup

version = "0.0.3"

setup(
    install_requires=["django", "celery", "djangorestframework",],
    # TODO: https://github.com/obytes/ob-dj-otp/issues/3
    # packages=["ob_dj_otp.apis", "ob_dj_otp.core", "ob_dj_otp.core.otp",],
    tests_require=["pytest"],
)
