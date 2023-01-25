# IntelligentSocketDatalogger
[![Docker image build](https://github.com/Technik-Tueftler/IntelligentSocketDatalogger/actions/workflows/build.yml/badge.svg)](https://github.com/Technik-Tueftler/IntelligentSocketDatalogger/actions/workflows/build.yml)[![Pylint/Unittest](https://github.com/Technik-Tueftler/IntelligentSocketDatalogger/actions/workflows/merge_test.yml/badge.svg)](https://github.com/Technik-Tueftler/IntelligentSocketDatalogger/actions/workflows/merge_test.yml)

IntelligentSocketDatalogger is an app which reads intelligent sockets in individually adjustable time intervals and stores their return values in an InfluxDB. Each socket can be set with additional parameters. So you can have the total Wh per device written into a text file once a day (time variable).

[English readme](https://github.com/Technik-Tueftler/IntelligentSocketDatalogger/blob/main/README.md)
 • [deutsche readme](https://github.com/Technik-Tueftler/IntelligentSocketDatalogger/blob/main/README.de.md)

## Overview
- Supported Python 3.10
- Runs locally, as well as a Docker container
- Shelly Plug S and Shelly 3EM sockets were tested

## Supported sockets
Via a plugin concept, you can include any socket by writing your own handler and specifying the data that will be returned. The individual steps are explained in chapter `Use your own socket`. Furthermore, there are some examples in the file device_plugin.py.
- Shelly Plug S (type name: shelly:plug-s)  
- Shelly 3EM (type name: shelly:3em)  

## Installation and execution
1. Locally the program runs by executing the `main.py`. Currently, care must still be taken to load the environment variables into the IDE or environment. To do this, simply copy the repository and run main.py. The program was tested and developed under Python 3.10.
2. Via a Docker container. See documentation: <https://hub.docker.com/r/techniktueftler/intelligent_socket_datalogger>. Example for a docker compose file you can see below.

## Environment variables
| Variable         | Explanation                            | Unit | Default value | Required |
|:-----------------|:---------------------------------------|:----:|:-------------:|:--------:|
| DB_IP_ADDRESS    | IP address or hostname of the database |  -   |       -       |   Yes    |
| DB_USER_NAME     | User name for logging into the DB      |  -   |       -       |   Yes    |
| DB_NAME          | Database name to store data            |  -   |       -       |   Yes    |
| DB_USER_PASSWORD | Password to username                   |  -   |     None      |    No    |
| DB_PORT          | Port to database                       |  -   |     8086      |    No    |
| SSL              | Is SSL used                            |  -   |     False     |    No    |
| VERIFY_SSL       | SSL verified                           |  -   |     False     |    No    |

## Database structure
| name                 |  type   | explanation                                                     |   unit    |
|:---------------------|:-------:|:----------------------------------------------------------------|:---------:|
| device               | String  | name of device                                                  |     -     |
| time                 | String  | Time stamp of the measurement in UTC                            |     -     |
| power                |  Float  | Current power of the device. Formatting: %Y-%m-%dT%H:%M:%S.%fZ" |   Watt    |
| is_valid             | Boolean | Returned values are ok                                          |     -     |
| device_temperature   |  Float  | temperature of the socket (no ambient temperature)              |    °C     |
| fetch_success        | Boolean | Device was accessible during query                              |     -     |
| energy_wh            |  Float  | Current work of the device in the last time period              | watt-hour |
| current_a _b _c      |  Float  | Current on module A, B or C of the Shelly 3EM                   |  Ampere   |
| energy_wh_a _b _c    |  Float  | Current work on module A, B or C of the Shelly 3EM              | watt-hour |
| is_valid_a _b _c     | Boolean | Returned values are ok on module A, B or C of the Shelly 3EM    |     -     |
| power_a _b _c        |  Float  | Current power on module A, B or C of the Shelly 3EM             |   Watt    |
| power_factor_a _b _c |  Float  | Power factor on module A, B or C of the Shelly 3EM              |   Watt    |
| voltage_a _b _c      |  Float  | Voltage on module A, B or C of the Shelly 3EM                   |  lambda   |

## Configuration files
In order to adapt the project to the own conceptions, two configuration files are available. Furthermore there are automatically created files, which depend on an error or the setting of the project.

| Name              | Explanation                      |   Path    |
|:------------------|:---------------------------------|:---------:|
| config.json       | General settings for the project | ../files/ |
| devices.json      | List of all smart sockets        | ../files/ |
| main.log          | Error and information logging    | ../files/ |

### config.json
````commandline 
{
  "general":
  {
    "log_level": "info",
    "cost_calc_request_time": "00:00",
    "price_kwh": 0.296
  }
}
````
`log_level:` Logging level for the project. Possible settings: *debug, info, warning, error, critical*.  
`cost_calc_request_time:` Specify the time when the cost calculation will start. This parameter is valid for all calculations. The default time is 00:00.  
`price_kwh:` Indicates the price per kilowatt-hour. The default price is 0.30€.

### devices.json
````commandline 
{
  "Waschmaschine":
  {
    "type": "shelly:plug-s",
    "ip": "192.168.178.200",
    "update_time": 10,
    "cost_calc_month": "01",
    "cost_calc_year": "01.01"
  },
  "Herd":
  {
    "type": "shelly:3em",
    "ip": "192.168.178.201",
    "update_time": 30,
    "cost_calc_day": true
  }
}
````
`washing machine:` Device name, which is recorded.  
`ip:` IP address in the connected network  
`update_time:` Update time at which interval new data should be requested. Specification is in __seconds__.  
`type:` The type of intelligent socket. Currently, only __shelly:plug-s__ and __shelly:3em__ are supported by default.
`cost_day:` Enables the feature that once a day the total costs and work of the device for the last 24 hours are stored. The time is set in __config.json__ with the parameter __cost_calc_request_time__. 
`cost_calc_month:` Activates the feature that once a month the total costs and the work of the device are calculated. The execution day in the month is set here.  
`cost_calc_year:` Activates the feature that once a year the total costs and the work of the device are calculated. The execution day and month are set here.

### ISDL Config Editor
If you are not familiar with the json formatting, you can use [ISDL Config Editor](isdledit.jojojux.de/editor) to create the config files in a graphical user interface.

## Docker Compose Example
````commandline
version: "2"
services:
  influxdb:
    image: techniktueftler/intelligent_socket_datalogger
    container_name: intelligent_socket_datalogger
    volumes:
      - /srv/dev-disk-by-uuid-0815/data/socket_datalogger/:/user/app/IntelligentSocketDatalogger/files/
    environment:
      - DB_IP_ADDRESS=192.193.194.195
      - DB_USER_NAME=shellyplug
      - DB_NAME=power_consumption
````

## Use your own socket
It is possible to create your own implementation to include your own smart sockets. To do this, the device must have a way to retrieve data. Either via a http request or via an API, which can be reached via Python. The steps would be:  
1. Copy the plugin template (project directory in files with the name device_plugin.py) into the mounted path of the docker container.  
2. Write a separate handler for each device and assign a type via the decorator. Here you can specify your own name. This type is then what you specify in the device.conf for the device as the type.  
3. The code under `def handler` must then contain the addressing of the device, the processing and at the end return the data in the required format.
Simply follow the example contained in the template file. If something is unclear or poorly defined, please be sure to write to me.  
