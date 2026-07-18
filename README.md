# Gleiswechsel
Gleiswechel ist ein Discord Bot, welcher einen Sprachkanal zu einer real-existierenden, aktuell befahrenden Zugverbindung umbenennt. Diesen Namen behält der Kanal so lange, wie die Verbindung in echt dauert.  

![Beispiel Kanal](.github/preview_kanal.png) 

Der Bot stellt außerdem den `/info` Befehl dar, welche einem weitere Informationen zur Verbindung zurückgibt  

![Beispiel info](.github/preview_info.png)

## Setup
```sh
git clone https://github.com/kaaninchen/Gleiswechsel.git
python -m venv venv 
source venv/bin/activate
pip install -r requirements.txt 
```

### Config

`$ mv config.json.example`

Aktuell gibt es kein error handling für die config (kommt bald!!), also BITTE stell sicher dass du keine unerwarteten Daten eingegeben hast
```
{
    "token": "", // Discord Token
    "stations": [ "Berlin Hbf", "Hamburg Hbf", "München Hbf", "Amsterdam Centraal"], // Stationen deiner Wahl. Im Zweifel auf https://dbf.finalrewind.org/ Namen raussuchen
    "server": ,  // Discord Server ID 
    "vc": , // Discord VC ID
    "formatting": "🚅┇", // Name des Kanals
    "random": false // Random Züge aussuchen (true) oder immer die erste Station der Anzeigetafel (false)
}

```

#### Erklärung bezüglich random:
Bei kleineren Bahnhöfen stehen an den Anzeigetafeln die Namen Züge öfters Stunden vor Abfahrt, da das Gleis sonst frei ist. Dadurch wird auch der Name des VC sehr lange gleich bleiben. Sollte man random ausmachen, würde immer der erste Zug an der Anzeigetafel genommen werden, welcher auch der erst der am frühesten losfährt. Wenn man aber wenige Bahnhöfen zur Auswahl hat könnte es repetitiv werden, da die Züge ja oft hin und her fahren.  

Wenn man nur einen Bahnhof hat ist es stark empfohlen random zu nutzen. Sonst könnte der Bot bei unvollständigen Einträgen in einer Schleife immer wieder vergeblichg den selben Zug probieren.

## Metadaten 
Es kann vorkommen, dass während dem `/info` Befehl das Logo und die Farbe des Bahnuntermehns fehlt.

![Beispiel für fehlende Daten](.github/info_fehlende_daten.png)  

Die zugehörigen Daten lassen sich innerhalb [operators.py](src/data/operators.py) ergänzen. Der Aufbau dabei sollte selbsterklärend sein, dennoch habe ich eine kleine Beschreibung in die Datei hinzugefügt. Bei Änderungen sind PR's willkommen, ebenso wie Issues falls man das nicht selber ändern will da das ja eigentlich mein Job sein sollte.  

Die Statuseinträge, von welchen der Bot alle 5 Minuten einen aussucht, kann mn in [status.py](src/data/operators.py) anpassen