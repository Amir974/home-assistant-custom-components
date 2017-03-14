"""
Pushover platform for notify via glances - small notifications
for apple iWatch for example!

#
glances1:
  sequence:
    - service: notify.pushoverglances
      data_template:
        message: "Rst msg"
        title: "Rst ttl"
        data:
          count: "100"
          precent: "100"
          subtext: "Rst subtxt"
#
glances2:
  sequence:
    - service: notify.pushoverglances
      data_template:
        message: "{{states('sensor.amir_work_to_home')}}msg"
        title: "{{states('sensor.amir_work_to_home')}} ttl"
        data:
          count: "{{states('sensor.amir_work_to_home')}}"
          precent: "{{(states('sensor.amir_work_to_home' ) | int) * 2}}"
          subtext: "{{((states('sensor.amir_work_to_home' ) | int) * 3)}}"
#


"""
import logging
import http.client, urllib
import voluptuous as vol
import time
import datetime

from homeassistant.components.notify import (
    ATTR_TITLE, ATTR_TARGET, ATTR_DATA,PLATFORM_SCHEMA, BaseNotificationService)
from homeassistant.const import CONF_API_KEY
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['python-pushover==0.2']
_LOGGER = logging.getLogger(__name__)

CONF_USER_KEY = 'user_key'

ATTR_MESSAGE = 'message'
ATTR_TITLE = 'title'

ATTR_COUNT = 'count'
ATTR_PERCENT = 'percent'
ATTR_SUBTEXT = 'subtext'

PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USER_KEY): cv.string,
    vol.Required(CONF_API_KEY): cv.string,
})

def get_service(hass, config,discovery_info):
    """Get the Pushover notification service (Verify the keys)"""
    from pushover import InitError
    #validation part
    try:
        return PushoverGlanceService(config[CONF_USER_KEY],
                                           config[CONF_API_KEY])
    except InitError:
        _LOGGER.error('Wrong API key supplied pushover glances. Get it at https://pushover.net')
        return None


class PushoverGlanceService(BaseNotificationService):
    """Implement the notification service for Pushover - Glances."""

    def __init__(self, user_key, api_token):
        """Initialize the service."""
        from pushover import Client
        self._user_key = user_key
        self._api_token = api_token
        self.pushover = Client(
            self._user_key, api_token=self._api_token)

    def send_message(self, message='', **kwargs):
        """Send a message to a user."""
        from pushover import RequestError
        ts = time.time()
        rTimefull = datetime.datetime.fromtimestamp(ts).strftime('%H:%M')
		
        data = kwargs.get(ATTR_DATA)
        myTitle = kwargs.get(ATTR_TITLE, rTimefull)
        # Set connection for API
        conn = http.client.HTTPSConnection("api.pushover.net:443")
		
        urlbuilder = { "token": self._api_token}
        urlbuilder ["user"] = self._user_key
		
        if myTitle:
          urlbuilder ["title"] = myTitle

        if message != "False":
          urlbuilder ["text"] = str(message)
          _LOGGER.debug("message = %s", str(message))
		  
        if data is not None and ATTR_COUNT in data:
          myCount = data.get(ATTR_COUNT, None)
          _LOGGER.debug("myCount = %s", str(myCount))
          urlbuilder["count"] = str(myCount).strip("''")

        if data is not None and ATTR_PERCENT in data:
          myPercent = data.get(ATTR_PERCENT, None)
          _LOGGER.debug("myPercent = %s", str(myPercent))
          urlbuilder["percent"] = str(myPercent).strip("''")
		  
        if data is not None and ATTR_SUBTEXT in data:
          mySubText = data.get(ATTR_SUBTEXT, None)
          _LOGGER.debug("mySubText = %s", str(mySubText))
          urlbuilder["subtext"] = str(mySubText).strip("''")
          
        _LOGGER.debug("Building = %s", str(urlbuilder))
        conn.request("POST", "/1/glances.json", urllib.parse.urlencode(urlbuilder), { "Content-type": "application/x-www-form-urlencoded" })
        try:
           _LOGGER.debug("got it!")
           conn.getresponse()
        except ValueError as val_err:
           _LOGGER.error(str(val_err))
        except RequestError:
           _LOGGER.exception('Could not send pushover glances notification')