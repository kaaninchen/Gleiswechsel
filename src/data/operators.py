db_slogans = ["Senk ju vor träwelling wis Deutsche Bahn.", "Bitte beachten Sie die umgekehrte Wagenreihung.", "Zurückbleiben bitte!", "Alle reden vom Wetter. Wir nicht.", "Die Bahn macht mobil.", "Grün abgefahren"]

db_allgemein = {
    "logo": "https://marketingportal.extranet.deutschebahn.com/resource/blob/13602522/c53f806b9df966e144010b276af72dd2/Bild_09-data.png",
    "color": 0xEC0016,
    "slogan": db_slogans
}

db_bawü = {
    "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Bwegt_Logo.svg/960px-Bwegt_Logo.svg.png",
    "color": 0xFFBF34,
    "slogan": ["Nett hier", "Aber waren Sie schon mal in Baden-Württemberg?", "Bwegt euch!"]
}

OPERATOR_ALIASES = {
    "DB Regio AG Baden-Württemberg": db_bawü,
    "DB Regio Stuttgart GmbH": db_bawü,
    "DB Fernverkehr": db_allgemein
}

OPERATORS = { 
    "fallback": {
        "unknown": True,
        "logo": "https://upload.wikimedia.org/wikipedia/commons/2/20/Bahn_aus_Zusatzzeichen_1024-15_A.png",
        "color": 0x000000
    },
    "Ostdeutsche Eisenbahn GmbH": {
        "logo": "https://www.odeg.de/fileadmin/user_upload/Unternehmensseite/presse/pressebilder/ODEG_Pressebilder_Logo-CMYK-JPG.jpg",
        "color": 0x00745C
    },
    "Nederlandse Spoorwegen": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Logo_NS.svg/960px-Logo_NS.svg.png",
        "color": 0X00337F
    }
}