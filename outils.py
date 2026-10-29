import re
import subprocess


def decoder(octets):
    """Les commandes Windows n'utilisent pas toutes le même encodage :
    netsh répond en UTF-8, ping dans l'encodage de la console (oem).
    On essaie UTF-8, et si ça échoue, on utilise oem."""
    try:
        return octets.decode("utf-8")
    except UnicodeDecodeError:
        return octets.decode("oem", errors="replace")


def executer(commande, delai=30):
    """Lance une commande Windows et renvoie sa sortie texte ('' en cas d'échec)."""
    try:
        resultat = subprocess.run(commande, capture_output=True, timeout=delai)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""
    return decoder(resultat.stdout)


def powershell(script, delai=30):
    """Lance une commande PowerShell et renvoie sa sortie texte."""
    return executer(["powershell", "-NoProfile", "-Command", script], delai)


# Fonctionne en français ("temps=14 ms", "temps<1ms") et en anglais ("time=14ms")
RE_TEMPS = re.compile(r"(?:temps|time)\s*[=<]\s*(\d+)\s*ms", re.IGNORECASE)


def analyser_ping(sortie):
    """Extrait la liste des temps de réponse (en ms) d'une sortie de ping."""
    return [int(t) for t in RE_TEMPS.findall(sortie)]


def ping(cible, nb=4, delai_ms=1000):
    """Envoie nb pings vers cible. Renvoie (liste des temps, sortie brute)."""
    commande = ["ping", "-n", str(nb), "-w", str(delai_ms), cible]
    sortie = executer(commande, delai=nb * delai_ms / 1000 + 10)
    return analyser_ping(sortie), sortie