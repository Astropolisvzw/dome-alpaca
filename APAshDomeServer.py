from bottle import route, get, put, post, request, response,run, template
import bottle
from dome import Dome
from fake_dome import FakeDome
import argparse
import logging

# ASCOM Reserved Error Numbers (https://ascom-standards.org/Developer/ASCOM%20Alpaca%20API%20Reference.pdf)
# Condition                             Alpaca Error Number         COM Exception Number
# Successful transaction                0x0 (0)                     N/A
# Property or method not implemented    0x400 (1024)                0x80040400
# Invalid value                         0x401 (1025)                0x80040401
# Value not set                         0x402 (1026)                0x80040402
# Not connected                         0x407 (1031)                0x80040407
# Invalid while parked                  0x408 (1032)                0x80040408
# Invalid while slaved                  0x409 (1033)                0x80040409
# Invalid operation                     0x40B (1035)                0x8004040B
# Action not implemented                0x40C (1036)                0x8004040C


dome = None

def get_url(suffix):
    return f"/api/v1/dome/<device_number:int>/{suffix}"

def std_res(request):
    ctID = request.query.ClientTransactionID
    return { "ClientTransactionID": int(ctID) if ctID else 0, "ServerTransactionID": 0, "ErrorNumber": 0, "ErrorMessage": ""}

# safe float conversion in case locale uses comma instead of points.
def _float(input: str):
    return float(input.replace(',', '.'))

# GENERIC

@post(get_url('action'))
def device_type_device_number_action_put(device_type, device_number, action=None, parameters=None, client_id=None, client_transaction_id=None):  # noqa: E501
    """Invokes the specified device-specific action.

    Invokes the specified device-specific action. # noqa: E501

    :param device_type: One of the recognised ASCOM device types e.g. Telescope
    :type device_type: str
    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param action:
    :type action: str
    :param parameters:
    :type parameters: str
    :param client_id:
    :type client_id: str
    :param client_transaction_id:
    :type client_transaction_id: str

    :rtype: MethodResponse
    """
    return 'do some magic!'


def device_type_device_number_command_blind_put(device_type, device_number, command=None, raw=None, client_id=None, client_transaction_id=None):  # noqa: E501
    """Transmits an arbitrary string to the device

    Transmits an arbitrary string to the device and does not wait for a response. Optionally, protocol framing characters may be added to the string before transmission. # noqa: E501

    :rtype: MethodResponse
    """
    return 'do some magic!'


def device_type_device_number_command_bool_put(device_type, device_number, command=None, raw=None, client_id=None, client_transaction_id=None):  # noqa: E501
    """Transmits an arbitrary string to the device and returns a boolean value from the device.

    Transmits an arbitrary string to the device and waits for a boolean response. Optionally, protocol framing characters may be added to the string before transmission. # noqa: E501
    """
    return 'do some magic!'


@get(get_url('commandstring'))
def device_type_device_number_command_string_put(device_number):  # noqa: E501
    """Transmits an arbitrary string to the device and returns a string value from the device.

    Transmits an arbitrary string to the device and waits for a string response. Optionally, protocol framing characters may be added to the string before transmission. # noqa: E501

    :param device_type: One of the recognised ASCOM device types e.g. Telescope
    :type device_type: str
    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param command:
    :type command: str
    :param raw:
    :type raw: str
    :param client_id:
    :type client_id: str
    :param client_transaction_id:
    :type client_transaction_id: str

    :rtype: StringResponse
    """
    ret = std_res(request)
    ret['Value'] = "Not implemented"
    response.status = 200
    return ret

@get(get_url('connected'))
def device_type_device_number_connected_get(device_number):  # noqa: E501
    """Retrieves the connected state of the device

    Retrieves the connected state of the device # noqa: E501

    :param device_type: One of the recognised ASCOM device types e.g. Telescope
    :type device_type: str
    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: BoolResponse
    """
    response.status = 200
    return dome.connected

@put(get_url('connected'))
def device_type_device_number_connected_put(device_number):  # noqa: E501
    """Sets the connected state of the device

    Sets the connected state of the device # noqa: E501

    :param device_type: One of the recognised ASCOM device types e.g. Telescope
    :type device_type: str
    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param connected:
    :type connected: bool
    :param client_id:
    :type client_id: str
    :param client_transaction_id:
    :type client_transaction_id: str

    :rtype: MethodResponse
    """
    response.status = 200
    dome.connected = request.forms['Connected']
    resp = std_res(request)
    return resp


@get(get_url('description'))
def device_type_device_number_description_get(device_number):  # noqa: E501
    """Device description

    The description of the device # noqa: E501

    :param device_type: One of the recognised ASCOM device types e.g. Telescope
    :type device_type: str
    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: StringResponse
    """
    ret = std_res(request)
    ret['Value'] = "Astropolis ASH Dome driver"
    return ret

@get(get_url('driverversion'))
def device_type_device_number_driver_version_get(device_number):  # noqa: E501
    """Driver Version

    A string containing only the major and minor version of the driver. # noqa: E501

    :param device_type: One of the recognised ASCOM device types e.g. Telescope
    :type device_type: str
    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: StringResponse
    """
    ret = std_res(request)
    ret['Value'] = "1.0"
    response.status = 200
    return ret


@get(get_url('driverinfo'))
def device_type_device_number_driverinfo_get(device_number):  # noqa: E501
    """Device driver description

    The description of the driver # noqa: E501

    :param device_type: One of the recognised ASCOM device types e.g. Telescope
    :type device_type: str
    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: StringResponse
    """
    ret = std_res(request)
    ret['Value'] = "Uses a pi, arduino and encoders to position the 6m ASH dome"
    response.status = 200
    return ret

@get(get_url('interfaceversion'))
def interfaceversion(device_number):
    # {
    # "Value": 0,
    # "ClientTransactionID": 0,
    # "ServerTransactionID": 0,
    # "ErrorNumber": 0,
    # "ErrorMessage": "string"
    # }
    ret = std_res(request)
    ret['Value'] = 2
    response.status = 200
    return ret

@get(get_url('name'))
def device_type_device_number_name_get(device_number):  # noqa: E501
    """Device name

    The name of the device # noqa: E501

    :param device_type: One of the recognised ASCOM device types e.g. Telescope
    :type device_type: str
    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: StringResponse
    """
    ret = std_res(request)
    ret['Value'] = "AstropolisAshDomeController"
    response.status = 200
    return ret


@get(get_url('supportedactions'))
def device_type_device_number_supported_actions_get(device_number):  # noqa: E501
    """Returns the list of action names supported by this driver.

    Returns the list of action names supported by this driver. # noqa: E501

    :param device_type: One of the recognised ASCOM device types e.g. Telescope
    :type device_type: str
    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: StringArrayResponse
    """
    ret = std_res(request)
    ret['Value'] = []
    response.status = 200
    return ret



# DOME

@put(get_url('abortslew'))
def dome_abort_slew_put(device_number):  # noqa: E501
    """Immediately cancel current dome operation.

    Calling this method will immediately disable hardware slewing (Slaved will become False). # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id:
    :type client_id: str
    :param client_transaction_id:
    :type client_transaction_id: str

    :rtype: MethodResponse
    """
    dome.abort_slew()
    ret = std_res(request)
    response.status = 200
    return ret


@get(get_url('altitude'))
def dome_altitude_get(device_number):  # noqa: E501
    """The dome altitude

    The dome altitude (degrees, horizon zero and increasing positive to 90 zenith). # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: DoubleResponse
    """
    # try:
    #     print(request.query)
    #     client_id = request.query.ClientID
    #     client_transaction_id = request.query.ClientTransactionID
    # except Exception as e:
    #     print("error was", e)
    ret = std_res(request)
    ret['Value'] = 0 # dome altitude is always zero
    response.status = 200
    return ret


@get(get_url('athome'))
def dome_at_home_get(device_number):  # noqa: E501
    """Indicates whether the dome is in the home position.

    Indicates whether the dome is in the home position. This is normally used following a FindHome()  operation. The value is reset with any azimuth slew operation that moves the dome away from the home position. AtHome may also become true durng normal slew operations, if the dome passes through the home position and the dome controller hardware is capable of detecting that; or at the end of a slew operation if the dome comes to rest at the home position. # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: BoolResponse
    """
    ret = std_res(request)
    ret['Value'] = dome.is_at_home()
    response.status = 200
    return ret


@get(get_url('atpark'))
def dome_at_park_get(device_number):  # noqa: E501
    """Indicates whether the telescope is at the park position

    True if the dome is in the programmed park position. Set only following a Park() operation and reset with any slew operation. # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: BoolResponse
    """
    ret = std_res(request)
    ret['Value'] = dome.is_at_park()
    response.status = 200
    return ret



@get(get_url('azimuth'))
def dome_azimuth_get(device_number):  # noqa: E501
    """The dome azimuth

    Returns the dome azimuth (degrees, North zero and increasing clockwise, i.e., 90 East, 180 South, 270 West) # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: DoubleResponse
    """
    ret = std_res(request)
    ret['Value'] = dome.get_azimuth()
    response.status = 200
    return ret


@get(get_url('canfindhome'))
def dome_can_find_home_get(device_number):  # noqa: E501
    """Indicates whether the dome can find the home position.

    True if the dome can move to the home position. # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: BoolResponse
    """
    ret = std_res(request)
    ret['Value'] = False
    response.status = 200
    return ret

@get(get_url('canpark'))
def dome_can_park_get(device_number):  # noqa: E501
    """Indicates whether the dome can be parked.

    True if the dome is capable of programmed parking (Park() method) # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: BoolResponse
    """
    ret = std_res(request)
    ret['Value'] = True
    response.status = 200
    return ret

@get(get_url('cansetaltitude'))
def dome_can_set_altitude_get(device_number):  # noqa: E501
    """Indicates whether the dome altitude can be set

    True if driver is capable of setting the dome altitude. # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: BoolResponse
    """
    ret = std_res(request)
    ret['Value'] = False
    response.status = 200
    return ret

@get(get_url('cansetazimuth'))
def dome_can_set_azimuth_get(device_number):  # noqa: E501
    """Indicates whether the dome azimuth can be set

    True if driver is capable of setting the dome azimuth. # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: BoolResponse
    """
    ret = std_res(request)
    ret['Value'] = True
    response.status = 200
    return ret

@get(get_url('cansetpark'))
def dome_can_set_park_get(device_number):  # noqa: E501
    """Indicates whether the dome park position can be set

    True if driver is capable of setting the dome park position. # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: BoolResponse
    """
    ret = std_res(request)
    ret['Value'] = True
    response.status = 200
    return ret


@get(get_url('cansetshutter'))
def dome_can_set_shutter_get(device_number):  # noqa: E501
    """Indicates whether the dome shutter can be opened

    True if driver is capable of automatically operating shutter # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: BoolResponse
    """
    ret = std_res(request)
    ret['Value'] = True
    response.status = 200
    return ret

@get(get_url('canslave'))
def dome_can_slave_get(device_number):  # noqa: E501
    """Indicates whether the dome supports slaving to a telescope

    True if driver is capable of slaving to a telescope. # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: BoolResponse
    """
    ret = std_res(request)
    ret['Value'] = True
    response.status = 200
    return ret


@get(get_url('cansyncazimuth'))
def dome_can_sync_azimuth_get(device_number):  # noqa: E501
    """Indicates whether the dome azimuth position can be synched

    True if driver is capable of synchronizing the dome azimuth position using the SyncToAzimuth(Double) method. # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: BoolResponse
    """
    ret = std_res(request)
    ret['Value'] = True
    response.status = 200
    return ret

@put(get_url('closeshutter'))
def dome_close_shutter_put(device_number):  # noqa: E501
    """Close the shutter or otherwise shield telescope from the sky.

    Close the shutter or otherwise shield telescope from the sky. # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id:
    :type client_id: str
    :param client_transaction_id:
    :type client_transaction_id: str

    :rtype: MethodResponse
    """
    dome.close_shutter()
    ret = std_res(request)
    response.status = 200
    return ret


@put(get_url('findhome'))
def dome_find_home_put(device_number):  # noqa: E501
    """Start operation to search for the dome home position.

    After Home position is established initializes Azimuth to the default value and sets the AtHome flag. # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id:
    :type client_id: str
    :param client_transaction_id:
    :type client_transaction_id: str

    :rtype: MethodResponse
    """
    dome.find_home()
    ret = std_res(request)
    response.status = 200
    return ret


@put(get_url('openshutter'))
def dome_open_shutter_put(device_number):  # noqa: E501
    """Open shutter or otherwise expose telescope to the sky.

    Open shutter or otherwise expose telescope to the sky. # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id:
    :type client_id: str
    :param client_transaction_id:
    :type client_transaction_id: str

    :rtype: MethodResponse
    """
    dome.open_shutter()
    ret = std_res(request)
    response.status = 200
    return ret

@put(get_url('park'))
def dome_park_put(device_number):  # noqa: E501
    """Rotate dome in azimuth to park position.

    After assuming programmed park position, sets AtPark flag. # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id:
    :type client_id: str
    :param client_transaction_id:
    :type client_transaction_id: str

    :rtype: MethodResponse
    """
    dome.park()
    ret = std_res(request)
    response.status = 200
    return ret



@put(get_url('setpark'))
def dome_set_park_put(device_number):  # noqa: E501
    """Set the current azimuth, altitude position of dome to be the park position

    Set the current azimuth, altitude position of dome to be the park position. # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id:
    :type client_id: str
    :param client_transaction_id:
    :type client_transaction_id: str

    :rtype: MethodResponse
    """
    dome.set_park_azimuth()
    ret = std_res(request)
    response.status = 200
    return ret


@get(get_url('shutterstatus'))
def dome_shutter_status_get(device_number):  # noqa: E501
    """Status of the dome shutter or roll-off roof

    Returns the status of the dome shutter or roll-off roof. 0 = Open, 1 = Closed, 2 = Opening, 3 = Closing, 4 = Shutter status error # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: IntResponse
    """
    status = dome.get_shutter_status()
    ret = std_res(request)
    ret['Value'] = status
    response.status = 200
    return ret


@get(get_url('slaved'))
def dome_slaved_get(device_number):  # noqa: E501
    """Indicates whether the dome is slaved to the telescope

    True if the dome is slaved to the telescope in its hardware, else False. # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: BoolResponse
    """
    ret = std_res(request)
    ret['Value'] = dome.slaved
    response.status = 200
    return ret

@put(get_url('slaved'))
def dome_slaved_put(device_number):  # noqa: E501
    """Sets whether the dome is slaved to the telescope

    Sets the current subframe height. # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param slaved:
    :type slaved: bool
    :param client_id:
    :type client_id: str
    :param client_transaction_id:
    :type client_transaction_id: str

    :rtype: MethodResponse
    """
    dome.slaved = request.forms.Slaved
    ret = std_res(request)
    response.status = 200
    return ret


@put(get_url('slewtoaltitude'))
def dome_slew_to_altitude_put(device_number, altitude=None, client_id=None, client_transaction_id=None):  # noqa: E501
    """Slew the dome to the given altitude position.

    Slew the dome to the given altitude position. # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param altitude:
    :type altitude: str
    :param client_id:
    :type client_id: str
    :param client_transaction_id:
    :type client_transaction_id: str

    :rtype: MethodResponse
    """
    ret = std_res(request)
    response.status = 200
    ret['ErrorNumber'] = 1024
    ret['ErrorMessage'] = "Slew to altitude not supported"
    return ret


@put(get_url('slewtoazimuth'))
def dome_slew_to_azimuth_put(device_number, azimuth=None, client_id=None, client_transaction_id=None):  # noqa: E501
    """Slew the dome to the given azimuth position.

    Slew the dome to the given azimuth position. # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param azimuth:
    :type azimuth: str
    :param client_id:
    :type client_id: str
    :param client_transaction_id:
    :type client_transaction_id: str

    :rtype: MethodResponse
    """
    ret = std_res(request)
    result = dome.slew_to_az(_float(request.forms.Azimuth))
    response.status = 200
    if(not result['OK']):
        ret['ErrorNumber'] = result['ErrorNumber']
        ret['ErrorMessage'] = result['ErrorMessage']
    return ret

@get(get_url('slewing'))
def dome_slewing_get(device_number):  # noqa: E501
    """Indicates whether the any part of the dome is moving

    True if any part of the dome is currently moving, False if all dome components are steady. # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param client_id: Client&#x27;s unique ID.
    :type client_id: int
    :param client_transaction_id: Client&#x27;s transaction ID.
    :type client_transaction_id: int

    :rtype: BoolResponse
    """
    ret = std_res(request)
    ret['Value'] = dome.slewing
    response.status = 200
    return ret

# TODO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@put(get_url('synctoazimuth'))
def dome_sync_to_azimuth_put(device_number, azimuth=None, client_id=None, client_transaction_id=None):  # noqa: E501
    """Synchronize the current position of the dome to the given azimuth.

    Synchronize the current position of the dome to the given azimuth. # noqa: E501

    :param device_number: Zero based device number as set on the server
    :type device_number: int
    :param azimuth:
    :type azimuth: str
    :param client_id:
    :type client_id: str
    :param client_transaction_id:
    :type client_transaction_id: str

    :rtype: MethodResponse
    """
    ret = std_res(request)
    result = dome.synctoazimuth(_float(request.forms.Azimuth))
    response.status = 200
    if(not result['OK']):
        ret['ErrorNumber'] = result['ErrorNumber']
        ret['ErrorMessage'] = result['ErrorMessage']
    return ret

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging.basicConfig(format="%(asctime)s %(name)s: %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Astropolis Ash Dome ASCOM Alpaca driver")
    parser.add_argument(
        "-v", "--verbose", help="Set logging to verbose mode", action="store_true"
    )
    parser.add_argument(
        "-vv", "--veryverbose", help="Set logging to debug mode", action="store_true"
    )
    parser.add_argument(
        "-l", "--logfile", help="Log to file", action="store_true"
    )
    parser.add_argument(
        "-t", "--test", help="Use a fake dome encoder", action="store_true"
    )
    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.INFO)
    if args.veryverbose:
        logger.setLevel(logging.DEBUG)

    if args.test:
        dome = FakeDome()
    else:
        dome = Dome()
    if args.logfile:
        filehandler = f"{datadir}vastlog-{datenow:%Y%M%d-%H_%M_%S}.log"
        fh = logging.FileHandler(filehandler)
        fh.setLevel(logging.DEBUG if args.verbose else logging.INFO)
        # add the handlers to the logger
        logger.addHandler(fh)

    bottle.debug(args.verbose)
    logging.info("Starting Astropolis Ash Dome ASCOM Alpaca driver")
    #run(host='0.0.0.0', port=11111, reloader=True)
    run(host='0.0.0.0', port=11111, reloader=False, quiet=not args.verbose)
