"""
Sensibo sensor platform for extracting data of Sensibo smart thermostat

"""
import logging
import voluptuous as vol

from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.entity import Entity

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

""" key's expected from user configuration"""
CONF_API = 'apiKey'
CONF_NAME = 'name'

SENSOR_TYPES = {
    'temperature': ['Temperature', TEMP_CELSIUS],
    'humidity': ['Humidity', '%']
}

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Find and return Sensibo data"""
    my_api_key = config.get(CONF_API)
    my_name = config.get(CONF_NAME)

    add_devices([
        SensiboSensor('Inside Temperature', 'temperature', 1, my_api_key, my_name),
        SensiboSensor('Inside Humidity', 'humidity', 2, my_api_key, my_name)
		])

class SensiboSensor(Entity):
    """Representation of an Sensibo sensor."""
    def __init__(self, sensor_name, sensor_type, sensor_index, given_api_key, sensibo_name):
        _LOGGER.info("Initialized Sensibo SENSOR %s", sensibo_name)
        self._sensibo = sensibo_name
        self._name = sensor_name
        self._givent_api_key = given_api_key
        self.type = sensor_type
        self.index = sensor_index
        self._state = None
        self._unit_of_measurement = SENSOR_TYPES[sensor_type][1]
        self.update()

    @property
    def name(self):
        """Return the name of the Sensibo sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement this sensor expresses itself in."""
        return self._unit_of_measurement

    def update(self):
        """Get the latest state of the sensor."""
        _LOGGER.debug("Checking Sensibo SENSOR stats for  %s", self._sensibo)
        client = SensiboClientAPI(self._givent_api_key)
        devices = client.devices()
        uid = devices[self._sensibo]
        current_measurements = client.pod_measurement(uid)[0]
        self._state = current_measurements[self.type]