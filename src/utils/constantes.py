from pathlib import Path

TARGET_YEARS = [2002, 2007, 2012, 2017, 2022]
BASE_DIR = Path(__file__).resolve().parents[2]  # remonte au dossier racine du projet
CLEAN_DIR = BASE_DIR / "data" / "clean"
DEPARTEMENT_MAP = {
    "ain": "01", "aisne": "02", "alpes-maritimes": "06", "bouches-du-rhône": "13",
    "charente-maritime": "17", "côte-d'or": "21", "finistère": "29", "haute-garonne": "31",
    "gironde": "33", "hérault": "34", "isère": "38", "loire-atlantique": "44",
    "meurthe-et-moselle": "54", "nord": "59", "oise": "60", "pas-de-calais": "62",
    "rhône": "69", "paris": "75", "var": "83", "la réunion": "974"
}
BORD_MAP = {
    "MACRON EMMANUEL":           "centre",
    "BAYROU FRANCOIS":           "centre",
    "LASSALLE JEAN":             "centre",
    "JOLY EVA":                  "centre",
    "LEPAGE CORINNE":            "centre",
    "CHIRAC JACQUES":            "droite",
    "SARKOZY NICOLAS":           "droite",
    "FILLON FRANCOIS":           "droite",
    "DE VILLIERS PHILIPPE":      "droite",
    "DUPONT-AIGNAN NICOLAS":     "droite",
    "SAINT-JOSSE JEAN":          "droite",
    "MADELIN ALAIN":             "droite",
    "NIHOUS FREDERIC":           "droite",
    "BOUTIN CHRISTINE":          "droite",
    "JOSPIN LIONEL":             "gauche",
    "HOLLANDE FRANCOIS":         "gauche",
    "ROYAL SEGOLENE":            "gauche",
    "HAMON BENOIT":              "gauche",
    "MELENCHON JEAN LUC":        "gauche",
    "BUFFET MARIE-GEORGE":       "gauche",
    "CHEVENEMENT JEAN-PIERRE":   "gauche",
    "TAUBIRA CHRISTIANE":        "gauche",
    "HUE ROBERT":                "gauche",
    "BESANCENOT OLIVIER":        "extreme_gauche",
    "LAGUILLER ARLETTE":         "extreme_gauche",
    "POUTOU PHILIPPE":           "extreme_gauche",
    "ARTHAUD NATHALIE":          "extreme_gauche",
    "GLUCKSTEIN DANIEL":         "extreme_gauche",
    "SCHIVARDI GERARD":          "extreme_gauche",
    "LE PEN JEAN MARIE":         "extreme_droite",
    "LE PEN MARINE":             "extreme_droite",
    "MEGRET BRUNO":              "extreme_droite",
    "ASSELINEAU FRANCOIS":       "extreme_droite",
    "BOVE JOSE":                 "autre",
    "VOYNET DOMINIQUE":          "autre",
    "MAMERE NOEL":               "autre",
    "CHEMINADE JACQUES":         "autre"
}
