# 🌿 Parole du Jour — Enfance Missionnaire
> **Paroisse Saint Michel de Houéto — Diocèse de Cotonou**  
> Système automatisé de création d'affiches quotidiennes et de diffusion de la Parole de Dieu.

---

## 📁 Architecture du projet

```text
Parole du jour/
├── index.html                   # Studio Web interactif & diffusion (Mobile & Desktop)
├── app.py                       # Serveur Web léger & API (/api/generate)
├── Dockerfile                   # Image de déploiement conteneurisée
├── docker-compose.yml           # Orchestration Docker
├── requirements.txt             # Dépendances Python minimales (Pillow, requests)
├── .env                         # Clé API Gemini (sécurisée et ignorée par Git)
├── .gitignore                   # Exclusion des secrets et caches
│
├── .github/workflows/
│   └── daily_poster.yml         # Automatisation cloud gratuite (GitHub Actions)
│
├── assets/
│   ├── logos/
│   │   ├── logo-EM-paroissial.jpeg     # Logo source
│   │   └── logo-EM-transparent.png    # Version détourée sur capsule blanche
│   ├── illustrations/                 # Galerie d'œuvres d'art sacré harmonisées
│   │   ├── saint-martin.jpg           # Saint Martin partageant son manteau (Charité)
│   │   ├── bon-berger.jpg             # Le Bon Berger et la brebis perdue (Miséricorde)
│   │   ├── samaritain.jpg             # Les dix lépreux et le Samaritain (Gratitude)
│   │   ├── sainte-cene.jpg            # La Sainte Cène et l'Eucharistie (Pain de Vie)
│   │   ├── resurrection.jpg           # Le Christ Ressuscité en gloire (Pâques)
│   │   └── croix-bible.jpg            # Sainte Écriture & Croix de lumière
│   └── archives/                      # Ébauches et références antérieures
│
├── scripts/
│   ├── generate_daily.py              # Script maître (AELF + Gemini LLM + Rendu synchronisé)
│   ├── generate_poster.py             # Moteur de composition graphique élastique (PIL 1080×1080)
│   ├── fetch_aelf.py                  # Client liturgique AELF
│   └── cron_daily.sh                  # Lanceur pour planificateur Linux (crontab)
│
└── output/                            # Affiches HD et textes prêts pour diffusion
    ├── parole-du-jour-saint-martin.png# Affiche Saint Martin (Blanc & Or)
    ├── parole-du-jour-bon-berger.png  # Affiche Bon Berger (Temps Ordinaire)
    ├── parole-du-jour-sainte-cene.png # Affiche Eucharistie
    ├── parole-du-jour-resurrection.png# Affiche Résurrection
    └── post-2026-11-11.txt            # Texte complet prêt à diffuser sur WhatsApp / Facebook
```

---

## 🚀 Options de Déploiement

### Option 1 : Déploiement Cloud Automatisé (GitHub Actions)
Le fichier `.github/workflows/daily_poster.yml` est déjà configuré :
1. Crée un dépôt GitHub (privé ou public).
2. Ajoute ta clé dans les secrets du dépôt : `Settings > Secrets and variables > Actions > New repository secret` :
   * Nom : `GEMINI_API_KEY`
   * Valeur : Ta clé API Gemini
3. **Le robot s'exécute automatiquement chaque jour à 05h00 UTC (06h00 au Bénin)**, récupère l'Évangile AELF, l'analyse avec Gemini, génère l'affiche et prépare le post prêt à diffuser.

---

### Option 2 : Déploiement Conteneurisé (Docker / VPS)
Sur un serveur ou VPS (avec Docker installé) :
```bash
# Lancer l'application et le serveur web
docker-compose up -d --build
```
L'application est immédiatement accessible sur `http://IP_DE_TON_SERVEUR:8080`.

---

### Option 3 : Déploiement Local / Tâche Cron Linux
Pour exécuter automatiquement la génération chaque matin sur ta machine Linux ou ton serveur :
```bash
crontab -e
```
Ajoute la ligne suivante (exemple pour 05h30 du matin) :
```text
30 5 * * * /bin/bash "/run/media/asteras/Nouveau nom/Mes projets/Parole du jour/scripts/cron_daily.sh"
```

---

### Option 4 : Serveur Web Local
Pour lancer l'application en local :
```bash
python3 app.py
```
Ouvre ensuite `http://localhost:8080` dans ton navigateur.

---

## 🎨 Les 4 Couleurs Liturgiques Automatisées

1. **Vert Liturgique** (*Temps Ordinaire*) : Vert émeraude adouci (`#1E5E3D`), doré et ivoire.
2. **Blanc & Or** (*Solennités, Pâques, Noël, Fêtes Mariales*) : Cartouche blanc pur immaculé (`#FFFFFF`), liseré et typographie or royal (`#C6922C`).
3. **Rouge** (*Martyrs, Apôtres, Rameaux, Pentecôte*) : Rouge rubis profond (`#7A1A22`).
4. **Violet** (*Avent, Carême*) : Pourpre améthyste solennel (`#441F63`).

> **Protection du logo** : Le logo officiel de l'Enfance Missionnaire est inséré dans une capsule blanche détourée à fin liseré doré, garantissant un contraste parfait sur tous les fonds.
