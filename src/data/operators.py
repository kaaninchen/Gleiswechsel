db_allgemein = {
    "logo": "https://marketingportal.extranet.deutschebahn.com/resource/blob/13602522/c53f806b9df966e144010b276af72dd2/Bild_09-data.png",
    "color": 0xEC0016,
    "slogan": ["Senk ju vor träwelling wis Deutsche Bahn.", "Bitte beachten Sie die umgekehrte Wagenreihung.", "Zurückbleiben bitte!", "Alle reden vom Wetter. Wir nicht.", "Die Bahn macht mobil.", "Grün abgefahren"]
}

db_bawü = {
    "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Bwegt_Logo.svg/960px-Bwegt_Logo.svg.png",
    "color": 0xFFBF34,
    "slogan": ["Nett hier", "Aber waren Sie schon mal in Baden-Württemberg?", "Bwegt euch!"]
}

OPERATOR_ALIASES = {
    "DB Regio AG Baden-Württemberg": db_bawü,
    "DB Regio Stuttgart GmbH": db_bawü,
    "DB Fernverkehr AG": db_allgemein,
    "DB Regio AG NRW": db_allgemein,
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
    },
    "eurobahn": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/3/34/Digital_Logo_eurobahn.png",
        "color": 0x005a9b
    },
    "Arverio Bayern": {
        "logo": "https://cdn.discordapp.com/attachments/1383843132906537023/1528006572805062776/Arverio_Avi_Bayern_blau_RGB.png?ex=6a5cba83&is=6a5b6903&hm=5781ae6c372c92ab4f52409c6fc91e5014ac34ccf24db665ade052e8135bdde0&animated=true", # alternative nötig!
        "color": 0x0083BE
    },
    "Bayerische Regiobahn": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Logo_BRB_2015.svg/1920px-Logo_BRB_2015.svg.png",
        "color": 0xF61526
    }
}