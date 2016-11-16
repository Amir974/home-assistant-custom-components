"""
Sensibo platform that offers a control over Sensibo type climate device.

"""
import logging
import voluptuous as vol

from homeassistant.util import convert
from homeassistant.components.switch import (SwitchDevice)
from homeassistant.const import (STATE_OFF, STATE_ON, CONF_NAME, CONF_SWITCHES)

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

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Find and return Sensibo data"""
    my_api_key = config.get(CONF_API)
    my_name = config.get(CONF_NAME)
    add_devices([SensiboSwitch(my_name,my_api_key)])


class SensiboSwitch(SwitchDevice):
    """Representation of a Sensibo Switch."""

    def __init__(self, name, given_api_key):
        _LOGGER.info("Initialized Sensibo SWITCH %s", name)
        self._name = name
        self._givent_api_key = given_api_key
        self._state = False
        self.update()

    def turn_on(self, **kwargs):
        """Turn device on."""
        _LOGGER.debug("Update Sensibo SWITCH to on")
        client = SensiboClientAPI(self._givent_api_key)
        devices = client.devices()
        uid = devices[self._name]
        _LOGGER.debug("Sensibo uid =%s", uid)
        """Get the latest settings from the thermostat."""
        current_settings = client.pod_ac_state(uid)
        client.pod_change_ac_state((uid), client.pod_ac_state(uid),"on",True)
        self.update()

    def turn_off(self, **kwargs):
        """Turn device off."""
        _LOGGER.debug("Update Sensibo SWITCH to off")
        client = SensiboClientAPI(self._givent_api_key)
        devices = client.devices()
        uid = devices[self._name]
        _LOGGER.debug("Sensibo uid =%s", uid)
        """Get the latest settings from the thermostat."""
        current_settings = client.pod_ac_state(uid)
        client.pod_change_ac_state((uid), client.pod_ac_state(uid),"on",False)
        self.update()

    def update(self):
        _LOGGER.debug("Checking Sensibo SWITCH stats for  %s", self._name)
        client = SensiboClientAPI(self._givent_api_key)
        devices = client.devices()
        uid = devices[self._name]
        _LOGGER.debug("Sensibo uid =%s", uid)
        """Get the latest settings from the thermostat."""
        current_settings = client.pod_ac_state(uid)
        self._state = current_settings['on']

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    @property
    def name(self):
        """Return the name of the climate device."""
        return self._name

    @property
    def should_poll(self):
        """Polling is needed."""
        return True