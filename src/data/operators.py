db_logo = "https://marketingportal.extranet.deutschebahn.com/resource/blob/13602522/c53f806b9df966e144010b276af72dd2/Bild_09-data.png"
db_slogans = ["Senk ju vor träwelling wis Deutsche Bahn.", "Bitte beachten Sie die umgekehrte Wagenreihung.", "Zurückbleiben bitte!", "Alle reden vom Wetter. Wir nicht.", "Die Bahn macht mobil.", "Grün abgefahren"]

OPERATORS = { 
    # alles außer slogan ist ESSENZIELL für den Bot. 
    # Color ist Hex Color Code mit 0x am anfang.
    "fallback": {
        "name": "Unbekannter Anbieter",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/2/20/Bahn_aus_Zusatzzeichen_1024-15_A.png",
        "color": 0x000000
    },
    "ICE": {
        "name": "Deutsche Bahn",
        "logo": db_logo,
        "color": 0xEC0016,
        "slogan": db_slogans
    },
    "RB": {
        "name": "DB Regio",
        "logo": db_logo,
        "color": 0xEC0016,
        "slogan": db_slogans
    },
    "RE": {
        "name": "DB Regio",
        "logo": db_logo,
        "color": 0xEC0016,
        "slogan": db_slogans
    },
    "NBE": {
        "name": "Nordbahn",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/b/b5/Logo_Nordbahn_NAH.SH_Blau_positiv_final.png",
        "color": 0x1A2848
    }
}