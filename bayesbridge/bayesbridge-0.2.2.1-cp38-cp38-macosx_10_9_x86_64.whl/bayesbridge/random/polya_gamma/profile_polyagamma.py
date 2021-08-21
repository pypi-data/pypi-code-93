import cProfile, sys, time
import random
import numpy as np
from polya_gamma import rand_polya_gamma


def generate_samples(tilt):
    n_repetition = 10 ** 6
    for i in range(n_repetition):
        rand_polya_gamma(tilt)

if __name__ == '__main__':
    random.seed(0)
    for tilt in 10. ** np.array([-4, 0, 4]):
        print("Generating PG(1, {:.2g})...\n".format(tilt))
        if len(sys.argv) > 1 and sys.argv[1] == 'profile':
            cProfile.runctx("generate_samples(tilts)", globals(), locals(), sort='time')
            print("\n")
        else:
            start = time.time()
            generate_samples(tilt)
            elapsed = time.time() - start
            print("Took {:.3g} seconds.\n".format(elapsed))