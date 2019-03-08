

# ******
# Important: these components are no longer supported
## I recommend you switch over to native componemts that provide superior expereience and funtionality these days 
# ******



``home-assistant-custom-components`` include some custom components I wrote for my implementation of home-assistant - the open-source home automation platform.

Learn more about the [Home-assistant platform](https://home-assistant.io/)


# Included Components

See below:
 * Sensibo Smart Thermostat compoennts
 * Pushover-Glances for displaying information on Apple Watch for example

## Sensibo

For my smart thermostat [Sensibo](https://www.sensibo.com/) I created 3 different components you can choose from:

* **Switch** - (``sensiboswitch``) a simple on/off switch that turns Sensibo on or off using the existing settings (this will be very easy to use as action for automation rules)
* **Sensor** - (``sensibosensor``) this will query the temperature / humidity from Sensibo at specific intervals and you can check this data on the dashboard / use it for automation rules as trigger / condition etc.
* **Climate** - this is a standard climate control component for Home-assistant that includes updated information similar to sensors, allows you to change the settings of the AC (hot / cold... fan speed etc.) but also allows you to set a temperature range (min - max) and automate on/off accordingly.
  * ``sensibosettingsandswitch`` includes on/off switch in operation selection
  * ``sensibosettingsonly`` only allows you to change the AC settings (for on/off use the switch mentioned above)
  
    These are just two implementations for climate components I was playing with - chose the one you prefer (no need to setup both!)

![Weather-Dashboard-Sensibo-On-Home-Assistant](/images/Weather-Dashboard-Sensibo-On-Home-Assistant.png?raw=true "Home Assistant Dashboard Sample For Sensibo Components")

![Climate-Options-Sensibo-On-HomeAssistant](/images/Climate-Options-Sensibo-On-HomeAssistant.png?raw=true "Climate Components Card For Sensibo")

## Pushover - Glances
While Home-Assistant already had a [notification platform implementation for pushover](https://home-assistant.io/components/notify.pushover/), at present it's only for sending push notifications...

My implementation of the ["Glances" A](https://pushover.net/api/glances) allows you to send information directly to Apple Watch face (not as push). 

* **Notify** - (``pushoverglances``) will let you connect the service and set it up so you can send *count numeric messages* to the little info placeholder and  *short text messages* to the the larger placeholder

**You will want to get [The Pushover App](https://itunes.apple.com/us/app/pushover-notifications/id506088175?mt=8&at=1010l3fx) from the Apple app store if you haven't already...**

![Apple-Watch-Example](/images/apple-watch-with-pushover-glances.PNG?raw=true "Apple Watch with Home-Assistant Data via Pushover Glances")

# If you want to go into Home-Assistant and are missing a Raspberry Pi

Here are a few places to find one
 * [Raspberry Pi 3 @Amazon](http://amzn.to/2g2hA31)
 * [Raspberry Pi 3 @BangGood](http://www.banggood.com/Raspberry-Pi-3-Model-B-ARM-Cortex-A53-CPU-1_2GHz-64-Bit-Quad-Core-1GB-RAM-10-Times-B-p-1041862.html?p=4S2609598718201405F0)
 * [Raspberry Pi 3 @eBay](http://rover.ebay.com/rover/1/711-53200-19255-0/1?icep_ff3=9&pub=5575128384&toolid=10001&campid=5337704811&customid=&icep_uq=raspberry+pi+3&icep_sellerId=&icep_ex_kw=&icep_sortBy=12&icep_catId=&icep_minPrice=&icep_maxPrice=&ipn=psmain&icep_vectorid=229466&kwid=902099&mtid=824&kw=lg)

_Prices / availability may vary – check both Banggood, Amazon & eBay before purchase 🙂_


# Installation Instructions

* I invite you to read about this component and more [on my blog](http://www.virtualida.com/2016/11/status-of-my-smart-home/)
* Once you are done setting up the platform (check out http://www.bruhautomation.com/ for excelnt video & written tutorials),
* Create a "custom_components" folder where the configuration.yaml file is located, and sub folders for the relevant components types similar to the structure I have [here](https://github.com/Amir974/home-assistant-custom-components/tree/master/custom_components) just for the componts you are going to use...
* Next you should take care of configuration and settings for the components - take a look at the [Yaml-Config-Example](https://github.com/Amir974/home-assistant-custom-components/tree/master/Yaml-Config-Example) folder and pay attention to the comments - it's not a straight forward copy-paste
