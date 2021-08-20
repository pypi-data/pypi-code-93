# -*- coding: utf-8 -*-
# auto-generated module
# fmt: off
# pylint: skip-file
import numba as nb
import numpy as np

from ..partonic_vars import build_eta, build_xi
from . import cgBar1

Power = np.power
ln = np.log
pi = np.pi


@nb.njit("f8(f8,f8)", cache=True)
def cqBarF1_F2_VV(xi, eta):
    rho, beta, chi = build_eta(eta)
    rhoq, betaq, chiq = build_xi(xi)
    h1 = cgBar1.cgBar1_h1(xi,eta)
    return (256*chi*chiq*(3*h1*rho*(rho - rhoq)*(-1 + rhoq)*(-2*rhoq + rho*(4 + rhoq)) - 2*beta*(-1 + rhoq)*rhoq*(-7*rho*rhoq - Power(rhoq,2) + Power(rho,2)*(16 + rhoq)) + rho*(-1 + rhoq)*(-21*rho*rhoq + 3*Power(rhoq,2) + Power(rho,2)*(14 + (-6 + rhoq)*rhoq))*ln(chi) + betaq*(-rho + rhoq)*(-2*rho*rhoq*(4 + rhoq) + Power(rhoq,2)*(4 + rhoq) + Power(rho,2)*(-14 + 19*rhoq))*ln((chi + chiq)/(1 + chi*chiq))))/(9.*(-1 + beta)*Power(1 + beta,5)*Power(1 + betaq,8)*Power(chi + chiq,3)*Power(1 + chi*chiq,3)*Power(1 - Power(chiq,2),2)*pi)

@nb.njit("f8(f8,f8)", cache=True)
def cqBarF1_FL_VV(xi, eta):
    rho, beta, chi = build_eta(eta)
    rhoq, betaq, chiq = build_xi(xi)
    
    return (256*chi*chiq*(-2*beta*(-1 + rhoq)*rhoq*(2*rho*Power(rhoq,2) + (2 - 3*rhoq)*Power(rhoq,2) + Power(rho,2)*(-6 + 5*rhoq)) - 4*Power(rho,2)*Power(-1 + rhoq,2)*(rho*(-3 + rhoq) + 3*rhoq)*ln(chi) + betaq*(-rho + rhoq)*(2*rho*Power(rhoq,2) + Power(rhoq,3)*(-4 + 3*rhoq) + Power(rho,2)*(12 + rhoq*(-22 + 9*rhoq)))*ln((chi + chiq)/(1 + chi*chiq))))/(9.*(-1 + beta)*Power(1 + beta,5)*Power(1 + betaq,8)*Power(chi + chiq,3)*Power(1 + chi*chiq,3)*Power(1 - Power(chiq,2),2)*pi*(-1 + rhoq))

@nb.njit("f8(f8,f8)", cache=True)
def cqBarF1_x2g1_VV(xi, eta):
    rho, beta, chi = build_eta(eta)
    rhoq, betaq, chiq = build_xi(xi)
    h1 = cgBar1.cgBar1_h1(xi,eta)
    return (256*chi*chiq*(-36*beta*rho*(rho - rhoq)*Power(-1 + rhoq,2)*rhoq + 6*h1*rho*Power(-1 + rhoq,2)*(2*Power(rho,2) - 3*rho*rhoq + Power(rhoq,2)) - 3*rho*(rho - rhoq)*Power(-1 + rhoq,2)*(rho*(-6 + rhoq) + 7*rhoq)*ln(chi) - 6*betaq*rho*Power(-1 + rhoq,2)*(3*Power(rho,2) - 4*rho*rhoq + Power(rhoq,2))*ln((chi + chiq)/(1 + chi*chiq))))/(9.*(-1 + beta)*Power(1 + beta,5)*Power(1 + betaq,8)*Power(chi + chiq,3)*Power(1 + chi*chiq,3)*Power(1 - Power(chiq,2),2)*pi*(-1 + rhoq))

@nb.njit("f8(f8,f8)", cache=True)
def cqBarF1_F2_AA(xi, eta):
    rho, beta, chi = build_eta(eta)
    rhoq, betaq, chiq = build_xi(xi)
    h1 = cgBar1.cgBar1_h1(xi,eta)
    return (256*chi*chiq*(-3*h1*rho*(rho - rhoq)*(-1 + rhoq)*(rho*(-4 + rhoq) - 2*(-1 + rhoq)*rhoq) + beta*(-1 + rhoq)*rhoq*(Power(rho,2)*(-32 + rhoq) + rho*(14 - 3*rhoq)*rhoq + 2*Power(rhoq,2)) + (rho*(-1 + rhoq)*(6*Power(rhoq,2)*(1 + rhoq) + 3*rho*rhoq*(-14 + (-6 + rhoq)*rhoq) - Power(rho,2)*(-28 + Power(rhoq,2)))*ln(chi))/2. + betaq*(Power(rho,3)*(14 - 13*rhoq) + 3*Power(rho,2)*(-2 + rhoq)*rhoq + (4 - 5*rhoq)*Power(rhoq,3) + 3*rho*Power(rhoq,2)*(-4 + 5*rhoq))*ln((chi + chiq)/(1 + chi*chiq))))/(9.*(-1 + beta)*Power(1 + beta,5)*Power(1 + betaq,8)*Power(chi + chiq,3)*Power(1 + chi*chiq,3)*Power(1 - Power(chiq,2),2)*pi)

@nb.njit("f8(f8,f8)", cache=True)
def cqBarF1_FL_AA(xi, eta):
    rho, beta, chi = build_eta(eta)
    rhoq, betaq, chiq = build_xi(xi)
    h1 = cgBar1.cgBar1_h1(xi,eta)
    return (128*chi*chiq*(12*h1*rho*(rho - rhoq)*(-1 + rhoq)*Power(rhoq,2) - 2*beta*(-1 + rhoq)*rhoq*(-4*Power(rhoq,2) + 3*rho*Power(rhoq,2) + Power(rho,2)*(12 + rhoq)) + rho*(-1 + rhoq)*(6*Power(rhoq,3) + 3*rho*rhoq*(-8 + (-6 + rhoq)*rhoq) + Power(rho,2)*(24 + (-4 + rhoq)*rhoq))*ln(chi) - 8*betaq*(3*Power(rho,2)*rhoq - 3*rho*Power(rhoq,3) + Power(rhoq,4) + Power(rho,3)*(-3 + 2*rhoq))*ln((chi + chiq)/(1 + chi*chiq))))/(9.*(-1 + beta)*Power(1 + beta,5)*Power(1 + betaq,8)*Power(chi + chiq,3)*Power(1 + chi*chiq,3)*Power(1 - Power(chiq,2),2)*pi)

@nb.njit("f8(f8,f8)", cache=True)
def cqBarF1_x2g1_AA(xi, eta):
    rho, beta, chi = build_eta(eta)
    rhoq, betaq, chiq = build_xi(xi)
    h1 = cgBar1.cgBar1_h1(xi,eta)
    return (256*chi*chiq*(-36*beta*rho*(rho - rhoq)*Power(-1 + rhoq,2)*rhoq + 6*h1*rho*Power(-1 + rhoq,2)*(2*Power(rho,2) - 3*rho*rhoq + Power(rhoq,2)) - 3*rho*(rho - rhoq)*Power(-1 + rhoq,2)*(rho*(-6 + rhoq) + 7*rhoq)*ln(chi) - 6*betaq*rho*Power(-1 + rhoq,2)*(3*Power(rho,2) - 4*rho*rhoq + Power(rhoq,2))*ln((chi + chiq)/(1 + chi*chiq))))/(9.*(-1 + beta)*Power(1 + beta,5)*Power(1 + betaq,8)*Power(chi + chiq,3)*Power(1 + chi*chiq,3)*Power(1 - Power(chiq,2),2)*pi*(-1 + rhoq))
