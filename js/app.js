// Palettes liturgiques catholiques officielles
    const palettes = {
      vert: {
        name: "Temps Ordinaire",
        chipClass: "chip-vert",
        outerBg: "#FAF8F2",
        cardBg: "#1E5E3D",
        cardInner: "#2A744D",
        gold: "#CFA852",
        goldLight: "#F2DC9B",
        verseColor: "#FFFFFF",
        verseSub: "#F2DC9B",
        snippetColor: "#E6EFEA",
        badgeBg: "#123E27",
        badgeText: "#FFFFFF",
        pillBg: "#13462C",
        qBg: "#FCF8EE",
        qTagBg: "#13462C",
        qTagText: "#F2DC9B",
        qText: "#1B2A22"
      },
      blanc: {
        name: "Solennités & Fêtes (Blanc & Or)",
        chipClass: "chip-blanc",
        outerBg: "#F8F6F0",
        cardBg: "#FFFFFF",
        cardInner: "#FAF6EC",
        gold: "#C6922C",
        goldLight: "#966B12",
        verseColor: "#17281F",
        verseSub: "#8E6510",
        snippetColor: "#334139",
        badgeBg: "#C6922C",
        badgeText: "#FFFFFF",
        pillBg: "#C6922C",
        qBg: "#FFFFFF",
        qTagBg: "#8E6510",
        qTagText: "#FFFFFF",
        qText: "#17281F"
      },
      rouge: {
        name: "Martyrs & Esprit Saint",
        chipClass: "chip-rouge",
        outerBg: "#FAF5F5",
        cardBg: "#7A1A22",
        cardInner: "#962630",
        gold: "#D4AF37",
        goldLight: "#F6DF9F",
        verseColor: "#FFFFFF",
        verseSub: "#F6DF9F",
        snippetColor: "#FBEAEA",
        badgeBg: "#4F1015",
        badgeText: "#FFFFFF",
        pillBg: "#541218",
        qBg: "#FDF6F6",
        qTagBg: "#541218",
        qTagText: "#F6DF9F",
        qText: "#2B0B0E"
      },
      violet: {
        name: "Avent & Carême",
        chipClass: "chip-violet",
        outerBg: "#FAF6FA",
        cardBg: "#441F63",
        cardInner: "#592982",
        gold: "#D4AF37",
        goldLight: "#F6DF9F",
        verseColor: "#FFFFFF",
        verseSub: "#F6DF9F",
        snippetColor: "#F5EDFA",
        badgeBg: "#2C1340",
        badgeText: "#FFFFFF",
        pillBg: "#311447",
        qBg: "#FAF5FC",
        qTagBg: "#311447",
        qTagText: "#F6DF9F",
        qText: "#220D33"
      }
    };

    // ==============================================================
// CONFIGURATION DU SERVEUR BACKEND API
// ==============================================================
// Détection automatique en local ou lorsque servi par app.py.
// Si le frontend est hébergé sur Cloudflare Pages et votre serveur Python sur Koyeb/Render,
// renseignez ici l'URL publique de votre backend (ex: "https://parole-api.koyeb.app").
const API_BASE_URL = (window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1'))
  ? (window.location.port === '8080' ? '' : 'http://localhost:8080')
  : '';

    let activePalette = palettes.violet;
    let canvas = document.getElementById('posterCanvas');
    let ctx = canvas.getContext('2d');
    let currentImage = new Image();
    let currentImageSrc = "assets/illustrations/croix-bible.jpg";

    let logoImage = new Image();
    logoImage.src = 'assets/logos/logo-EM-transparent.png';
    logoImage.onload = () => renderPoster();

    // Mode Toggle
    function setMode(m) {
      document.getElementById('btnModeView').classList.toggle('active', m === 'view');
      document.getElementById('btnModeEdit').classList.toggle('active', m === 'edit');
      document.getElementById('viewSection').style.display = (m === 'view') ? 'block' : 'none';
      document.getElementById('editSection').style.display = (m === 'edit') ? 'block' : 'none';
      const testBar = document.getElementById('testModeBar');
      if (testBar) {
        testBar.style.display = (m === 'edit') ? 'flex' : 'none';
      }
    }

    // Liturgical Theme Switcher
    function setLiturgyTheme(colorKey, btn) {
      document.querySelectorAll('.liturgy-option').forEach(b => b.classList.remove('active'));
      const targetBtn = btn || document.getElementById('opt' + colorKey.charAt(0).toUpperCase() + colorKey.slice(1));
      if (targetBtn) targetBtn.classList.add('active');
      
      activePalette = palettes[colorKey] || palettes.vert;

      const chip = document.getElementById('liturgyChip');
      chip.className = 'liturgy-chip ' + activePalette.chipClass;
      chip.innerText = activePalette.name;

      renderPoster();
    }

    // Select and Set Illustration
    function selectIllustration(src, el) {
      document.querySelectorAll('.img-card').forEach(o => o.classList.remove('active'));
      if (el) el.classList.add('active');
      currentImageSrc = src;
      currentImage = new Image();
      currentImage.src = src;
      currentImage.onload = () => renderPoster();
    }

    function handleFileUpload(e) {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = function(evt) {
        selectIllustration(evt.target.result, null);
        showToast('Image personnalisée importée !');
      };
      reader.readAsDataURL(file);
    }

    // Date Utilities in French
    const JOURS = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];
    const MOIS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];

    function formatDateFr(dt) {
      const jour = JOURS[dt.getDay()];
      const mois = MOIS[dt.getMonth()];
      return `${jour} ${dt.getDate()} ${mois} ${dt.getFullYear()}`;
    }

    // Check if poster already exists for selected date (Anti-duplication logic)
    async function checkAndDisplayDate(dateStr) {
      if (!dateStr) return;
      const parts = dateStr.split('-');
      const dt = new Date(parts[0], parts[1] - 1, parts[2]);
      const formatted = formatDateFr(dt);

      document.getElementById('displayDateLabel').innerText = formatted;
      document.getElementById('inpDate').value = 'PAROLE DU JOUR  •  ' + formatted.toUpperCase();

      // 1. Vérifier si l'affiche existe dans localStorage
      const cached = localStorage.getItem('parole_du_jour_' + dateStr);
      if (cached) {
        try {
          const data = JSON.parse(cached);
          displayExistingPoster(data, dateStr);
          return;
        } catch (e) {
          console.warn("Erreur lecture localStorage:", e);
        }
      }

      // 2. Vérifier si l'affiche existe sur le serveur backend ou output (en mode serveur HTTP)
      if (window.location.protocol !== 'file:') {
        try {
          const resp = await fetch(`${API_BASE_URL}/api/check?date=${dateStr}`);
          if (resp.ok) {
            const res = await resp.json();
            if (res.exists && res.data) {
              localStorage.setItem('parole_du_jour_' + dateStr, JSON.stringify(res.data));
              displayExistingPoster(res.data, dateStr);
              return;
            }
          }
        } catch (err) {}

        try {
          const localJson = await fetch(`output/data-${dateStr}.json`);
          if (localJson.ok) {
            const data = await localJson.json();
            if (data && data.ref) {
              localStorage.setItem('parole_du_jour_' + dateStr, JSON.stringify(data));
              displayExistingPoster(data, dateStr);
              return;
            }
          }
        } catch (e) {}
      }

      // 3. Aucune affiche existante : afficher l'état d'attente
      displayEmptyState(dateStr, formatted);
    }

    function displayExistingPoster(data, dateStr) {
      // Rendre visible le canvas et masquer l'état vide
      document.getElementById('posterEmptyState').style.display = 'none';
      document.getElementById('posterCanvas').style.display = 'block';

      applyHarmonizedData(data);
      setActionButtonsEnabled(true);
      setGenerateButtonState('locked', dateStr);
    }

    function displayEmptyState(dateStr, formatted) {
      document.getElementById('posterEmptyState').style.display = 'flex';
      document.getElementById('posterCanvas').style.display = 'none';
      document.getElementById('emptyStateDateDesc').innerText = `L'affiche officielle n'a pas encore été créée pour le ${formatted}. Cliquez sur le bouton ci-dessus pour la composer.`;

      document.getElementById('postTextContent').innerText = `En attente de la génération de l'affiche et de la méditation pour le ${formatted}...`;

      setActionButtonsEnabled(false);
      setGenerateButtonState('ready', dateStr);
    }

    function setActionButtonsEnabled(enabled) {
      const btns = ['btnCopyText', 'btnDownloadPoster', 'btnShareWhatsapp', 'btnShareFacebook'];
      btns.forEach(id => {
        const b = document.getElementById(id);
        if (!b) return;
        b.disabled = !enabled;
        b.classList.toggle('action-disabled', !enabled);
      });
    }

    function setGenerateButtonState(state, dateStr) {
      const btn = document.getElementById('btnGenerate');
      if (!btn) return;

      const parts = dateStr ? dateStr.split('-') : [];
      let subText = "Contenu du jour sélectionné";
      if (parts.length === 3) {
        const dt = new Date(parts[0], parts[1] - 1, parts[2]);
        subText = `Contenu du ${dt.getDate()} ${MOIS[dt.getMonth()].toLowerCase()} ${dt.getFullYear()}`;
      }

      if (state === 'locked') {
        btn.disabled = true;
        btn.classList.add('btn-locked');
        btn.title = "Affiche déjà existante pour ce jour. Génération verrouillée pour éviter toute duplication.";
        btn.innerHTML = `
          <div class="hero-icon-pulse">
            <svg class="icon icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
              <path d="m9 12 2 2 4-4"></path>
            </svg>
          </div>
          <div class="hero-text-block">
            <span class="hero-title">AFFICHE DÉJÀ GÉNÉRÉE</span>
            <span class="hero-subtitle" id="generateSubLabel">Génération verrouillée · Affiche enregistrée</span>
          </div>
        `;
      } else {
        btn.disabled = false;
        btn.classList.remove('btn-locked');
        btn.title = "Générer la parole du jour pour cette date";
        btn.innerHTML = `
          <div class="hero-icon-pulse">
            <svg class="icon icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h7" />
              <path d="M14 2v4a2 2 0 0 0 2 2h4" />
              <line x1="8" y1="9" x2="12" y2="9" />
              <line x1="8" y1="13" x2="13" y2="13" />
              <line x1="8" y1="17" x2="10" y2="17" />
              <path d="M19 12l1.2 2.8L23 16l-2.8 1.2L19 20l-1.2-2.8L15 16l2.8-1.2L19 12z" fill="currentColor" stroke="none" />
            </svg>
          </div>
          <div class="hero-text-block">
            <span class="hero-title">GÉNÉRER LA PAROLE DU JOUR CHOISI</span>
            <span class="hero-subtitle" id="generateSubLabel">${subText}</span>
          </div>
        `;
      }
    }

    function onDateChanged(val) {
      if (!val) return;
      checkAndDisplayDate(val);
    }

    function shiftDay(delta) {
      const picker = document.getElementById('datePicker');
      const parts = picker.value.split('-');
      const cur = new Date(parts[0], parts[1] - 1, parts[2]);
      cur.setDate(cur.getDate() + delta);
      const y = cur.getFullYear();
      const m = String(cur.getMonth() + 1).padStart(2, '0');
      const d = String(cur.getDate()).padStart(2, '0');
      const nextDate = `${y}-${m}-${d}`;
      picker.value = nextDate;
      onDateChanged(nextDate);
    }

    function setToday() {
      const now = new Date();
      const y = now.getFullYear();
      const m = String(now.getMonth() + 1).padStart(2, '0');
      const d = String(now.getDate()).padStart(2, '0');
      const todayStr = `${y}-${m}-${d}`;
      const picker = document.getElementById('datePicker');
      picker.value = todayStr;
      onDateChanged(todayStr);
    }

    function triggerDatePicker(e) {
      const picker = document.getElementById('datePicker');
      if (e.target !== picker) {
        if (typeof picker.showPicker === 'function') {
          try { picker.showPicker(); } catch (err) { picker.focus(); }
        } else {
          picker.focus();
        }
      }
    }

    // Réinitialiser les données de test pour recommencer de zéro
    function resetCurrentDayTest() {
      const dateStr = document.getElementById('datePicker').value;
      if (!dateStr) return;
      localStorage.removeItem('parole_du_jour_' + dateStr);
      checkAndDisplayDate(dateStr);
      showToast("✓ Données réinitialisées pour le " + dateStr + ". Prêt à générer !");
    }

    function clearAllTestData() {
      Object.keys(localStorage).forEach(k => {
        if (k.startsWith('parole_du_jour_')) localStorage.removeItem(k);
      });
      const dateStr = document.getElementById('datePicker').value;
      checkAndDisplayDate(dateStr);
      showToast("✓ Tout le cache de test a été réinitialisé.");
    }

    function showToast(msg) {
      const t = document.getElementById('toast');
      t.innerText = msg;
      t.style.display = 'block';
      setTimeout(() => { t.style.display = 'none'; }, 2800);
    }

    function copyPostText() {
      const text = document.getElementById('postTextContent').innerText;
      navigator.clipboard.writeText(text).then(() => {
        showToast('Texte de méditation copié !');
      });
    }

    function shareOnWhatsApp() {
      const text = document.getElementById('postTextContent').innerText;
      const url = 'https://api.whatsapp.com/send?text=' + encodeURIComponent(text);
      window.open(url, '_blank');
    }

    function shareOnFacebook() {
      const url = 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(window.location.href);
      window.open(url, '_blank');
    }

    function downloadPoster() {
      const date = document.getElementById('datePicker').value;
      try {
        const link = document.createElement('a');
        link.download = 'Parole-du-jour-' + date + '.png';
        link.href = canvas.toDataURL('image/png', 1.0);
        link.click();
        showToast('Affiche téléchargée en haute résolution !');
      } catch (err) {
        window.open('output/parole-du-jour-' + date + '.png', '_blank');
        showToast('Affiche générée dans output/');
      }
    }

    // ==============================================================
    // UNIFIED HARMONIZATION GENERATOR (The core workflow)
    // ==============================================================
    async function generateDailySynchronized() {
      const dateStr = document.getElementById('datePicker').value;
      if (!dateStr) return;

      // Anti-duplication stricte : si l'affiche existe déjà, charger sans recréer
      if (localStorage.getItem('parole_du_jour_' + dateStr)) {
        showToast("Cette affiche existe déjà pour ce jour. Duplication évitée.");
        checkAndDisplayDate(dateStr);
        return;
      }

      const progressBox = document.getElementById('generationProgress');
      const progressTxt = document.getElementById('genProgressText');
      const btnGen = document.getElementById('btnGenerate');

      progressBox.style.display = 'flex';
      btnGen.disabled = true;
      progressTxt.innerText = "1/3 Consultation de la liturgie AELF...";

      try {
        let synchronizedData = null;

        // Étape 1 : Essayer l'API backend si servi via HTTP/HTTPS
        if (window.location.protocol !== 'file:') {
          try {
            const apiResp = await fetch(`${API_BASE_URL}/api/generate`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ date: dateStr })
            });
            if (apiResp.ok) {
              const res = await apiResp.json();
              if (res && res.ref) {
                synchronizedData = res;
              }
            }
          } catch (e) {
            // Serveur non joignable, bascule en direct navigateur
          }
        }

        // Étape 2 : Si pas de serveur local, exécution complète dans le navigateur
        if (!synchronizedData) {
          progressTxt.innerText = "2/3 Récupération des lectures officielles AELF...";
          let aelfJson = null;
          // Interroger l'API AELF (zones afrique, romain, france selon https://api.aelf.org)
          for (const zone of ['afrique', 'romain', 'france']) {
            try {
              const aelfResp = await fetch(`https://api.aelf.org/v1/messes/${dateStr}/${zone}`);
              if (aelfResp.ok) {
                const res = await aelfResp.json();
                if (res && res.messes && res.messes.length > 0) {
                  aelfJson = res;
                  break;
                }
              }
            } catch (e) {}
          }
          if (!aelfJson) throw new Error('Impossible de contacter AELF pour cette date.');

          // Tenter la méditation par Gemini LLM en direct dans le navigateur
          let aiResult = null;
          let evangileText = "";
          let evangileRef = "ÉVANGILE";

          if (aelfJson.messes && aelfJson.messes.length > 0) {
            for (let m of aelfJson.messes) {
              if (m.lectures) {
                for (let l of m.lectures) {
                  if (l.type === 'evangile') {
                    evangileRef = l.ref ? l.ref.replace(/&nbsp;/g, ' ').toUpperCase() : 'ÉVANGILE';
                    evangileText = l.contenu ? l.contenu.replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ') : '';
                    break;
                  }
                }
              }
              if (evangileText) break;
            }
          }

          progressTxt.innerText = "3/3 Harmonisation liturgique & art sacré officiel...";
          // Si le serveur backend n'est pas joignable, harmonisation directe via le corpus liturgique AELF
          synchronizedData = parseAndHarmonizeAELF(aelfJson, dateStr, null, null);
        }

        // Étape 3 : Sauvegarde dans le stockage persistant (anti-duplication)
        localStorage.setItem('parole_du_jour_' + dateStr, JSON.stringify(synchronizedData));

        // Étape 4 : Affichage immédiat et verrouillage
        displayExistingPoster(synchronizedData, dateStr);

        showToast("✓ Parole du Jour générée et enregistrée avec succès !");
      } catch (err) {
        console.error(err);
        showToast("Erreur de synchronisation : " + err.message);
        setGenerateButtonState('ready', dateStr);
      } finally {
        progressBox.style.display = 'none';
      }
    }

    // Moteur d'harmonisation spirituelle et d'art sacré (sans "de la férie")
    function parseAndHarmonizeAELF(data, dateStr, aiResult, aiImageUri = null) {
      const info = data.informations || {};
      const couleur = (info.couleur || 'vert').toLowerCase();
      const rawFete = info.fete || info.ligne2 || '';
      const ligne1 = info.ligne1 || '';

      // Nettoyer strictement "de la férie"
      const feteAffichee = (rawFete && !rawFete.toLowerCase().includes('férie')) ? rawFete : ligne1;

      let evangile = null;
      if (data.messes && data.messes.length > 0) {
        for (let m of data.messes) {
          if (m.lectures) {
            for (let l of m.lectures) {
              if (l.type === 'evangile') {
                evangile = l;
                break;
              }
            }
          }
          if (evangile) break;
        }
      }

      const ref = (evangile && evangile.ref) ? evangile.ref.replace(/&nbsp;/g, ' ').toUpperCase() : 'ÉVANGILE';
      const titre = (evangile && evangile.titre) ? evangile.titre.trim() : '';
      const contenu = (evangile && evangile.contenu) ? evangile.contenu.replace(/<[^>]+>/g, ' ') : '';
      const corpus = `${dateStr} ${ref} ${feteAffichee} ${titre} ${contenu}`.toLowerCase();

      let passage_fort, theme_titre, theme_synthese, question_du_jour, resume, reflexion, priere, illusPath, cardId;

      // Si Gemini a produit une réponse complète
      if (aiResult && aiResult.passage_fort) {
        passage_fort = aiResult.passage_fort;
        theme_titre = aiResult.theme_titre;
        theme_synthese = aiResult.theme_synthese;
        question_du_jour = aiResult.question_du_jour;
        resume = aiResult.resume;
        reflexion = aiResult.reflexion;
        priere = aiResult.priere;
      } else {
        // Moteur liturgique expert intégré (fallback robuste sans "de la férie")
        // 1. Évangile des dix lépreux et du Samaritain reconnaissant (Lc 17, 11-19)
        if (corpus.includes('lépreux') || corpus.includes('lepreux') || corpus.includes('samaritain') || (ref.includes('17') && ['11-19', '11 - 19', '11, 19', '11–19'].some(v => ref.includes(v)))) {
          passage_fort = "« Il ne s'est trouvé parmi eux que cet étranger pour revenir sur ses pas et rendre gloire à Dieu. »";
          theme_titre = "La Puissance de la Gratitude";
          theme_synthese = "Sur les dix lépreux purifiés par Jésus, un seul est revenu sur ses pas pour rendre gloire à Dieu et dire merci. Ne soyons pas de ceux qui oublient Dieu aussitôt exaucés.";
          question_du_jour = "« Est-ce que je prends réellement le temps de remercier Dieu pour ses bienfaits quotidiens, ou est-ce que je me contente de lui demander toujours davantage ? »";
          resume = "Sur son chemin vers Jérusalem, Jésus rencontre dix lépreux qui l'implorent d'avoir pitié d'eux. Il les renvoie vers les prêtres et, en chemin, ils sont tous guéris.\n\nSeul un Samaritain rebrousse chemin en glorifiant Dieu à haute voix pour se prosterner aux pieds de Jésus.";
          reflexion = "Cet Évangile met en lumière la vertu si rare de la reconnaissance. Combien de fois avons-nous crié vers le Ciel dans l'angoisse pour ensuite oublier d'offrir une prière de louange ?\n\nLa gratitude transforme la bénédiction reçue en relation vivante et salvatrice avec le Seigneur.\n\nReconnaître les bienfaits du Très-Haut ouvre notre âme à la plénitude de sa grâce.";
          priere = "Seigneur, pardonne-moi pour toutes les fois où j'ai consommé tes grâces sans te rendre grâce. Donne-moi un cœur reconnaissant, prompt à louer ta bonté dans les joies comme dans les épreuves. Amen.";
        }
        // 2. Le Règne de Dieu au milieu de vous (Lc 17, 20-25)
        else if (corpus.includes('règne de dieu') || corpus.includes('regne de dieu') || (ref.includes('17') && ['20-25', '20 - 25', '20, 25', '20–25'].some(v => ref.includes(v)))) {
          passage_fort = "« Le règne de Dieu est au milieu de vous. »";
          theme_titre = "Le Règne de Dieu au Milieu de Nous";
          theme_synthese = "Jésus nous enseigne que le Royaume de Dieu ne vient pas avec éclat extérieur : il est déjà présent, agissant au fond de nos cœurs et dans notre foi vécue.";
          question_du_jour = "« Est-ce que je sais discerner la présence discrète mais agissante du Seigneur au cœur de mes activités quotidiennes ? »";
          resume = "Interrogé par les pharisiens sur la venue du règne de Dieu, Jésus leur répond que sa venue n'est pas observable à vue d'œil.\n\nLe Royaume des Cieux n'est pas une conquête terrestre, il est déjà vivant et agissant au milieu de nous.";
          reflexion = "Nous attendons souvent Dieu dans l'extraordinaire ou le spectaculaire, alors qu'il se fait humblement proche de chacun de nous.\n\nAccueillir le Règne de Dieu aujourd'hui, c'est laisser l'amour du Christ guider nos décisions et nos regards.\n\nFaisons de notre journée une demeure pour sa paix et sa justice.";
          priere = "Seigneur Jésus, règne en maître dans mon cœur et dans ma vie. Éloigne de moi les illusions et apprends-moi à reconnaître ta présence vivante à chaque instant de ce jour. Amen.";
        }
        // 3. Le Fils de l'homme et la vigilance (Lc 17, 26-37)
        else if (corpus.includes('fils de l\'homme') || corpus.includes('noé') || corpus.includes('noe') || (ref.includes('17') && ['26-37', '26 - 37', '26, 37', '26–37'].some(v => ref.includes(v)))) {
          passage_fort = "« Le jour où le Fils de l’homme se révélera. »";
          theme_titre = "La Vigilance du Cœur";
          theme_synthese = "Le Christ nous appelle à une vigilance constante : celui qui cherche à préserver sa vie pour lui-même la perdra, mais qui la donne par amour la sauvera.";
          question_du_jour = "« Suis-je prêt spirituellement si le Seigneur venait me visiter aujourd'hui, ou mon cœur est-il assoupi dans les soucis matériels ? »";
          resume = "Évoquant les jours de Noé et de Loth, Jésus exhorte ses disciples à une vigilance totale face à la venue du Fils de l'homme.\n\nIl nous rappelle l'urgence d'attacher notre cœur à ce qui demeure éternellement.";
          reflexion = "Le train-train du quotidien peut endormir notre foi si nous oublions notre destinée céleste.\n\nVivre dans la vigilance chrétienne, ce n'est pas vivre dans l'angoisse, mais dans l'amour actif et confiant.\n\nEngageons chaque journée comme une offrande agréable à Dieu.";
          priere = "Seigneur Jésus, garde mon âme en éveil dans la prière et la charité. Que mon cœur ne s'alourdisse pas des fardeaux passagers de ce monde, mais demeure fixé sur ton retour glorieux. Amen.";
        }
        // 4. La prière persévérante et la veuve (Lc 18, 1-8)
        else if (corpus.includes('crient vers lui') || corpus.includes('juge') || corpus.includes('veuve') || (ref.includes('18') && ['1-8', '1 - 8', '1, 8', '1–8'].some(v => ref.includes(v)))) {
          passage_fort = "« Dieu ne ferait pas justice à ses élus qui crient vers lui ? »";
          theme_titre = "La Prière Persévérante";
          theme_synthese = "Par la parabole de la veuve et du juge, Jésus nous invite à prier sans cesse avec persévérance et confiance, sans jamais nous décourager.";
          question_du_jour = "« Est-ce que je persévère dans ma prière avec foi quand la réponse semble tarder, ou est-ce que j'abandonne rapidement ? »";
          resume = "Jésus raconte à ses disciples la parabole du juge sans scrupules qui finit par rendre justice à une pauvre veuve à force d'insistance.\n\nÀ plus forte raison, Dieu notre Père écoute et exauce la prière confiante de ses enfants.";
          reflexion = "La prière persévérante n'a pas pour but de changer la volonté de Dieu, mais d'ajuster notre cœur à sa grâce.\n\nLe Seigneur nous invite à une foi inébranlable qui ne désespère jamais.\n\nQuand le Fils de l'homme viendra, trouvera-t-il la foi sur notre terre ?";
          priere = "Seigneur, fortifie ma foi lorsque le doute m'assaille. Donne-moi la persévérance dans la prière et la certitude consolante que tu écoutes toujours le cri de tes humbles enfants. Amen.";
        } else if (corpus.includes('compassion') || corpus.includes('brebis qui n\'ont pas de berger') || corpus.includes('mt 9')) {
          passage_fort = "« Voyant les foules, Jésus fut saisi de compassion envers elles. »";
          theme_titre = "La Compassion du Christ";
          theme_synthese = "Voyant les foules désemparées comme des brebis sans berger, Jésus est saisi d'une profonde compassion. Il guérit toute infirmité et nous appelle à la prière.";
          question_du_jour = "« Est-ce que mon regard sur les personnes vulnérables est habité par la compassion et la tendresse du Christ, ou par l'indifférence ? »";
          resume = "Parcourant les villes et villages, Jésus enseigne dans les synagogues, proclame l'Évangile du Royaume et guérit toute maladie.\n\nSaisi de compassion devant les foules désemparées comme des brebis sans berger, il appelle ses disciples à prier le Maître de la moisson d'envoyer des ouvriers.";
          reflexion = "La compassion de Jésus n'est pas une simple émotion passive, elle est un élan d'amour actif qui console, relève et guérit.\n\nEn ce temps de l'Avent, le Seigneur nous confie la mission de porter sa tendresse à ceux qui sont éprouvés.\n\nSoyons chaque jour des instruments d'espérance et de paix dans notre entourage.";
          priere = "Seigneur Jésus, toi dont le Cœur est plein de miséricorde pour les foules désemparées, donne-moi un regard attentif et compatissant. Fais de moi un ouvrier fidèle de ta moisson. Amen.";
        } else if (corpus.includes('ce que vous avez fait') || ref.includes('MT 25') || corpus.includes('matthieu 25')) {
          passage_fort = "« Ce que vous avez fait à l'un de ces plus petits de mes frères, c'est à moi que vous l'avez fait. »";
          theme_titre = "La Charité Vivante du Christ";
          theme_synthese = "En partageant son manteau avec le pauvre transi de froid, saint Martin nous enseigne que chaque geste d'amour fraternel s'adresse au Seigneur Jésus lui-même.";
          question_du_jour = "« Suis-je prêt aujourd'hui à ouvrir mon cœur et à partager concrètement ce que j'ai avec celui qui est dans le besoin autour de moi ? »";
          resume = "En ce jour de fête de saint Martin de Tours, l'Église célèbre le zèle pastoral et la charité inconditionnelle de ce grand évêque.\n\nSon geste mémorable de partage de son manteau avec un mendiant aux portes d'Amiens est la démonstration éclatante de l'Évangile vécu.";
          reflexion = "La charité chrétienne n'est pas une simple philanthropie, elle est rencontre intime avec le Christ voilé sous les traits du pauvre.\n\nSaint Martin n'a pas hésité à fendre son vêtement en deux : la sainteté commence dès lors que nous acceptons de donner de notre nécessaire.\n\nDemandons la grâce d'avoir des yeux attentifs aux détresses invisibles de notre quotidien.";
          priere = "Seigneur Jésus, accorde-moi un cœur généreux et compatissant à l'exemple de saint Martin. Apprends-moi à reconnaître ton visage dans le visage de mes frères démunis et à aimer en actes et en vérité. Amen.";
        } else if (corpus.includes('berger') || corpus.includes('brebis') || corpus.includes('pasteur') || corpus.includes('jean 10') || corpus.includes('luc 15')) {
          passage_fort = "« Je suis le bon pasteur : le bon pasteur donne sa vie pour ses brebis. »";
          theme_titre = "La Tendresse du Bon Berger";
          theme_synthese = "Le Bon Berger connaît chacune de ses brebis par son nom et donne sa vie pour elles. Aucune ne sera abandonnée ni perdue.";
          question_du_jour = "« Est-ce que je reconnais la voix du Bon Berger au milieu du tumulte de mes journées pour me laisser guider par Lui ? »";
          resume = "Le Christ se présente à nous comme le Bon Berger qui rassemble, protège et nourrit son troupeau.\n\nContrairement au mercenaire, Jésus veille avec amour sur chaque âme et part à la recherche de celle qui s'égare.";
          reflexion = "Dans un monde saturé de voix discordantes, la voix du Bon Berger apporte la paix profonde et la vérité.\n\nApprenons à faire silence dans la prière pour discerner ses appels dans notre vie.\n\nConfions-lui nos peurs et nos doutes : entre ses mains bienveillantes, nous ne manquons de rien.";
          priere = "Seigneur Jésus, toi qui es mon Bon Berger, guide mes pas sur les sentiers de la justice. Garde-moi près de ton cœur et ramène-moi toujours à toi lorsque je m'égare. Amen.";
        } else if (corpus.includes('cène') || corpus.includes('cene') || corpus.includes('pain') || corpus.includes('corps') || corpus.includes('vin') || corpus.includes('eucharistie')) {
          passage_fort = "« Prenez, mangez : ceci est mon corps donné pour vous. »";
          theme_titre = "Le Pain Vivant du Ciel";
          theme_synthese = "En instituant l'Eucharistie, le Christ se donne tout entier pour nourrir notre foi et nous unir intimement à sa vie divine.";
          question_du_jour = "« Comment puis-je m'approcher de la Sainte Eucharistie avec plus de recueillement et un cœur disponible à la grâce ? »";
          resume = "Au cours de la Sainte Cène, la veille de sa Passion, Jésus bénit le pain et le vin en instituant le sacrement de l'Eucharistie.\n\nIl nous laisse le mémorial éternel de son sacrifice d'amour et de sa présence réelle parmi nous.";
          reflexion = "L'Eucharistie est la source et le sommet de toute la vie chrétienne.\n\nEn recevant le Pain du Ciel, nous sommes fortifiés pour devenir à notre tour des témoins vivants de la miséricorde.\n\nQue notre communion dominicale transforme nos relations et nos actes au quotidien.";
          priere = "Seigneur Jésus, Pain vivant descendu du Ciel, nourris mon âme de ta sainte présence. Fais de moi un instrument d'unité et de paix dans ton Église. Amen.";
        } else if (corpus.includes('résurrection') || corpus.includes('resurrection') || corpus.includes('tombeau') || corpus.includes('pâques') || corpus.includes('paques')) {
          passage_fort = "« Pourquoi cherchez-vous le Vivant parmi les morts ? Il est ressuscité ! »";
          theme_titre = "La Victoire de la Résurrection";
          theme_synthese = "Le Christ a vaincu les ténèbres de la mort et nous ouvre les portes de la vie éternelle. Marchons en enfants de lumière !";
          question_du_jour = "« En quoi la victoire de la résurrection du Seigneur renouvelle-t-elle aujourd'hui mon espérance au cœur des épreuves ? »";
          resume = "Au matin de Pâques, le tombeau est vide et les anges annoncent la plus grande nouvelle de l'histoire humaine : Jésus est vivant !\n\nIl apparaît à ses disciples et répand sur eux sa paix souveraine.";
          reflexion = "La résurrection n'est pas un événement du passé, elle est une puissance agissante dans la vie de chaque croyant.\n\nAucune obscurité n'a le dernier mot face au Christ ressuscité.\n\nVivons chaque jour avec la certitude joyeuse que l'amour de Dieu triomphe toujours.";
          priere = "Ô Christ ressuscité, illumine ma vie de ta clarté glorieuse. Éloigne de moi le découragement et fais de moi un témoin radieux de ton espérance. Amen.";
        } else {
          const cleanTitre = titre.replace(/[«»]/g, '').trim();
          passage_fort = cleanTitre ? `« ${cleanTitre} »` : "« Ta foi t'a sauvé, va en paix. »";

          if (cleanTitre && cleanTitre.length <= 36 && !['en ce temps', 'comme', 'quand'].some(w => cleanTitre.toLowerCase().includes(w))) {
            theme_titre = cleanTitre;
          } else if (ligne1.toLowerCase().includes('avent')) {
            theme_titre = "L'Espérance de l'Avent";
          } else if (ligne1.toLowerCase().includes('carême') || ligne1.toLowerCase().includes('careme')) {
            theme_titre = "La Grâce de la Conversion";
          } else if (feteAffichee && !feteAffichee.toLowerCase().startsWith('de la')) {
            theme_titre = feteAffichee.slice(0, 36);
          } else {
            theme_titre = "Parole de Vie Éternelle";
          }

          theme_synthese = `Méditons la Parole du Seigneur (${ref}) qui illumine notre route chaque jour. Elle est une source inépuisable de réconfort et de sanctification pour notre foi.`;
          question_du_jour = "« Comment puis-je accueillir et mettre en pratique cette Parole de Dieu aujourd'hui dans ma vie concrète ? »";
          resume = `Lecture de la sainte liturgie de ce jour selon ${ref}.\n\nLe Seigneur nous invite à renouveler notre confiance et à avancer avec fidélité sur le chemin de l'Évangile.`;
          reflexion = "Chaque verset de l'Écriture Sainte porte une promesse de renouveau pour celui qui écoute avec un cœur droit.\n\nNe laissons pas passer cette journée sans laisser la Parole porter du fruit dans nos actes et nos pensées.\n\nEn communion avec toute la communauté paroissiale, fortifions notre engagement spirituel.";
          priere = "Seigneur, que ta Parole vivante soit la lampe de mes pas et la lumière sur ma route. Conduis-moi selon ta vérité et accorde-moi ta grâce. Amen.";
        }
      }

      // Nettoyer strictement toute trace résiduelle de "de la férie" dans le titre
      if (theme_titre && theme_titre.toLowerCase().includes('férie')) {
        theme_titre = corpus.includes('compassion') ? "La Compassion du Christ" : "Parole de Vie Éternelle";
      }

      // Résolution de l'illustration (IA avec chefs-d'œuvre par temps liturgique)
      if (aiImageUri) {
        illusPath = aiImageUri;
        cardId = "cardAi";
        const aiImgEl = document.getElementById('cardAiImg');
        if (aiImgEl) aiImgEl.src = aiImageUri;
        const cardAiEl = document.getElementById('cardAi');
        if (cardAiEl) cardAiEl.style.display = 'block';
      } else {
        const seasonArt = getSeasonalArtwork(couleur, ligne1, feteAffichee, ref, theme_titre);
        illusPath = seasonArt.path;
        cardId = seasonArt.cardId;
      }

      const parts = dateStr.split('-');
      const dt = new Date(parts[0], parts[1] - 1, parts[2]);
      const dateCourt = `${String(dt.getDate()).padStart(2, '0')}/${String(dt.getMonth() + 1).padStart(2, '0')}/${dt.getFullYear()}`;
      const feteHeader = feteAffichee ? `\n*${feteAffichee}*\n` : '';

      const post_text = `🌿 Parole du jour — ${ref} (${dateCourt})${feteHeader}

📖 Résumé :
${resume}

✨ Réflexion :
${reflexion}

• Question du jour :
${question_du_jour}

🙏 Prière :
${priere}

Paroisse Saint Michel de Houéto · Enfance Missionnaire`;

      return {
        date: dateStr,
        couleur: couleur,
        ref: ref,
        passage_fort: passage_fort,
        theme_titre: theme_titre,
        theme_synthese: theme_synthese,
        question_du_jour: question_du_jour,
        illustration_path: illusPath,
        card_id: cardId,
        post_text: post_text
      };
    }

    // Sélection intelligente de l'art liturgique par saison
    function getSeasonalArtwork(couleur, ligne1 = '', fete = '', ref = '', themeTitre = '') {
      const c = (couleur || 'vert').toLowerCase();
      const l1 = (ligne1 || '').toLowerCase();
      const f = (fete || '').toLowerCase();
      const r = (ref || '').toLowerCase();
      const th = (themeTitre || '').toLowerCase();

      // 1. Péricopes majeures spécifiques
      if (r.includes('mt 26') || r.includes('mc 14') || r.includes('lc 22') || r.includes('1 co 11') || f.includes('cène') || th.includes('eucharistie')) {
        return { path: 'assets/illustrations/sainte-cene.jpg', label: 'La Sainte Cène (Eucharistie)', cardId: 'cardCene' };
      }
      if (th.includes('compassion')) {
        return { path: 'assets/illustrations/jesus-compassion.jpg', label: 'La Compassion du Christ', cardId: 'cardCompassion' };
      }

      // 2. Par Temps Liturgique et Couleur
      if (c === 'rouge' || f.includes('martyr') || l1.includes('pentecôte') || l1.includes('rameaux')) {
        return { path: 'assets/illustrations/pentecote-esprit-saint.jpg', label: 'La Pentecôte & Esprit Saint (Rouge / Martyrs)', cardId: 'cardEspritSaint' };
      } else if (c === 'violet') {
        if (l1.includes('carême') || l1.includes('careme') || l1.includes('cendres')) {
          return { path: 'assets/illustrations/croix-bible.jpg', label: 'Croix et Sainte Bible HD (Carême)', cardId: 'cardCroix' };
        } else {
          // Temps de l'Avent
          return { path: 'assets/illustrations/avent-annonciation.jpg', label: 'L\'Annonciation (Temps de l\'Avent)', cardId: 'cardAvent' };
        }
      } else if (c === 'blanc' || c === 'or' || c === 'dore') {
        if (f.includes('martin')) {
          return { path: 'assets/illustrations/saint-martin.jpg', label: 'Saint Martin de Tours (Mémoire)', cardId: 'cardSaintMartin' };
        }
        return { path: 'assets/illustrations/resurrection.jpg', label: 'Le Christ Ressuscité (Solennités & Fêtes)', cardId: 'cardResurrection' };
      } else {
        // Temps Ordinaire (Vert)
        return { path: 'assets/illustrations/bon-berger.jpg', label: 'Le Bon Berger (Temps Ordinaire)', cardId: 'cardBonBerger' };
      }
    }

    // Appliquer l'illustration harmonisée avec sélection de la carte adéquate
    function applyHarmonizedIllustration(illusPath, cardId) {
      if (!illusPath) illusPath = "assets/illustrations/croix-bible.jpg";

      // Si c'est une image IA générée (base64 ou output/)
      if (illusPath.startsWith('data:') || illusPath.includes('output/')) {
        const aiCard = document.getElementById('cardAi');
        const aiImg = document.getElementById('cardAiImg');
        if (aiCard && aiImg) {
          aiImg.src = illusPath;
          aiCard.style.display = 'block';
        }
        selectIllustration(illusPath, aiCard);
        return;
      }

      // Si un cardId spécifique est fourni et existe dans le DOM
      if (cardId && document.getElementById(cardId)) {
        selectIllustration(illusPath, document.getElementById(cardId));
        return;
      }

      // Recherche dynamique de la carte dans la galerie dont l'image correspond au chemin
      let matchedCard = null;
      document.querySelectorAll('#sacredGallery .img-card').forEach(card => {
        const img = card.querySelector('img');
        if (img && img.getAttribute('src') === illusPath) {
          matchedCard = card;
        }
      });

      if (matchedCard) {
        selectIllustration(illusPath, matchedCard);
      } else {
        selectIllustration(illusPath, document.getElementById('cardCroix'));
      }
    }

    // Appliquer l'ensemble synchronisé
    function applyHarmonizedData(data) {
      if (!data) return;

      // 1. Liturgical theme
      if (data.couleur) {
        setLiturgyTheme(data.couleur);
      }

      // 2. Poster Fields
      if (data.passage_fort) document.getElementById('inpVerse').value = data.passage_fort;
      if (data.ref) document.getElementById('inpRef').value = data.ref;
      if (data.theme_titre) document.getElementById('inpThemeTitle').value = data.theme_titre;
      if (data.theme_synthese) document.getElementById('inpThemeSnippet').value = data.theme_synthese;
      if (data.question_du_jour) document.getElementById('inpQuestion').value = data.question_du_jour;

      // 3. Post Text
      if (data.post_text) {
        document.getElementById('postTextContent').innerText = data.post_text;
      }

      // 4. Harmonized Illustration (IA ou Chefs-d'œuvre par temps liturgique)
      applyHarmonizedIllustration(data.illustration_path, data.card_id);
    }

    // Canvas Helpers
    function roundRect(ctx, x, y, width, height, radius, fill, stroke, strokeWidth) {
      ctx.beginPath();
      ctx.moveTo(x + radius, y);
      ctx.lineTo(x + width - radius, y);
      ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
      ctx.lineTo(x + width, y + height - radius);
      ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
      ctx.lineTo(x + radius, y + height);
      ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
      ctx.lineTo(x, y + radius);
      ctx.quadraticCurveTo(x, y, x + radius, y);
      ctx.closePath();
      if (fill) ctx.fill();
      if (stroke) {
        ctx.lineWidth = strokeWidth || 1;
        ctx.stroke();
      }
    }

    function wrapCanvasLines(ctx, text, maxWidth) {
      const words = text.split(/\s+/);
      const lines = [];
      let curLine = '';

      for (let w of words) {
        const testLine = curLine ? (curLine + ' ' + w) : w;
        if (ctx.measureText(testLine).width <= maxWidth) {
          curLine = testLine;
        } else {
          if (curLine) lines.push(curLine);
          curLine = w;
        }
      }
      if (curLine) lines.push(curLine);
      return lines;
    }

    // ==============================================================
    // MAIN ELASTIC POSTER RENDERER (Never overflows!)
    // ==============================================================
    function renderPoster() {
      const W = 1080, H = 1080;
      const p = activePalette;

      // 1. Outer Background
      ctx.fillStyle = p.outerBg;
      ctx.fillRect(0, 0, W, H);

      ctx.strokeStyle = '#e4dcce';
      ctx.lineWidth = 2;
      ctx.strokeRect(24, 24, W - 48, H - 48);

      ctx.strokeStyle = p.gold;
      ctx.lineWidth = 1;
      ctx.strokeRect(32, 32, W - 64, H - 64);

      // 2. Header: Logo Capsule (Guarantees contrast on all backgrounds)
      if (logoImage.complete && logoImage.naturalWidth > 0) {
        const lh = 80;
        const lw = Math.round(lh * 1.4728);
        const capX = 52, capY = 44;
        const capW = lw + 24, capH = lh + 14;

        ctx.fillStyle = '#ffffff';
        ctx.strokeStyle = p.gold;
        roundRect(ctx, capX, capY, capW, capH, 14, true, true, 1);
        ctx.drawImage(logoImage, capX + 12, capY + 7, lw, lh);
      }

      // Top Right Date & Liturgy Pill
      const pillTxt = document.getElementById('inpDate').value.toUpperCase();
      ctx.font = '700 19px "Plus Jakarta Sans", sans-serif';
      const pillMetrics = ctx.measureText(pillTxt);
      const pillW = Math.max(pillMetrics.width + 50, 520);
      const pillX = W - 56 - pillW;
      const pillY = 66;

      ctx.fillStyle = p.pillBg;
      ctx.strokeStyle = p.gold;
      roundRect(ctx, pillX, pillY, pillW, 48, 24, true, true, 1.5);

      ctx.fillStyle = p.goldLight;
      ctx.textAlign = 'center';
      ctx.fillText(pillTxt, pillX + pillW / 2, pillY + 30);

      // 3. Main Liturgical Card
      const cardX = 56, cardY = 158, cardW = W - 112, cardH = 565;
      ctx.fillStyle = p.cardBg;
      ctx.strokeStyle = p.gold;
      roundRect(ctx, cardX, cardY, cardW, cardH, 28, true, true, 2);

      ctx.strokeStyle = p.cardInner;
      roundRect(ctx, cardX + 8, cardY + 8, cardW - 16, cardH - 16, 20, false, true, 1);

      // Quotation Mark
      ctx.font = 'italic 700 94px "Playfair Display", Georgia, serif';
      ctx.fillStyle = p.gold;
      ctx.textAlign = 'left';
      ctx.fillText("“", cardX + 45, cardY + 110);

      // DYNAMIC VERSE FONT SIZING & MULTI-LINE WRAPPING
      const verseRaw = document.getElementById('inpVerse').value.trim();
      const availW = cardW - 170; // ~798px

      let verseFontSize = 46;
      if (verseRaw.length > 95) {
        verseFontSize = 32;
      } else if (verseRaw.length > 65) {
        verseFontSize = 36;
      } else if (verseRaw.length > 45) {
        verseFontSize = 40;
      }

      ctx.font = 'italic 700 ' + verseFontSize + 'px "Playfair Display", Georgia, serif';
      const lines = wrapCanvasLines(ctx, verseRaw, availW);

      const lineH = Math.round(verseFontSize * 1.25);
      const vStartY = cardY + 38;

      lines.forEach((line, i) => {
        const ly = vStartY + i * lineH;
        ctx.fillStyle = (i === 0) ? p.verseColor : p.verseSub;
        ctx.fillText(line, cardX + 130, ly + verseFontSize);
      });

      const lastVY = vStartY + lines.length * lineH;

      // Dynamic Reference Badge Placement
      const refY = lastVY + 14;
      const refTxt = document.getElementById('inpRef').value.toUpperCase();
      ctx.font = '700 18px "Plus Jakarta Sans", sans-serif';
      const refMetrics = ctx.measureText(refTxt);
      const refW = refMetrics.width + 36;

      ctx.fillStyle = p.badgeBg;
      ctx.strokeStyle = p.gold;
      roundRect(ctx, cardX + 130, refY, refW, 36, 10, true, true, 1);
      ctx.fillStyle = p.badgeText;
      ctx.textAlign = 'center';
      ctx.fillText(refTxt, cardX + 130 + refW / 2, refY + 23);
      ctx.textAlign = 'left';

      // Dynamic Inner Divider Line
      const dividerY = refY + 46;
      ctx.strokeStyle = p.cardInner;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(cardX + 40, dividerY);
      ctx.lineTo(cardX + cardW - 40, dividerY);
      ctx.stroke();

      // Dynamic Lower Section (Illustration + Theme)
      const lowerY = dividerY + 16;
      const availLowerH = cardY + cardH - lowerY - 18;
      const imgX = cardX + 40, imgW = 380, imgH = Math.max(180, availLowerH);

      if (currentImage.complete && currentImage.naturalWidth > 0) {
        ctx.save();
        ctx.beginPath();
        roundRect(ctx, imgX, lowerY, imgW, imgH, 20, false, false);
        ctx.clip();
        ctx.drawImage(currentImage, imgX, lowerY, imgW, imgH);
        ctx.restore();

        ctx.strokeStyle = p.gold;
        roundRect(ctx, imgX - 2, lowerY - 2, imgW + 4, imgH + 4, 22, false, true, 2);
      }

      // Right Theme text
      const textX = cardX + 450;
      ctx.textAlign = 'left';
      ctx.font = '700 18px "Plus Jakarta Sans", sans-serif';
      ctx.fillStyle = p.gold;
      ctx.fillText("THÈME SPIRITUEL", textX, lowerY + 24);

      const themeTitle = document.getElementById('inpThemeTitle').value;
      ctx.font = 'italic 700 29px "Playfair Display", Georgia, serif';
      ctx.fillStyle = p.verseColor;
      ctx.fillText(themeTitle, textX, lowerY + 58);

      const themeSnippet = document.getElementById('inpThemeSnippet').value;
      ctx.font = 'italic 400 21px "Lora", Georgia, serif';
      ctx.fillStyle = p.snippetColor;
      
      const snipLines = wrapCanvasLines(ctx, themeSnippet, cardW - 480);
      snipLines.slice(0, 4).forEach((sl, idx) => {
        ctx.fillText(sl, textX, lowerY + 98 + idx * 28);
      });

      // 4. Question du Jour Card
      const qX = 56, qY = 755, qW = W - 112, qH = 230;
      ctx.fillStyle = p.qBg;
      ctx.strokeStyle = p.gold;
      roundRect(ctx, qX, qY, qW, qH, 24, true, true, 2);

      const tagTxt = "✦  QUESTION DU JOUR  ✦";
      ctx.font = '700 18px "Plus Jakarta Sans", sans-serif';
      const tagMetrics = ctx.measureText(tagTxt);
      const tagW = tagMetrics.width + 48;
      ctx.fillStyle = p.qTagBg;
      ctx.strokeStyle = p.gold;
      roundRect(ctx, qX + 40, qY - 18, tagW, 36, 12, true, true, 1.5);

      ctx.fillStyle = p.qTagText;
      ctx.textAlign = 'center';
      ctx.fillText(tagTxt, qX + 40 + tagW / 2, qY + 6);

      // Question Text
      const qText = document.getElementById('inpQuestion').value;
      ctx.font = 'italic 500 29px "Lora", Georgia, serif';
      ctx.fillStyle = p.qText;
      ctx.textAlign = 'left';
      const qLines = wrapCanvasLines(ctx, qText, qW - 90);
      qLines.slice(0, 3).forEach((ql, idx) => {
        ctx.fillText(ql, qX + 45, qY + 54 + idx * 40);
      });

      // 5. Parochial Footer
      ctx.textAlign = 'center';
      ctx.font = '500 18px "Plus Jakarta Sans", sans-serif';
      ctx.fillStyle = '#64748b';
      ctx.fillText("Paroisse Saint Michel de Houéto  •  Aumônerie de l'Enfance Missionnaire  •  Cotonou", W / 2, 1024);
    }

    // Initialisation
    window.addEventListener('DOMContentLoaded', () => {
      currentImage.src = currentImageSrc;
      currentImage.onload = () => {
        if (document.getElementById('posterCanvas').style.display !== 'none') {
          renderPoster();
        }
      };

      // Initialiser à la date du jour et vérifier si l'affiche existe déjà
      setToday();

      // Fonts ready check
      document.fonts.ready.then(() => {
        if (document.getElementById('posterCanvas').style.display !== 'none') {
          renderPoster();
        }
      });
    });
