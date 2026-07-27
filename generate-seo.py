#!/usr/bin/env python3
import os
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Configuration
# Change this domain variable to your target public domain (e.g., https://www.marinaserenella.it)
BASE_DOMAIN = "https://www.marinaserenella.it"

LANGUAGES = {
    "it": "",
    "en": "en",
    "de": "de",
    "fr": "fr"
}

PAGES = [
    "index.html",
    "cantiere.html",
    "contatti.html",
    "galleria.html",
    "meccanica-nautica.html",
    "posti-barca.html",
    "rimessaggio.html",
    "servizi.html",
    "verniciatura.html",
    "privacy-policy.html",
    "cookie-policy.html"
]

def clean_url_path(lang, page):
    folder = LANGUAGES[lang]
    if page == "index.html":
        return f"{folder}/" if folder else ""
    else:
        return f"{folder}/{page}" if folder else page

def main():
    print(f"Starting SEO & Security optimization process with BASE_DOMAIN={BASE_DOMAIN}...")
    
    # 1. Update HTML files with canonical, hreflang, Open Graph, and Netlify Forms
    for page in PAGES:
        for lang, folder in LANGUAGES.items():
            file_path = os.path.join(folder, page) if folder else page
            if not os.path.exists(file_path):
                print(f"Warning: File {file_path} not found. Skipping.")
                continue
                
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # --- META TAGS CLEANUP ---
            # Remove any existing canonical, alternate, og:*, and twitter:* tags
            content = re.sub(r'\s*<link rel="canonical"[^>]*>', '', content)
            content = re.sub(r'\s*<link rel="alternate"\s+hreflang=[^>]*>', '', content)
            content = re.sub(r'\s*<meta property="og:[^>]*>', '', content)
            content = re.sub(r'\s*<meta name="twitter:[^>]*>', '', content)
            
            # --- EXTRACT TITLE AND DESCRIPTION ---
            title_match = re.search(r'<title>(.*?)</title>', content)
            title = title_match.group(1) if title_match else "Marina Serenella"
            
            desc_match = re.search(r'<meta name="description" content="(.*?)">', content)
            description = desc_match.group(1) if desc_match else ""
            
            # --- CONSTRUCT NEW HEAD TAGS ---
            canonical_path = clean_url_path(lang, page)
            canonical_url = f"{BASE_DOMAIN}/{canonical_path}"
            
            new_tags = f'\n  <link rel="canonical" href="{canonical_url}">'
            
            # Add hreflangs
            for alt_lang, alt_folder in LANGUAGES.items():
                alt_path = clean_url_path(alt_lang, page)
                alt_url = f"{BASE_DOMAIN}/{alt_path}"
                new_tags += f'\n  <link rel="alternate" hreflang="{alt_lang}" href="{alt_url}">'
            
            # Add x-default
            it_path = clean_url_path("it", page)
            x_default_url = f"{BASE_DOMAIN}/{it_path}"
            new_tags += f'\n  <link rel="alternate" hreflang="x-default" href="{x_default_url}">'
            
            # Add Open Graph Tags
            new_tags += f'\n  <meta property="og:title" content="{title}">'
            if description:
                new_tags += f'\n  <meta property="og:description" content="{description}">'
            new_tags += f'\n  <meta property="og:type" content="website">'
            new_tags += f'\n  <meta property="og:url" content="{canonical_url}">'
            new_tags += f'\n  <meta property="og:image" content="https://www.marinaserenella.it/site/assets/files/1906/topview.png">'
            
            # Add Twitter Card Tags
            new_tags += f'\n  <meta name="twitter:card" content="summary_large_image">'
            new_tags += f'\n  <meta name="twitter:title" content="{title}">'
            if description:
                new_tags += f'\n  <meta name="twitter:description" content="{description}">'
            
            # Insert tags before closing </head>
            if "</head>" in content:
                content = content.replace("</head>", f"{new_tags}\n</head>", 1)
            else:
                print(f"Warning: </head> tag not found in {file_path}")
            
            # --- FORM AND SECURITY FIXES (Only in contatti.html) ---
            if page == "contatti.html":
                # Clean up any leftover required words/attributes from prior runs to keep it clean
                content = content.replace(" required", "")
                content = content.replace("> required", ">")
                
                # Netlify Forms Setup:
                form_name = f"contact-{lang}"
                
                # Replace form tag with Netlify attributes
                # Clean existing Netlify attributes if present
                content = re.sub(
                    r'<form class="form-grid"[^>]*>',
                    f'<form class="form-grid" name="{form_name}" method="POST" data-netlify="true" data-netlify-honeypot="bot-field">',
                    content
                )
                
                # Clean up any previously injected Netlify hidden/honeypot inputs to avoid duplicates
                content = re.sub(r'\s*<input type="hidden" name="form-name"[^>]*>', '', content)
                content = re.sub(r'\s*<div class="netlify-bot-container"[^>]*>.*?</div>', '', content, flags=re.DOTALL)
                
                # Insert netlify hidden form-name and honeypot bot-field immediately inside the form
                netlify_injections = f'\n        <input type="hidden" name="form-name" value="{form_name}">'
                netlify_injections += f'\n        <div class="netlify-bot-container" style="display: none;">'
                netlify_injections += f'\n          <label>Don\'t fill this out if you\'re human: <input name="bot-field" /></label>'
                netlify_injections += f'\n        </div>'
                
                # Place right after the start of <form ...>
                form_start_match = re.search(rf'<form class="form-grid" name="{form_name}" method="POST" data-netlify="true" data-netlify-honeypot="bot-field">', content)
                if form_start_match:
                    content = content.replace(form_start_match.group(0), form_start_match.group(0) + netlify_injections, 1)
                
                # Add validation (required) attributes to name, email, and privacy checkbox
                # Find and replace name input
                content = re.sub(
                    r'(<input id="nome-[a-z]+" name="nome" autocomplete="name")',
                    r'\1 required',
                    content
                )
                
                # Find and replace email input and verify type="email"
                content = re.sub(
                    r'(<input id="email-[a-z]+" name="email" type="email" autocomplete="email")',
                    r'\1 required',
                    content
                )
                # Fallback email match just in case
                content = re.sub(
                    r'(<input id="email-[a-z]+" name="email" autocomplete="email")',
                    r'\1 type="email" required',
                    content
                )
                
                # Find and replace privacy checkbox with linked Privacy Policy text
                privacy_links = {
                    "it": 'Acconsento al trattamento dei dati personali ai sensi della <a href="privacy-policy.html" target="_blank" style="color:var(--blue-700); text-decoration:underline;">Privacy Policy</a>.',
                    "en": 'I consent to the processing of personal data in accordance with the <a href="privacy-policy.html" target="_blank" style="color:var(--blue-700); text-decoration:underline;">Privacy Policy</a>.',
                    "de": 'Ich stimme der Verarbeitung personenbezogener Daten gemäß der <a href="privacy-policy.html" target="_blank" style="color:var(--blue-700); text-decoration:underline;">Datenschutzerklärung</a> zu.',
                    "fr": "J'accepte le traitement des données personnelles conformément à la <a href=\"privacy-policy.html\" target=\"_blank\" style=\"color:var(--blue-700); text-decoration:underline;\">Politique de Confidentialité</a>."
                }
                
                privacy_text = privacy_links.get(lang, privacy_links["it"])
                content = re.sub(
                    r'<div class="full"><label><input type="checkbox" name="privacy"[^>]*>.*?</label></div>',
                    f'<div class="full"><label><input type="checkbox" name="privacy" style="width:auto; min-height:auto; margin-right:.45rem;" required> {privacy_text}</label></div>',
                    content
                )
            
            # --- POLICY PAGES LAST UPDATED DATE BADGE ---
            if page in ["privacy-policy.html", "cookie-policy.html"]:
                updated_dates = {
                    "it": "Ultimo aggiornamento: 27 Luglio 2026",
                    "en": "Last updated: July 27, 2026",
                    "de": "Zuletzt aktualisiert: 27. Juli 2026",
                    "fr": "Dernière mise à jour : 27 juillet 2026"
                }
                date_str = updated_dates.get(lang, updated_dates["it"])
                content = re.sub(
                    r'<span class="eyebrow">[^<]*</span>',
                    f'<span class="eyebrow">{date_str}</span>',
                    content,
                    count=1
                )
            
            # Normalize button classes site-wide:
            # btn-dark should be btn-primary (cyan CTA) for visual consistency across all pages
            content = content.replace('class="btn btn-dark"', 'class="btn btn-primary"')
            
            # Clean up kicker inline styles to maintain stylesheet consistency
            content = content.replace('class="kicker" style="color: rgba(255,255,255,.7);"', 'class="kicker light"')
            content = content.replace('class="kicker" style="color: rgba(255, 255, 255, 0.7);"', 'class="kicker light"')
            
            # Remove redundant double .section nesting around the CTA band banner
            content = re.sub(
                r'<section class="section tight">\s*<div class="section">\s*<div class="band">',
                r'<section class="section tight">\n  <div class="band">',
                content
            )
            content = re.sub(
                r'</div>\s*</div>\s*</section>\s*<footer class="footer">',
                r'</div>\n</section>\n<footer class="footer">',
                content
            )

            # --- CLEAN UP DRAFT NOTES & DEVELOPER COMMENTS SITE-WIDE ---
            # 1. servizi.html draft card & copy
            content = re.sub(
                r'<div class="card"><h3>Correzioni applicate ai testi</h3><p>Sono stati corretti termini come [^<]*</p></div>',
                r'<div class="image-frame"><img src="https://www.darsena-serenella-venezia.com/site/assets/files/1907/02-vista-della-darsena.jpg" alt="Videosorveglianza Marina Serenella"></div>',
                content
            )
            content = re.sub(
                r'<div class="card"><h3>Text corrections applied</h3><p>[^<]*</p></div>',
                r'<div class="image-frame"><img src="https://www.darsena-serenella-venezia.com/site/assets/files/1907/02-vista-della-darsena.jpg" alt="Video surveillance Marina Serenella"></div>',
                content
            )
            content = re.sub(
                r'<div class="card"><h3>Textkorrekturen angewendet</h3><p>[^<]*</p></div>',
                r'<div class="image-frame"><img src="https://www.darsena-serenella-venezia.com/site/assets/files/1907/02-vista-della-darsena.jpg" alt="Videoüberwachung Marina Serenella"></div>',
                content
            )
            content = re.sub(
                r'<div class="card"><h3>Corrections appliquées aux textes</h3><p>[^<]*</p></div>',
                r'<div class="image-frame"><img src="https://www.darsena-serenella-venezia.com/site/assets/files/1907/02-vista-della-darsena.jpg" alt="Vidéosurveillance Marina Serenella"></div>',
                content
            )
            content = content.replace(
                "Tra i servizi indicati dalla marina è presente anche il collegamento alla videosorveglianza da casa: un elemento da valorizzare meglio sul sito, spiegando modalità di accesso e disponibilità.",
                "Tra i servizi di Marina Serenella è disponibile il sistema di videosorveglianza e controllo a distanza, per verificare lo stato della tua imbarcazione in ogni momento."
            )
            content = content.replace(
                "The marina also lists access to home video surveillance among its services: a feature to highlight better on the website, explaining access methods and availability.",
                "Marina Serenella provides round-the-clock video surveillance and remote monitoring services, allowing you to check on your boat at any time."
            )
            content = content.replace(
                "Die Marina führt auch den Zugang zur Videoüberwachung von zu Hause aus in ihren Leistungen auf: eine Funktion, die auf der Website besser hervorgehoben werden sollte, indem Zugangsmethoden und Verfügbarkeit erklärt werden.",
                "Zu den Leistungen von Marina Serenella gehört die Videoüberwachung und Fernkontrolle, mit der Sie den Status Ihres Bootes jederzeit überprüfen können."
            )
            content = content.replace(
                "La marina mentionne également l'accès à la vidéosurveillance depuis chez soi parmi ses services: un élément à mieux valoriser sur le site, en expliquant les modalités d'accès et la disponibilité.",
                "Parmi les services de Marina Serenella figure la vidéosurveillance et le contrôle à distance, vous permettant de vérifier l'état de votre bateau à tout moment."
            )

            # 2. galleria.html draft notes
            content = content.replace(
                "La galleria è stata riorganizzata con titoli corretti e immagini più leggibili. Nel sito definitivo consigliamo di aggiungere categorie e, dove possibile, foto prima/dopo.",
                "Esplora la galleria fotografica per scoprire la darsena, il cantiere nautico, gli ormeggi e le principali lavorazioni eseguite su imbarcazioni."
            )
            content = content.replace(
                "The gallery has been reorganized with correct titles and readable images. On the final website we recommend adding categories and, where possible, before/after photos.",
                "Explore our photo gallery to discover the marina, boatyard, moorings, and key repair and maintenance work."
            )
            content = content.replace(
                "Die Galerie wurde mit korrekten Titeln und besser lesbaren Bildern neu organisiert. Auf der endgültigen Website empfehlen wir das Hinzufügen von Kategorien und Vorher-Nachher-Fotos.",
                "Entdecken Sie unsere Fotogalerie, um die Darsena, die Werft, die Liegeplätze und die wichtigsten Arbeiten zu sehen."
            )
            content = content.replace(
                "La galerie a été réorganisée avec des titres corrects et des images plus lisibles. Sur le site définitif, nous conseillons d'ajouter des catégories et des photos avant/après.",
                "Explorez notre galerie photos pour découvrir la marina, le chantier naval, les amarres et les principaux travaux réalisés."
            )

            # 3. contatti.html draft notices
            content = re.sub(
                r'<p class="notice" style="margin-top:1rem;">Nel sito definitivo si può inserire qui[^<]*</p>',
                r'<p class="notice" style="margin-top:1rem;">Orari di apertura: Lunedì - Sabato: 08:00 - 18:00 | Domenica: Chiuso</p>',
                content
            )
            content = re.sub(
                r'<p class="notice" style="margin-top:1rem;">On the final website an embedded map[^<]*</p>',
                r'<p class="notice" style="margin-top:1rem;">Opening hours: Monday - Saturday: 08:00 - 18:00 | Sunday: Closed</p>',
                content
            )
            content = re.sub(
                r'<p class="notice" style="margin-top:1rem;">Auf der endgültigen Website[^<]*</p>',
                r'<p class="notice" style="margin-top:1rem;">Öffnungszeiten: Montag - Samstag: 08:00 - 18:00 | Sonntag: Geschlossen</p>',
                content
            )
            content = re.sub(
                r'<p class="notice" style="margin-top:1rem;">Sur le site définitif[^<]*</p>',
                r'<p class="notice" style="margin-top:1rem;">Horaires d\'ouverture: Lundi - Samedi: 08:00 - 18:00 | Dimanche: Fermé</p>',
                content
            )
            content = re.sub(r'<p class="notice">Nota tecnica: il form è statico[^<]*</p>', '', content)
            content = re.sub(r'<p class="notice">Technical note: the form is static[^<]*</p>', '', content)
            content = re.sub(r'<p class="notice">Technische Anmerkung: Das Formular[^<]*</p>', '', content)
            content = re.sub(r'<p class="notice">Note technique: le formulaire est static[^<]*</p>', '', content)
            content = re.sub(r'<p class="notice">Note technique: le formulaire est statique[^<]*</p>', '', content)

            # 4. Footer Columns Normalization (Ensuring both Servizi and Legale columns exist on every page)
            FOOTER_SERVIZI = {
                "it": """    <div>
      <h3>Servizi</h3>
      <ul>
        <li><a href="posti-barca.html">Posti barca</a></li>
        <li><a href="rimessaggio.html">Rimessaggio</a></li>
        <li><a href="cantiere.html">Riparazioni</a></li>
        <li><a href="verniciatura.html">Verniciatura</a></li>
        <li><a href="meccanica-nautica.html">Meccanica nautica</a></li>
      </ul>
    </div>""",
                "en": """    <div>
      <h3>Services</h3>
      <ul>
        <li><a href="posti-barca.html">Moorings</a></li>
        <li><a href="rimessaggio.html">Storage</a></li>
        <li><a href="cantiere.html">Repairs</a></li>
        <li><a href="verniciatura.html">Painting</a></li>
        <li><a href="meccanica-nautica.html">Marine mechanics</a></li>
      </ul>
    </div>""",
                "de": """    <div>
      <h3>Leistungen</h3>
      <ul>
        <li><a href="posti-barca.html">Liegeplätze</a></li>
        <li><a href="rimessaggio.html">Lagerung</a></li>
        <li><a href="cantiere.html">Reparaturen</a></li>
        <li><a href="verniciatura.html">Lackierung</a></li>
        <li><a href="meccanica-nautica.html">Schiffsmechanik</a></li>
      </ul>
    </div>""",
                "fr": """    <div>
      <h3>Services</h3>
      <ul>
        <li><a href="posti-barca.html">Amarres</a></li>
        <li><a href="rimessaggio.html">Hivernage</a></li>
        <li><a href="cantiere.html">Réparations</a></li>
        <li><a href="verniciatura.html">Peinture</a></li>
        <li><a href="meccanica-nautica.html">Mécanique navale</a></li>
      </ul>
    </div>"""
            }

            FOOTER_LEGALE = {
                "it": """    <div>
      <h3>Legale</h3>
      <ul>
        <li><a href="privacy-policy.html">Privacy Policy</a></li>
        <li><a href="cookie-policy.html">Cookie Policy</a></li>
      </ul>
    </div>""",
                "en": """    <div>
      <h3>Legal</h3>
      <ul>
        <li><a href="privacy-policy.html">Privacy Policy</a></li>
        <li><a href="cookie-policy.html">Cookie Policy</a></li>
      </ul>
    </div>""",
                "de": """    <div>
      <h3>Rechtliches</h3>
      <ul>
        <li><a href="privacy-policy.html">Datenschutz</a></li>
        <li><a href="cookie-policy.html">Cookie-Richtlinie</a></li>
      </ul>
    </div>""",
                "fr": """    <div>
      <h3>Mentions légales</h3>
      <ul>
        <li><a href="privacy-policy.html">Politique de Confidentialité</a></li>
        <li><a href="cookie-policy.html">Politique de Cookies</a></li>
      </ul>
    </div>"""
            }

            # Ensure Servizi column is in footer
            servizi_keywords = ["<h3>Servizi</h3>", "<h3>Services</h3>", "<h3>Leistungen</h3>"]
            if not any(k in content for k in servizi_keywords):
                servizi_block = FOOTER_SERVIZI[lang]
                if re.search(r'<div>\s*<h3>(?:Legale|Legal|Rechtliches|Mentions légales)</h3>', content):
                    content = re.sub(
                        r'(\s*<div>\s*<h3>(?:Legale|Legal|Rechtliches|Mentions légales)</h3>)',
                        f"\n{servizi_block}\n\\1",
                        content,
                        count=1
                    )
                else:
                    content = content.replace("  </div>\n</footer>", f"{servizi_block}\n  </div>\n</footer>", 1)

            # Ensure Legale column is in footer
            if "privacy-policy.html" not in content and "cookie-policy.html" not in content:
                legale_block = FOOTER_LEGALE[lang]
                content = content.replace("  </div>\n</footer>", f"{legale_block}\n  </div>\n</footer>", 1)

            # --- CARD SVG ICONS UPGRADE ---
            # 1. Homepage / Main service cards (01 to 06)
            content = content.replace(
                '<div class="icon">01</div>',
                '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="3"/><line x1="12" y1="8" x2="12" y2="21"/><line x1="5" y1="12" x2="19" y2="12"/><path d="M5 12a7 7 0 0 0 14 0"/></svg></div>'
            )
            content = content.replace(
                '<div class="icon">02</div>',
                '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18"/><path d="M5 21V7l7-4 7 4v14"/><path d="M9 21v-8a3 3 0 0 1 6 0v8"/></svg></div>'
            )
            content = content.replace(
                '<div class="icon">03</div>',
                '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg></div>'
            )
            content = content.replace(
                '<div class="icon">04</div>',
                '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 11h20v3H2z"/><path d="M19 14v1a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-1"/><path d="M12 17v5"/><circle cx="12" cy="7" r="4"/></svg></div>'
            )
            content = content.replace(
                '<div class="icon">05</div>',
                '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg></div>'
            )
            content = content.replace(
                '<div class="icon">06</div>',
                '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg></div>'
            )

            # 2. Servizi page cards (B, M, S / Q, M, S)
            content = content.replace(
                '<div class="icon">B</div>',
                '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></div>'
            )
            content = content.replace(
                '<div class="icon">Q</div>',
                '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></div>'
            )
            content = content.replace(
                '<div class="icon">M</div>',
                '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg></div>'
            )
            content = content.replace(
                '<div class="icon">S</div>',
                '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>'
            )

            # 3. Posti-barca cards (60, 25, 4.5, 14t)
            content = content.replace(
                '<div class="icon">60</div>',
                '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="3"/><line x1="12" y1="8" x2="12" y2="21"/><line x1="5" y1="12" x2="19" y2="12"/><path d="M5 12a7 7 0 0 0 14 0"/></svg></div>'
            )
            content = content.replace(
                '<div class="icon">25</div>',
                '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.3 15.3a2.4 2.4 0 0 1 0 3.4l-2.6 2.6a2.4 2.4 0 0 1-3.4 0L2.7 8.7a2.4 2.4 0 0 1 0-3.4l2.6-2.6a2.4 2.4 0 0 1 3.4 0z"/><line x1="14.5" y1="12.5" x2="16.5" y2="14.5"/><line x1="11.5" y1="9.5" x2="13.5" y2="11.5"/><line x1="8.5" y1="6.5" x2="10.5" y2="8.5"/></svg></div>'
            )
            content = content.replace(
                '<div class="icon">4.5</div>',
                '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/></svg></div>'
            )
            content = content.replace(
                '<div class="icon">14t</div>',
                '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg></div>'
            )

            # 4. cantiere.html, meccanica-nautica.html, and German servi.html card icons
            tools_svg = '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg></div>'
            wood_svg = '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg></div>'
            fiberglass_svg = '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg></div>'
            water_svg = '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg></div>'
            prep_svg = '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg></div>'
            shield_svg = '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>'
            lifebuoy_svg = '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><line x1="4.93" y1="4.93" x2="9.17" y2="9.17"/><line x1="14.83" y1="14.83" x2="19.07" y2="19.07"/><line x1="14.83" y1="9.17" x2="19.07" y2="4.93"/><line x1="4.93" y1="19.07" x2="9.17" y2="14.83"/></svg></div>'
            calendar_svg = '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg></div>'

            if page == "cantiere.html":
                content = content.replace('<div class="icon">A</div>', tools_svg)
                content = content.replace('<div class="icon">L</div>', wood_svg)
                content = content.replace('<div class="icon">W</div>', wood_svg)
                content = content.replace('<div class="icon">H</div>', wood_svg)
                content = content.replace('<div class="icon">V</div>', fiberglass_svg)
                content = content.replace('<div class="icon">F</div>', fiberglass_svg)
                content = content.replace('<div class="icon">G</div>', fiberglass_svg)
                content = content.replace('<div class="icon">C</div>', water_svg)
                content = content.replace('<div class="icon">P</div>', prep_svg)
                content = content.replace('<div class="icon">R</div>', tools_svg)

            if page == "meccanica-nautica.html":
                content = content.replace('<div class="icon">1</div>', shield_svg)
                content = content.replace('<div class="icon">2</div>', lifebuoy_svg)
                content = content.replace('<div class="icon">3</div>', calendar_svg)
            
            if page == "servizi.html":
                content = content.replace('<div class="icon">K</div>', '<div class="icon" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></div>')

            # 5. JS Email Obfuscation for Anti-Spam Protection
            # Replace plain text mailto links with JS obfuscated tags
            content = re.sub(
                r'<a href="mailto:info@marinaserenella\.it">info@marinaserenella\.it</a>',
                r'<a href="javascript:void(0)" class="js-email" data-u="info" data-d="marinaserenella.it">info [at] marinaserenella.it</a>',
                content
            )
            content = re.sub(
                r'<a href="mailto:info@marinaserenella\.it">',
                r'<a href="javascript:void(0)" class="js-email" data-u="info" data-d="marinaserenella.it">',
                content
            )

            # 6. Inject main.js script tag before </body>
            js_path = "../assets/js/main.js" if lang != "it" else "assets/js/main.js"
            js_script_tag = f'<script src="{js_path}" defer></script>'
            if js_script_tag not in content and "</body>" in content:
                content = content.replace("</body>", f"{js_script_tag}\n</body>", 1)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  [Updated] {file_path}")

    # 2. Generate multilingual sitemap.xml
    print("Generating sitemap.xml...")
    ET.register_namespace("xhtml", "http://www.w3.org/1999/xhtml")
    urlset = ET.Element("urlset", {
        "xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"
    })
    
    for page in PAGES:
        for lang, folder in LANGUAGES.items():
            file_path = os.path.join(folder, page) if folder else page
            if not os.path.exists(file_path):
                continue
                
            url_el = ET.SubElement(urlset, "url")
            
            loc_path = clean_url_path(lang, page)
            loc_url = f"{BASE_DOMAIN}/{loc_path}"
            
            loc_el = ET.SubElement(url_el, "loc")
            loc_el.text = loc_url
            
            # Add hreflangs for all languages
            for alt_lang, alt_folder in LANGUAGES.items():
                alt_path = clean_url_path(alt_lang, page)
                alt_url = f"{BASE_DOMAIN}/{alt_path}"
                ET.SubElement(url_el, "{http://www.w3.org/1999/xhtml}link", {
                    "rel": "alternate",
                    "hreflang": alt_lang,
                    "href": alt_url
                })
            
            # Add x-default hreflang
            it_path = clean_url_path("it", page)
            x_default_url = f"{BASE_DOMAIN}/{it_path}"
            ET.SubElement(url_el, "{http://www.w3.org/1999/xhtml}link", {
                "rel": "alternate",
                "hreflang": "x-default",
                "href": x_default_url
            })
            
    # Pretty-print xml
    xml_str = ET.tostring(urlset, encoding="utf-8")
    parsed_xml = minidom.parseString(xml_str)
    pretty_xml = parsed_xml.toprettyxml(indent="  ")
    
    # Fix minidom adding unnecessary empty lines
    pretty_xml = "\n".join([line for line in pretty_xml.splitlines() if line.strip()])
    
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(pretty_xml)
    print("  [Created] sitemap.xml")

    # 3. Generate robots.txt
    print("Generating robots.txt...")
    robots_content = f"""# https://www.robotstxt.org/robotstxt.html
User-agent: *
Allow: /

Sitemap: {BASE_DOMAIN}/sitemap.xml
"""
    with open("robots.txt", "w", encoding="utf-8") as f:
        f.write(robots_content)
    print("  [Created] robots.txt")
    print("SEO & Security generation completed successfully!")

if __name__ == "__main__":
    main()
