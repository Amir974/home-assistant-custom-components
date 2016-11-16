"""
Pushover platform for notify via glances - small notifications

for apple iWatch for example!
"""
import logging
import http.client, urllib
import voluptuous as vol

from homeassistant.components.notify import (
    ATTR_TITLE, ATTR_TITLE_DEFAULT, ATTR_TARGET, ATTR_DATA,PLATFORM_SCHEMA, BaseNotificationService)
from homeassistant.const import CONF_API_KEY
import homeassistant.helpers.config_validation as cv

#Keeping structure of original pushover home-assistant implementation for validation
REQUIREMENTS = ['python-pushover==0.2']
_LOGGER = logging.getLogger(__name__)

CONF_USER_KEY = 'user_key'
# Count attribute is optional in data
ATTR_COUNT = 'count'
ATTR_PERCENT = 'percent'

PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USER_KEY): cv.string,
    vol.Required(CONF_API_KEY): cv.string,
})

# pylint: disable=unused-variable
def get_service(hass, config):
    """Get the Pushover notification service (Verify the keys)"""
    from pushover import InitError
    #validation part
    try:
        return PushoverGlanceService(config[CONF_USER_KEY],
                                           config[CONF_API_KEY])
    except InitError:
        _LOGGER.error(
            'Wrong API key supplied pushover glances. Get it at https://pushover.net')
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

        # Make a copy and use empty dict if necessary
        data = dict(kwargs.get(ATTR_DATA) or {})
        # Get message title for parssing
        myTitle = kwargs.get(ATTR_TITLE)
		
        data['title'] = kwargs.get(ATTR_TITLE, ATTR_TITLE_DEFAULT)
        # Set connection for API
        conn = http.client.HTTPSConnection("api.pushover.net:443")

        # Notification can hold Text / Numeric (count) / both
        gotText = False
        gotCount = False
        gotPercent = False

        # If Message ="False" it will not be sent to API
        if message != "False":
            gotText = True
		
        # Parse the title & message into glance notification 
        #(if no title is added only message will be sent)
        if myTitle:
            myText = '{} {}'.format(myTitle, message)
        else:
            myText = message

        # Numeric (count) attribute is optional - check if we got it
        if data is not None and ATTR_COUNT in data:
            myCount = data.get(ATTR_COUNT, None)
            gotCount = True
        
        if data is not None and ATTR_PERCENT in data:
            myPercent = data.get(ATTR_PERCENT, None)
            gotPercent = True

        if gotCount and gotPercent:
            # Message & Numeric (count) notification will be sent
            _LOGGER.debug("Pushover glances pushing Percent =%s", myPercent)
            conn.request("POST", "/1/glances.json", urllib.parse.urlencode({ "token": self._api_token, "user":self._user_key, "title": myTitle , "percent": myPercent}), { "Content-type": "application/x-www-form-urlencoded" })
            try:
               conn.getresponse()
            except ValueError as val_err:
               _LOGGER.error(str(val_err))
            except RequestError:
               _LOGGER.exception('Could not send pushover glances notification')

        if gotCount and gotText:
            # Message & Numeric (count) notification will be sent
            _LOGGER.debug("Pushover glances pushing Count & Text =%s", '{} {}'.format(myCount, myText))
            conn.request("POST", "/1/glances.json", urllib.parse.urlencode({ "token": self._api_token, "user":self._user_key, "text": myText, "count": myCount}), { "Content-type": "application/x-www-form-urlencoded" })
            # Only Message notification will be sent
        elif gotText:
            _LOGGER.debug("Pushover glances pushing Text =%s", myText)
            conn.request("POST", "/1/glances.json", urllib.parse.urlencode({ "token": self._api_token, "user":self._user_key, "text": myText}), { "Content-type": "application/x-www-form-urlencoded" })
        elif gotCount:
            # Only Numeric (count) notification will be sent
            _LOGGER.debug("Pushover glances pushing Count =%s", myCount)
            conn.request("POST", "/1/glances.json", urllib.parse.urlencode({ "token": self._api_token, "user":self._user_key, "count": myCount}), { "Content-type": "application/x-www-form-urlencoded" })			

            # Percent and some of the other attributes in glances API 
            # do not seem to effect iWatch complication so not handled for now
			
        try:
           conn.getresponse()
        except ValueError as val_err:
           _LOGGER.error(str(val_err))
        except RequestError:
           _LOGGER.exception('Could not send pushover glances notification')