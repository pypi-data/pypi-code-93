# -*- coding: utf-8 -*-
# auto-generated module
# fmt: off
# pylint: skip-file
import numba as nb
import numpy as np

from ..partonic_vars import build_eta, build_xi
from ..utils import Li2

Power = np.power
ln = np.log
pi = np.pi

@nb.njit("f8(f8,f8)", cache=True)
def cgBar1_h1(xi, eta):
    rho, beta, chi = build_eta(eta)
    rhoq, betaq, chiq = build_xi(xi)
    return -Power(pi,2)/6. - 2*Li2(-chi) + Li2((1 - chiq)/(1 + chi)) - Li2((chi*(1 - chiq))/(1 + chi)) - Li2(-((chi*(1 - chiq))/((1 + chi)*chiq))) + Li2((-1 + chiq)/((1 + chi)*chiq)) + Power(ln(chi),2)/2. + ln(chi)*(ln(chiq) - ln(chi + chiq) - ln(1 + chi*chiq));

@nb.njit("f8(f8,f8)", cache=True)
def cgBar1_h2(xi, eta):
    rho, beta, chi = build_eta(eta)
    rhoq, betaq, chiq = build_xi(xi)
    return -Power(pi,2)/6. + 2*Li2(-chi) + 2*Li2(chi) - ln(chi)/2. - ln(chi)*(ln(chiq) - ln(chi + chiq) - ln(1 + chi*chiq));

@nb.njit("f8(f8,f8)", cache=True)
def cgBar1_h3(xi, eta):
    rho, beta, chi = build_eta(eta)
    rhoq, betaq, chiq = build_xi(xi)
    return ln(1 - chi) + ln(1 + chi) + (-ln(chi) + ln(chiq) - ln(chi + chiq) - ln(1 + chi*chiq))/2.;



@nb.njit("f8(f8,f8)", cache=True)
def cgBar1_F2_VV(xi, eta):
    rho, beta, chi = build_eta(eta)
    rhoq, betaq, chiq = build_xi(xi)
    h1 = cgBar1_h1(xi,eta)
    h2 = cgBar1_h2(xi,eta)
    h3 = cgBar1_h3(xi,eta)
    return (8*chi*chiq*(96*beta*h3*rho*(-1 + rhoq)*(Power(rho,2) + Power(rhoq,2) + rho*rhoq*(6 + rhoq)) + 48*h1*rho*(rho - rhoq)*(-1 + rhoq)*(-rhoq + rho*(5 + 2*rhoq)) + 2*beta*(-1 + rhoq)*rhoq*(62*rho*rhoq + 8*Power(rhoq,2) - Power(rho,2)*(632 + 95*rhoq)) + 24*h2*rho*(-1 + rhoq)*(-2*Power(rhoq,2) - 2*rho*Power(rhoq,2) + Power(rho,2)*(-2 + (-4 + rhoq)*rhoq)) + rho*(-1 + rhoq)*(568*Power(rho,2) - 48*rho*(11 + 8*rho)*rhoq + (48 + rho*(-96 + 59*rho))*Power(rhoq,2))*ln(chi) - 8*betaq*(rho - rhoq)*(-2*rho*rhoq*(4 + rhoq) + Power(rhoq,2)*(4 + rhoq) + Power(rho,2)*(-68 + 73*rhoq))*ln((chi + chiq)/(1 + chi*chiq))))/((-1 + beta)*Power(1 + beta,5)*Power(1 + betaq,8)*Power(chi + chiq,3)*Power(1 + chi*chiq,3)*Power(1 - Power(chiq,2),2)*pi)


@nb.njit("f8(f8,f8)", cache=True)
def cgBar1_FL_VV(xi, eta):
    rho, beta, chi = build_eta(eta)
    rhoq, betaq, chiq = build_xi(xi)
    
    h2 = cgBar1_h2(xi,eta)
    h3 = cgBar1_h3(xi,eta)
    return (64*chi*chiq*(48*beta*h3*Power(rho,2)*Power(-1 + rhoq,2)*rhoq - 12*h2*Power(rho,3)*Power(-1 + rhoq,2)*rhoq + 2*beta*(-1 + rhoq)*rhoq*(36*Power(rho,2) - 35*Power(rho,2)*rhoq - 2*(1 + rho)*Power(rhoq,2) + 3*Power(rhoq,3)) - 8*Power(rho,2)*Power(-1 + rhoq,2)*(3*rhoq + rho*(-6 + 5*rhoq))*ln(chi) + betaq*(-rho + rhoq)*(2*rho*Power(rhoq,2) + Power(rhoq,3)*(-4 + 3*rhoq) + Power(rho,2)*(-6 + 5*rhoq)*(-8 + 9*rhoq))*ln((chi + chiq)/(1 + chi*chiq))))/((-1 + beta)*Power(1 + beta,5)*Power(1 + betaq,8)*Power(chi + chiq,3)*Power(1 + chi*chiq,3)*Power(1 - Power(chiq,2),2)*pi*(-1 + rhoq))


@nb.njit("f8(f8,f8)", cache=True)
def cgBar1_x2g1_VV(xi, eta):
    rho, beta, chi = build_eta(eta)
    rhoq, betaq, chiq = build_xi(xi)
    h1 = cgBar1_h1(xi,eta)
    h2 = cgBar1_h2(xi,eta)
    h3 = cgBar1_h3(xi,eta)
    return (192*chi*chiq*(-1 + rhoq)*(4*h1*rho*(rho - rhoq)*(2*rho - rhoq) + 32*beta*rho*rhoq*(-rho + rhoq) - 2*h2*rho*(rho - rhoq)*(rho + rhoq) + 4*beta*h3*rho*(rho - rhoq)*(rho + 3*rhoq) - rho*(rho - rhoq)*(11*rhoq + rho*(-13 + 4*rhoq))*ln(chi) - 4*betaq*rho*(3*Power(rho,2) - 4*rho*rhoq + Power(rhoq,2))*ln((chi + chiq)/(1 + chi*chiq))))/((-1 + beta)*Power(1 + beta,5)*Power(1 + betaq,8)*Power(chi + chiq,3)*Power(1 + chi*chiq,3)*Power(1 - Power(chiq,2),2)*pi)


@nb.njit("f8(f8,f8)", cache=True)
def cgBar1_F2_AA(xi, eta):
    rho, beta, chi = build_eta(eta)
    rhoq, betaq, chiq = build_xi(xi)
    h1 = cgBar1_h1(xi,eta)
    h2 = cgBar1_h2(xi,eta)
    h3 = cgBar1_h3(xi,eta)
    return (8*chi*chiq*(2*beta*(-1 + rhoq)*rhoq*(-632*Power(rho,2) + (62 - 95*rho)*rho*rhoq + (8 + 9*(-2 + rho)*rho)*Power(rhoq,2)) + 48*h1*rho*(rho - rhoq)*(-1 + rhoq)*((-1 + rhoq)*rhoq + rho*(5 + rhoq)) + 96*beta*h3*rho*(-1 + rhoq)*(Power(rho,2) + Power(rhoq,2) + rho*rhoq*(6 + rhoq)) + 24*h2*rho*(-1 + rhoq)*(-6*rho*Power(rhoq,2) + 2*(-1 + rhoq)*Power(rhoq,2) + Power(rho,2)*(-2 + (-2 + rhoq)*rhoq)) + rho*(1 - rhoq)*(-48*Power(rhoq,2)*(1 + rhoq) - 24*rho*rhoq*(-22 + (-10 + rhoq)*rhoq) + Power(rho,2)*(-568 + rhoq*(312 + rhoq*(-59 + 9*rhoq))))*ln(chi) - 8*betaq*(rho - rhoq)*((4 - 5*rhoq)*Power(rhoq,2) + 2*rho*rhoq*(-4 + 5*rhoq) + Power(rho,2)*(-68 + 67*rhoq))*ln((chi + chiq)/(1 + chi*chiq))))/((-1 + beta)*Power(1 + beta,5)*Power(1 + betaq,8)*Power(chi + chiq,3)*Power(1 + chi*chiq,3)*Power(1 - Power(chiq,2),2)*pi)


@nb.njit("f8(f8,f8)", cache=True)
def cgBar1_FL_AA(xi, eta):
    rho, beta, chi = build_eta(eta)
    rhoq, betaq, chiq = build_xi(xi)
    h1 = cgBar1_h1(xi,eta)
    h2 = cgBar1_h2(xi,eta)
    h3 = cgBar1_h3(xi,eta)
    return (8*chi*chiq*(192*beta*h3*Power(rho,2)*(-1 + rhoq)*rhoq*(2 + rhoq) + 48*h1*rho*(rho - rhoq)*(-1 + rhoq)*rhoq*(3*rho + rhoq) + 48*h2*rho*(-1 + rhoq)*rhoq*(Power(rho,2)*(-1 + rhoq) - 4*rho*rhoq + Power(rhoq,2)) + 2*beta*(-1 + rhoq)*rhoq*(-288*Power(rho,2) - 184*Power(rho,2)*rhoq + (16 + 9*(-2 + rho)*rho)*Power(rhoq,2)) - rho*(-1 + rhoq)*(-384*Power(rho,2) + 8*rho*(24 + 35*rho)*rhoq - 112*(-3 + rho)*rho*Power(rhoq,2) + 3*(-4 + rho)*(4 + 3*rho)*Power(rhoq,3))*ln(chi) - 32*betaq*(rho - rhoq)*(2*rho*Power(rhoq,2) - Power(rhoq,3) + Power(rho,2)*(-12 + 11*rhoq))*ln((chi + chiq)/(1 + chi*chiq))))/((-1 + beta)*Power(1 + beta,5)*Power(1 + betaq,8)*Power(chi + chiq,3)*Power(1 + chi*chiq,3)*Power(1 - Power(chiq,2),2)*pi)

def cgBar1_x2g1_AA(xi, eta):
    return cgBar1_x2g1_VV(xi, eta)
