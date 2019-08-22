# ===============================================================================
# Copyright 2011 Jake Ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================


def get_valve_address(obj):
    if isinstance(obj, (str, int)):
        addr = obj
    else:
        addr = obj.address
    return addr


def get_valve_name(obj):
    if isinstance(obj, (str, int)):
        name = obj
    else:
        name = obj.name.split('-')[1]
    return name


base = 'pychron.hardware'
PACKAGES = dict(AgilentGPActuator='{}.agilent.agilent_gp_actuator'.format(base),
                ArduinoGPActuator='{}.arduino.arduino_gp_actuator'.format(base),
                QtegraGPActuator='{}.actuators.qtegra_gp_actuator'.format(base),
                PychronGPActuator='{}.actuators.pychron_gp_actuator'.format(base),
                NGXGPActuator='{}.actuators.ngx_gp_actuator'.format(base),
                WiscArGPActuator='{}.actuators.wiscar_actuactor'.format(base),
                NMGRLFurnaceActuator='{}.actuators.nmgrl_furnace_actuator'.format(base),
                DummyGPActuator='{}.actuators.dummy_gp_actuator'.format(base),
                RPiGPIO='{}.rpi_gpio'.format(base))
