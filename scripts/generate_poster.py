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
    words = text.split()
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

def render_poster(
    liturgical_theme="vert",
    date_text="PAROLE DU JOUR  •  11 NOVEMBRE 2026",
    verse_text="« Il ne s'est trouvé parmi eux que cet étranger pour revenir sur ses pas et rendre gloire à Dieu. »",
    ref_text="LC 17, 11-19",
    theme_title="La Puissance de la Gratitude",
    theme_snippet="Sur les dix lépreux purifiés par Jésus, un seul est revenu sur ses pas pour rendre gloire à Dieu et dire merci. « Ne soyons pas de ceux qui oublient Dieu aussitôt leur prière exaucée. »",
    question_text="« Est-ce que je prends réellement le temps de remercier Dieu pour ses bienfaits quotidiens, ou est-ce que je me contente de lui demander toujours davantage ? »",
    illustration_path="assets/illustrations/samaritain.jpg",
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

    # Outer decorative framing
    draw.rectangle([24, 24, W - 25, H - 25], outline="#E4DCce", width=2)
    draw.rectangle([32, 32, W - 33, H - 33], outline=p["gold"], width=1)

    # --- TOP HEADER ---
    # Logo Capsule (White container guarantees 100% contrast)
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

    # Top Right Date Pill
    pill_w, pill_h = 540, 48
    pill_x = W - 56 - pill_w
    pill_y = 66
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=24, fill=p["pill_bg"], outline=p["gold"], width=1)
    font_sans_bold = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", 19)
    bbox_pill = draw.textbbox((0, 0), date_text, font=font_sans_bold)
    wb = bbox_pill[2] - bbox_pill[0]
    draw.text((pill_x + (pill_w - wb) // 2, pill_y + 13), date_text, font=font_sans_bold, fill=p["gold_light"])

    card_y1 = 158

    # --- MAIN LITURGICAL CARD (Elastic dynamic layout) ---
    card_x1, card_x2, card_y2 = 56, W - 57, 725
    card_w = card_x2 - card_x1
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=28, fill=p["card_bg"], outline=p["gold"], width=2)
    draw.rounded_rectangle([card_x1 + 8, card_y1 + 8, card_x2 - 8, card_y2 - 8], radius=20, outline=p["card_inner"], width=1)

    # Big Quotation mark
    font_quote = ImageFont.truetype("/usr/share/fonts/liberation-serif-fonts/LiberationSerif-BoldItalic.ttf", 94)
    draw.text((card_x1 + 45, card_y1 + 18), "“", font=font_quote, fill=p["gold"])

    # DYNAMIC VERSE FONT SIZING & MULTI-LINE WRAPPING
    avail_w = card_w - 170  # ~798px
    verse_len = len(verse_text)
    if verse_len > 95:
        verse_font_size = 32
    elif verse_len > 65:
        verse_font_size = 36
    elif verse_len > 45:
        verse_font_size = 40
    else:
        verse_font_size = 46

    font_verse = ImageFont.truetype("/usr/share/fonts/liberation-serif-fonts/LiberationSerif-BoldItalic.ttf", verse_font_size)
    lines = wrap_text_lines(verse_text, font_verse, avail_w)
    
    line_h = int(verse_font_size * 1.25)
    v_start_y = card_y1 + 38
    
    for i, line in enumerate(lines):
        ly = v_start_y + i * line_h
        color = p["verse_color"] if i == 0 else p["verse_sub"]
        draw.text((card_x1 + 130, ly), line, font=font_verse, fill=color)

    last_v_y = v_start_y + (len(lines) - 1) * line_h + verse_font_size

    # DYNAMIC REFERENCE BADGE PLACEMENT (Always 16px below verse)
    ref_y = last_v_y + 16
    font_ref = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", 18)
    bbox_r = draw.textbbox((0, 0), ref_text, font=font_ref)
    wr = bbox_r[2] - bbox_r[0]
    badge_w = wr + 36
    draw.rounded_rectangle([card_x1 + 130, ref_y, card_x1 + 130 + badge_w, ref_y + 36], radius=10, fill=p["badge_bg"], outline=p["gold"], width=1)
    draw.text((card_x1 + 130 + 18, ref_y + 8), ref_text, font=font_ref, fill=p["badge_text"])

    # DYNAMIC INNER DIVIDER LINE
    divider_y = ref_y + 48
    draw.line([card_x1 + 40, divider_y, card_x2 - 40, divider_y], fill=p["card_inner"], width=1)

    # LOWER SECTION: ELASTIC HEIGHT ILLUSTRATION + THEME
    lower_y = divider_y + 16
    avail_lower_h = card_y2 - lower_y - 20
    target_w = 380
    target_h = max(180, avail_lower_h)

    # Framed Illustration
    if os.path.exists(illustration_path):
        ill = Image.open(illustration_path).convert("RGB")
        ill_resized = ill.resize((target_w, target_h), Image.Resampling.LANCZOS)
        mask = create_rounded_mask((target_w, target_h), radius=20)
        draw.rounded_rectangle([card_x1 + 40 - 2, lower_y - 2, card_x1 + 40 + target_w + 2, lower_y + target_h + 2], radius=22, outline=p["gold"], width=2)
        im.paste(ill_resized, (card_x1 + 40, lower_y), mask)

    # Right side theme text
    right_x = card_x1 + 455
    font_sub_sec = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", 18)
    draw.text((right_x, lower_y + 6), "THÈME SPIRITUEL", font=font_sub_sec, fill=p["gold"])

    font_theme = ImageFont.truetype("/usr/share/fonts/liberation-serif-fonts/LiberationSerif-BoldItalic.ttf", 29)
    draw.text((right_x, lower_y + 38), theme_title, font=font_theme, fill=p["verse_color"])

    font_serif_reg = ImageFont.truetype("/usr/share/fonts/liberation-serif-fonts/LiberationSerif-Italic.ttf", 21)
    snip_lines = wrap_text_lines(theme_snippet, font_serif_reg, card_w - 480)
    for i, s_line in enumerate(snip_lines[:4]):
        draw.text((right_x, lower_y + 85 + i * 28), s_line, font=font_serif_reg, fill=p["snippet_color"])

    # --- BOTTOM QUESTION DU JOUR CARD ---
    q_y1 = card_y2 + 28
    q_x1, q_x2, q_y2 = 56, W - 57, 985
    draw.rounded_rectangle([q_x1, q_y1, q_x2, q_y2], radius=24, fill=p["q_bg"], outline=p["gold"], width=2)

    # Question Tag Badge
    tag_w, tag_h = 300, 38
    draw.rounded_rectangle([q_x1 + 40, q_y1 - 19, q_x1 + 40 + tag_w, q_y1 - 19 + tag_h], radius=12, fill=p["q_tag_bg"], outline=p["gold"], width=1)
    tag_lbl = "✦  QUESTION DU JOUR  ✦"
    bbox_tag = draw.textbbox((0, 0), tag_lbl, font=font_sub_sec)
    wt = bbox_tag[2] - bbox_tag[0]
    draw.text((q_x1 + 40 + (tag_w - wt) // 2, q_y1 - 10), tag_lbl, font=font_sub_sec, fill=p["q_tag_text"])

    # Question Text
    font_serif_q = ImageFont.truetype("/usr/share/fonts/liberation-serif-fonts/LiberationSerif-Italic.ttf", 30)
    q_lines = wrap_text_lines(question_text, font_serif_q, q_x2 - q_x1 - 90)
    for i, q_line in enumerate(q_lines[:3]):
        draw.text((q_x1 + 45, q_y1 + 48 + i * 40), q_line, font=font_serif_q, fill=p["q_text"])

    # --- FOOTER ---
    footer_text = "Paroisse Saint Michel de Houéto  •  Aumônerie de l'Enfance Missionnaire  •  Cotonou"
    font_sans_reg = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf", 18)
    bbox_f = draw.textbbox((0, 0), footer_text, font=font_sans_reg)
    wf = bbox_f[2] - bbox_f[0]
    draw.text(((W - wf) // 2, 1018), footer_text, font=font_sans_reg, fill="#67756D")

    im.save(output_path, "PNG", quality=95)
    print(f"Rendered elastic poster to: {output_path}")

if __name__ == "__main__":
    # Test with long verse from user upload
    render_poster(
        liturgical_theme="blanc",
        date_text="PAROLE DU JOUR  •  11 NOVEMBRE 2026",
        verse_text="« Il ne s'est trouvé parmi eux que cet étranger pour revenir sur ses pas et rendre gloire à Dieu. »",
        ref_text="LC 17, 11-19",
        output_path="output/test_verset_long.png"
    )
