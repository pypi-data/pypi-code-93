#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 25 18:39:39 2021

@author: Alejandro Maldonado.
"""
#Archivo distribuible
from setuptools import setup


setup(
      name="zilonis",
      version="1.7",
      author="Alejandro Maldonado",
      author_email="alejandro.maldonado@gonet.us",
      description="Consumo Privado de API Cotizador",
      url="",
      scripts=[],
      packages=["zilonis",
                  "zilonis.login", 
                  "zilonis.constantes",
                  "zilonis.vehiculo",
                  "zilonis.ubicacion",
                  "zilonis.persona",
                  "zilonis.cotizador",
                  "zilonis.monitorTasks"
                  ]
)