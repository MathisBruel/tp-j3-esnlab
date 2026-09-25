# TP J3 — Projet Systèmes & Réseaux (Bootcamp SR)

## Contexte

Domaine : `esnlab.local`
Objectif : intégrer et prouver le fonctionnement bout-en-bout d'une infra Windows Server (AD DS/DNS/DHCP + partage SMB) et d'un réseau segmenté en VLAN avec routage inter-VLAN.

## Topologie

Voir `topologie-tp-j3-esnlab.drawio`.

**Adressage (source de vérité) :**

| Élément | Adresse | Rôle |
|---|---|---|
| DC01 | 192.168.10.10/24 | AD DS + DNS + DHCP |
| FILE01 | 192.168.10.20/24 | Partage SMB "Compta" |
| CLIENT01 | DHCP (bail 192.168.10.100-150) | Joint au domaine |
| VLAN 10 (Users) | 192.168.2.0/25 | GW .1 |
| VLAN 20 (Servers) | 192.168.2.128/25 | GW .129 |

> ⚠️ À vérifier avec le formateur : DC01/FILE01 sont sur `192.168.10.0/24`, distinct des sous-réseaux VLAN — R1 route donc entre 3 réseaux (voir note dans le fichier .drawio).

## Journal des décisions

| Date/heure | Action | Justification |
|---|---|---|
| 23/09 (session initiale) | Promotion DC01 en DC (esnlab.local), forêt créée | Rôle AD DS installé |
| 23/09 (juste après) | Renommage WIN-HNE5NMVES2Q → DC01 (via `netdom`, poste déjà promu) | Cohérence du nommage avant jonction des autres postes |
| 23/09 19:42 | Dossier `C:\Partages\Compta` créé sur FILE01, droits NTFS (G-Compta, Admins du domaine, SYSTEM) | Préparer le partage SMB |
| 23/09 | FILE01 joint au domaine `esnlab.local` | Prérequis pour appliquer des droits AD sur le partage |
| 23/09 | Groupe `G-Compta` créé, Alice ajoutée (membre), Bob non ajouté | Préparer le test PASS/DENY |
| 23/09 | Partage SMB `Compta` créé (droits partage + NTFS, double verrou) | Premier essai en PowerShell non-élevé refusé (Accès refusé) → recréé via session élevée |
| 23/09 | Rôle DHCP installé et autorisé sur DC01, étendue `192.168.10.100-150`, options 003/006/015 | Permettre à CLIENT01 d'obtenir un bail cohérent |
| 23/09 23:57 | VM CLIENT01 installée (Windows 10), bail DHCP obtenu (`192.168.10.100`) | — |
| 23/09 | **Incident réseau** : CLIENT01 recevait une IP `10.0.2.x` (DHCP interne VirtualBox) au lieu du DHCP de DC01 | Cause : le "Réseau NAT" de CLIENT01 (`NatNetwork`, créé par défaut) avait son propre DHCP actif, distinct de celui utilisé par DC01/FILE01 malgré le même mode réseau ; corrigé via `VBoxManage natnetwork modify --dhcp off` + redémarrage à froid des VM |
| 23/09 | CLIENT01 renommé et joint au domaine `esnlab.local`, placé dans l'OU `PostesClients` | L'OU par défaut `Computers` ne supporte pas le lien de GPO |
| 23/09 | GPO `GPO-Lecteur-Compta` créée (mappage lecteur `Z:` → `\\FILE01\Compta`), liée à `PostesClients` | Relier la preuve GPO à la preuve SMB dans un seul test |
| 23/09 | **Incident GPO** : `gpresult` renvoyait `N/A` malgré la GPO liée — cause 1 : session en compte local (`CLIENT01\Administrateur`), cause 2 : Alice dans `CN=Users` donc hors de portée de l'OU ciblée pour les réglages "Configuration utilisateur" | Corrigé par reconnexion en compte domaine + activation du **loopback processing (mode Fusion)** sur la GPO |
| 24/09 00:19 | `gpresult /r` confirme `GPO-Lecteur-Compta` sous "Objets Stratégie de groupe appliqués" pour `ESNLAB\alice` | Preuve d'application, pas seulement de liaison |
| — | Topologie Packet Tracer montée : SW1/SW2 (VLAN 10/20, trunk 802.1Q), R1 (sous-interfaces `.10`/`.20`, router-on-a-stick) | GNS3 écarté faute d'image Cisco IOS disponible |
| — | **Incident VLAN** : ping PC10→PC20 en échec (100% perte) malgré une config SW1/SW2/R1 correcte | Cause : câblage physique inversé (PC10 branché sur le port access-VLAN20 de SW2, PC20 sur le port access-VLAN10 de SW1) — corrigé en permutant les deux câbles |
| — | Ping inter-VLAN PC10 → PC20 validé (TTL=127, 1 saut via R1) | Le premier paquet perdu sur le test final est un délai ARP normal, pas un défaut |

## Recette de tests

| Test | Source | Cible | Attendu | Résultat |
|---|---|---|---|---|
| Boot VM | — | DC01/FILE01/CLIENT01 | Démarrage complet | ✅ PASS |
| DNS domaine + SRV | DC01 | esnlab.local | Résolution + SRV LDAP/Kerberos | ✅ PASS |
| FILE01 membre du domaine | DC01 | FILE01 | `Get-ADComputer` réussit | ✅ PASS |
| CLIENT01 membre du domaine | DC01 | CLIENT01 | `Get-ADComputer` réussit, OU `PostesClients` | ✅ PASS |
| Bail DHCP CLIENT01 | DC01 | CLIENT01 | IP dans le scope, GW/DNS/domaine cohérents | ✅ PASS |
| SMB Alice → Compta | FILE01 | \\FILE01\Compta | PASS | ✅ PASS |
| SMB Bob → Compta | FILE01 | \\FILE01\Compta | DENY | ✅ DENY |
| GPO appliquée | CLIENT01 | — | PASS (via `gpresult`) | ✅ PASS |
| Inter-VLAN | PC10 (VLAN10) | PC20 (VLAN20) | PASS via R1 | ✅ PASS |

**11/11 preuves renseignées** — détail complet dans `evidence.json` et le dossier `evidence/`.

## Vérifier les preuves

```bash
python3 check_evidence.py
```

## Limites

- **VLAN/trunk/routage validés dans Packet Tracer avec des PC simulés (PC10/PC20), pas avec les vraies VM système.** Faute d'image Cisco IOS pour GNS3, le trafic réel de CLIENT01 (VirtualBox) n'a pas traversé physiquement la topologie Packet Tracer — la logique VLAN/trunk/inter-VLAN est prouvée, mais pas l'intégration bout-en-bout avec le vrai poste client.
- **DC01, FILE01 et CLIENT01 tournent sur une seule machine hôte**, reliés par un Réseau NAT VirtualBox — aucun test n'a été fait à travers un réseau physique ou plusieurs hôtes.
- **Le test SMB PASS/DENY ne couvre que deux comptes** (Alice/Bob) sur un seul dossier — pas de test de récursivité sur des sous-dossiers, ni de comptes multiples/groupes imbriqués.
- **Seuls 2 des 5 scénarios d'incidents prévus par le TP ont été traités** (GPO non appliquée, ping inter-VLAN cassé par câblage) — rencontrés naturellement pendant la construction plutôt que simulés volontairement. Les incidents DNS (jointure par IP), DHCP (mauvaise config reçue) et boot VM n'ont pas été testés.
- **Les preuves de boot** montrent l'heure du dernier démarrage au moment de la capture, pas un test de résilience sur un cycle complet d'extinction/rallumage de chaque VM.
- **Le mapping DC01/FILE01 (192.168.10.0/24) vs VLAN20 "Serveurs" (192.168.2.128/25)** reste tel quel (R1 route entre 3 réseaux distincts) — non confirmé avec le formateur comme étant l'architecture réellement attendue.
