from dataclasses import dataclass, field
from enum import Enum

class Statut(Enum):
    OK = "ok"
    ATTENTION = "attention"
    PROBLEME = "probleme"
    ECHEC = "echec"          # le test n'a pas pu s'exécuter

@dataclass
class ResultatTest:
    nom: str
    statut: Statut
    valeur: float | None = None   # mesure principale (ms, %, Mbit/s…)
    unite: str = ""
    details: dict = field(default_factory=dict)
    message: str = ""

@dataclass
class Diagnostic:
    cause: str                    # code de la cause, ex. "wifi_faible", "dns"
    zone: str                     # où se situe le problème
    confiance: str                # "forte" ou "moyenne"
    preuves: list = field(default_factory=list)       # mesures qui justifient la conclusion
    secondaires: list = field(default_factory=list)   # autres points à surveiller
    non_realises: list = field(default_factory=list)  # tests en échec
