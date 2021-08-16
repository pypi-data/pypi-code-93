from .analyses.experiments import parameters
from .analyses.experiments import gradients
from .analyses.experiments import metrics
from .analyses.experiments import outputs
from .analyses.experiments import hyperparameters
from .analyses.experiments import comparison

from .analyses.computers import cpu
from .analyses.computers import gpu
from .analyses.computers import memory
from .analyses.computers import network
from .analyses.computers import disk
from .analyses.computers import battery
from .analyses.computers import process

experiment_analyses = [gradients.GradientsAnalysis,
                       outputs.OutputsAnalysis,
                       parameters.ParametersAnalysis,
                       hyperparameters.HyperParamsAnalysis,
                       metrics.MetricsAnalysis]

computer_analyses = [cpu.CPUAnalysis,
                     gpu.GPUAnalysis,
                     memory.MemoryAnalysis,
                     network.NetworkAnalysis,
                     disk.DiskAnalysis,
                     battery.BatteryAnalysis,
                     process.ProcessAnalysis]
