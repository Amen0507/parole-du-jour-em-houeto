#!/usr/bin/env python3
"""
generate_daily.py
Script maître d'automatisation pour "Parole du Jour" (Paroisse Saint Michel de Houéto) :
1. Récupère l'Évangile et la liturgie du jour via l'API AELF
2. Analyse et enrichit les contenus via Google Gemini API (ou extraction théologique avancée)
3. Sélectionne intelligemment l'œuvre d'art sacré en harmonie avec l'Évangile et la fête
4. Génère l'affiche HD 1080x1080 adaptée au temps liturgique avec typographie élastique
5. Exporte le texte complet prêt à diffuser sur WhatsApp / Facebook
6. Retourne l'objet complet synchronisé pour l'API web
"""

import os
import sys
import json
import re
import urllib.request
import urllib.parse
import base64
from datetime import datetime

try:
    from generate_poster import render_poster
except ImportError:
    from scripts.generate_poster import render_poster

# 1. Charger la clé API depuis .env
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

JOURS_FR = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
MOIS_FR = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
]

def format_date_fr(date_str):
    """Formatte YYYY-MM-DD en français soigné : Mercredi 11 Novembre 2026"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    jour = JOURS_FR[dt.weekday()]
    mois = MOIS_FR[dt.month - 1]
    return f"{jour} {dt.day} {mois} {dt.year}"

# 2. Récupérer les lectures depuis l'API AELF (selon la documentation https://api.aelf.org/)
def get_aelf_data(date_str):
    """
    Interroge l'API AELF (https://api.aelf.org/v1/messes/{date}/{zone})
    Priorité 1 : zone 'afrique' (Afrique francophone / Bénin / Paroisse St Michel de Houéto)
    Priorité 2 : zone 'romain'
    Priorité 3 : zone 'france'
    """
    zones = ["afrique", "romain", "france"]
    for zone in zones:
        url = f"https://api.aelf.org/v1/messes/{date_str}/{zone}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "application/json"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data and "messes" in data and len(data["messes"]) > 0:
                    return data
        except Exception:
            continue

    print(f"[-] AELF non joignable ({date_str}) sur toutes les zones liturgiques.", file=sys.stderr)
    return None

# 3. Résolution d'illustration : Génération par IA avec chefs-d'œuvre par temps liturgique
def get_seasonal_default_artwork(couleur="vert", ligne1="", fete="", ref="", theme_titre=""):
    """
    Sélectionne le chef-d'œuvre sacré par défaut correspondant au Temps Liturgique et à la couleur du jour.
    """
    c = (couleur or "vert").lower()
    l1 = (ligne1 or "").lower()
    f = (fete or "").lower()
    r = (ref or "").lower()
    th = (theme_titre or "").lower()

    # 1. Péricopes spécifiques majeures si l'œuvre existe
    if any(k in r for k in ["mt 26", "mc 14", "lc 22", "1 co 11"]) or "cène" in f or "eucharistie" in th:
        if os.path.exists("assets/illustrations/sainte-cene.jpg"):
            return "assets/illustrations/sainte-cene.jpg", "La Sainte Cène (Eucharistie)"

    if "compassion" in th and os.path.exists("assets/illustrations/jesus-compassion.jpg"):
        return "assets/illustrations/jesus-compassion.jpg", "La Compassion du Christ"

    # 2. Chefs-d'œuvre sacrés par temps liturgique
    if c == "rouge" or "martyr" in f or "pentecôte" in l1 or "rameaux" in l1:
        if os.path.exists("assets/illustrations/pentecote-esprit-saint.jpg"):
            return "assets/illustrations/pentecote-esprit-saint.jpg", "La Pentecôte & Esprit Saint (Rouge / Martyrs)"
        return "assets/illustrations/croix-bible.jpg", "Croix et Sainte Bible HD"

    elif c == "violet":
        if "carême" in l1 or "careme" in l1 or "cendres" in l1:
            return "assets/illustrations/croix-bible.jpg", "Croix et Sainte Bible HD (Carême)"
        else:
            # Temps de l'Avent
            if os.path.exists("assets/illustrations/avent-annonciation.jpg"):
                return "assets/illustrations/avent-annonciation.jpg", "L'Annonciation (Temps de l'Avent)"
            return "assets/illustrations/croix-bible.jpg", "Croix et Sainte Bible HD"

    elif c in ["blanc", "or", "doré"]:
        if "martin" in f and os.path.exists("assets/illustrations/saint-martin.jpg"):
            return "assets/illustrations/saint-martin.jpg", "Saint Martin de Tours (Mémoire)"
        if os.path.exists("assets/illustrations/resurrection.jpg"):
            return "assets/illustrations/resurrection.jpg", "Le Christ Ressuscité (Solennités & Fêtes)"
        return "assets/illustrations/croix-bible.jpg", "Croix et Sainte Bible HD"

    else:
        # Temps Ordinaire (Vert)
        if os.path.exists("assets/illustrations/bon-berger.jpg"):
            return "assets/illustrations/bon-berger.jpg", "Le Bon Berger (Temps Ordinaire)"
        return "assets/illustrations/croix-bible.jpg", "Croix et Sainte Bible HD"

def resolve_harmonious_illustration(date_str, ref, fete, theme_titre, couleur="vert", ligne1="", prompt_img=""):
    """
    Tente de générer l'illustration sacrée via l'IA (modèles d'images Gemini).
    En cas d'échec ou d'indisponibilité (quota, réseau, etc.), bascule sur le
    chef-d'œuvre sacré officiel correspondant au temps liturgique du jour.
    """
    default_fallback, default_label = get_seasonal_default_artwork(couleur, ligne1, fete, ref, theme_titre)

    prompt_text = prompt_img.strip() if prompt_img else (
        f"A reverent, sacred Catholic religious oil painting depicting the biblical theme: {theme_titre} ({ref}). "
        "Warm divine light, classical Renaissance fine art style, solemn, highly detailed, beautiful sacred church art, "
        "4:3 aspect ratio, no modern elements, no text, no signatures."
    )

    if not GEMINI_API_KEY:
        print(f"[!] Pas de clé API. Utilisation de l'illustration liturgique par défaut : {default_label}.")
        return default_fallback, default_label

    os.makedirs("output", exist_ok=True)
    ai_img_path = f"output/illustration-{date_str}.jpg"

    if os.path.exists(ai_img_path):
        print(f"[i] Réutilisation de l'illustration IA existante : {ai_img_path}")
        return ai_img_path, "Illustration générée par l'IA"

    models_to_try = [
        "gemini-2.5-flash-image",
        "gemini-3.1-flash-image",
        "gemini-3.1-flash-lite-image",
        "imagen-3.0-generate-002"
    ]

    print("[*] Tentative de génération de l'illustration sacrée par l'IA...")
    for model in models_to_try:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt_text}]}],
                "generationConfig": {"responseModalities": ["image", "text"]}
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=25) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                parts = res.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                for part in parts:
                    if "inlineData" in part and part["inlineData"].get("data"):
                        img_bytes = base64.b64decode(part["inlineData"]["data"])
                        with open(ai_img_path, "wb") as f_out:
                            f_out.write(img_bytes)
                        print(f"[✓] Illustration générée par l'IA avec succès ({model}) : {ai_img_path}")
                        return ai_img_path, "Illustration sacrée générée par l'IA"
        except Exception as e:
            # Tester modèle suivant sans interrompre le flux
            pass

    print(f"[!] Illustration IA indisponible (quota ou réseau). Bascule sur l'art liturgique : {default_label}.")
    return default_fallback, default_label

# 4. Analyse et extraction via l'IA Gemini
def analyze_with_gemini(date_str, evangile_ref, evangile_text, liturgical_info):
    if not GEMINI_API_KEY:
        print("[!] GEMINI_API_KEY non configurée. Utilisation de l'analyseur liturgique local.")
        return None

    fete_clean = liturgical_info.get('fete', '')
    if "férie" in fete_clean.lower():
        fete_clean = liturgical_info.get('ligne1', '')

    prompt = f"""Tu es le rédacteur en chef spirituel pour la paroisse Saint Michel de Houéto (Enfance Missionnaire).
À partir des lectures catholiques de ce jour ({date_str}, {liturgical_info.get('ligne1', '')} - {fete_clean}), et de l'Évangile :
Référence : {evangile_ref}
Texte de l'Évangile :
{evangile_text}

Génère une réponse STRICTEMENT au format JSON (sans markdown ```json, juste l'objet JSON brut) contenant :
{{
  "passage_fort": "Une citation exacte, frappante et transformatrice de l'Évangile (max 18 mots, avec guillemets « »)",
  "theme_titre": "Titre du thème du jour (3 à 5 mots percutants, JAMAIS 'de la férie')",
  "theme_synthese": "Synthèse en 3-4 lignes courtes pour l'affiche paroissiale (environ 25-35 mots)",
  "question_du_jour": "Question d'introspection personnelle commençant par '« Est-ce que je...' invitant à un examen de conscience concret aujourd'hui",
  "resume": "Court résumé didactique de l'Évangile en 2 paragraphes clairs",
  "reflexion": "Réflexion spirituelle concrète et édifiante en 3 paragraphes",
  "priere": "Prière fervente du jour adressée au Seigneur (commençant par Seigneur... et finissant par Amen)",
  "prompt_illustration": "A concise artistic prompt in English for a sacred biblical painting depicting the scene, reverent, oil on canvas, morning natural light, no modern elements, no text"
}}"""

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-flash"
    ]

    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.4,
                "response_mime_type": "application/json"
            }
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers={"Content-Type": "application/json"})
        
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                candidates = res_json.get("candidates", [])
                if candidates:
                    raw_text = candidates[0]["content"]["parts"][0]["text"].strip()
                    if raw_text.startswith("```"):
                        raw_text = raw_text.split("```")[1]
                        if raw_text.startswith("json"):
                            raw_text = raw_text[4:]
                    return json.loads(raw_text.strip())
        except Exception:
            continue

    return None

# 5. Extraction liturgique harmonisée de secours (avec élimination de "de la férie")
def harmonize_fallback(date_str, ref, evangile, liturgical_info, raw_text):
    titre = evangile.get("titre", "").strip()
    fete = liturgical_info.get("fete") or liturgical_info.get("ligne2", "")
    ligne1 = liturgical_info.get("ligne1", "")
    corpus = f"{date_str} {ref} {fete} {titre} {raw_text}".lower()

    # Nettoyage rigoureux de "de la férie"
    fete_clean = fete if fete and "férie" not in fete.lower() else ""
    if not fete_clean and ligne1:
        fete_clean = ligne1

    # 1. Évangile des dix lépreux et du Samaritain reconnaissant (Lc 17, 11-19)
    if any(k in corpus for k in ["lépreux", "lepreux", "samaritain"]) or ("17" in ref and any(v in ref for v in ["11-19", "11 - 19", "11, 19", "11–19"])):
        passage_fort = "« Il ne s'est trouvé parmi eux que cet étranger pour revenir sur ses pas et rendre gloire à Dieu. »"
        theme_titre = "La Puissance de la Gratitude"
        theme_synthese = "Sur les dix lépreux purifiés par Jésus, un seul est revenu sur ses pas pour rendre gloire à Dieu et dire merci. Ne soyons pas de ceux qui oublient Dieu une fois exaucés."
        question_du_jour = "« Est-ce que je prends réellement le temps de remercier Dieu pour ses bienfaits quotidiens, ou est-ce que je me contente de lui demander toujours davantage ? »"
        resume = "Sur son chemin vers Jérusalem, Jésus rencontre dix lépreux qui l'implorent d'avoir pitié d'eux. Il les renvoie vers les prêtres et, en chemin, ils sont tous guéris.\n\nSeul un Samaritain rebrousse chemin en glorifiant Dieu à haute voix pour se prosterner aux pieds de Jésus."
        reflexion = "Cet Évangile met en lumière la vertu si rare de la reconnaissance. Combien de fois avons-nous crié vers le Ciel dans l'angoisse pour ensuite oublier d'offrir une prière de louange ?\n\nLa gratitude transforme la bénédiction reçue en relation vivante et salvatrice avec le Seigneur.\n\nReconnaître les bienfaits du Très-Haut ouvre notre âme à la plénitude de sa grâce."
        priere = "Seigneur, pardonne-moi pour toutes les fois où j'ai consommé tes grâces sans te rendre grâce. Donne-moi un cœur reconnaissant, prompt à louer ta bonté dans les joies comme dans les épreuves. Amen."

    # 2. Le Règne de Dieu au milieu de vous (Lc 17, 20-25)
    elif any(k in corpus for k in ["règne de dieu", "regne de dieu"]) or ("17" in ref and any(v in ref for v in ["20-25", "20 - 25", "20, 25", "20–25"])):
        passage_fort = "« Le règne de Dieu est au milieu de vous. »"
        theme_titre = "Le Règne de Dieu au Milieu de Nous"
        theme_synthese = "Jésus nous enseigne que le Royaume de Dieu ne vient pas avec éclat extérieur : il est déjà présent, agissant au fond de nos cœurs et dans notre foi vécue."
        question_du_jour = "« Est-ce que je sais discerner la présence discrète mais agissante du Seigneur au cœur de mes activités quotidiennes ? »"
        resume = "Interrogé par les pharisiens sur la venue du règne de Dieu, Jésus leur répond que sa venue n'est pas observable à vue d'œil.\n\nLe Royaume des Cieux n'est pas une conquête terrestre, il est déjà vivant et agissant au milieu de nous."
        reflexion = "Nous attendons souvent Dieu dans l'extraordinaire ou le spectaculaire, alors qu'il se fait humblement proche de chacun de nous.\n\nAccueillir le Règne de Dieu aujourd'hui, c'est laisser l'amour du Christ guider nos décisions et nos regards.\n\nFaisons de notre journée une demeure pour sa paix et sa justice."
        priere = "Seigneur Jésus, règne en maître dans mon cœur et dans ma vie. Éloigne de moi les illusions et apprends-moi à reconnaître ta présence vivante à chaque instant de ce jour. Amen."

    # 3. Le Fils de l'homme et la vigilance (Lc 17, 26-37)
    elif any(k in corpus for k in ["fils de l'homme", "noé", "noe"]) or ("17" in ref and any(v in ref for v in ["26-37", "26 - 37", "26, 37", "26–37"])):
        passage_fort = "« Le jour où le Fils de l’homme se révélera. »"
        theme_titre = "La Vigilance du Cœur"
        theme_synthese = "Le Christ nous appelle à une vigilance constante : celui qui cherche à préserver sa vie pour lui-même la perdra, mais qui la donne par amour la sauvera."
        question_du_jour = "« Suis-je prêt spirituellement si le Seigneur venait me visiter aujourd'hui, ou mon cœur est-il assoupi dans les soucis matériels ? »"
        resume = "Évoquant les jours de Noé et de Loth, Jésus exhorte ses disciples à une vigilance totale face à la venue du Fils de l'homme.\n\nIl nous rappelle l'urgence d'attacher notre cœur à ce qui demeure éternellement."
        reflexion = "Le train-train du quotidien peut endormir notre foi si nous oublions notre destinée céleste.\n\nVivre dans la vigilance chrétienne, ce n'est pas vivre dans l'angoisse, mais dans l'amour actif et confiant.\n\nEngageons chaque journée comme une offrande agréable à Dieu."
        priere = "Seigneur Jésus, garde mon âme en éveil dans la prière et la charité. Que mon cœur ne s'alourdisse pas des fardeaux passagers de ce monde, mais demeure fixé sur ton retour glorieux. Amen."

    # 4. La prière persévérante et la veuve (Lc 18, 1-8)
    elif any(k in corpus for k in ["crient vers lui", "juge", "veuve"]) or ("18" in ref and any(v in ref for v in ["1-8", "1 - 8", "1, 8", "1–8"])):
        passage_fort = "« Dieu ne ferait pas justice à ses élus qui crient vers lui ? »"
        theme_titre = "La Prière Persévérante"
        theme_synthese = "Par la parabole de la veuve et du juge, Jésus nous invite à prier sans cesse avec persévérance et confiance, sans jamais nous décourager."
        question_du_jour = "« Est-ce que je persévère dans ma prière avec foi quand la réponse semble tarder, ou est-ce que j'abandonne rapidement ? »"
        resume = "Jésus raconte à ses disciples la parabole du juge sans scrupules qui finit par rendre justice à une pauvre veuve à force d'insistance.\n\nÀ plus forte raison, Dieu notre Père écoute et exauce la prière confiante de ses enfants."
        reflexion = "La prière persévérante n'a pas pour but de changer la volonté de Dieu, mais d'ajuster notre cœur à sa grâce.\n\nLe Seigneur nous invite à une foi inébranlable qui ne désespère jamais.\n\nQuand le Fils de l'homme viendra, trouvera-t-il la foi sur notre terre ?"
        priere = "Seigneur, fortifie ma foi lorsque le doute m'assaille. Donne-moi la persévérance dans la prière et la certitude consolante que tu écoutes toujours le cri de tes humbles enfants. Amen."

    elif "compassion" in corpus or "brebis qui n'ont pas de berger" in corpus or "mt 9" in corpus:
        passage_fort = "« Voyant les foules, Jésus fut saisi de compassion envers elles. »"
        theme_titre = "La Compassion du Christ"
        theme_synthese = "Voyant les foules désemparées comme des brebis sans berger, Jésus est saisi d'une profonde compassion. Il guérit toute infirmité et nous appelle à la prière."
        question_du_jour = "« Est-ce que mon regard sur les personnes démunies est habité par la compassion et la tendresse du Christ, ou par l'indifférence ? »"
        resume = "Parcourant les villes et villages, Jésus enseigne dans les synagogues, proclame l'Évangile du Royaume et guérit toute maladie.\n\nSaisi de compassion devant les foules prostrées comme des brebis sans pasteur, il invite ses disciples à prier le Maître de la moisson d'envoyer des ouvriers."
        reflexion = "La compassion de Jésus n'est pas une simple émotion passagère, elle est un engagement total d'amour pour relever l'être humain blessé.\n\nEn ce temps de l'Avent, le Seigneur nous appelle à devenir les mains et le cœur de sa tendresse.\n\nNe détournons pas le regard devant la solitude ou la peine de notre prochain."
        priere = "Seigneur Jésus, toi dont le Cœur est brûlant de miséricorde pour les foules désemparées, donne-moi un regard attentif et compatissant. Fais de moi un serviteur fidèle de ton amour. Amen."

    elif any(k in corpus for k in ["ce que vous avez fait", "mt 25", "matthieu 25"]):
        passage_fort = "« Ce que vous avez fait à l'un de ces plus petits de mes frères, c'est à moi que vous l'avez fait. »"
        theme_titre = "La Charité Vivante du Christ"
        theme_synthese = "En partageant son manteau avec le pauvre transi de froid, saint Martin nous enseigne que chaque geste d'amour fraternel s'adresse au Seigneur Jésus lui-même."
        question_du_jour = "« Suis-je prêt aujourd'hui à ouvrir mon cœur et à partager concrètement ce que j'ai avec celui qui est dans le besoin autour de moi ? »"
        resume = "En ce jour de fête de saint Martin de Tours, l'Église célèbre le zèle pastoral et la charité inconditionnelle de ce grand évêque.\n\nSon geste mémorable de partage de son manteau avec un mendiant aux portes d'Amiens est la démonstration éclatante de l'Évangile vécu."
        reflexion = "La charité chrétienne n'est pas une simple philanthropie, elle est rencontre intime avec le Christ voilé sous les traits du pauvre.\n\nSaint Martin n'a pas hésité à fendre son vêtement en deux : la sainteté commence dès lors que nous acceptons de donner de notre nécessaire.\n\nDemandons la grâce d'avoir des yeux attentifs aux détresses invisibles de notre quotidien."
        priere = "Seigneur Jésus, accorde-moi un cœur généreux et compatissant à l'exemple de saint Martin. Apprends-moi à reconnaître ton visage dans le visage de mes frères démunis et à aimer en actes et en vérité. Amen."

    elif any(k in corpus for k in ["berger", "brebis", "pasteur", "jean 10", "luc 15"]):
        passage_fort = "« Je suis le bon pasteur : le bon pasteur donne sa vie pour ses brebis. »"
        theme_titre = "La Tendresse du Bon Berger"
        theme_synthese = "Le Bon Berger connaît chacune de ses brebis par son nom et donne sa vie pour elles. Aucune ne sera abandonnée ni perdue."
        question_du_jour = "« Est-ce que je reconnais la voix du Bon Berger au milieu du tumulte de mes journées pour me laisser guider par Lui ? »"
        resume = "Le Christ se présente à nous comme le Bon Berger qui rassemble, protège et nourrit son troupeau.\n\nContrairement au mercenaire, Jésus veille avec amour sur chaque âme et part à la recherche de celle qui s'égare."
        reflexion = "Dans un monde saturé de bruits et de sollicitations, la voix du Bon Berger apporte la paix profonde et la vérité.\n\nApprenons à faire silence dans la prière pour discerner ses appels dans notre vie.\n\nConfions-lui nos peurs et nos doutes : entre ses mains bienveillantes, nous ne manquons de rien."
        priere = "Seigneur Jésus, toi qui es mon Bon Berger, guide mes pas sur les sentiers de la justice. Garde-moi près de ton cœur et ramène-moi toujours à toi lorsque je m'égare. Amen."

    elif any(k in corpus for k in ["cène", "cene", "pain", "corps", "vin", "eucharistie"]):
        passage_fort = "« Prenez, mangez : ceci est mon corps livré pour vous. »"
        theme_titre = "Le Pain Vivant du Ciel"
        theme_synthese = "En instituant l'Eucharistie, le Christ se donne tout entier pour nourrir notre foi et nous unir intimement à sa vie divine."
        question_du_jour = "« Comment puis-je m'approcher de la Sainte Eucharistie avec plus de recueillement et un cœur disponible à la grâce ? »"
        resume = "Au cours de la Sainte Cène, la veille de sa Passion, Jésus bénit le pain et le vin en instituant le sacrement de l'Eucharistie.\n\nIl nous laisse le mémorial éternel de son sacrifice d'amour et de sa présence réelle parmi nous."
        reflexion = "L'Eucharistie est la source et le sommet de toute la vie chrétienne.\n\nEn recevant le Pain du Ciel, nous sommes fortifiés pour devenir à notre tour des témoins vivants de la miséricorde.\n\nQue notre communion dominicale transforme nos relations et nos actes au quotidien."
        priere = "Seigneur Jésus, Pain vivant descendu du Ciel, nourris mon âme de ta sainte présence. Fais de moi un instrument d'unité et de paix dans ton Église. Amen."

    else:
        clean_title = titre.replace("«", "").replace("»", "").strip() if titre else "Ta foi t'a sauvé"
        passage_fort = f"« {clean_title} »"
        
        # Thème dérivé du temps liturgique si pas de fête
        if "avent" in ligne1.lower():
            theme_titre = "L'Espérance de l'Avent"
        elif "carême" in ligne1.lower() or "careme" in ligne1.lower():
            theme_titre = "La Grâce de la Conversion"
        elif fete_clean and not fete_clean.lower().startswith("de la"):
            theme_titre = fete_clean[:35]
        else:
            theme_titre = "Parole de Vie Éternelle"

        theme_synthese = "Méditons la Parole du Seigneur qui illumine notre route chaque jour. Elle est une source inépuisable de réconfort et de sanctification pour notre foi."
        question_du_jour = "« Comment puis-je accueillir et mettre en pratique cette Parole de Dieu aujourd'hui dans ma vie concrète ? »"
        resume = f"Lecture de la sainte liturgie de ce jour selon {ref}.\n\nLe Seigneur nous invite à renouveler notre confiance et à avancer avec fidélité sur le chemin de l'Évangile."
        reflexion = "Chaque verset de l'Écriture Sainte porte une promesse de renouveau pour celui qui écoute avec foi.\n\nNe laissons pas passer cette journée sans laisser la Parole porter du fruit dans nos actes et nos pensées.\n\nEn communion avec toute l'Église, fortifions notre engagement baptismal."
        priere = "Seigneur, que ta Parole vivante soit la lumière de mes pas et la joie de mon âme. Conduis-moi selon ta vérité et accorde-moi la paix. Amen."

    return {
        "passage_fort": passage_fort,
        "theme_titre": theme_titre,
        "theme_synthese": theme_synthese,
        "question_du_jour": question_du_jour,
        "resume": resume,
        "reflexion": reflexion,
        "priere": priere,
        "fete_clean": fete_clean,
        "prompt_illustration": "A sacred oil painting depicting a holy biblical scene, golden morning light"
    }

# 6. Pipeline complet orchestré
def run_pipeline(date_str=None):
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    # Vérification anti-duplication : si l'affiche de ce jour existe déjà, la renvoyer directement
    data_file = f"output/data-{date_str}.json"
    if os.path.exists(data_file):
        print(f"[i] Affiche déjà existante pour le {date_str} (chargement immédiat, zéro duplication).")
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    print(f"\n=======================================================")
    print(f"🌿 EXÉCUTION DU PIPELINE : {date_str}")
    print(f"=======================================================")

    date_fr = format_date_fr(date_str)

    # AELF
    aelf = get_aelf_data(date_str)
    if aelf:
        info = aelf.get("informations", {})
        couleur = info.get("couleur", "vert").lower()
        fete = info.get("fete") or info.get("ligne2", "")
        ligne1 = info.get("ligne1", "")

        evangile = None
        for messe in aelf.get("messes", []):
            for l in messe.get("lectures", []):
                if l.get("type") == "evangile":
                    evangile = l
                    break
            if evangile:
                break

        if not evangile:
            for messe in aelf.get("messes", []):
                lects = messe.get("lectures", [])
                if lects:
                    evangile = lects[-1]
                    break
    else:
        print(f"[!] AELF non accessible (mode hors-ligne/sandbox). Utilisation du calendrier liturgique.")
        if date_str.endswith("11-11"):
            couleur = "blanc"
            fete = "Saint Martin de Tours, évêque - Mémoire"
            ligne1 = "32e semaine du Temps Ordinaire"
            evangile = {
                "ref": "LC 17, 11-19",
                "titre": "Les dix lépreux purifiés et la foi du Samaritain",
                "contenu": "En ce temps-là, Jésus marchait vers Jérusalem. Il passait entre la Samarie et la Galilée. Comme il entrait dans un village, dix lépreux vinrent à sa rencontre. Ils s’arrêtèrent à distance et lui crièrent : « Jésus, maître, prends pitié de nous ! » À cette vue, Jésus leur dit : « Allez vous montrer aux prêtres. » En cours de route, ils furent purifiés. L’un d’eux, voyant qu’il était guéri, revint sur ses pas, en glorifiant Dieu à pleine voix. Il tomba face contre terre aux pieds de Jésus et lui rendit grâce. Or, c’était un Samaritain. Alors Jésus prit la parole et dit : « Tous les dix n’ont-ils pas été purifiés ? Les neuf autres, où sont-ils ? Il ne s’est trouvé parmi eux que cet étranger pour revenir sur ses pas et rendre gloire à Dieu ! » Puis il lui dit : « Relève-toi et va : ta foi t’a sauvé. »"
            }
        elif date_str.endswith("11-12"):
            couleur = "rouge"
            fete = "Saint Josaphat, évêque et martyr - Mémoire"
            ligne1 = "32e semaine du Temps Ordinaire"
            evangile = {
                "ref": "LC 17, 20-25",
                "titre": "Le règne de Dieu est au milieu de vous",
                "contenu": "En ce temps-là, comme les pharisiens demandaient à Jésus quand viendrait le règne de Dieu, il prit la parole et dit : « La venue du règne de Dieu n’est pas observable. On ne dira pas : “Voilà, il est ici !” ou bien : “Il est là !” En effet, voici que le règne de Dieu est au milieu de vous. » Puis il dit aux disciples : « Des jours viendront où vous désirerez voir un seul des jours du Fils de l’homme, et vous ne le verrez pas. On vous dira : “Voilà, il est là-bas !” ou bien : “Voici, il est ici !” N’y allez pas, n’y courez pas. En effet, comme l’éclair qui jaillit illumine l’horizon d’un bout à l’autre, ainsi le Fils de l’homme, quand son jour sera là. »"
            }
        elif date_str.endswith("11-13"):
            couleur = "vert"
            fete = ""
            ligne1 = "32e semaine du Temps Ordinaire"
            evangile = {
                "ref": "LC 17, 26-37",
                "titre": "Le jour où le Fils de l’homme se révélera",
                "contenu": "En ce temps-là, Jésus disait à ses disciples : « Comme cela s’est passé dans les jours de Noé, ainsi en sera-t-il dans les jours du Fils de l’homme... Celui qui cherchera à préserver sa vie la perdra, et celui qui la perdra la sauvera. »"
            }
        elif date_str.endswith("11-14"):
            couleur = "vert"
            fete = ""
            ligne1 = "32e semaine du Temps Ordinaire"
            evangile = {
                "ref": "LC 18, 1-8",
                "titre": "Dieu fera justice à ses élus qui crient vers lui",
                "contenu": "En ce temps-là, Jésus disait à ses disciples une parabole sur la nécessité pour eux de toujours prier sans se décourager... « Dieu ne ferait pas justice à ses élus qui crient vers lui jour et nuit ? »"
            }
        elif date_str.endswith("12-05") or "-12-" in date_str:
            couleur = "violet"
            fete = ""
            ligne1 = "Samedi de la 1ère semaine de l'Avent"
            evangile = {
                "ref": "MT 9, 35 - 10, 1.5A.6-8",
                "titre": "Voyant les foules, Jésus fut saisi de compassion",
                "contenu": "En ce temps-là, Jésus parcourait toutes les villes et les villages, enseignant dans leurs synagogues, proclamant l'Évangile du Royaume et guérissant toute maladie et toute infirmité. Voyant les foules, il fut saisi de compassion envers elles parce qu'elles étaient désemparées et prostrées comme des brebis qui n'ont pas de berger..."
            }
        else:
            couleur = "vert"
            fete = ""
            ligne1 = "Férie du Temps Ordinaire"
            evangile = {
                "ref": "ÉVANGILE",
                "titre": "Parole de Vie Éternelle",
                "contenu": "En ce temps-là, Jésus disait à ses disciples : Ta foi t'a sauvé, va en paix."
            }
        info = {"couleur": couleur, "fete": fete, "ligne1": ligne1}

    print(f"[+] Couleur liturgique : {couleur.upper()} ({fete or ligne1})")

    ref = evangile.get("ref", "Évangile").replace("&nbsp;", " ").upper()
    texte_brut = evangile.get("contenu", "")
    texte_clair = re.sub(r'<[^>]+>', ' ', texte_brut).replace("&nbsp;", " ")
    texte_clair = re.sub(r'\s+', ' ', texte_clair).strip()

    print(f"[+] Évangile : {ref}")

    # Analyse IA Gemini avec fallback
    print("[*] Génération de l'analyse spirituelle...")
    ai_data = analyze_with_gemini(date_str, ref, texte_clair, info)

    if not ai_data:
        ai_data = harmonize_fallback(date_str, ref, evangile, info, texte_clair)

    passage_fort = ai_data.get("passage_fort", "« Ta foi t'a sauvé »")
    theme_titre = ai_data.get("theme_titre", "Parole du Jour")
    theme_synthese = ai_data.get("theme_synthese", "")
    question_du_jour = ai_data.get("question_du_jour", "")
    resume = ai_data.get("resume", "")
    reflexion = ai_data.get("reflexion", "")
    priere = ai_data.get("priere", "")
    prompt_img = ai_data.get("prompt_illustration", "")

    # Nettoyage rigoureux de "de la férie" dans le titre
    if "férie" in theme_titre.lower():
        theme_titre = "La Compassion du Christ" if "compassion" in texte_clair.lower() else "Parole de Vie Éternelle"

    # Résolution de l'illustration sacrée harmonisée par temps liturgique
    illus_path, illus_label = resolve_harmonious_illustration(
        date_str, ref, fete, theme_titre, couleur=couleur, ligne1=ligne1, prompt_img=prompt_img
    )
    print(f"[+] Illustration choisie : {illus_label} ({illus_path})")

    # Génération du post complet WhatsApp & Facebook
    dt_obj = datetime.strptime(date_str, "%Y-%m-%d")
    date_court = dt_obj.strftime("%d/%m/%Y")

    fete_affichee = fete if fete and "férie" not in fete.lower() else ligne1
    header_fete = f"\n*{fete_affichee}*\n" if fete_affichee else ""

    post_complet = f"""🌿 Parole du jour — {ref} ({date_court}){header_fete}

📖 Résumé :
{resume}

✨ Réflexion :
{reflexion}

• Question du jour :
{question_du_jour}

🙏 Prière :
{priere}

Paroisse Saint Michel de Houéto · Enfance Missionnaire"""

    # Enregistrement du fichier texte
    os.makedirs("output", exist_ok=True)
    post_path = f"output/post-{date_str}.txt"
    with open(post_path, "w", encoding="utf-8") as f:
        f.write(post_complet)

    # Rendu de l'affiche HD avec tous les paramètres synchronisés
    out_img = f"output/parole-du-jour-{date_str}.png"
    render_poster(
        liturgical_theme=couleur,
        date_text=f"PAROLE DU JOUR  •  {date_fr.upper()}",
        verse_text=passage_fort,
        ref_text=ref,
        theme_title=theme_titre,
        theme_snippet=theme_synthese,
        question_text=question_du_jour,
        illustration_path=illus_path,
        output_path=out_img
    )

    print(f"[✓] Affiche HD générée : {out_img}")
    print(f"[✓] Post texte généré  : {post_path}")

    result_dict = {
        "status": "success",
        "date": date_str,
        "date_formatted": date_fr,
        "couleur": couleur,
        "fete": fete_affichee,
        "ref": ref,
        "passage_fort": passage_fort,
        "theme_titre": theme_titre,
        "theme_synthese": theme_synthese,
        "question_du_jour": question_du_jour,
        "resume": resume,
        "reflexion": reflexion,
        "priere": priere,
        "illustration_path": illus_path,
        "illustration_label": illus_label,
        "post_text": post_complet,
        "poster_path": out_img
    }

    try:
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[-] Erreur sauvegarde cache : {e}")

    return result_dict

if __name__ == "__main__":
    t_date = datetime.now().strftime("%Y-%m-%d")
    if len(sys.argv) > 1:
        if sys.argv[1] in ("--date", "-d") and len(sys.argv) > 2:
            t_date = sys.argv[2]
        elif not sys.argv[1].startswith("-"):
            t_date = sys.argv[1]

    data = run_pipeline(t_date)
    print("\n--- SYNTHÈSE SYNCHRONISÉE ---")
    print(f"Date : {data['date_formatted']}")
    print(f"Thème : {data['theme_titre']}")
    print(f"Verset : {data['passage_fort']}")
    print(f"Illustration : {data['illustration_label']}")
