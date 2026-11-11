#!/usr/bin/env python3
"""
fetch_aelf.py
Script d'automatisation pour récupérer les lectures du jour depuis l'API AELF
et générer l'affiche ainsi que le texte de diffusion.
"""
import sys
import json
import urllib.request
from datetime import datetime
from generate_poster import render_poster

def get_aelf_data(date_str=None):
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    url = f"https://api.aelf.org/v1/messes/{date_str}/france"
    req = urllib.request.Request(url, headers={"User-Agent": "ParoleDuJour/1.0"})
    
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Erreur lors de la récupération AELF : {e}", file=sys.stderr)
        return None

def process_daily_word(date_str=None):
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    print(f"[*] Récupération de la Parole du Jour pour le {date_str}...")
    data = get_aelf_data(date_str)
    if not data:
        print("[-] Impossible de récupérer les données.")
        return

    info = data.get("informations", {})
    couleur = info.get("couleur", "vert").lower()
    fete = info.get("fete") or info.get("ligne2", "")
    print(f"[+] Couleur liturgique : {couleur.upper()} ({fete})")

    # Extraire l'Évangile
    evangile = None
    for messe in data.get("messes", []):
        for lecture in messe.get("lectures", []):
            if lecture.get("type") == "evangile":
                evangile = lecture
                break
        if evangile:
            break

    if not evangile:
        print("[-] Aucun évangile trouvé pour cette date.")
        return

    ref = evangile.get("ref", "Évangile").replace("&nbsp;", " ").upper()
    titre = evangile.get("titre", "").strip()

    print(f"[+] Évangile : {ref}")
    print(f"[+] Titre : {titre}")

    out_file = f"output/parole-du-jour-{date_str}.png"
    render_poster(liturgical_theme=couleur, output_path=out_file)
    print(f"[✓] Affiche générée avec succès : {out_file}")

if __name__ == "__main__":
    target_date = sys.argv[1] if len(sys.argv) > 1 else "2026-11-10"
    process_daily_word(target_date)
