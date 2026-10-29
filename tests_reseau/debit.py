import time
import urllib.request

import speedtest

from modele import ResultatTest, Statut
from seuils import classer_debit

URL_DESCENDANT = "https://speed.cloudflare.com/__down?bytes={}"
URL_MONTANT = "https://speed.cloudflare.com/__up"
ENTETES = {"User-Agent": "diagnostic-internet/1.0"}


def mesurer_speedtest():
    st = speedtest.Speedtest(secure=True)
    st.get_best_server()
    descendant = st.download() / 1e6              # bits/s -> Mbit/s
    montant = st.upload(pre_allocate=False) / 1e6
    return {
        "source": "speedtest.net",
        "serveur": st.results.server.get("sponsor"),
        "descendant": round(descendant, 1),
        "montant": round(montant, 1),
    }


def mesurer_cloudflare(taille=25_000_000):
    """Solution de repli : chronomètre un téléchargement puis un envoi."""
    requete = urllib.request.Request(URL_DESCENDANT.format(taille), headers=ENTETES)
    debut = time.perf_counter()
    with urllib.request.urlopen(requete, timeout=30) as reponse:
        recu = len(reponse.read())
    descendant = recu * 8 / (time.perf_counter() - debut) / 1e6

    donnees = b"0" * (taille // 2)
    requete = urllib.request.Request(URL_MONTANT, data=donnees, headers=ENTETES, method="POST")
    debut = time.perf_counter()
    with urllib.request.urlopen(requete, timeout=30) as reponse:
        reponse.read()
    montant = len(donnees) * 8 / (time.perf_counter() - debut) / 1e6

    return {"source": "Cloudflare", "descendant": round(descendant, 1), "montant": round(montant, 1)}


def tester_debit(attendu=None):
    nom = "Débit"
    try:
        mesure = mesurer_speedtest()
    except Exception as erreur:                   # speedtest.net refuse parfois (403…)
        try:
            mesure = mesurer_cloudflare()
            mesure["erreur_speedtest"] = str(erreur)
        except Exception as erreur_repli:
            return ResultatTest(nom, Statut.ECHEC,
                                message=f"Mesure du débit impossible : {erreur_repli}")

    mesure["attendu"] = attendu
    message = (f"{mesure['descendant']} Mbit/s en réception, "
               f"{mesure['montant']} Mbit/s en envoi ({mesure['source']}).")
    if attendu:
        pourcent = round(100 * mesure["descendant"] / attendu)
        message += f" Soit {pourcent} % de l'abonnement ({attendu:g} Mbit/s)."

    statut = classer_debit(mesure["descendant"], attendu)
    return ResultatTest(nom, statut, mesure["descendant"], "Mbit/s", mesure, message)