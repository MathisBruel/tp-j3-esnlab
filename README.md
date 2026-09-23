# TP J3 — Projet Systèmes & Réseaux (Bootcamp SR)

## Contexte

Domaine : `esnlab.local`
Objectif : intégrer et prouver le fonctionnement bout-en-bout d'une infra Windows Server (AD DS/DNS/DHCP + partage SMB) et d'un réseau segmenté en VLAN avec routage inter-VLAN.

## Topologie

Voir `topologie-tp-j3-esnlab.drawio` (à exporter en PNG et référencer ici une fois finalisée).

**Adressage (source de vérité) :**

| Élément | Adresse | Rôle |
|---|---|---|
| DC01 | 192.168.10.10/24 | AD DS + DNS + DHCP |
| FILE01 | 192.168.10.20/24 | Partage SMB "Compta" |
| CLIENT01 | DHCP | Joint au domaine |
| VLAN 10 (Users) | 192.168.2.0/25 | GW .1 |
| VLAN 20 (Servers) | 192.168.2.128/25 | GW .129 |

> ⚠️ À vérifier avec le formateur : DC01/FILE01 sont sur `192.168.10.0/24`, distinct des sous-réseaux VLAN — R1 route donc entre 3 réseaux (voir note dans le fichier .drawio).

## Journal des décisions

_(à compléter au fil du TP — une ligne par action significative)_

| Date/heure | Action | Justification |
|---|---|---|
| | Promotion DC01 en DC (esnlab.local) | Rôle AD DS installé, forêt créée |
| | Renommage WIN-HNE5NMVES2Q → DC01 | Cohérence du nommage avant jonction des autres postes |
| | FILE01 joint au domaine | Prérequis pour le partage SMB avec droits AD |
| | Création G-Compta, Alice (membre), Bob (non-membre) | Préparer le test PASS/DENY |
| | Partage SMB "Compta" (droits partage + NTFS) | Double verrou volontaire |

## Recette de tests

| Test | Source | Cible | Attendu | Résultat |
|---|---|---|---|---|
| Boot VM | — | DC01/FILE01/CLIENT01 | Démarrage complet | ⏳ |
| DNS domaine + SRV | DC01 | esnlab.local | Résolution + SRV LDAP/Kerberos | ✅ PASS |
| SMB Alice → Compta | FILE01 | \\FILE01\Compta | PASS | ⏳ |
| SMB Bob → Compta | FILE01 | \\FILE01\Compta | DENY | ⏳ |
| GPO appliquée | CLIENT01 | — | PASS | ⏳ |
| DHCP client | CLIENT01 | — | Bail cohérent (GW/DNS/domaine) | ⏳ |
| Inter-VLAN | PC VLAN10 | Serveur VLAN20 | PASS | ⏳ |

Détail des preuves : voir `evidence.json` et le dossier `evidence/`.

## Vérifier les preuves

```bash
python3 check_evidence.py
```

## Limites

_(à compléter en fin de TP — ce que la recette ne démontre pas)_

## Restitution orale (90s)

Problème → Action → Preuve → Limite.
