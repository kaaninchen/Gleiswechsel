OPERATORS = { 
    "fallback": {
        "unknown": True,
        "logo": "https://images.emojiterra.com/google/noto-emoji/unicode-15/color/512px/1f686.png",
        "color": 0x087BBB
    },
    "db_allgemein": {
        "logo": "https://marketingportal.extranet.deutschebahn.com/resource/blob/13602522/c53f806b9df966e144010b276af72dd2/Bild_09-data.png",
        "color": 0xEC0016,
        "slogan": ["Senk ju vor träwelling wis Deutsche Bahn.", "Bitte beachten Sie die umgekehrte Wagenreihung.", "Zurückbleiben bitte!", "Alle reden vom Wetter. Wir nicht.", "Die Bahn macht mobil.", "Grün abgefahren"]
    },
    "db_bawü": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/d/d1/Bwegt_Logo_%282020%29.jpg",
        "color": 0xFFBF34,
        "slogan": ["Nett hier", "Aber waren Sie schon mal in Baden-Württemberg?", "Bwegt euch!"]
    },
    "Ostdeutsche Eisenbahn GmbH": {
        "logo": "https://www.odeg.de/fileadmin/user_upload/Unternehmensseite/presse/pressebilder/ODEG_Pressebilder_Logo-CMYK-JPG.jpg",
        "color": 0x00745C
    },
    "Nederlandse Spoorwegen": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Logo_NS.svg/960px-Logo_NS.svg.png",
        "color": 0X00337F,
        "slogan": ["Goed op weg", "Welkom in de trein van morgen", "Veilig, Vlug, Voordelig", "we haben een serious probleem", "Neuken in de keuken"]
    },
    "eurobahn": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/3/34/Digital_Logo_eurobahn.png",
        "color": 0x005a9b,
    },
    "Arverio Bayern": {
        "logo": "https://cdn.discordapp.com/attachments/1383843132906537023/1528006572805062776/Arverio_Avi_Bayern_blau_RGB.png?ex=6a5cba83&is=6a5b6903&hm=5781ae6c372c92ab4f52409c6fc91e5014ac34ccf24db665ade052e8135bdde0&animated=true", # alternative nötig!
        "color": 0x0083BE
    },
    "Bayerische Regiobahn": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Logo_BRB_2015.svg/1920px-Logo_BRB_2015.svg.png",
        "color": 0xF61526
    },
    "Abellio Rail Mitteldeutschland GmbH": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Abellio_logo.svg/1920px-Abellio_logo.svg.png",
        "color": 0xD7002E
    },
    "SBB": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/SBB_logo_simplified.svg/960px-SBB_logo_simplified.svg.png",
        "color": 0xEB0000
    }
}

OPERATOR_ALIASES = {
    "DB Regio AG Baden-Württemberg": OPERATORS["db_bawü"],
    "DB Regio Stuttgart GmbH": OPERATORS["db_bawü"],
    "DB Fernverkehr AG": OPERATORS["db_allgemein"],
    "DB Regio AG NRW": OPERATORS["db_allgemein"],
    "DB Regio AG Nord": OPERATORS["db_allgemein"],
    "SBB GmbH": OPERATORS["SBB"],
    "Schweizerische Bundesbahnen SBB": OPERATORS["SBB"],
}