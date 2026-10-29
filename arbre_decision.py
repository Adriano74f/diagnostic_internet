from modele import Diagnostic, Statut
from seuils import PERTE_POURCENT

ZONE_PC = "Votre ordinateur"
ZONE_LOCAL = "Votre réseau local (Wi-Fi / box)"
ZONE_FAI = "Votre fournisseur d'accès"
ZONE_DNS = "Le serveur DNS"
ZONE_INTERNET = "Internet, au-delà de votre fournisseur"

# Causes qui font échouer tous les tests suivants : inutile de les lister en plus
CAUSES_BLOQUANTES = {"pas_connexion", "box_ou_reseau_local", "panne_fai"}


def statut(resultats, cle):
    r = resultats.get(cle)
    return r.statut if r else None


def en_probleme(resultats, cle):
    return statut(resultats, cle) == Statut.PROBLEME


def trouver_cause(r):
    """Parcourt l'arbre. Renvoie (cause, zone, confiance, tests servant de preuves)."""
    interface = r.get("interface")
    est_wifi = bool(interface and interface.details.get("type") == "wifi")

    # 1. Le PC est-il connecté ? Le signal Wi-Fi est-il correct ?
    if en_probleme(r, "interface"):
        if est_wifi:
            return "wifi_faible", ZONE_LOCAL, "forte", ["interface"]
        return "pas_connexion", ZONE_PC, "forte", ["interface"]

    # 2. La box répond-elle correctement ? (latence, perte vers la box)
    perte = r.get("perte")
    perte_box = perte.details.get("box") if perte else None
    if en_probleme(r, "passerelle") or (perte_box or 0) > PERTE_POURCENT[1]:
        cles = ["passerelle"]
        if perte_box:
            cles.append("perte")
        if est_wifi and statut(r, "interface") == Statut.ATTENTION:
            cles.append("interface")
        return "box_ou_reseau_local", ZONE_LOCAL, "forte", cles

    # 3. Internet est-il joignable au-delà de la box ?
    if en_probleme(r, "acces_internet"):
        return "panne_fai", ZONE_FAI, "forte", ["passerelle", "acces_internet"]

    # 4. Le DNS fonctionne-t-il ?
    if en_probleme(r, "dns"):
        return "dns", ZONE_DNS, "forte", ["dns"]

    # 5. Latence ou perte vers Internet : le traceroute dit OÙ ça se dégrade
    if en_probleme(r, "latence") or en_probleme(r, "perte"):
        trace = r.get("traceroute")
        degradation = trace.details.get("degradation") if trace else None
        cles = [c for c in ("latence", "perte") if en_probleme(r, c)]
        if trace:
            cles.append("traceroute")
        if degradation and degradation["saut"] > 4:
            return "internet_lointain", ZONE_INTERNET, "moyenne", cles
        return "fai_sature", ZONE_FAI, "forte" if degradation else "moyenne", cles

    # 6. Le débit est-il conforme ?
    if en_probleme(r, "debit"):
        return "debit_insuffisant", ZONE_FAI, "moyenne", ["debit"]

    # 7. Aucun problème trouvé
    return "connexion_saine", "Aucune", "forte", ["latence", "debit"]


def diagnostiquer(resultats):
    """resultats : dictionnaire {clé du test: ResultatTest}. Renvoie un Diagnostic."""
    cause, zone, confiance, cles = trouver_cause(resultats)

    preuves = [f"{resultats[c].nom} : {resultats[c].message}" for c in cles if c in resultats]

    secondaires = []
    if cause not in CAUSES_BLOQUANTES:
        secondaires = [
            f"{r.nom} : {r.message}"
            for c, r in resultats.items()
            if c not in cles and r.statut in (Statut.ATTENTION, Statut.PROBLEME)
        ]

    non_realises = [r.nom for r in resultats.values() if r.statut == Statut.ECHEC]
    return Diagnostic(cause, zone, confiance, preuves, secondaires, non_realises)