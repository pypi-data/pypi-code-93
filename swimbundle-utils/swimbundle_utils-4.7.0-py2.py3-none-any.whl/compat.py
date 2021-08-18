import itertools
import iocextract
import timeout_decorator
from iocextract import extract_ips, extract_emails, extract_hashes, extract_urls


class TimeoutError(Exception):
    pass


def _extract_iocs_without_yara(data, refang=True, strip=False):
    """Extract all IOCs.

    Note: this is a patch from extract_iocs function in iocextract where matching yara rules causes
          hanging on long texts of strings due to exponential regex usage in the package.
          In ioc.py we try/except with these functions. I simply removed "extract_yara_rules()"
    """
    return itertools.chain(
        extract_urls(data, refang=refang, strip=strip),
        extract_ips(data, refang=refang),
        extract_emails(data, refang=refang),
        extract_hashes(data),
    )


@timeout_decorator.timeout(10, use_signals=False, timeout_exception=TimeoutError)
def _extract_iocs(data):
    """
    This calls the extract_iocs call with a timeout decorator in case yara hang persists.
    """

    return set(iocextract.extract_iocs(data, refang=True))
