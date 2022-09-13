# IntelligentSocketDatalogger
[![Docker image build](https://github.com/Technik-Tueftler/IntelligentSocketDatalogger/actions/workflows/build.yml/badge.svg)](https://github.com/Technik-Tueftler/IntelligentSocketDatalogger/actions/workflows/build.yml)[![Pylint](https://github.com/Technik-Tueftler/IntelligentSocketDatalogger/actions/workflows/pylint.yml/badge.svg)](https://github.com/Technik-Tueftler/IntelligentSocketDatalogger/actions/workflows/pylint.yml)

IntelligentSocketDatalogger ist eine App, welche in einzel einstellbaren Zeitintervallen intelligente Steckdosen abfragt und deren Rückgabewerten in eine InfluxDB speichert. Dabei kann jede Steckdose mit zusätzlichen Parametern eingestellt werden. So kann man sich einmal am Tag (Uhrzeit variable) die gesamten Wh pro Gerät in eine Textdatei schreiben lassen.

[English readme](https://github.com/Technik-Tueftler/IntelligentSocketDatalogger/blob/main/README.md)
 • [deutsche readme](https://github.com/Technik-Tueftler/IntelligentSocketDatalogger/blob/main/README.de.md)

## Übersicht
- Unterstützt wird Python 3.10
- Getestet wurden Shelly Plug S Steckdosen
- Läuft lokal, als auch als Docker Container

## Unterstütze Steckdosen
Aktuell wurden nur die Shelly Plug S Steckdosen getestet. Prinzipiell könnte jede Steckdose benutzt werden, welche folgende Elemente als Json zurückgeben:

## Installation und Ausführung
1. Lokal läuft das Programm durch Ausführen der `main.py`. Aktuell muss noch darauf geachtet werden, dass die Umgebungsvariablen in die IDE oder in die Umgebung geladen werden. Hierzu einfach das Repository kopieren und die main.py starten. Getestet und entwickelt wurde das Programm unter Python 3.10.
2. Über einen Docker Container. Siehe Dokumentation: <https://hub.docker.com/r/techniktueftler/intelligent_socket_datalogger>

## Umgebungsvariablen
| Variable                  | Erklärung                              | Einheit | Standardwert | Nötig |
|:--------------------------|:---------------------------------------|:-------:|:------------:|:-----:|
| DB_IP_ADDRESS             | IP Adresse oder Hostname der Datenbank |    -    |      -       |  Ja   |
| DB_USER_NAME              | Benutzername zum einloggen in die DB   |    -    |      -       |  Ja   |
| DB_NAME                   | Datenbankname zum speichern der Daten  |    -    |      -       |  Ja   |
| DB_USER_PASSWORD          | Passwort zum Benutzername              |    -    |    Keins     | Nein  |
| DB_PORT                   | Port zur Datenbank                     |    -    |     8086     | Nein  |
| SSL                       | Wird SSL benutzt                       |    -    |    False     | Nein  |
| VERIFY_SSL                | SSL verifizierte                       |    -    |    False     | Nein  |

## Database structure
| Name               |   Typ   | Erklärung                                                           |  Einheit   |
|:-------------------|:-------:|:--------------------------------------------------------------------|:----------:|
| device             | String  | Name des Gerätes                                                    |     -      |
| time               | String  | Zeitstempel der Messung in UTC                                      |     -      |
| power              |  Float  | Aktuelle Leistung des Gerätes. Formatierung: %Y-%m-%dT%H:%M:%S.%fZ" |    Watt    |
| is_valid           | Boolean | Zurückgegebene Werte sind ok                                        |     -      |
| device_temperature |  Float  | Temperatur der Steckdose (keine Umgebungstemperatur                 |     °C     |
| fetch_success      | Boolean | Gerät war während der Abfrage erreichbar                            |     -      |
| energy_wh          |  Float  | Aktuelle Arbeit des Gerätes in der letzten Zeitperiode              | Wattstunde |

## Konfigurationsdateien
Um das Projekt an die eigenen Vorstellungen anzupassen, stehen zwei Konfigurationsdateien zur Verfügung. Des Weiteren gibt es automatisch erzeuge Dateien, welche von einem Fehler abhängen oder der Einstellung des Projektes.

| Name             | Erklärung                                 |    Pfad     |
|:-----------------|:------------------------------------------|:-----------:|
| config.json      | Allgemeine Einstellungen für das Projekt  |  ../files/  |
| devices.json     | Auflistung aller Intelligenten Steckdosen |  ../files/  |
| main.log         | Fehler- und Informationsprotokollierung   |  ../files/  |
| <Gerätename>.log | Informationsprotokollierung               |  ../files/  |

### config.json
````commandline 
{
  "general":
  {
    "log_level": "info"
  }
}
````
`log_level:` Protokollierungslevel für das Projekt. Mögliche Einstellungen: *debug, info, warning, error, critical*

### devices.json
````commandline 
{
  "Waschmaschine":
  {
    "ip": "192.168.178.200",
    "update_time": 10,
    "cost_day": "00:00"
  },
  "Herd":
  {
    "ip": "192.168.178.201",
    "update_time": 30
  }
}
````
`Waschmaschine:` Gerätename, welcher aufgezeichnet wird.  
`ip:` IP-Adresse im verbundenen Netzwerk  
`update_time:` Aktualisierungszeit in welchem Abstand neue Daten abgefragt werden sollen. Angabe ist in `Sekunden`.  
`cost_day:` Aktiviert das Feature, dass einmal am Tag die gesamten Kosten und die Arbeit des Gerätes für die letzten 24 Stunden abgelegt werden. Eingestellt wird hier der Zeitpunkt, wann der Prozess starten soll. Die Formatierung ist: `HH:MM`. Es wird auch angegeben, wie viele Messwerte fehlen für eine Einschätzung, welche Güte der Wert hat. Die Uhrzeit ist abhängig von der Einstellung auf dem Server.    