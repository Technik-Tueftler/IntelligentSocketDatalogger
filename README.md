# IntelligentSocketDatalogger
[![Docker image build](https://github.com/Technik-Tueftler/IntelligentSocketDatalogger/actions/workflows/build.yml/badge.svg)](https://github.com/Technik-Tueftler/IntelligentSocketDatalogger/actions/workflows/build.yml)[![Pylint/Unittest](https://github.com/Technik-Tueftler/IntelligentSocketDatalogger/actions/workflows/merge_test.yml/badge.svg)](https://github.com/Technik-Tueftler/IntelligentSocketDatalogger/actions/workflows/merge_test.yml)

IntelligentSocketDatalogger is an app which reads intelligent sockets in individually adjustable time intervals and stores their return values in an InfluxDB. Each socket can be set with additional parameters. So you can have the total Wh per device written into a text file once a day (time variable).

[English readme](https://github.com/Technik-Tueftler/IntelligentSocketDatalogger/blob/main/README.md)
 • [deutsche readme](https://github.com/Technik-Tueftler/IntelligentSocketDatalogger/blob/main/README.de.md)

## Overview
- Supported Python 3.10
- Shelly Plug S sockets were tested
- Runs locally, as well as a Docker container

## Supported sockets
Currently, only the Shelly Plug S sockets have been tested. In principle, any socket could be used that returns the following elements as json:

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
| name               |  type   | explanation                                                     |   unit    |
|:-------------------|:-------:|:----------------------------------------------------------------|:---------:|
| device             | String  | name of device                                                  |     -     |
| time               | String  | Time stamp of the measurement in UTC                            |     -     |
| power              |  Float  | Current power of the device. Formatting: %Y-%m-%dT%H:%M:%S.%fZ" |   Watt    |
| is_valid           | Boolean | Returned values are ok                                          |     -     |
| device_temperature |  Float  | temperature of the socket (no ambient temperature               |    °C     |
| fetch_success      | Boolean | Device was accessible during query                              |     -     |
| energy_wh          |  Float  | Current work of the device in the last time period              | watt-hour |

## Configuration files
In order to adapt the project to the own conceptions, two configuration files are available. Furthermore there are automatically created files, which depend on an error or the setting of the project.

| Name              | Explanation                      |   Path    |
|:------------------|:---------------------------------|:---------:|
| config.json       | General settings for the project | ../files/ |
| devices.json      | List of all smart sockets        | ../files/ |
| main.log          | Error and information logging    | ../files/ |
| <device name>.log | Information logging              | ../files/ |

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
    "ip": "192.168.178.200",
    "update_time": 10,
    "cost_calc_month": "01",
    "cost_calc_year": "01.01"
  },
  "Herd":
  {
    "ip": "192.168.178.201",
    "update_time": 30,
    "cost_calc_day": true
  }
}
````
`washing machine:` Device name, which is recorded.  
`ip:` IP address in the connected network  
`update_time:` Update time at which interval new data should be requested. Specification is in `seconds`.  
`cost_day:` Enables the feature that once a day the total costs and work of the device for the last 24 hours are stored. The time when the process should start is set here. The formatting is: `HH:MM`. It is also indicated how many measured values are missing for an estimation, which quality the value has. The time depends on the setting on the server.  
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
