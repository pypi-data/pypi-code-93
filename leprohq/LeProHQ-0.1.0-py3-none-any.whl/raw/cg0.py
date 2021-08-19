# -*- coding: utf-8 -*-
# auto-generated module
# fmt: off
# pylint: skip-file
import numpy as np
from ..partonic_vars import PartonicVars

Power = np.power
ln = np.log
pi = np.pi


def cg0_F2_VV(xi, eta):
    p = PartonicVars(xi,eta)
    rho, beta, chi = p.rho, p.beta, p.chi
    rhoq = p.rho_q
    return (beta*pi*rho*rhoq*(Power(rho,2) + Power(rhoq,2) + rho*rhoq*(6 + rhoq)))/(2.*Power(rho - rhoq,3)) + (pi*rho*rhoq*(2*Power(rhoq,2) + 2*rho*Power(rhoq,2) + Power(rho,2)*(2 - (-4 + rhoq)*rhoq))*ln(chi))/(4.*Power(rho - rhoq,3))

def cg0_FL_VV(xi, eta):
    p = PartonicVars(xi,eta)
    rho, beta, chi = p.rho, p.beta, p.chi
    rhoq = p.rho_q
    return (2*beta*pi*Power(rho,2)*Power(rhoq,2))/Power(rho - rhoq,3) + (pi*Power(rho,3)*Power(rhoq,2)*ln(chi))/Power(rho - rhoq,3)

def cg0_x2g1_VV(xi, eta):
    p = PartonicVars(xi,eta)
    rho, beta, chi = p.rho, p.beta, p.chi
    rhoq = p.rho_q
    return (beta*pi*rho*rhoq*(rho + 3*rhoq))/(2.*Power(rho - rhoq,2)) + (pi*rho*rhoq*(rho + rhoq)*ln(chi))/(2.*Power(rho - rhoq,2))

def cg0_F2_AA(xi, eta):
    p = PartonicVars(xi,eta)
    rho, beta, chi = p.rho, p.beta, p.chi
    rhoq = p.rho_q
    return (beta*pi*rho*rhoq*(Power(rho,2) + Power(rhoq,2) + rho*rhoq*(6 + rhoq)))/(2.*Power(rho - rhoq,3)) + (pi*rho*rhoq*(6*rho*Power(rhoq,2) - 2*(-1 + rhoq)*Power(rhoq,2) + Power(rho,2)*(2 - (-2 + rhoq)*rhoq))*ln(chi))/(4.*Power(rho - rhoq,3))

def cg0_FL_AA(xi, eta):
    p = PartonicVars(xi,eta)
    rho, beta, chi = p.rho, p.beta, p.chi
    rhoq = p.rho_q
    return (beta*pi*Power(rho,2)*Power(rhoq,2)*(2 + rhoq))/Power(rho - rhoq,3) - (pi*rho*Power(rhoq,2)*(Power(rho,2)*(-1 + rhoq) - 4*rho*rhoq + Power(rhoq,2))*ln(chi))/(2.*Power(rho - rhoq,3))

def cg0_x2g1_AA(xi, eta):
    p = PartonicVars(xi,eta)
    rho, beta, chi = p.rho, p.beta, p.chi
    rhoq = p.rho_q
    return (beta*pi*rho*rhoq*(rho + 3*rhoq))/(2.*Power(rho - rhoq,2)) + (pi*rho*rhoq*(rho + rhoq)*ln(chi))/(2.*Power(rho - rhoq,2))
