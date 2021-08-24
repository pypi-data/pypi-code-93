template_bash_shbang = """#!/bin/bash"""

template_nohup = """nohup ./$name > $logfile 2>&1 &"""

template_wispy_autoencoder_fit = """wispy_autoencoder_fit --config-file $config -v"""