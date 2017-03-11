"""
Pushover platform for notify via glances - small notifications

# Message only
    - service: notify.pushoverglances
      data:
        message: "glances1"
#
# Count only
    - service: notify.pushoverglances
      data:
        message: "False"
        data:
          count: "2"
#
# Percent only
    - service: notify.pushoverglances
      data:
        message: "False"
        data:
          percent: "10"
#
# Percent & Title
    - service: notify.pushoverglances
      data:
        message: "False"
        title: "glances4"
        data:
          percent: "90"
#
# Message & percent
    - service: notify.pushoverglances
      data:
        message: "glances5"
        data:
          percent: "90"
#
# Message & percent
    - service: notify.pushoverglances
      data:
        message: "glances6"
        data:
          percent: 90
#
# Message & count
    - service: notify.pushoverglances
      data:
        message: "glances7"
        data:
          count: "7"
#

for apple iWatch for example!
"""
import logging
import http.client, urllib
import voluptuous as vol
import time
import datetime

from homeassistant.components.notify import (
    ATTR_TITLE, ATTR_TITLE_DEFAULT, ATTR_TARGET, ATTR_DATA,PLATFORM_SCHEMA, BaseNotificationService)
from homeassistant.const import CONF_API_KEY
import homeassistant.helpers.config_validation as cv

#Keeping structure of original pushover home-assistant implementation for validation
REQUIREMENTS = ['python-pushover==0.2']
_LOGGER = logging.getLogger(__name__)

CONF_USER_KEY = 'user_key'

# Text to notify user of
ATTR_MESSAGE = 'message'
# Title of notification
ATTR_TITLE = 'title'

# Count attribute is optional in data
ATTR_COUNT = 'count'
ATTR_PERCENT = 'percent'

PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USER_KEY): cv.string,
    vol.Required(CONF_API_KEY): cv.string,
})

# pylint: disable=unused-variable
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
        #rTimefull = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        rTimefull = datetime.datetime.fromtimestamp(ts).strftime('%H:%M')
		
        # Make a copy and use empty dict if necessary
        data = dict(kwargs.get(ATTR_DATA) or {})
        # Get message title for parssing
        myTitle = kwargs.get(ATTR_TITLE)
		
        data['title'] = kwargs.get(ATTR_TITLE, ATTR_TITLE_DEFAULT)
        # Set connection for API
        conn = http.client.HTTPSConnection("api.pushover.net:443")

        # Notification can hold Text / Numeric (count) / both
        gotTitle = False
        gotText = False
        gotCount = False
        gotPercent = False

#        s = "-";
#        seq = (rTimefull,message); # This is sequence of strings.
#        timemsg = s.join( seq )
		
        # If Message ="False" it will not be sent to API
        if message != "False":
            gotText = True
		
        # Parse the title & message into glance notification 
        #(if no title is added only message will be sent)
        if myTitle:
            gotTitle = True
#            myText = '{} {}'.format(myTitle, timemsg)
#        else:
#            myText = timemsg

        # Numeric (count) attribute is optional - check if we got it
        if data is not None and ATTR_COUNT in data:
            myCount = data.get(ATTR_COUNT, None)
            gotCount = True
        
        if data is not None and ATTR_PERCENT in data:
            myPercent = data.get(ATTR_PERCENT, None)
            gotPercent = True
			
        _LOGGER.debug("Glances gotTitle = %s, gotText = %s, gotCount = %s, gotPercent = %s", str(gotTitle), str(gotText), str(gotCount), str(gotPercent))
		
        urlbuilder = { "token": self._api_token}
        _LOGGER.debug("Building = %s", str(urlbuilder))
        urlbuilder ["user"] = self._user_key
        _LOGGER.debug("Building = %s", str(urlbuilder))
        if gotTitle: 
          urlbuilder ["title"] = myTitle
        else:
          urlbuilder ["title"] = str(rTimefull)
        _LOGGER.debug("Building = %s", str(urlbuilder))
        if gotText:
          urlbuilder ["text"] = str(message)
          _LOGGER.debug("Building = %s", str(urlbuilder))
          _LOGGER.debug("message = %s", str(message))
        if gotCount:
          urlbuilder["count"] = int(myCount)
          _LOGGER.debug("Building = %s", str(urlbuilder))
        if gotPercent:
          urlbuilder["percent"] = int(myPercent)
          _LOGGER.debug("Building = %s", str(urlbuilder))
		
        conn.request("POST", "/1/glances.json", urllib.parse.urlencode(urlbuilder), { "Content-type": "application/x-www-form-urlencoded" })
        try:
           _LOGGER.debug("got it!")
           conn.getresponse()
        except ValueError as val_err:
           _LOGGER.error(str(val_err))
        except RequestError:
           _LOGGER.exception('Could not send pushover glances notification')