# Manuel utilisateur — « Pourquoi mon Internet est lent ? »

## À quoi sert ce logiciel ?

Quand Internet est lent ou ne fonctionne plus, il est difficile de savoir d'où vient le problème : votre ordinateur, votre Wi-Fi, votre box, votre fournisseur d'accès ou le site que vous visitez ?

Ce logiciel vérifie votre connexion **étape par étape**, puis vous dit **où se situe le problème** et **quoi faire**, sans jargon technique.

## Lancer un diagnostic

1. Double-cliquez sur **`lancer.bat`** dans le dossier du logiciel.
2. *(Facultatif)* Indiquez le **débit de votre abonnement** en Mbit/s. Vous le trouverez sur votre contrat ou votre facture, par exemple « Fibre 500 Mb/s » → tapez `500`. Le logiciel pourra alors vérifier que vous recevez bien ce que vous payez.
3. Cliquez sur **Lancer le diagnostic**.
4. Patientez environ **2 minutes**. La barre de progression indique l'étape en cours.

**Conseil :** lancez le diagnostic **au moment où la lenteur se produit**. Si le problème a disparu, le logiciel ne pourra pas le voir.

## Lire les résultats

### Le tableau des tests

Chaque ligne correspond à une vérification, de la plus proche de vous à la plus lointaine :

| Couleur | Signification |
|---|---|
| 🟢 **OK** | Tout va bien |
| 🟠 **À surveiller** | Légèrement en dessous de la normale, sans être bloquant |
| 🔴 **Problème** | Anomalie nette |
| 🟣 **Non réalisé** | Le test n'a pas pu s'exécuter |

### Le diagnostic

Sous le tableau, le logiciel affiche sa conclusion :

- **Le titre** résume le problème (par exemple « Le signal Wi-Fi est trop faible »).
- **Où ?** indique la zone concernée : votre ordinateur, votre réseau local (Wi-Fi / box), le serveur DNS, votre fournisseur ou Internet.
- **Certitude :** « forte » quand un test échoue clairement, « moyenne » quand la conclusion est une déduction.
- **Ce qui le montre :** les mesures qui justifient la conclusion.
- **Que faire ?** des actions concrètes à essayer, dans l'ordre.
- **À surveiller aussi :** d'autres points moins graves.

## Les diagnostics possibles

| Diagnostic | En résumé | Première chose à faire |
|---|---|---|
| Pas de connexion | L'ordinateur n'est connecté à aucun réseau | Vérifier que le Wi-Fi est activé |
| Wi-Fi faible | L'ordinateur capte mal la box | Se rapprocher de la box |
| Box ou réseau local | Le souci est dans votre logement | Redémarrer la box |
| Panne du fournisseur | La box fonctionne, mais Internet ne répond pas | Regarder les voyants de la box, consulter les incidents du fournisseur |
| Problème DNS | Les sites mettent du temps à s'ouvrir | Redémarrer la box, ou utiliser un DNS public |
| Fournisseur saturé | Ralentissement sur le réseau du fournisseur | Refaire le test à une autre heure |
| Problème loin sur Internet | Ralentissement hors de votre portée | Réessayer plus tard |
| Débit insuffisant | Téléchargements et vidéos lents | Tester en câble, puis contacter le fournisseur |
| Connexion saine | Tout fonctionne | Le problème vient sans doute du site utilisé |

## Le rapport

Cliquez sur **Exporter le rapport** : une page s'ouvre dans votre navigateur avec le diagnostic complet et toutes les mesures. Elle est enregistrée dans le dossier `rapports`.

Si vous contactez votre fournisseur d'accès, **envoyez-lui ce rapport** : il contient les informations techniques dont son service client aura besoin.

## Questions fréquentes

**Le test Wi-Fi indique « Non réalisé » et parle de localisation.**
Windows 11 demande d'autoriser la localisation pour lire les informations Wi-Fi : *Paramètres → Confidentialité et sécurité → Localisation*, puis activez les services de localisation et l'accès pour les applications de bureau.

**Le test de débit indique « Non réalisé ».**
Le service de mesure n'a pas répondu. C'est normal si Internet ou le DNS ne fonctionnent pas. Sinon, relancez le diagnostic un peu plus tard.

**Le diagnostic dit que tout va bien, mais Internet est lent.**
Le problème vient probablement du site ou de l'application que vous utilisez. Essayez un autre site pour comparer, et relancez le diagnostic au moment exact où la lenteur se produit.

**Les résultats changent d'un diagnostic à l'autre.**
C'est normal : une connexion varie selon l'heure, le nombre d'appareils connectés et l'activité de votre fournisseur.
