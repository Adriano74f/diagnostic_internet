EXPLICATIONS = {
    "pas_connexion": {
        "titre": "Votre ordinateur n'est connecté à aucun réseau",
        "explication": "Ni le Wi-Fi ni un câble ne sont actifs : le problème se situe "
                       "sur votre ordinateur, avant même la box.",
        "conseils": [
            "Vérifiez que le Wi-Fi est activé et que le mode avion est désactivé.",
            "Si vous êtes en câble, vérifiez qu'il est bien branché des deux côtés.",
            "Redémarrez l'ordinateur si le Wi-Fi n'apparaît plus dans la liste.",
        ],
    },
    "wifi_faible": {
        "titre": "Le signal Wi-Fi est trop faible",
        "explication": "Votre ordinateur capte mal la box. Un signal faible ralentit "
                       "la connexion et provoque des coupures, même si Internet "
                       "fonctionne bien jusqu'à la box.",
        "conseils": [
            "Rapprochez-vous de la box ou éloignez les obstacles (murs épais, micro-ondes).",
            "Placez la box en hauteur et dans un endroit dégagé.",
            "Pour un poste fixe, utilisez un câble ou un répéteur Wi-Fi.",
        ],
    },
    "box_ou_reseau_local": {
        "titre": "Le problème se situe entre votre ordinateur et votre box",
        "explication": "Votre box répond lentement ou perd des données : le souci est "
                       "dans votre logement (Wi-Fi perturbé, box surchargée), "
                       "pas chez votre fournisseur.",
        "conseils": [
            "Redémarrez la box : débranchez-la 30 secondes puis rebranchez-la.",
            "Testez avec un câble : si tout va mieux, c'est le Wi-Fi qui est en cause.",
            "Arrêtez les téléchargements ou vidéos en cours sur les autres appareils.",
        ],
    },
    "panne_fai": {
        "titre": "Votre box fonctionne, mais Internet ne répond pas",
        "explication": "Votre ordinateur communique bien avec la box, mais rien ne "
                       "passe au-delà : la panne vient de la ligne ou de votre "
                       "fournisseur d'accès.",
        "conseils": [
            "Regardez les voyants de la box (un voyant rouge indique souvent une panne de ligne).",
            "Redémarrez la box.",
            "Consultez la page des incidents de votre fournisseur, ou appelez son "
            "service client en lui donnant ce rapport.",
        ],
    },
    "dns": {
        "titre": "Le service qui traduit les noms de sites (DNS) fonctionne mal",
        "explication": "Internet fonctionne, mais le « carnet d'adresses » qui "
                       "transforme un nom comme google.fr en adresse est lent ou en "
                       "panne : les sites mettent longtemps à s'ouvrir, ou ne "
                       "s'ouvrent pas du tout.",
        "conseils": [
            "Redémarrez la box.",
            "Utilisez un DNS public (1.1.1.1 ou 8.8.8.8) dans les paramètres réseau de l'ordinateur.",
            "Si le problème persiste, signalez-le à votre fournisseur.",
        ],
    },
    "fai_sature": {
        "titre": "Le réseau de votre fournisseur est ralenti",
        "explication": "Tout va bien jusqu'à votre box, mais les délais ou les pertes "
                       "augmentent juste après, sur le réseau du fournisseur : "
                       "saturation ou incident de son côté.",
        "conseils": [
            "Refaites le test à une autre heure (la saturation est fréquente le soir).",
            "Consultez la page des incidents de votre fournisseur.",
            "Si cela dure plusieurs jours, contactez-le en lui donnant ce rapport.",
        ],
    },
    "internet_lointain": {
        "titre": "Le ralentissement se situe loin sur Internet",
        "explication": "Votre connexion et le réseau de votre fournisseur sont "
                       "corrects : la dégradation apparaît plus loin, sur des réseaux "
                       "que ni vous ni votre fournisseur ne contrôlez.",
        "conseils": [
            "Ce type de problème est souvent temporaire : réessayez plus tard.",
            "Si un seul site est lent, le problème vient sans doute de ce site.",
            "Aucune action n'est nécessaire de votre côté.",
        ],
    },
    "debit_insuffisant": {
        "titre": "Le débit est inférieur à ce qu'il devrait être",
        "explication": "La connexion répond vite, mais la quantité de données "
                       "transférée par seconde est faible : téléchargements et vidéos "
                       "sont lents.",
        "conseils": [
            "Vérifiez qu'aucun autre appareil ne télécharge en même temps.",
            "Refaites le test en câble : le Wi-Fi peut limiter le débit.",
            "Si le débit reste faible en câble, contactez votre fournisseur.",
        ],
    },
    "connexion_saine": {
        "titre": "Votre connexion fonctionne normalement",
        "explication": "Tous les tests sont bons : Wi-Fi, box, DNS, fournisseur et "
                       "débit. Si un site ou une application est lent, le problème "
                       "vient sans doute de ce site.",
        "conseils": [
            "Essayez un autre site pour comparer.",
            "Vérifiez si le service utilisé a une panne connue.",
            "Relancez le diagnostic au moment précis où la lenteur se produit.",
        ],
    },
}