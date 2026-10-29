import time
from statistics import median

import dns.exception
import dns.resolver

from modele import ResultatTest, Statut
from seuils import classer, pire, DNS_MS

DOMAINES = ["google.com", "wikipedia.org", "github.com", "cloudflare.com", "lemonde.fr"]
DNS_PUBLICS = {"Cloudflare": "1.1.1.1", "Google": "8.8.8.8"}


def creer_resolveur(serveur=None, delai=2.0):
    """Résolveur DNS : celui du PC si serveur est None, sinon le serveur donné."""
    if serveur is None:
        resolveur = dns.resolver.Resolver()            # lit la configuration du PC
    else:
        resolveur = dns.resolver.Resolver(configure=False)
        resolveur.nameservers = [serveur]
    resolveur.lifetime = delai                         # délai max par requête (s)
    return resolveur


def mesurer_resolution(resolveur, domaine):
    """Temps de résolution en ms, ou None en cas d'échec."""
    debut = time.perf_counter()
    try:
        resolveur.resolve(domaine, "A")
    except dns.exception.DNSException:
        return None
    return (time.perf_counter() - debut) * 1000


def mesurer_serveur(serveur=None):
    """Résout tous les domaines avec un serveur et renvoie les statistiques."""
    try:
        resolveur = creer_resolveur(serveur)
    except dns.resolver.NoResolverConfiguration:
        return {"serveurs": [], "temps": [], "echecs": len(DOMAINES), "mediane": None}

    temps, echecs = [], 0
    for domaine in DOMAINES:
        t = mesurer_resolution(resolveur, domaine)
        if t is None:
            echecs += 1
        else:
            temps.append(t)

    return {
        "serveurs": [str(s) for s in resolveur.nameservers],
        "temps": [round(t, 1) for t in temps],
        "echecs": echecs,
        "mediane": round(median(temps), 1) if temps else None,
    }


def tester_dns():
    nom = "DNS"
    systeme = mesurer_serveur()
    publics = {nom_dns: mesurer_serveur(ip) for nom_dns, ip in DNS_PUBLICS.items()}
    details = {"systeme": systeme, "publics": publics}

    valides = [(n, p) for n, p in publics.items() if p["mediane"] is not None]
    meilleur = min(valides, key=lambda x: x[1]["mediane"], default=None)
    serveurs_pc = ", ".join(systeme["serveurs"]) or "aucun"

    # Cas 1 : le DNS du PC ne répond pas du tout
    if systeme["mediane"] is None:
        if meilleur:
            message = (f"Le DNS configuré sur le PC ({serveurs_pc}) ne répond pas, "
                       f"alors que les DNS publics fonctionnent.")
        else:
            message = "Aucun serveur DNS ne répond (ni celui du PC, ni les DNS publics)."
        return ResultatTest(nom, Statut.PROBLEME, details=details, message=message)

    # Cas 2 : le DNS du PC répond -> on évalue sa rapidité
    statut = classer(systeme["mediane"], DNS_MS)
    if systeme["echecs"]:
        statut = pire(statut, Statut.ATTENTION)

    message = (f"DNS du PC ({serveurs_pc}) : {systeme['mediane']} ms, "
               f"{systeme['echecs']} échec(s) sur {len(DOMAINES)}.")
    if meilleur:
        nom_meilleur, stats = meilleur
        message += f" Plus rapide en public : {nom_meilleur} ({stats['mediane']} ms)."
        ecart = systeme["mediane"] - stats["mediane"]
        if systeme["mediane"] > 2 * stats["mediane"] and ecart > 50:
            message += " Changer de DNS accélérerait l'ouverture des sites."

    return ResultatTest(nom, statut, systeme["mediane"], "ms", details, message)