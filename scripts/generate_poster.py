import os
from PIL import Image, ImageDraw, ImageFont

def create_rounded_mask(size, radius):
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask

def wrap_text_lines(text, font, max_width):
    dummy = Image.new('RGB', (10, 10))
    d = ImageDraw.Draw(dummy)
    
    # Remplacer les espaces avant ponctuation par des espaces insécables
    text = text.replace(" »", " »").replace(" ?", " ?").replace(" !", " !").replace(" :", " :")
    words = text.split(" ")
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = d.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def wrap_verse_bicolor(text, font, max_width):
    """
    Découpe harmonique du verset pour garantir un effet bicolore élégant et équilibré :
    - Évite d'isoler un ou deux mots sur la seconde ligne
    - Équilibre le poids visuel entre la strophe blanche et la strophe dorée
    """
    dummy = Image.new('RGB', (10, 10))
    d = ImageDraw.Draw(dummy)
    
    text = text.replace(" »", " »").replace(" ?", " ?").replace(" !", " !").replace(" :", " :")
    words = text.split(" ")
    
    # Si le verset comporte au moins 4 mots, chercher une coupure équilibrée en 2 lignes
    if len(words) >= 4:
        best_split = None
        min_diff = float("inf")
        for i in range(2, len(words) - 1):
            l1 = " ".join(words[:i])
            l2 = " ".join(words[i:])
            b1 = d.textbbox((0, 0), l1, font=font)
            b2 = d.textbbox((0, 0), l2, font=font)
            w1 = b1[2] - b1[0]
            w2 = b2[2] - b2[0]
            if w1 <= max_width and w2 <= max_width:
                diff = abs(w1 - w2)
                # Priorité aux respirations naturelles sur virgule ou deux-points
                if words[i-1].endswith(',') or words[i-1].endswith(';'):
                    diff -= 80
                if diff < min_diff:
                    min_diff = diff
                    best_split = [l1, l2]
        if best_split:
            return best_split

    # Sinon (verset long sur 3+ lignes), wrapping dynamique standard
    return wrap_text_lines(text, font, max_width)

def render_poster(
    liturgical_theme="vert",
    date_text="PAROLE DU JOUR  •  12 NOVEMBRE 2026",
    verse_text="« Le règne de Dieu est au milieu de vous. »",
    ref_text="LC 17, 20-25",
    theme_title="Le Règne de Dieu au Milieu de Nous",
    theme_snippet="Jésus nous enseigne que le Royaume de Dieu ne vient pas avec éclat extérieur : il est déjà présent, agissant au fond de nos cœurs et dans notre foi vécue.",
    question_text="« Est-ce que je sais discerner la présence discrète mais agissante du Seigneur au cœur de mes activités quotidiennes ? »",
    illustration_path="assets/illustrations/pentecote-esprit-saint.jpg",
    output_path="output/parole-du-jour.png"
):
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    W, H = 1080, 1080

    palettes = {
        "vert": {
            "name": "Temps Ordinaire",
            "outer_bg": "#FAF8F2",
            "card_bg": "#1E5E3D",
            "card_inner": "#2A744D",
            "gold": "#CFA852",
            "gold_light": "#F2DC9B",
            "verse_color": "#FFFFFF",
            "verse_sub": "#F2DC9B",
            "snippet_color": "#E6EFEA",
            "badge_bg": "#123E27",
            "badge_text": "#FFFFFF",
            "pill_bg": "#13462C",
            "q_bg": "#FCF8EE",
            "q_tag_bg": "#13462C",
            "q_tag_text": "#F2DC9B",
            "q_text": "#1B2A22"
        },
        "blanc": {
            "name": "Solennités & Fêtes (Blanc & Or)",
            "outer_bg": "#F8F6F0",
            "card_bg": "#FFFFFF",
            "card_inner": "#FAF6EC",
            "gold": "#C6922C",
            "gold_light": "#966B12",
            "verse_color": "#17281F",
            "verse_sub": "#8E6510",
            "snippet_color": "#334139",
            "badge_bg": "#C6922C",
            "badge_text": "#FFFFFF",
            "pill_bg": "#C6922C",
            "q_bg": "#FFFFFF",
            "q_tag_bg": "#8E6510",
            "q_tag_text": "#FFFFFF",
            "q_text": "#17281F"
        },
        "rouge": {
            "name": "Martyrs & Esprit Saint",
            "outer_bg": "#FAF5F5",
            "card_bg": "#7A1A22",
            "card_inner": "#962630",
            "gold": "#D4AF37",
            "gold_light": "#F6DF9F",
            "verse_color": "#FFFFFF",
            "verse_sub": "#F6DF9F",
            "snippet_color": "#FBEAEA",
            "badge_bg": "#4F1015",
            "badge_text": "#FFFFFF",
            "pill_bg": "#541218",
            "q_bg": "#FDF6F6",
            "q_tag_bg": "#541218",
            "q_tag_text": "#F6DF9F",
            "q_text": "#2B1416"
        },
        "violet": {
            "name": "Avent & Carême",
            "outer_bg": "#F9F6FC",
            "card_bg": "#441F63",
            "card_inner": "#5B2C84",
            "gold": "#CFA852",
            "gold_light": "#F2DC9B",
            "verse_color": "#FFFFFF",
            "verse_sub": "#F2DC9B",
            "snippet_color": "#F3EBF9",
            "badge_bg": "#2B123F",
            "badge_text": "#FFFFFF",
            "pill_bg": "#2F1445",
            "q_bg": "#FAF6FD",
            "q_tag_bg": "#2F1445",
            "q_tag_text": "#F2DC9B",
            "q_text": "#241630"
        }
    }
    p = palettes.get(liturgical_theme, palettes["vert"])

    im = Image.new("RGB", (W, H), p["outer_bg"])
    draw = ImageDraw.Draw(im)

    # Cadre extérieur décoratif
    draw.rectangle([24, 24, W - 25, H - 25], outline="#E4DCCE", width=2)
    draw.rectangle([32, 32, W - 33, H - 33], outline=p["gold"], width=1)

    # --- TOP HEADER ---
    # Logo Capsule
    logo_path = "assets/logos/logo-EM-transparent.png"
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        lh = 80
        lw = int(lh * 1.4728)
        logo_res = logo.resize((lw, lh), Image.Resampling.LANCZOS)
        cap_x, cap_y = 52, 44
        cap_w, cap_h = lw + 24, lh + 14
        draw.rounded_rectangle([cap_x, cap_y, cap_x + cap_w, cap_y + cap_h], radius=14, fill="#FFFFFF", outline=p["gold"], width=1)
        im.paste(logo_res, (cap_x + 12, cap_y + 7), logo_res)

    # Date Pill (Taille 18px avec auto-ajustement anti-débordement)
    pill_w, pill_h = 580, 48
    pill_x = W - 56 - pill_w
    pill_y = 66
    
    font_size_date = 18
    font_sans_date = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", font_size_date)
    bbox_pill = draw.textbbox((0, 0), date_text, font=font_sans_date)
    wb = bbox_pill[2] - bbox_pill[0]
    
    while wb > pill_w - 40 and font_size_date > 14:
        font_size_date -= 1
        font_sans_date = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", font_size_date)
        bbox_pill = draw.textbbox((0, 0), date_text, font=font_sans_date)
        wb = bbox_pill[2] - bbox_pill[0]
        
    hb = bbox_pill[3] - bbox_pill[1]
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=24, fill=p["pill_bg"], outline=p["gold"], width=1)
    draw.text((pill_x + (pill_w - wb) // 2, pill_y + (pill_h - hb) // 2 - 2), date_text, font=font_sans_date, fill=p["gold_light"])

    card_y1 = 158

    # --- MAIN LITURGICAL CARD (Elastic dynamic layout) ---
    card_x1, card_x2, card_y2 = 56, W - 57, 725
    card_w = card_x2 - card_x1
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=28, fill=p["card_bg"], outline=p["gold"], width=2)
    draw.rounded_rectangle([card_x1 + 8, card_y1 + 8, card_x2 - 8, card_y2 - 8], radius=20, outline=p["card_inner"], width=1)

    # Guillemet décoratif en Or
    font_quote = ImageFont.truetype("/usr/share/fonts/liberation-serif-fonts/LiberationSerif-BoldItalic.ttf", 96)
    draw.text((card_x1 + 42, card_y1 + 16), "“", font=font_quote, fill=p["gold"])

    # DYNAMIC VERSE FONT SIZING
    avail_w = card_w - 170
    v_clean = verse_text.replace(" »", " »").replace(" ?", " ?").replace(" !", " !").replace(" :", " :")
    verse_len = len(v_clean)
    
    if verse_len > 95:
        verse_font_size = 32
    elif verse_len > 65:
        verse_font_size = 36
    elif verse_len > 40:
        verse_font_size = 40
    else:
        verse_font_size = 44

    font_verse = ImageFont.truetype("/usr/share/fonts/liberation-serif-fonts/LiberationSerif-BoldItalic.ttf", verse_font_size)
    lines = wrap_verse_bicolor(v_clean, font_verse, avail_w)
    line_h = int(verse_font_size * 1.25)
    v_start_y = card_y1 + 38

    # EFFET BICOLORE MAJESTUEUX : Ligne 1 en Blanc, Lignes suivantes en Doré
    for i, line in enumerate(lines):
        ly = v_start_y + i * line_h
        color = p["verse_color"] if i == 0 else p["verse_sub"]
        draw.text((card_x1 + 130, ly), line, font=font_verse, fill=color)

    last_v_y = v_start_y + (len(lines) - 1) * line_h + verse_font_size

    # DYNAMIC REFERENCE BADGE PLACEMENT
    ref_y = last_v_y + 14
    font_ref = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", 22)
    bbox_r = draw.textbbox((0, 0), ref_text, font=font_ref)
    wr = bbox_r[2] - bbox_r[0]
    hr = bbox_r[3] - bbox_r[1]
    badge_w = wr + 40
    badge_h = 40
    draw.rounded_rectangle([card_x1 + 130, ref_y, card_x1 + 130 + badge_w, ref_y + badge_h], radius=12, fill=p["badge_bg"], outline=p["gold"], width=1)
    draw.text((card_x1 + 130 + 20, ref_y + (badge_h - hr) // 2 - 2), ref_text, font=font_ref, fill=p["badge_text"])

    # DYNAMIC INNER DIVIDER LINE
    divider_y = ref_y + 50
    draw.line([card_x1 + 40, divider_y, card_x2 - 40, divider_y], fill=p["card_inner"], width=1)

    # LOWER SECTION: ELASTIC HEIGHT ILLUSTRATION + THEME
    lower_y = divider_y + 14
    avail_lower_h = card_y2 - lower_y - 20
    target_w = 370
    target_h = max(180, avail_lower_h)

    # Framed Illustration
    if os.path.exists(illustration_path):
        ill = Image.open(illustration_path).convert("RGB")
        ill_resized = ill.resize((target_w, target_h), Image.Resampling.LANCZOS)
        mask = create_rounded_mask((target_w, target_h), radius=20)
        draw.rounded_rectangle([card_x1 + 40 - 2, lower_y - 2, card_x1 + 40 + target_w + 2, lower_y + target_h + 2], radius=22, outline=p["gold"], width=2)
        im.paste(ill_resized, (card_x1 + 40, lower_y), mask)

    # Right side theme text
    right_x = card_x1 + 440
    right_w = card_w - 470

    # 1. Label "THÈME SPIRITUEL" (Taille 21)
    font_sub_sec = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", 21)
    draw.text((right_x, lower_y + 4), "THÈME SPIRITUEL", font=font_sub_sec, fill=p["gold"])

    # 2. Titre du Thème (Taille 34 avec retour à la ligne automatique)
    font_theme = ImageFont.truetype("/usr/share/fonts/liberation-serif-fonts/LiberationSerif-BoldItalic.ttf", 34)
    theme_title_lines = wrap_text_lines(theme_title, font_theme, right_w)
    for idx_t, t_line in enumerate(theme_title_lines[:2]):
        draw.text((right_x, lower_y + 36 + idx_t * 40), t_line, font=font_theme, fill=p["verse_color"])

    offset_snippet = lower_y + 36 + len(theme_title_lines[:2]) * 40 + 10

    # 3. Synthèse spirituelle (Taille 26 au lieu de 21, interligne 36px)
    font_serif_reg = ImageFont.truetype("/usr/share/fonts/liberation-serif-fonts/LiberationSerif-Italic.ttf", 26)
    snip_lines = wrap_text_lines(theme_snippet, font_serif_reg, right_w)
    for i, s_line in enumerate(snip_lines[:4]):
        draw.text((right_x, offset_snippet + i * 36), s_line, font=font_serif_reg, fill=p["snippet_color"])

    # --- BOTTOM QUESTION DU JOUR CARD ---
    q_y1 = card_y2 + 28
    q_x1, q_x2, q_y2 = 56, W - 57, 985
    draw.rounded_rectangle([q_x1, q_y1, q_x2, q_y2], radius=24, fill=p["q_bg"], outline=p["gold"], width=2)

    # Question Tag Badge (Taille 21, badge 340x42)
    tag_w, tag_h = 340, 42
    font_tag = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", 21)
    draw.rounded_rectangle([q_x1 + 40, q_y1 - 21, q_x1 + 40 + tag_w, q_y1 - 21 + tag_h], radius=14, fill=p["q_tag_bg"], outline=p["gold"], width=1)
    tag_lbl = "✦  QUESTION DU JOUR  ✦"
    bbox_tag = draw.textbbox((0, 0), tag_lbl, font=font_tag)
    wt = bbox_tag[2] - bbox_tag[0]
    ht = bbox_tag[3] - bbox_tag[1]
    draw.text((q_x1 + 40 + (tag_w - wt) // 2, q_y1 - 21 + (tag_h - ht) // 2 - 2), tag_lbl, font=font_tag, fill=p["q_tag_text"])

    # Question Text (Taille 36 au lieu de 30, interligne 46px)
    font_serif_q = ImageFont.truetype("/usr/share/fonts/liberation-serif-fonts/LiberationSerif-Italic.ttf", 36)
    q_lines = wrap_text_lines(question_text, font_serif_q, q_x2 - q_x1 - 80)
    for i, q_line in enumerate(q_lines[:3]):
        draw.text((q_x1 + 42, q_y1 + 46 + i * 46), q_line, font=font_serif_q, fill=p["q_text"])

    # --- FOOTER ---
    footer_text = "Paroisse Saint Michel de Houéto  •  Aumônerie de l'Enfance Missionnaire  •  Cotonou"
    font_sans_footer = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf", 21)
    bbox_f = draw.textbbox((0, 0), footer_text, font=font_sans_footer)
    wf = bbox_f[2] - bbox_f[0]
    draw.text(((W - wf) // 2, 1018), footer_text, font=font_sans_footer, fill="#4A564F")

    im.save(output_path, "PNG", quality=95)
    print(f"Rendered elastic poster to: {output_path}")

if __name__ == "__main__":
    import json
    data_file = "output/data-2026-11-12.json"
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as f:
            d = json.load(f)
        render_poster(
            liturgical_theme=d.get("couleur", "rouge"),
            date_text=f"PAROLE DU JOUR  •  {d.get('date_formatted', '12 NOVEMBRE 2026').upper()}",
            verse_text=d.get("passage_fort"),
            ref_text=d.get("ref"),
            theme_title=d.get("theme_titre"),
            theme_snippet=d.get("theme_synthese"),
            question_text=d.get("question_du_jour"),
            illustration_path=d.get("illustration_path", "assets/illustrations/pentecote-esprit-saint.jpg"),
            output_path="output/parole-du-jour-test.png"
        )
    else:
        render_poster(output_path="output/parole-du-jour-test.png")
