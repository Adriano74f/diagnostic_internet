import json
import re

from modele import ResultatTest, Statut
from outils import executer, powershell
from seuils import classer_signal


def cartes_actives():
    """Liste des cartes réseau physiques connectées."""
    script = (
        "Get-NetAdapter -Physical | Where-Object Status -eq 'Up' | "
        "Select-Object Name, InterfaceDescription, MediaType, LinkSpeed | ConvertTo-Json"
    )
    sortie = powershell(script).strip()
    if not sortie:
        return []
    try:
        donnees = json.loads(sortie)
    except json.JSONDecodeError:
        return []
    # Une seule carte -> PowerShell renvoie un objet, pas une liste
    return donnees if isinstance(donnees, list) else [donnees]


def infos_wifi():
    """Lit 'netsh wlan show interfaces' et renvoie un dictionnaire clé -> valeur."""
    sortie = executer(["netsh", "wlan", "show", "interfaces"])
    infos = {}
    for ligne in sortie.splitlines():
        m = re.match(r"^\s*(.+?)\s+:\s(.*)$", ligne)
        if m:
            infos.setdefault(m.group(1).strip(), m.group(2).strip())
    return infos


def chercher(infos, *cles):
    """Renvoie la première clé trouvée (gère les libellés FR et EN)."""
    for cle in cles:
        if cle in infos:
            return infos[cle]
    return None


def pourcentage_vers_dbm(pourcent):
    """Windows donne le signal en %, conversion approximative en dBm."""
    return pourcent / 2 - 100


def tester_interface():
    cartes = cartes_actives()
    if not cartes:
        return ResultatTest(
            "Connexion réseau", Statut.PROBLEME,
            message="Aucune carte réseau connectée (Wi-Fi désactivé ou câble débranché).",
        )

    wifi = [c for c in cartes if "802.11" in str(c.get("MediaType"))]
    if not wifi:
        carte = cartes[0]
        return ResultatTest(
            "Connexion réseau", Statut.OK,
            details={"type": "filaire", "carte": carte.get("InterfaceDescription"),
                     "vitesse": carte.get("LinkSpeed")},
            message=f"Connexion filaire ({carte.get('LinkSpeed')}).",
        )

    infos = infos_wifi()
    signal = chercher(infos, "Signal")
    if signal is None:
        return ResultatTest(
            "Wi-Fi", Statut.ECHEC,
            details={"brut": infos},
            message="Wi-Fi connecté, mais impossible de lire la force du signal.",
        )

    pourcent = int(signal.rstrip("%").strip())
    dbm = pourcentage_vers_dbm(pourcent)
    ssid = chercher(infos, "SSID")
    details = {
        "type": "wifi",
        "ssid": ssid,
        "signal_pourcent": pourcent,
        "canal": chercher(infos, "Canal", "Channel"),
        "reception_mbps": chercher(infos, "Réception (Mbits/s)", "Receive rate (Mbps)"),
        "transmission_mbps": chercher(infos, "Transmission (Mbits/s)", "Transmit rate (Mbps)"),
    }
    return ResultatTest(
        "Wi-Fi", classer_signal(dbm), dbm, "dBm", details,
        f"Réseau « {ssid} », signal {pourcent} % (≈ {dbm:.0f} dBm).",
    )