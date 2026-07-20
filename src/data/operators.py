''''
Die Datei gibt dem Embed zugehörige Metadaten der Zugbetreiber. Identifiziert wird dabei durch die genauen Namen der Unternehmen. 
Diese werden sowohl im /info Embed als auch in der Konsole angezeigt. 

| Feld    | Optional | Wert  | Beschreibung                                                          |
|---------|----------|-------|-----------------------------------------------------------------------|
| Unknown | Ja       | Bool  | Eigentlich nur für fallback relevant, sollte man weglassen            |
| Logo    | Nein     | URL   | Das Logo in der Ecke des Embeds. Am besten PNG, SVG geht leider nicht |
| Color   | Nein     | HEX   | HEX Color Code des Streifen vom Embed, muss mit 0x anfangen           |
| Slogan  | Ja       | Liste | Zufälliger Text aus der Liste im Footer                               |

Sollte es dazu kommen, dass mehrere Anbieter die selben Metadaten nutzen sollen, kann man einen Eintrag für alle in OPERATORS setzen und 
die zugehörigen Anbieternamen in OPERATOR_ALIASES auf den Eintrag lenken lassen. db_bawü ist dafür ein gutes Beispiel.

Nachdem diese Datei editiert wurde muss der Bot nicht neugestartet werden.
'''
OPERATORS = { 
    "fallback": {
        "unknown": True,
        "logo": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQCVeC5E0mNNBKyQftQaFMzxIVkbDvEnSzWv07h_c8PdA&s=10",
        "color": 0xFFFFFF
    },
    "db_allgemein": {
        "logo": "https://marketingportal.extranet.deutschebahn.com/resource/blob/13602522/c53f806b9df966e144010b276af72dd2/Bild_09-data.png",
        "color": 0xEC0016,
        "slogan": ["Senk ju vor träwelling wis Deutsche Bahn.", "Bitte beachten Sie die umgekehrte Wagenreihung.", "Zurückbleiben bitte!", "Alle reden vom Wetter. Wir nicht.", "Die Bahn macht mobil.", "Grün abgefahren"]
    },
    "db_bayern": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Bahnland_Bayern_Logo_2021.svg/500px-Bahnland_Bayern_Logo_2021.svg.png",
        "color": 0x0095DB
    },
    "db_bawü": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Bwegt_Logo.svg/960px-Bwegt_Logo.svg.png",
        "color": 0xFFBF34,
        "slogan": ["Nett hier", "Aber waren Sie schon mal in Baden-Württemberg?", "Bwegt euch!"]
    },
    "Ostdeutsche Eisenbahn GmbH": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/ODEG-Logo_Neu.svg/960px-ODEG-Logo_Neu.svg.png",
        "color": 0x00745C
    },
    "Nederlandse Spoorwegen": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Logo_NS.svg/960px-Logo_NS.svg.png",
        "color": 0X00337F,
        "slogan": ["Goed op weg", "Welkom in de trein van morgen", "Veilig, Vlug, Voordelig", "we haben een serious probleem", "Neuken in de keuken"]
    },
    "eurobahn": {
        "logo": "https://cdn.discordapp.com/attachments/1383843132906537023/1528405390260179146/Eurpnajm.png?ex=6a5e2df1&is=6a5cdc71&hm=d73fc3458f59f8942a5a0f51311308b12567b35b55b64aab0726bf6be92b3b0e&animated=true",
        "color": 0x005a9b,
    },
    "Arverio Bayern": {
        "logo": "https://cdn.discordapp.com/attachments/1383843132906537023/1528006572805062776/Arverio_Avi_Bayern_blau_RGB.png?ex=6a5cba83&is=6a5b6903&hm=5781ae6c372c92ab4f52409c6fc91e5014ac34ccf24db665ade052e8135bdde0&animated=true", # alternative nötig!
        "color": 0x0083BE
    },
    "Abellio Rail Mitteldeutschland GmbH": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Abellio_logo.svg/1920px-Abellio_logo.svg.png",
        "color": 0xD7002E
    },
    "SBB": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/SBB_logo_simplified.svg/960px-SBB_logo_simplified.svg.png",
        "color": 0xEB0000
    },
    "Nordbahn Eisenbahngesellschaft": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/b/b5/Logo_Nordbahn_NAH.SH_Blau_positiv_final.png",
        "color": 0x1A2848
    },
    "Erfurter Bahn GmbH": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Erfurter_Bahn_logo.svg/960px-Erfurter_Bahn_logo.svg.png",
        "color": 0x009133
    },
    "S-Bahn Hannover (Transdev)": {
        "logo": "https://cdn.discordapp.com/attachments/1526274436523888732/1528470315234234520/sbahn.png?ex=6a5e6a68&is=6a5d18e8&hm=c9f630c6f0c646eafeccef9b4d591ce8fcf8856b2b45f14e72fbf25e32edb017&animated=true",
        "color": 0x1A4389
    },
    "Regionalverkehre Start Deutschland GmbH (Start Mitteldeutschland)": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Logo_der_Regionalverkehre_Start_Deutschland.svg/960px-Logo_der_Regionalverkehre_Start_Deutschland.svg.png",
        "color": 0x61A731
    },
    "Westbahn Management GmbH": {
        "logo": "https://corporate.westbahn.at/uploads/Logos/westbahn2025-logo-signet-small.png",
        "color": 0x1D4A83
    },
    "European Sleeper": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/European_Sleeper_Logo.svg/960px-European_Sleeper_Logo.svg.png",
        "color": 0xEB4A27
    }
}

OPERATOR_ALIASES = {
    "DB Regio AG Baden-Württemberg": OPERATORS["db_bawü"],
    "DB Regio Stuttgart GmbH": OPERATORS["db_bawü"],
    "Arverio Baden-Württemberg": OPERATORS["db_bawü"],
    "Bayerische Regiobahn": OPERATORS["db_bayern"],
    "DB Regio AG Bayern": OPERATORS["db_bayern"],
    "DB Fernverkehr AG": OPERATORS["db_allgemein"],
    "DB Regio AG NRW": OPERATORS["db_allgemein"],
    "DB Regio AG Nord": OPERATORS["db_allgemein"],
    "DB Regio AG Südost": OPERATORS["db_allgemein"],
    "DB Regio AG Nordost": OPERATORS["db_allgemein"],
    "DB Regio AG Mitte": OPERATORS["db_allgemein"],
    "SBB GmbH": OPERATORS["SBB"],
    "Schweizerische Bundesbahnen SBB": OPERATORS["SBB"],
}