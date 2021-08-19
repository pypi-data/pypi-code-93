import argparse, os
import numpy as np

def check(num):
    if num < 10:
        num = 10
    if num % 2 != 0:
        num += 1
    if num % 4 != 0:
        num += 2
    return num

def main():
    parser = argparse.ArgumentParser(description='spins2cpu: A Monte Carlo Simulation Code for the Phase Transition in 2D/3D Materials',
                                     epilog='''
configurations:      init:                             parameters:         model:
triangle             fm, afm1, afm2, afm3              Ja, Jb, Jc          ising, single, mae
c_rectangle          fm, afm1, afm2, afm3, afm4, afm5  Ja, Jb, Jc, Jd, Je  ising, single, mae
ammm                 fm, afm1, afm2, afm3, afm4        Ja, Jb, Jc          ising               (CQ)
square               fm, afm1, afm2, afm3              Ja, Jb, Jc          ising, single, mae
rectangle            fm, afm1, afm2, afm3, afm4, afm5  Ja, Jb, Jc, Jd, Je  ising, single, mae
honeycomb            fm, afm1, random                  Ja, Jb, Jc          ising, single
p6mmm                fm, afm1, afm2, afm3              Ja, J0, J1          ising, single       (1H)
i_p6mmm              fm, afm1, afm2, afm3              Ja, J0, J1          ising, single       (M3×3)
p3m1                 fm, afm1, afm2, afm3              Ja, J0, J1          ising, single       (1T)
c2m                  fm, afm1, afm2, afm3, afm4        Ja, Jb, J0, J1      ising, single, mae
kagome               fm, random                        Ja                  ising
cube                 fm, afm1                          Ja, Jb, Jc          ising

default values:
x, y, z = 64, 64, 64
iterations for equilibrium, works = 64, 64
exchange coupling (meV) = 1.0
single-ion anisotropy (meV) = 0.1
temperatures = 0 15 5 16 60

Example:
spins2cpu -c square -x 200 -y 200 -e 200 -w 1000 -t 35 -r
''',
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', "--version", action="version", version="spins2cpu 0.1.3")
    parser.add_argument('-x', "--length",       type=int,   default=64)
    parser.add_argument('-y', "--width",        type=int,   default=64)
    parser.add_argument('-z', "--height",       type=int,   default=64)
    parser.add_argument('-e', "--equilibrium",  type=int,   default=64)
    parser.add_argument('-w', "--works",        type=int,   default=64)
    parser.add_argument('-a', "--single",       type=float, default=[0.1], nargs='+')
    parser.add_argument('-p', "--parameters",   type=float, default=[1.0], nargs='+')
    parser.add_argument('-j', "--parametersX",  type=float, default=[], nargs='+')
    parser.add_argument('-k', "--parametersY",  type=float, default=[], nargs='+')
    parser.add_argument('-t', "--temperatures", type=float, default=[0, 15, 5, 16, 60], nargs='+')
    parser.add_argument('-s', "--sample", action='store_true', help="show sample")
    parser.add_argument('-r', "--export", action='store_true', help="plot figures after iterations")
    parser.add_argument('-o', "--plot",   type=str, help="plot figures from .log file")
    parser.add_argument('-m', "--model",  default="ising",    type=str.lower, choices=['ising', 'single', 'mae'])
    parser.add_argument('-i', "--init",   default="fm",       type=str.lower, choices=['fm', 'afm1', 'afm2','afm3', 'afm4', 'afm5', 'random'])
    parser.add_argument('-c', "--config", default="triangle", type=str.lower,
                        choices=['triangle', 'c_rectangle', 'ammm', 'square', 'rectangle', 'honeycomb', 'p6mmm', 'i_p6mmm', 'p3m1', 'c2m', 'kagome', 'cube'])
    args = parser.parse_args()

    X = check(args.length)
    Y = check(args.width)
    Z = check(args.height)
    config = args.config
    init = args.init

    i = len(args.temperatures)
    if i == 1:
        arrays_temperatures = np.arange(args.temperatures[0]+1)
    elif i == 2:
        arrays_temperatures = np.arange(args.temperatures[0], args.temperatures[1]+1)
    else:
        k = i // 3
        l = i % 3
        arrays_temperatures = np.arange(args.temperatures[0], args.temperatures[1]+1, args.temperatures[2])
        j = 1
        while j < k:
            arrays_temperatures=np.concatenate((arrays_temperatures,
                np.arange(args.temperatures[j * 3], args.temperatures[j * 3 + 1]+1, args.temperatures[j * 3 + 2])))
            j += 1
        if l == 2:
            arrays_temperatures=np.concatenate((arrays_temperatures,
                np.arange(args.temperatures[j * 3], args.temperatures[j * 3 + 1]+1)))

    nequilibrium = args.equilibrium
    nworks = args.works
    J = args.parameters
    A = args.single
    JX = args.parametersX
    JY = args.parametersY

    if args.plot and os.path.exists(args.plot):
        from spins2cpu import plots
        plots.main(args.plot)
    elif args.sample:
        from spins2cpu import plots, sample
        f = open('honeycomb_200_200.log', 'w')
        print(sample.honeycomb)
        print(sample.honeycomb, file=f)
        f.close()
        plots.main('honeycomb_200_200.log')
    else:
        if args.model == "ising":
            if config == "triangle":
                file = '{}_{}_{}.log'.format(config, X, Y)
                from spins2cpu.ising import triangle
                triangle.run(file, init, X, Y, J, arrays_temperatures, nequilibrium, nworks)
            elif config == "c_rectangle":
                file = '{}_{}_{}.log'.format(config, X, Y)
                from spins2cpu.ising import c_rectangle
                c_rectangle.run(file, init, X, Y, J, arrays_temperatures, nequilibrium, nworks)
            elif config == "ammm":
                file = '{}_{}_{}.log'.format(config, X, Y)
                from spins2cpu.ising import ammm
                ammm.run(file, init, X, Y, J, arrays_temperatures, nequilibrium, nworks)
            elif config == "square":
                file = '{}_{}_{}.log'.format(config, X, Y)
                from spins2cpu.ising import square
                square.run(file, init, X, Y, J, arrays_temperatures, nequilibrium, nworks)
            elif config == "rectangle":
                file = '{}_{}_{}.log'.format(config, X, Y)
                from spins2cpu.ising import rectangle
                rectangle.run(file, init, X, Y, J, arrays_temperatures, nequilibrium, nworks)
            elif config == "honeycomb":
                file = '{}_{}_{}.log'.format(config, X, Y)
                from spins2cpu.ising import honeycomb
                honeycomb.run(file, init, X, Y, J, arrays_temperatures, nequilibrium, nworks)
            elif config == "p6mmm":
                file = '{}_{}_{}.log'.format(config, X, Y)
                from spins2cpu.ising import p6mmm
                p6mmm.run(file, init, X, Y, J, arrays_temperatures, nequilibrium, nworks)
            elif config == "i_p6mmm":
                file = '{}_{}_{}.log'.format(config, X, Y)
                from spins2cpu.ising import i_p6mmm
                i_p6mmm.run(file, init, X, Y, J, arrays_temperatures, nequilibrium, nworks)
            elif config == "p3m1":
                file = '{}_{}_{}.log'.format(config, X, Y)
                from spins2cpu.ising import p3m1
                p3m1.run(file, init, X, Y, J, arrays_temperatures, nequilibrium, nworks)
            elif config == "c2m":
                file = '{}_{}_{}.log'.format(config, X, Y)
                from spins2cpu.ising import c2m
                c2m.run(file, init, X, Y, J, arrays_temperatures, nequilibrium, nworks)
            elif config == "kagome":
                file = '{}_{}_{}.log'.format(config, X, Y)
                from spins2cpu.ising import kagome
                kagome.run(file, init, X, Y, J, arrays_temperatures, nequilibrium, nworks)
            elif config == "cube":
                file = '{}_{}_{}_{}.log'.format(config, X, Y, Z)
                from spins2cpu.ising import cube
                cube.run(file, init, X, Y, Z, J, arrays_temperatures, nequilibrium, nworks)
            else:
                print("Inconsistent parameters...")
        elif args.model == "single":
            if config == "triangle":
                file = '{}_single_{}_{}.log'.format(config, X, Y)
                from spins2cpu.single import triangle
                triangle.run(file, init, X, Y, J, A, arrays_temperatures, nequilibrium, nworks)
            elif config == "c_rectangle":
                file = '{}_single_{}_{}.log'.format(config, X, Y)
                from spins2cpu.single import c_rectangle
                c_rectangle.run(file, init, X, Y, J, A, arrays_temperatures, nequilibrium, nworks)
            elif config == "square":
                file = '{}_single_{}_{}.log'.format(config, X, Y)
                from spins2cpu.single import square
                square.run(file, init, X, Y, J, A, arrays_temperatures, nequilibrium, nworks)
            elif config == "rectangle":
                file = '{}_single_{}_{}.log'.format(config, X, Y)
                from spins2cpu.single import rectangle
                rectangle.run(file, init, X, Y, J, A, arrays_temperatures, nequilibrium, nworks)
            elif config == "honeycomb":
                file = '{}_single_{}_{}.log'.format(config, X, Y)
                from spins2cpu.single import honeycomb
                honeycomb.run(file, init, X, Y, J, A, arrays_temperatures, nequilibrium, nworks)
            elif config == "p6mmm":
                file = '{}_single_{}_{}.log'.format(config, X, Y)
                from spins2cpu.single import p6mmm
                p6mmm.run(file, init, X, Y, J, A, arrays_temperatures, nequilibrium, nworks)
            elif config == "i_p6mmm":
                file = '{}_single_{}_{}.log'.format(config, X, Y)
                from spins2cpu.single import i_p6mmm
                i_p6mmm.run(file, init, X, Y, J, A, arrays_temperatures, nequilibrium, nworks)
            elif config == "p3m1":
                file = '{}_single_{}_{}.log'.format(config, X, Y)
                from spins2cpu.single import p3m1
                p3m1.run(file, init, X, Y, J, A, arrays_temperatures, nequilibrium, nworks)
            elif config == "c2m":
                file = '{}_single_{}_{}.log'.format(config, X, Y)
                from spins2cpu.single import c2m
                c2m.run(file, init, X, Y, J, A, arrays_temperatures, nequilibrium, nworks)
            else:
                print("Inconsistent parameters...")
        elif args.model == "mae":
            if config == "triangle":
                file = '{}_mae_{}_{}.log'.format(config, X, Y)
                from spins2cpu.mae import triangle
                triangle.run(file, init, X, Y, J, JX, JY, A, arrays_temperatures, nequilibrium, nworks)
            elif config == "c_rectangle":
                file = '{}_mae_{}_{}.log'.format(config, X, Y)
                from spins2cpu.mae import c_rectangle
                c_rectangle.run(file, init, X, Y, J, JX, JY, A, arrays_temperatures, nequilibrium, nworks)
            elif config == "square":
                file = '{}_mae_{}_{}.log'.format(config, X, Y)
                from spins2cpu.mae import square
                square.run(file, init, X, Y, J, JX, JY, A, arrays_temperatures, nequilibrium, nworks)
            elif config == "rectangle":
                file = '{}_single_{}_{}.log'.format(config, X, Y)
                from spins2cpu.mae import rectangle
                rectangle.run(file, init, X, Y, J, JX, JY, A, arrays_temperatures, nequilibrium, nworks)
            elif config == "c2m":
                file = '{}_single_{}_{}.log'.format(config, X, Y)
                from spins2cpu.mae import c2m
                c2m.run(file, init, X, Y, J, JX, JY, A, arrays_temperatures, nequilibrium, nworks)
            else:
                print("Inconsistent parameters...")
        else:
            print("Inconsistent parameters...")

        if args.export and os.path.exists(file):
            from spins2cpu import plots
            plots.main(file)
