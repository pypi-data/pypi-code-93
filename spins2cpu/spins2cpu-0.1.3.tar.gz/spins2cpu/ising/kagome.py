import logging
import numpy as np
from spins2cpu import functions
from spins2cpu.ising import kagome_update

kB = 8.61733e-2 # 玻尔兹曼常数(meV/K)

def run(file, init, X, Y, J, arrays_temperatures, nequilibrium, nworks):
    logging.basicConfig(level=logging.INFO,format="%(message)s",filename=file,filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    N = X * Y
    num = N * 3
    logging.info("{} {:<12} {} {} × {:<8} {} {} + {:<8} {} {}".format(
        "configuration:", file.split('_')[0], "lattice dimensions:", X, Y, "iterations:", nequilibrium, nworks, "Atom number:", num))
    p = len(J)
    np.seterr(divide='ignore', invalid='ignore')
    arrays_values = np.where(arrays_temperatures < 0.01, 0, 1.0/(arrays_temperatures * kB))
    lav = len(arrays_values)
    if p == 1:
        Ja = J[0]
        logging.info("{} {:<8} {} {:<8}".format("init:", init, "parameters(meV):", Ja))
        if init == "fm":
            logging.info("{:>16} {:>16}".format("Round", "magnetism"))
            latt = functions.Onesint3(3, Y, X)
            m_ave = functions.Average(latt)
            logging.info("{:>16} {:>16.6}".format(0, m_ave))
            logging.info("{:>16} {:>16} {:>16} {:>16} {:>16}".format("Temperature", "magnetism", "susceptibility", "specific heat", "time(s)"))
            for i in range(lav):
                t, Nw, Ew = kagome_update.iteration(latt, X, Y, Ja, arrays_values[i], nequilibrium, nworks)
                m_ave = functions.Average(Nw)
                s_ave = functions.Average2(Nw)
                susceptibility = arrays_values[i] * num * (s_ave - m_ave ** 2)
                Cv = arrays_values[i] ** 2 * (functions.Average2(Ew) - functions.Average(Ew) ** 2) / num
                logging.info("{:>16.2f} {:>16.6f} {:>16.6f} {:>16.6f} {:>16.6f}".format(arrays_temperatures[i], m_ave, susceptibility, Cv, t))
        elif init == "random":
            logging.info("{:>16} {:>16} {:>16}".format("Round", "magnetism", "time(s)"))
            latt = functions.Uniformint3(3, Y, X)
            m_ave = functions.Average(latt)
            logging.info("{:>16} {:>16.6f}".format(0, m_ave))
            for i in range(1,21):
                val = i + np.random.rand() + 1
                t, m_ave = kagome_update.looping(latt, X, Y, Ja, val, nequilibrium)
                logging.info("{:>16} {:>16.6f} {:>16.6f}".format(i, m_ave, t))
                if abs(m_ave) > 0.99:
                    break
            if abs(m_ave) > 0.99:
                logging.info("init: fm")
                logging.info("{:>16} {:>16} {:>16} {:>16} {:>16}".format("Temperature", "magnetism", "susceptibility", "specific heat", "time(s)"))
                for i in range(lav):
                    t, Nw, Ew = kagome_update.iteration(latt, X, Y, Ja, arrays_values[i], nequilibrium, nworks)
                    m_ave = functions.Average(Nw)
                    s_ave = functions.Average2(Nw)
                    susceptibility = arrays_values[i] * num * (s_ave - m_ave ** 2)
                    Cv = arrays_values[i] ** 2 * (functions.Average2(Ew) - functions.Average(Ew) ** 2) / num
                    logging.info("{:>16.2f} {:>16.6f} {:>16.6f} {:>16.6f} {:>16.6f}".format(arrays_temperatures[i], m_ave, susceptibility, Cv, t))
        else:
            print("Inconsistent parameters...")

    else:
        print("Inconsistent parameters...")
