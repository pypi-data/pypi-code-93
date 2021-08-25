#    Virtual-IPM is a software for simulating IPMs and other related devices.
#    Copyright (C) 2021  The IPMSim collaboration <https://ipmsim.gitlab.io/>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import injector

import virtual_ipm.simulation.devices.models as devices
import virtual_ipm.simulation.output as output_recorder
import virtual_ipm.simulation.particle_generation.models as particle_generation_models
import virtual_ipm.simulation.particle_tracking.em_fields.guiding_fields.models as \
    guiding_fields_models
import virtual_ipm.simulation.particle_tracking.models as particle_tracking_models
from virtual_ipm.simulation.beams.beams import BeamsWrapper
from virtual_ipm.simulation.simulation import IPMSimulation as Simulation
from virtual_ipm.simulation.devices import DeviceManager
from virtual_ipm.simulation.particle_generation import ParticleGenerationManager
from virtual_ipm.simulation.auxiliaries import ParticleSupervisor
from virtual_ipm.simulation.particle_tracking.em_fields import EMFieldsCollector
from virtual_ipm.simulation.particle_tracking.em_fields.guiding_fields import GuidingFieldsManager
from virtual_ipm.simulation.particle_tracking import ParticleTrackingManager
from virtual_ipm.simulation.setup import Setup
from virtual_ipm.utils import get_logger
from . import components
from . import models


logger = get_logger(__name__)


def create_binding(name, key, to_class, provider=injector.ClassProvider):
    def configure(self, binder):
        binder.bind(key, provider(to_class), scope=injector.SingletonScope)

    return type(name, (injector.Module,), {'configure': configure})


def create_binding_for_component(component, key):
    logger.debug('Create binding for %s' % component)
    return create_binding(f'{component.__name__}Module', key, component)


def create_for_components():
    return [
        create_binding_for_component(BeamsWrapper, components.beams),
        create_binding_for_component(DeviceManager, components.device),
        create_binding_for_component(EMFieldsCollector, components.em_fields),
        create_binding_for_component(GuidingFieldsManager, components.guiding_fields),
        create_binding_for_component(ParticleGenerationManager, components.particle_generation),
        create_binding_for_component(ParticleTrackingManager, components.particle_tracking),
        create_binding_for_component(ParticleSupervisor, components.particle_supervisor),
        create_binding_for_component(Setup, components.setup),
        create_binding_for_component(Simulation, components.simulation),
    ]


def create_binding_for_mutable(module, key, configuration):
    component_name = configuration.get_text(module.Interface.CONFIG_PATH_TO_IMPLEMENTATION)
    if ',' in component_name:
        logger.debug('Create derived component from: %s', component_name)
        component_names = component_name.split(',')
        components = list(map(
            lambda x: getattr(module, x),
            component_names
        ))
        type_ = type(components[0])
        component = type_(
            '_'.join(component_names),
            tuple(components),
            {}
        )
    else:
        component = getattr(module, component_name)
    logger.debug('Create binding for %s: use %s', module.Interface, component)
    return create_binding(
        f'{module.Interface.__name__}Module',
        key,
        component
    )


def create_for_models(configuration):
    return [
        create_binding_for_mutable(particle_generation_models, models.particle_generation, configuration),
        create_binding_for_mutable(particle_tracking_models, models.particle_tracking, configuration),
        create_binding_for_mutable(guiding_fields_models.electric, models.electric_guiding_field, configuration),
        create_binding_for_mutable(guiding_fields_models.magnetic, models.magnetic_guiding_field, configuration),
        create_binding_for_mutable(devices, models.device, configuration),
        create_binding_for_mutable(output_recorder, components.output, configuration),
    ]


def create_for_configuration(configuration):
    return [
        create_binding('ConfigurationModule', components.configuration,
                       configuration, provider=injector.InstanceProvider),
    ]


def create_bindings(config):
    return create_for_components() + create_for_models(config) + create_for_configuration(config)
