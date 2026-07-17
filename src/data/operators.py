db_slogans = ["Senk ju vor träwelling wis Deutsche Bahn.", "Bitte beachten Sie die umgekehrte Wagenreihung.", "Zurückbleiben bitte!", "Alle reden vom Wetter. Wir nicht.", "Die Bahn macht mobil.", "Grün abgefahren"]

OPERATORS = { 
    # alles außer slogan ist ESSENZIELL für den Bot. 
    # Color ist Hex Color Code mit 0x am anfang.
    "fallback": {
        "unknown": True,
        "logo": "https://upload.wikimedia.org/wikipedia/commons/2/20/Bahn_aus_Zusatzzeichen_1024-15_A.png",
        "color": 0x000000
    },
    "DB": {
        "unknown": False,
        "logo": "https://marketingportal.extranet.deutschebahn.com/resource/blob/13602522/c53f806b9df966e144010b276af72dd2/Bild_09-data.png",
        "color": 0xEC0016,
        "slogan": db_slogans
    },
    "Ostdeutsche Eisenbahn GmbH": {
        "unknown": False,
        "logo": "https://www.odeg.de/fileadmin/user_upload/Unternehmensseite/presse/pressebilder/ODEG_Pressebilder_Logo-CMYK-JPG.jpg",
        "color": 0x00745C
    }
}