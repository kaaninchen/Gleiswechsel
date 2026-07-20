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
```
{
    "token": "", # Token des Bots
    "stations": [ "Berlin Hbf", "Hamburg Hbf", "München Hbf", "Amsterdam Centraal"], # Bahnhöfe, von denen die Anzeigetafelns gelesen werden. Namen kann man auf https://dbf.finalrewind.org/ nachschlagen.
    "server": , # Discord Server ID
    "vc": , # Server VC ID
    "random": true, # Random Zug aus der Anzeigetafel (true) oder erster Zug, der angezeigt wird (false)
    "formatting": "┇", # VC Name. Davor steht der Emoji, danach der Zug
    "blacklist": [] # Blacklist für bestimmte Zug-Typen
}

```

#### random:
Bei kleineren Bahnhöfen stehen an den Anzeigetafeln die Namen Züge öfters Stunden, bevor der Zug eigentlich abfährt, da dort sonst keiner fährt. Dadurch wird auch der Name des VC sehr lange gleich bleiben.   
Sollte man `random = false` setzen, würde immer der erste Zug an der Anzeigetafel genommen werden, welcher auch der erst der am frühesten losfährt. Wenn man viele Bahnhöfe hat besteht darin keine Gefahr. 

Wenn man nur einen Bahnhof hat ist es stark empfohlen random zu nutzen. Sonst könnte der Bot bei unvollständigen Einträgen in einer Schleife immer wieder vergeblich den selben Zug probieren.

#### blacklist:  
Die Blacklist ist dafür gedacht, ganze Zugtypen zu ignorieren. So würde man es beispielsweise bevorzugen, dass der Bot keine ICE's, keine NightJets und keine European Sleepers auswählt, da diese sehr lange Strecken haben und der VC somit lange unverändert bleibt:
```
{
    ...
    "blacklist": [
        "ICE",
        "NJ",
        "ES
    ]
}
```  

Die Namen der einzelnen Zugtypen kann mit im Footer von `/info` oder im Terminal log erfahren.

## Data 
Es kann vorkommen, dass während dem `/info` Befehl das Logo und die Farbe des Bahnuntermehns fehlt.

![Beispiel für fehlende Daten](.github/info_fehlende_daten.png)  

Die zugehörigen Daten lassen sich innerhalb [operators.py](src/data/operators.py) ergänzen. Der Aufbau dabei sollte selbsterklärend sein, dennoch habe ich eine kleine Beschreibung in die Datei hinzugefügt. Bei Änderungen sind PR's willkommen.  
Die Datei wird leider nie vollständig sein da die verschiedenen Fahrtaufträge in Deutschland sehr fragmentiert sind.   

Emojis für die Formattierung werden dynamisch anhand des Zugtypens gepulled. Dabei wird zwischen Nahverkehr und Fernverkehr unterschieden. Bei einem Zugtyp, welcher zu keiner der Kategorie assigned ist, wird ein Fallback Emoji ist. Sollte man einen Zugtypen hinzufügen wollen oder die Emojis ändern/deaktivieren wollen ist dies in [emojis.py](src/data/emojis.py) möglich. Die Namen der einzelnen Zugtypen kann mit im Footer von `/info` oder im Terminal log erfahren.

Die Statuseinträge, von welchen der Bot alle 5 Minuten einen aussucht, kann mn in [status.py](src/data/status.py) anpassen.