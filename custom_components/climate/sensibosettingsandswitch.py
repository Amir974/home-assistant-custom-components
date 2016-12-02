"""
Sensibo platform that offers a control over Sensibo type climate device.

Settings and switch controls all the AC settings and also enable on / off control via operation attribute. (no need for separate switch.sensiboswitch)
"""
import logging
import voluptuous as vol

from homeassistant.components.climate import (
    ClimateDevice, ATTR_TARGET_TEMP_HIGH, ATTR_TARGET_TEMP_LOW, PLATFORM_SCHEMA)
from homeassistant.const import (TEMP_CELSIUS, TEMP_FAHRENHEIT, ATTR_TEMPERATURE, CONF_SCAN_INTERVAL)
import homeassistant.helpers.config_validation as cv

import requests
import json

_LOGGER = logging.getLogger(__name__)

_SERVER = 'https://home.sensibo.com/api/v2'

class SensiboClientAPI(object):
    def __init__(self, api_key):
        self._api_key = api_key

    def _get(self, path, ** params):
        params['apiKey'] = self._api_key
        response = requests.get(_SERVER + path, params = params)
        response.raise_for_status()
        return response.json()

    def _patch(self, path, data, ** params):
        params['apiKey'] = self._api_key
        response = requests.patch(_SERVER + path, params = params, data = data)
        response.raise_for_status()
        return response.json()

    def devices(self):
        result = self._get("/users/me/pods", fields="id,room")
        return {x['room']['name']: x['id'] for x in result['result']}

    def pod_measurement(self, podUid):
        result = self._get("/pods/%s/measurements" % podUid)
        return result['result']

    def pod_ac_state(self, podUid):
        result = self._get("/pods/%s/acStates" % podUid, limit = 1, fields="status,reason,acState")
        return result['result'][0]['acState']

    def pod_change_ac_state(self, podUid, currentAcState, propertyToChange, newValue):
        self._patch("/pods/%s/acStates/%s" % (podUid, propertyToChange),
                json.dumps({'currentAcState': currentAcState, 'newValue': newValue}))

"""I want to make sure there is a minimal difference between min & max target temperatures """
const_min_max_minimal_dif = 2

""" key's expected from user configuration"""
CONF_API = 'apiKey'
CONF_NAME = 'name'
CONF_MIN_TEMP = 'min_temp'
CONF_MAX_TEMP = 'max_temp'
CONF_TARGET_TEMP_HIGHT = 'target_temp_high'
CONF_TARGET_TEMP_LOW = 'target_temp_low'
CONF_TARGET_TEMP = 'target_temp'

""" validating user configuration """
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
vol.Required(CONF_API): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL):vol.All(vol.Coerce(int), vol.Range(min=1)),
    vol.Optional(CONF_MAX_TEMP): vol.Coerce(float),
    vol.Optional(CONF_MIN_TEMP): vol.Coerce(float),
    vol.Optional(CONF_TARGET_TEMP_HIGHT): vol.Coerce(float),
    vol.Optional(CONF_TARGET_TEMP_LOW): vol.Coerce(float),
    vol.Optional(CONF_TARGET_TEMP): vol.Coerce(float),	
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Sensibo climate devices."""
    my_api_key = config.get(CONF_API)
    my_name = config.get(CONF_NAME)
    my_min_temp = config.get(CONF_MIN_TEMP)
    my_max_temp = config.get(CONF_MAX_TEMP)
    my_target_temp_high = config.get(CONF_TARGET_TEMP_HIGHT)
    my_target_temp_low = config.get(CONF_TARGET_TEMP_LOW)
    my_target_temp = config.get(CONF_TARGET_TEMP)

    add_devices([
        SensiboClimate(my_name, my_target_temp, TEMP_CELSIUS, None, 23,  "Auto",
                    None, 99, None, "auto", None, my_target_temp_high, my_target_temp_low, my_api_key, my_min_temp, my_max_temp)
    ])

# pylint: disable=too-many-arguments, too-many-public-methods
class SensiboClimate(ClimateDevice):
    """Representation of a Sensibo climate device.
    ** the init is based on the demo device, added the api parameter at the end to pass along
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, name, target_temperature, unit_of_measurement,
                 away, current_temperature, current_fan_mode,
                 target_humidity, current_humidity, current_swing_mode,
                 current_operation, aux, target_temp_high, target_temp_low,give_api_key, min_temp, max_temp):
        """Initialize the climate device with given values"""
        _LOGGER.info("Initialized Sensibo CLIMATE %s", name)
        self._name = name
        self._givent_api_key = give_api_key
        self._target_temperature = target_temperature
        self._target_humidity = target_humidity
        self._unit_of_measurement = unit_of_measurement
        self._away = away
        self._current_temperature = current_temperature
        self._current_humidity = current_humidity
        self._current_fan_mode = current_fan_mode
        self._current_operation = current_operation
        self._aux = aux
        self._current_swing_mode = current_swing_mode
        self._fan_list = ["low", "medium", "high", "auto"]
        self._operation_list = ["heat", "cool", "fan", "off"]
        self._swing_list = [True,False]
        self._target_temperature_low = target_temp_low
        self._min_temp = min_temp
        self._max_temp = max_temp
		
        """Making sure there is at least 2 degree difference between high / low target temps"""
        if (target_temp_high - target_temp_low < 2):
            self._target_temperature_high = target_temp_low + 2
            _LOGGER.info("Min - Max temp difference too low - changing max to ", self._target_temperature_high)
        else:
            self._target_temperature_high = target_temp_high

        """Fetching updated values from the climate device"""
        self.update()


    def update(self):
        """Thermostat object settings"""
        _LOGGER.debug("Checking Sensibo CLIMATE stats for  %s", self._name)
        client = SensiboClientAPI(self._givent_api_key)
        devices = client.devices()
        uid = devices[self._name]
        _LOGGER.debug("Sensibo uid =%s", uid)
        """Get the latest measurements from the thermostat."""
        current_measurements = client.pod_measurement(uid)[0]
		
        self._current_temperature = current_measurements['temperature']
        self._current_humidity = current_measurements['humidity']

        """Get the latest settings from the thermostat."""		
        current_settings = client.pod_ac_state(uid)

        """Holding same unit of measurements as set in the thermostat"""
        if (current_settings['temperatureUnit'] == 'C'):
            self._unit_of_measurement = TEMP_CELSIUS
        else:
            self._unit_of_measurement = TEMP_FAHRENHEIT
			
        self._target_temperature = current_settings['targetTemperature']
        self._current_fan_mode = current_settings['fanLevel']

        """ this is the part that merges the operation mode and on/off state"""
        self.TermostatState = current_settings['on']
        if (self.TermostatState):		
            self._current_operation = current_settings['mode']
        else:
            self._current_operation = 'off'
			

    def makeitso(self,changeaction,cahngevalue):
        """Setting thermostat to change the relevant value in settings """
        _LOGGER.debug("Changing Sensibo CLIMATE stats for  %s", changeaction)
        client = SensiboClientAPI(self._givent_api_key)
        devices = client.devices()
        uid = devices[self._name]
        client.pod_change_ac_state((uid), client.pod_ac_state(uid),changeaction,cahngevalue)
        self.update_ha_state()
        self.update()
			
    @property
    def name(self):
        """Return the name of the climate device."""
        return self._name

    @property
    def _state(self):
        """Return the state of the climate device."""
        return self.TermostatState

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temperature

    @property
    def target_temperature_high(self):
        """Return the highbound target temperature we try to reach."""
        return self._target_temperature_high

    @property
    def target_temperature_low(self):
        """Return the lowbound target temperature we try to reach."""
        return self._target_temperature_low

    @property
    def current_humidity(self):
        """Return the current humidity."""
        return self._current_humidity

    @property
    def target_humidity(self):
        """Return the humidity we try to reach."""
        return self._target_humidity

    @property
    def current_operation(self):
        """Return current operation ie. heat, cool, idle."""
        return self._current_operation

    @property
    def operation_list(self):
        """List of available operation modes."""
        return self._operation_list

    @property
    def is_away_mode_on(self):
        """Return if away mode is on."""
        return self._away

    @property
    def is_aux_heat_on(self):
        """Return true if away mode is on."""
        return self._aux

    @property
    def current_fan_mode(self):
        """Return the fan setting."""
        return self._current_fan_mode

    @property
    def fan_list(self):
        """List of available fan modes."""
        return self._fan_list

    def set_temperature(self, **kwargs):
        """Set new target temperatures."""
        if kwargs.get(ATTR_TEMPERATURE) is not None:
            self._target_temperature = kwargs.get(ATTR_TEMPERATURE)
            self.makeitso('targetTemperature',int(kwargs.get(ATTR_TEMPERATURE)))

        """Making sure there is at least (const_min_max_minimal_dif) degree difference between high / low target temps"""
        if kwargs.get(ATTR_TARGET_TEMP_HIGH) is not None and \
           kwargs.get(ATTR_TARGET_TEMP_LOW) is not None:
            self._target_temperature_low = kwargs.get(ATTR_TARGET_TEMP_LOW)
            self._target_temperature_high = kwargs.get(ATTR_TARGET_TEMP_HIGH)
            if (kwargs.get(ATTR_TARGET_TEMP_HIGH) - kwargs.get(ATTR_TARGET_TEMP_LOW) < const_min_max_minimal_dif):
                self._target_temperature_high = kwargs.get(ATTR_TARGET_TEMP_LOW) + const_min_max_minimal_dif
            else:
                self._target_temperature_high = kwargs.get(ATTR_TARGET_TEMP_HIGH)

    def set_humidity(self, humidity):
        """Set new target temperature."""
        self._target_humidity = humidity
        self.update_ha_state()

    def set_swing_mode(self, swing_mode):
        """Set new target temperature."""
        self._current_swing_mode = swing_mode
        """
        if (swing_mode):
            sensibo_on_mode = True
        else:
            sensibo_on_mode = False
        self.makeitso('on',sensibo_on_mode)"""

    def set_fan_mode(self, fan):
        """Set new fan level"""
        self._current_fan_mode = fan
        self.makeitso('fanLevel',self._current_fan_mode)

    def set_operation_mode(self, operation_mode):
        """Set new mode & on state"""
        self._current_operation = operation_mode

        """ this is another part that merges the operation mode and on/off state"""
        if (self._current_operation == 'off'):
            self.TermostatState = False
            self.makeitso('on',self.TermostatState)
        else:
            self.makeitso('mode',self._current_operation)
            if (not self.TermostatState):
                self.TermostatState = True
                self.makeitso('on',self.TermostatState)
#        self.makeitso('mode',self._current_operation)
			
    @property
    def current_swing_mode(self):
        """Return the swing setting."""
        return self._current_swing_mode

    @property
    def swing_list(self):
        """List of available swing modes."""
        return self._swing_list

    def turn_away_mode_on(self):
        """Turn away mode on."""
        self._away = True
        self.update_ha_state()

    def turn_away_mode_off(self):
        """Turn away mode off."""
        self._away = False
        self.update_ha_state()

    def turn_aux_heat_on(self):
        """Turn away auxillary heater on."""
        self._aux = True
        self.update_ha_state()

    def turn_aux_heat_off(self):
        """Turn auxillary heater off."""
        self._aux = False
        self.update_ha_state()

    @property
    def min_temp(self):
        """return min temp set for AC."""
        return self._min_temp

    @property
    def max_temp(self):
        """return max temp set for AC."""
        return self._max_temp