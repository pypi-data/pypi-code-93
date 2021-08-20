# This is replaced during release process.
__version_suffix__ = '142'

APP_NAME = "zalando-kubectl"

KUBECTL_VERSION = "v1.20.8"
KUBECTL_SHA512 = {
    "linux": "882727866b4dab3e997671f19f4a8ef5093117789970d963d2d2c6cdc64c2eac720ad14bb6b68a5b6c0773db8f7727ed658a7753c22780e366abb0f974c3e2ec",
    "darwin": "5c94e146d0fdfe94c1992b589a7555284e24fe8f057bc2f7865e8bddadd6a2e4c6763bf9fb5c8ef1667e373c30dda601d929e8cf11c7203ffb20d1e4eaf0a4c4",
}

STERN_VERSION = "1.19.0"
STERN_SHA256 = {
    "linux": "fcd71d777b6e998c6a4e97ba7c9c9bb34a105db1eb51637371782a0a4de3f0cd",
    "darwin": "18a42e08c5f995ffabb6100f3a57fe3c2e2b074ec14356912667eeeca950e849",
}

APP_VERSION = KUBECTL_VERSION + "." + __version_suffix__
