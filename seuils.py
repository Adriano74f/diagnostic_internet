from modele import Statut

# (limite OK, limite ATTENTION) — au-delà : PROBLEME
LATENCE_BOX_MS = (10, 30)
LATENCE_INTERNET_MS = (50, 100)
PERTE_POURCENT = (0, 2)
DNS_MS = (100, 300)

# Pour le signal Wi-Fi, plus c'est haut, mieux c'est (en dBm)
SIGNAL_WIFI_DBM = (-60, -70)


def classer(valeur, limites):
    """Classe une mesure où une valeur plus grande est pire (latence, perte…)."""
    ok, attention = limites
    if valeur <= ok:
        return Statut.OK
    if valeur <= attention:
        return Statut.ATTENTION
    return Statut.PROBLEME


def classer_signal(dbm):
    """Classe le signal Wi-Fi : une valeur plus grande est meilleure."""
    bon, moyen = SIGNAL_WIFI_DBM
    if dbm >= bon:
        return Statut.OK
    if dbm >= moyen:
        return Statut.ATTENTION
    return Statut.PROBLEME