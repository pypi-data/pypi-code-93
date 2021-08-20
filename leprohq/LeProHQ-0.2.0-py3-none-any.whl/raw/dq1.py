# -*- coding: utf-8 -*-
# auto-generated module
# fmt: off
# pylint: skip-file
import numba as nb
import numpy as np

from ..partonic_vars import build_eta, build_prime
from ..utils import Li2

Power = np.power
ln = np.log
pi = np.pi


@nb.njit("f8(f8,f8)", cache=True)
def dq1_h4(xi, eta):
    rho, beta, chi = build_eta(eta)
    rhop, betap, chip = build_prime(xi,eta)
    return -Li2(((1 + chi)*chip)/(1 + chip)) + Li2(((1 + chi)*chip)/(chi*(1 + chip))) + Li2((1 + chip)/(1 + chi)) - Li2((chi*(1 + chip))/(1 + chi)) + Power(ln(chi),2)/2. + ln(chi)*(ln(1 + chi) - ln(chi - chip) + ln(1 + chip) - ln(1 - chi*chip))


@nb.njit("f8(f8,f8)", cache=True)
def dq1_F2_VV(xi, eta):
    rho, beta, chi = build_eta(eta)
    rhop, betap, chip = build_prime(xi,eta)
    h4 = dq1_h4(xi,eta)
    return (beta*(2*Power(rho,2)*(718 + 5*rho) - 4*rho*(758 + 91*rho)*rhop + (2488 + 5108*rho)*Power(rhop,2) - 6456*Power(rhop,3)) + h4*(-288*Power(rho,2) + 288*rho*rhop + 36*(-4 + 3*Power(rho,2))*Power(rhop,2) - 972*rho*Power(rhop,3) + 972*Power(rhop,4)) + (27*Power(rho,2)*(-8 + Power(rho,2)) + 18*rho*(8 + 3*Power(rho,2))*rhop + 486*Power(rho,2)*Power(rhop,2) - 972*rho*Power(rhop,3))*ln(chi) + betap*(912*Power(rho,2) - 24*rho*(56 + 23*rho)*rhop + 48*(17 + 52*rho)*Power(rhop,2) - 2256*Power(rhop,3))*ln((chi - chip)/(1 - chi*chip)))/(5184.*pi*rho)

@nb.njit("f8(f8,f8)", cache=True)
def dq1_FL_VV(xi, eta):
    rho, beta, chi = build_eta(eta)
    rhop, betap, chip = build_prime(xi,eta)
    h4 = dq1_h4(xi,eta)
    return (rhop*(beta*(4*rho*(-38 + 23*rho) + (200 + 532*rho)*rhop - 744*Power(rhop,2)) + h4*(-108*rho*Power(rhop,2) + 108*Power(rhop,3)) + (18*Power(rho,3) + 54*Power(rho,2)*rhop - 108*rho*Power(rhop,2))*ln(chi) + betap*(-48*rho + (48 + 264*rho)*rhop - 264*Power(rhop,2))*ln((chi - chip)/(1 - chi*chip))))/(864.*pi*rho)

@nb.njit("f8(f8,f8)", cache=True)
def dq1_x2g1_VV(xi, eta):
    rho, beta, chi = build_eta(eta)
    rhop, betap, chip = build_prime(xi,eta)
    h4 = dq1_h4(xi,eta)
    return (beta*(2*Power(rho,2)*(718 + 5*rho) - 4*rho*(530 + 229*rho)*rhop + 8*(218 + 205*rho)*Power(rhop,2) - 1200*Power(rhop,3)) + h4*(-288*Power(rho,2) + 288*rho*rhop + 36*(-4 + 3*Power(rho,2))*Power(rhop,2) - 108*rho*Power(rhop,3)) + (27*Power(rho,2)*(-8 + Power(rho,2)) + 9*rho*(16 - 6*Power(rho,2))*rhop + 108*Power(rho,2)*Power(rhop,2))*ln(chi) + betap*(912*Power(rho,2) - 24*rho*(44 + 23*rho)*rhop + (672 + 912*rho)*Power(rhop,2) - 600*Power(rhop,3))*ln((chi - chip)/(1 - chi*chip)))/(5184.*pi*rho)

@nb.njit("f8(f8,f8)", cache=True)
def dq1_F2_AA(xi, eta): 
    return dq1_F2_VV(xi, eta)

@nb.njit("f8(f8,f8)", cache=True)
def dq1_FL_AA(xi, eta): 
    return dq1_FL_VV(xi, eta)

@nb.njit("f8(f8,f8)", cache=True)
def dq1_x2g1_AA(xi, eta): 
    return dq1_x2g1_VV(xi, eta)

@nb.njit("f8(f8,f8)", cache=True)
def dq1_xF3_VA(xi, eta):
    return dq1_x2g1_VV(xi, eta)

@nb.njit("f8(f8,f8)", cache=True)
def dq1_g4_VA(xi, eta):
    return -dq1_F2_VV(xi, eta)

@nb.njit("f8(f8,f8)", cache=True)
def dq1_gL_VA(xi, eta):
    return -dq1_FL_VV(xi, eta)
