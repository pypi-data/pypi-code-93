from yucebio_wdladaptor.backend.base import BaseAdaptor, PLACEHOLDER_GLOBAL_PATH, PLACEHOLDER_SIMG_PATH
from yucebio_wdladaptor.backend.sge import Adaptor as SgeAdaptor
from yucebio_wdladaptor.backend.bcs import Adaptor as BcsAdaptor
from yucebio_wdladaptor.backend.aws import Adaptor as AwsAdaptor


SUPPORTTED_BACKENDS = {
    SgeAdaptor.PLATFORM.lower(): SgeAdaptor,
    BcsAdaptor.PLATFORM.lower(): BcsAdaptor,
    AwsAdaptor.PLATFORM.lower(): AwsAdaptor
}

def create_adaptor(backend: str= None) -> BaseAdaptor:
    if not backend:
        return BaseAdaptor()
    if backend not in SUPPORTTED_BACKENDS:
        raise RuntimeError(f"当前未支持{backend}平台")
    cls = SUPPORTTED_BACKENDS[backend]
    return cls()