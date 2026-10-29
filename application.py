import queue
import threading
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk

from arbre_decision import diagnostiquer
from execution import NB_ETAPES, executer_diagnostic
from explications import EXPLICATIONS
from modele import Statut
from rapport import COULEURS, LIBELLES, enregistrer_rapport, texte_mesure

POLICE = "Segoe UI"


class Application:
    def __init__(self, fenetre):
        self.fenetre = fenetre
        self.messages = queue.Queue()   # communication thread de test -> fenêtre
        self.resultats = None
        self.diagnostic = None
        self.attendu = None

        fenetre.title("Pourquoi mon Internet est lent ?")
        fenetre.geometry("860x700")
        fenetre.minsize(720, 580)

        cadre = ttk.Frame(fenetre, padding=16)
        cadre.pack(fill="both", expand=True)

        # --- En-tête ---
        ttk.Label(cadre, text="Pourquoi mon Internet est lent ?",
                  font=(POLICE, 16, "bold")).pack(anchor="w")
        ttk.Label(cadre, wraplength=800,
                  text="Ce diagnostic teste votre connexion étape par étape (environ "
                       "2 minutes) et vous explique où se situe le problème."
                  ).pack(anchor="w", pady=(4, 12))

        # --- Saisie + bouton ---
        ligne = ttk.Frame(cadre)
        ligne.pack(fill="x")
        ttk.Label(ligne, text="Débit de votre abonnement (Mbit/s, facultatif) :").pack(side="left")
        self.champ_debit = ttk.Entry(ligne, width=8)
        self.champ_debit.pack(side="left", padx=6)
        self.bouton_lancer = ttk.Button(ligne, text="Lancer le diagnostic", command=self.lancer)
        self.bouton_lancer.pack(side="right")

        # --- Progression ---
        self.barre = ttk.Progressbar(cadre, maximum=NB_ETAPES)
        self.barre.pack(fill="x", pady=(12, 4))
        self.etat = ttk.Label(cadre, text="Prêt.")
        self.etat.pack(anchor="w")

        # --- Tableau des résultats ---
        self.tableau = ttk.Treeview(cadre, columns=("statut", "mesure", "detail"), height=8)
        self.tableau.heading("#0", text="Test")
        self.tableau.heading("statut", text="Statut")
        self.tableau.heading("mesure", text="Mesure")
        self.tableau.heading("detail", text="Détail")
        self.tableau.column("#0", width=150, stretch=False)
        self.tableau.column("statut", width=100, stretch=False)
        self.tableau.column("mesure", width=90, stretch=False)
        self.tableau.column("detail", width=440)
        for statut, couleur in COULEURS.items():
            self.tableau.tag_configure(statut.value, foreground=couleur)
        self.tableau.pack(fill="x", pady=12)

        # --- Diagnostic ---
        self.titre_diag = ttk.Label(cadre, text="", font=(POLICE, 13, "bold"), wraplength=800)
        self.titre_diag.pack(anchor="w")
        self.texte_diag = tk.Text(cadre, height=12, wrap="word", relief="flat",
                                  font=(POLICE, 10), padx=8, pady=8)
        self.texte_diag.tag_configure("gras", font=(POLICE, 10, "bold"))
        self.texte_diag.configure(state="disabled")
        self.texte_diag.pack(fill="both", expand=True, pady=(4, 8))

        self.bouton_rapport = ttk.Button(cadre, text="Exporter le rapport (HTML)",
                                         command=self.exporter, state="disabled")
        self.bouton_rapport.pack(anchor="e")

    # ---------- Lancement ----------

    def lancer(self):
        texte = self.champ_debit.get().strip().replace(",", ".")
        try:
            self.attendu = float(texte) if texte else None
        except ValueError:
            messagebox.showwarning("Débit invalide",
                                   "Indiquez un nombre (par exemple 300), ou laissez le champ vide.")
            return

        self.bouton_lancer.configure(state="disabled")
        self.bouton_rapport.configure(state="disabled")
        self.tableau.delete(*self.tableau.get_children())
        self.titre_diag.configure(text="")
        self.ecrire_diagnostic([])
        self.barre["value"] = 0

        threading.Thread(target=self.travailler, daemon=True).start()
        self.fenetre.after(100, self.verifier_messages)

    def travailler(self):
        """Exécuté dans un thread séparé : ne touche JAMAIS directement à la fenêtre."""
        try:
            resultats = executer_diagnostic(
                self.attendu,
                lambda numero, total, texte: self.messages.put(("progression", numero, texte)),
            )
            self.messages.put(("fini", resultats))
        except Exception as erreur:
            self.messages.put(("erreur", erreur))

    def verifier_messages(self):
        """Exécuté dans la fenêtre toutes les 100 ms : lit les nouvelles du thread."""
        try:
            while True:
                message = self.messages.get_nowait()
                if message[0] == "progression":
                    _, numero, texte = message
                    self.barre["value"] = numero
                    self.etat.configure(text=texte)
                elif message[0] == "fini":
                    self.afficher(message[1])
                    return
                elif message[0] == "erreur":
                    self.etat.configure(text="Erreur pendant le diagnostic.")
                    messagebox.showerror("Erreur", str(message[1]))
                    self.bouton_lancer.configure(state="normal")
                    return
        except queue.Empty:
            pass
        self.fenetre.after(100, self.verifier_messages)

    # ---------- Affichage ----------

    def afficher(self, resultats):
        self.resultats = resultats
        self.diagnostic = diagnostiquer(resultats)
        d = self.diagnostic

        for r in resultats.values():
            self.tableau.insert("", "end", text=r.nom, tags=(r.statut.value,),
                                values=(LIBELLES[r.statut], texte_mesure(r), r.message))

        texte = EXPLICATIONS[d.cause]
        couleur = COULEURS[Statut.OK] if d.cause == "connexion_saine" else COULEURS[Statut.PROBLEME]
        self.titre_diag.configure(text=texte["titre"], foreground=couleur)

        morceaux = [("Où ? ", "gras"), (f"{d.zone} (certitude : {d.confiance})\n\n", None),
                    (texte["explication"] + "\n", None)]
        if d.preuves:
            morceaux.append(("\nCe qui le montre :\n", "gras"))
            morceaux += [(f"  • {p}\n", None) for p in d.preuves]
        morceaux.append(("\nQue faire ?\n", "gras"))
        morceaux += [(f"  {i}. {c}\n", None) for i, c in enumerate(texte["conseils"], 1)]
        if d.secondaires:
            morceaux.append(("\nÀ surveiller aussi :\n", "gras"))
            morceaux += [(f"  • {s}\n", None) for s in d.secondaires]
        if d.non_realises:
            morceaux.append((f"\nTests non réalisés : {', '.join(d.non_realises)}\n", None))
        self.ecrire_diagnostic(morceaux)

        self.barre["value"] = NB_ETAPES
        self.etat.configure(text="Diagnostic terminé.")
        self.bouton_lancer.configure(state="normal")
        self.bouton_rapport.configure(state="normal")

    def ecrire_diagnostic(self, morceaux):
        self.texte_diag.configure(state="normal")
        self.texte_diag.delete("1.0", "end")
        for texte, style in morceaux:
            self.texte_diag.insert("end", texte, style or ())
        self.texte_diag.configure(state="disabled")

    def exporter(self):
        chemin = enregistrer_rapport(self.resultats, self.diagnostic, self.attendu)
        webbrowser.open(chemin.resolve().as_uri())
        self.etat.configure(text=f"Rapport enregistré : {chemin}")


def main():
    fenetre = tk.Tk()
    Application(fenetre)
    fenetre.mainloop()


if __name__ == "__main__":
    main()