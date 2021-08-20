# coding: utf-8

import crappy

adda = crappy.blocks.IOBlock("Waveshare_ad_da_ft232h", labels=['t(s)', 'U(V)'],
                             cmd_labels=['U(V)'], v_ref=5,
                             adc_channels=['AD0'], dac_channels=['DAC0'],
                             ft232h_ser_num='54321')

graph = crappy.blocks.Grapher(('t(s)', 'U(V)'))

crappy.link(adda, graph)

crappy.link(adda, adda)

Nau7802 = crappy.blocks.IOBlock('Nau7802', labels=['t(s)', 'F(N)'],
                                backend='ft232h', ft232h_ser_num='12345')

#Ads1115 = crappy.blocks.IOBlock('Ads1115', labels=['t(s)', 'P(mm)'],
                                #backend='ft232h')

graph1 = crappy.blocks.Grapher(('t(s)', 'F(N)'))

#graph2 = crappy.blocks.Grapher(('t(s)', 'P(mm)'))

crappy.link(Nau7802, graph1)

#crappy.link(Ads1115, graph2)

crappy.start()
