from hashlib import md5
import random
import time

__author__ = 'osso'


# dd if=/dev/zero of=output.dat  bs=1M  count=1 && md5sum output.dat
OPTIONS = {
    'KB': {
        'md5_hash': '0f343b0931126a20f133d67c2b018a3b',
        'size': 1024},
    'MB': {
        'md5_hash': 'b6d81b360a5672d80c27430f39153e2c',
        'size': 1024 ** 2}
}


class SpuriousReadError(OSError):
    pass


class DiskEmptySampler(object):
    """
    Divide the disk in 'sample_count' regions
    and sample (md5sum) 'sample_size' bytes randomly per region
    """

    def __init__(self, devname, sample_count=100, sample_size='MB'):
        if sample_size not in OPTIONS:
            raise Exception('Unknown sample_size, options are {0}'.format(
                OPTIONS.keys()))
        self.devname = devname

        # No divide by zero errors
        if sample_count == 0:
            raise Exception('Sample size should not be zero')

        self.sample_count = sample_count
        self.sample_size_opt = sample_size
        self.expected_hash = OPTIONS[sample_size]['md5_hash']
        self.sample_size = OPTIONS[sample_size]['size']

    def sample_disk(self):
        attempts = 3
        for attempt in range(1, attempts + 1):
            try:
                ret = self._sample_disk()
            except SpuriousReadError:
                if attempt == attempts:
                    raise
                print('WARNING: Read error. Possibly too fast after disk wipe')
                time.sleep(5)
                print('Retrying...')
            else:
                break
        return ret

    def _sample_disk(self):
        is_empty = True

        with open(self.devname, 'rb') as fp:
            # Get the size of disk (e.g. 256GB).
            size = fp.seek(0, 2)

            # Divide the disk into sample_regions (e.g. 256GB/2000 = ~131MB).
            sample_region_size = size // self.sample_count

            # Check if the regions are large enough to get a sample from.
            if self.sample_size > sample_region_size:
                print('ERROR: Sample size is too large: {} > {}/{}'.format(
                    self.sample_size, size, self.sample_count))
                return None

            # Loop over the sample_regions and select a random sample inside
            # that region:
            # - 0: first 131MB: choose a random sample_size block there
            # - 1: second 131MB: choose a random sample_size block there
            # ..etc..
            for sample_nr in range(self.sample_count):
                # Calculate begin and end of region based on sample_region
                # size and pick a random offset in it:
                region_start = sample_nr * sample_region_size
                region_end_ex = min((sample_nr + 1) * sample_region_size, size)
                offset = random.randint(
                    region_start, region_end_ex - self.sample_size)

                # Jump there, and fetch block.
                fp.seek(offset)
                try:
                    data = fp.read(self.sample_size)
                except OSError as e:
                    # On NVMe drives, we have seen that a read() here
                    # fails immediately after an nvme sanitize
                    # operation. The SpuriousReadError allows us to back
                    # off and retry after a little sleep.
                    errno = e.args[0]
                    if errno == 5:  # EIO
                        raise SpuriousReadError() from e
                    raise

                # Check if md5 is same as the expected_hash
                md5_sum = md5(data).hexdigest()
                if md5_sum != self.expected_hash:
                    print('Digests are not same: {0} {1}'.format(
                        md5_sum, self.expected_hash))
                    print('for offset: {0} (sample_size: {1})'.format(
                        offset, self.sample_size))
                    is_empty = False
                    break

        return is_empty
