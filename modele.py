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
