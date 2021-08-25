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

beams = injector.BindingKey('beams')
configuration = injector.BindingKey('configuration')
device = injector.BindingKey('device')
em_fields = injector.BindingKey('em_fields')
guiding_fields = injector.BindingKey('guiding_fields')
output = injector.BindingKey('output')
particle_generation = injector.BindingKey('particle_generation')
particle_tracking = injector.BindingKey('particle_tracking')
particle_supervisor = injector.BindingKey('particle_supervisor')
setup = injector.BindingKey('setup')
simulation = injector.BindingKey('simulation')
