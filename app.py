import streamlit as st
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
from rembg import remove
import io
import base64 # Novi alat za ugradnju ikone direktno u kod
import os
from streamlit_cropper import st_cropper 
# components.html JavaScript hack smo maknuli jer na mobitelu rijetko radi,
# rješavamo to na sigurniji način.

# --- MAGIČNI KOD ZA UGRADNJU IKONE DIREKTNO U KOD (da se učita na mobitelu) ---
def get_base64_of_image(filename):
    try:
        with open(filename, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except:
        return None # Ako nema ikone, ne radi ništa

# Provjera i ugradnja tvoje .png ikone
image_base64 = get_base64_of_image("ikona.png") # Obavezno stavi ikona.png na GitHub

# Postavljanje ikone za sam preglednik (page icon)
# Koristimo Python verziju jer je sigurnija.
if image_base64:
    page_icon_final = Image.open("ikona.png") # Pokušavamo direktno učitati sliku
else:
    page_icon_final = "🎨" # Ako nema slike, fallback na emoji

# 1. POSTAVKE STRANICE 
st.set_page_config(
    page_title="TINČEK DIZAJN PRO EDITOR",
    page_icon=page_icon_final, 
    layout="centered" 
)

# 2. CSS STILIZACIJA (Proširena paleta za nove opcije)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&display=swap');

    header, [data-testid="stHeader"], .stAppHeader { display: none !important; height: 0px !important; }
    [data-testid="stToolbar"], [data-testid="stDecoration"], .stDeployButton, #MainMenu, footer { display: none !important; }
    .stApp > div:first-child { padding-top: 0px !important; }

    .stApp { background-color: #050505 !important; }
    .block-container { max-width: 700px !important; padding-top: 2rem !important; }
    
    html body div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #121212 !important; 
        border: none !important; 
        border-radius: 15px !important;
        box-shadow: 0 10px 40px rgba(138, 43, 226, 0.15) !important; 
        padding: 30px 20px !important;
    }

    .naslov-kontejner {
        display: flex; align-items: center; justify-content: center; gap: 20px; 
        background: linear-gradient(180deg, #2a0a4a 0%, #121212 100%);
        margin: -30px -20px 30px -20px; padding: 40px 20px;
        border-bottom: 1px solid rgba(138, 43, 226, 0.3); 
    }
    .naslov-ikona { font-size: 5.5rem; text-shadow: 0 0 25px rgba(138, 43, 226, 0.7); }
    .naslov-tekst {
        color: #ffffff !important; font-family: 'Orbitron', sans-serif !important;
        font-weight: 900; letter-spacing: 3px;
        text-shadow: 0 0 10px #8a2be2, 0 0 20px #8a2be2, 0 0 40px #d896ff !important;
        font-size: 2.6rem !important; line-height: 1.2 !important; margin: 0;
    }

    /* GUMBI I PADAJUĆI IZBORNICI - POJAČANI LJUBIČASTI DŽAJN */
    div[data-testid="stButton"] button {
        width: 100% !important; border-radius: 8px !important; height: 3.5em !important;
        background-color: #1a0b2e !important; color: #ffffff !important; 
        border: 1px solid #8a2be2 !important; transition: all 0.3s ease-in-out !important;
        font-weight: 600 !important; white-space: nowrap !important; margin-top: 0 !important;
    }
    div[data-testid="stButton"] button:hover {
        border-color: #d896ff !important; background-color: #3b1361 !important;
        color: #ffffff !important; box-shadow: 0 0 15px rgba(138, 43, 226, 0.8) !important; 
    }

    div[data-baseweb="select"] > div {
        background-color: #1a0b2e !important; border: 1px solid #8a2be2 !important; 
        border-radius: 8px !important; height: 3.5em !important; transition: all 0.3s ease-in-out !important;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: #d896ff !important; box-shadow: 0 0 15px rgba(138, 43, 226, 0.8) !important;
    }
    div[data-baseweb="select"] > div > div { color: #ffffff !important; font-weight: 600 !important; }
    div[data-baseweb="popover"] div[role="listbox"] { background-color: #1a0b2e !important; border: 2px solid #8a2be2 !important; border-radius: 8px; }
    li[role="option"] { color: #ffffff !important; font-weight: 600 !important; background-color: #1a0b2e !important; }
    li[role="option"]:hover, li[role="option"][aria-selected="true"] { background-color: #8a2be2 !important; color: #ffffff !important; }

    /* NOVO: STILIZACIJA ZA UNOS TEKSTA I BROJEVA DA PAŠE UZ TAMNU TEMU */
    div[data-baseweb="input"] {
        background-color: #1a0b2e !important; border-radius: 8px !important; border: 1px solid #8a2be2 !important;
    }
    div[data-baseweb="input"] input { color: #ffffff !important; font-weight: bold !important; }
    label { color: #d896ff !important; font-weight: bold !important; }

    .stFileUploader { border: 2px dashed #8a2be2 !important; border-radius: 10px; }
    
    .veliki-pozdrav {
        color: #d896ff !important; font-size: 1.2rem !important;
        font-weight: 700 !important; text-align: center; margin-top: 40px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIJALIZACIJA MEMORIJE ---
if 'uredjena' not in st.session_state: st.session_state.uredjena = None
if 'original' not in st.session_state: st.session_state.original = None
if 'aktivni_alat' not in st.session_state: st.session_state.aktivni_alat = None
if 'zadnji_ai_mod' not in st.session_state: st.session_state.zadnji_ai_mod = "AI: Standardno"

with st.container(border=True):
    # --- NOVI HAK NASLOVA - Učitavamo tvoju ikonu direktno u HTML ---
    if image_base64:
        # Ugrađujemo tvoju .png ikonu direktno u kod (na vrhu stranice u HTML)
        logo_html = f'<img src="data:image/png;base64,{image_base64}" alt="Logo" class="naslov-ikona">'
    else:
        # Fallback na emoji ako nema ikone
        logo_html = '<div class="naslov-ikona">🎨</div>'
        
    st.markdown(f'<div class="naslov-kontejner">{logo_html}<div class="naslov-tekst">TINČEK DIZAJN<br>PRO EDITOR</div></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 2rem; color: #ffffff; font-family: Orbitron; text-align: center; margin-bottom: 25px; text-shadow: 0 0 15px #8a2be2;">🛠️ Alati za obradu</div>', unsafe_allow_html=True)

    # Alatna traka - dodali smo Tekst i Veličinu
    c_sel, c1, c2, c3, c4, c5, c6 = st.columns([1.8, 1, 1, 1, 1, 1, 1], gap="small")
    
    with c_sel:
        bg_level = st.selectbox("AI", ["AI: Standardno", "AI: Precizno", "AI: Snažno"], label_visibility="collapsed")
        if bg_level != st.session_state.zadnji_ai_mod and bg_level != "AI: Standardno":
            if st.session_state.uredjena:
                with st.spinner("AI odmah odrađuje radnju..."):
                    try:
                        if "Precizno" in bg_level:
                            st.session_state.uredjena = remove(st.session_state.uredjena, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
                        else:
                            st.session_state.uredjena = remove(st.session_state.uredjena, alpha_matting=True, alpha_matting_foreground_threshold=250, alpha_matting_background_threshold=20, alpha_matting_erode_size=15)
                        st.session_state.zadnji_ai_mod = bg_level
                        st.toast("AI uspješno uklonio pozadinu!")
                    except:
                        st.error("AI trenutno ne može obraditi ovu sliku.")
            else:
                st.warning("⚠️ Prvo učitaj sliku!")

    with c1:
        if st.button("✂️ Izreži"):
            st.session_state.aktivni_alat = "izrezivanje" if st.session_state.aktivni_alat != "izrezivanje" else None
    with c2:
        if st.button("📏 Vel"):
            st.session_state.aktivni_alat = "velicina" if st.session_state.aktivni_alat != "velicina" else None
    with c3:
        if st.button("✍️ Tekst"):
            st.session_state.aktivni_alat = "tekst" if st.session_state.aktivni_alat != "tekst" else None
    with c4:
        btn_rotate = st.button("🔄 Rotiraj")
    with c5:
        btn_cmyk = st.button("🧪 CMYK")
    with c6:
        btn_reset = st.button("↩️ Reset")

    if btn_rotate and st.session_state.uredjena:
        st.session_state.uredjena = st.session_state.uredjena.rotate(-90, expand=True)
    if btn_cmyk and st.session_state.uredjena:
        st.session_state.uredjena = st.session_state.uredjena.convert("RGB").convert("CMYK").convert("RGB")
    if btn_reset:
        st.session_state.uredjena = st.session_state.original
        st.session_state.zadnji_ai_mod = "AI: Standardno"
        st.session_state.aktivni_alat = None
        st.rerun()

    st.markdown("---")
    učitana_datoteka = st.file_uploader("📥 Odaberi sliku za obradu", type=["jpg", "png", "jpeg", "webp"])

    if učitana_datoteka:
        if st.session_state.original is None or učitana_datoteka.name != st.session_state.get('last_name', ''):
            img = Image.open(učitana_datoteka).convert("RGBA")
            st.session_state.original = img
            st.session_state.uredjena = img
            st.session_state.last_name = učitana_datoteka.name

        # === 1. ALAT ZA IZREZIVANJE ===
        if st.session_state.aktivni_alat == "izrezivanje":
            st.info("Podesi okvir za izrezivanje na slici ispod i klikni 'POTVRDI REZ'")
            img_crop = st_cropper(st.session_state.uredjena, realtime_update=True, box_color='#8a2be2', aspect_ratio=None)
            if st.button("✅ POTVRDI REZ", use_container_width=True):
                st.session_state.uredjena = img_crop
                st.session_state.aktivni_alat = None
                st.rerun()
                
        # === 2. ALAT ZA VELIČINU ===
        elif st.session_state.aktivni_alat == "velicina":
            st.info("Unesi novu širinu i visinu u pikselima:")
            col_w, col_h = st.columns(2)
            with col_w: nova_sirina = st.number_input("Širina", value=st.session_state.uredjena.width, min_value=1)
            with col_h: nova_visina = st.number_input("Visina", value=st.session_state.uredjena.height, min_value=1)
            
            if st.button("✅ PRIMIJENI VELIČINU", use_container_width=True):
                st.session_state.uredjena = st.session_state.uredjena.resize((nova_sirina, nova_visina), Image.Resampling.LANCZOS)
                st.session_state.aktivni_alat = None
                st.rerun()

        # === 3. ALAT ZA TEKST ===
        elif st.session_state.aktivni_alat == "tekst":
            st.info("Unesi tekst koji želiš dodati na sliku:")
            tekst_unos = st.text_input("Tekst", value="Tinček")
            col_t1, col_t2 = st.columns(2)
            with col_t1: velicina_fonta = st.number_input("Veličina fonta", value=40, min_value=10)
            with col_t2: boja_teksta = st.color_picker("Boja", "#FF0000")
            
            if st.button("✅ DODAJ TEKST NA SLIKU", use_container_width=True):
                crtanje = ImageDraw.Draw(st.session_state.uredjena)
                try:
                    font = ImageFont.truetype("arial.ttf", velicina_fonta)
                except:
                    font = ImageFont.load_default() # Sigurnosna mjera ako server nema font
                crtanje.text((20, 20), tekst_unos, font=font, fill=boja_teksta)
                st.session_state.aktivni_alat = None
                st.rerun()
                
        # === GLAVNI PRIKAZ SLIKE ===
        else:
            st.markdown("### 🎨 Boje")
            sat = st.slider("Zasićenost", 0.0, 3.0, 1.0, 0.1)
            bright = st.slider("Svjetlina", 0.5, 2.0, 1.0, 0.1)

            img_final = st.session_state.uredjena
            if sat != 1.0: img_final = ImageEnhance.Color(img_final).enhance(sat)
            if bright != 1.0: img_final = ImageEnhance.Brightness(img_final).enhance(bright)

            st.image(img_final, caption="Pregled obrade", use_container_width=True)

            st.markdown("---")
            col_f, col_b = st.columns([1, 1])
            with col_f:
                fmt = st.selectbox("Format", ["PNG", "JPG", "WEBP", "ICO"], label_visibility="collapsed")
            with col_b:
                buf = io.BytesIO()
                mime_type = f"image/{fmt.lower()}"
                ime_fajla = f"tincek_dizajn.{fmt.lower()}"
                
                if fmt == "ICO":
                    img_export = img_final.copy()
                    img_export.thumbnail((256, 256)) # Automatski stisne sliku za ikonu!
                    img_export.save(buf, format="ICO")
                    mime_type = "image/x-icon"
                elif fmt == "JPG": 
                    img_final = img_final.convert("RGB")
                    img_final.save(buf, format="JPEG")
                else:
                    img_final.save(buf, format=fmt)
                    
                st.download_button(label=f"⬇️ SPREMI KAO {fmt}", data=buf.getvalue(), file_name=ime_fajla, mime=mime_type)
    else:
        st.markdown('<p class="veliki-pozdrav">👋 Pozdrav! Učitaj sliku ispod kako bi se otvorila vrata alata na vrhu.</p>', unsafe_allow_html=True)    [data-testid="stToolbar"], [data-testid="stDecoration"], .stDeployButton, #MainMenu, footer { display: none !important; }
    .stApp > div:first-child { padding-top: 0px !important; }

    .stApp { background-color: #050505 !important; }
    .block-container { max-width: 700px !important; padding-top: 2rem !important; }
    
    html body div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #121212 !important; 
        border: none !important; 
        border-radius: 15px !important;
        box-shadow: 0 10px 40px rgba(138, 43, 226, 0.15) !important; 
        padding: 30px 20px !important;
    }

    .naslov-kontejner {
        display: flex; align-items: center; justify-content: center; gap: 20px; 
        background: linear-gradient(180deg, #2a0a4a 0%, #121212 100%);
        margin: -30px -20px 30px -20px; padding: 40px 20px;
        border-bottom: 1px solid rgba(138, 43, 226, 0.3); 
    }
    .naslov-ikona { font-size: 5.5rem; text-shadow: 0 0 25px rgba(138, 43, 226, 0.7); }
    .naslov-tekst {
        color: #ffffff !important; font-family: 'Orbitron', sans-serif !important;
        font-weight: 900; letter-spacing: 3px;
        text-shadow: 0 0 10px #8a2be2, 0 0 20px #8a2be2, 0 0 40px #d896ff !important;
        font-size: 2.6rem !important; line-height: 1.2 !important; margin: 0;
    }

    /* GUMBI I PADAJUĆI IZBORNICI */
    div[data-testid="stButton"] button {
        width: 100% !important; border-radius: 8px !important; height: 3.5em !important;
        background-color: #1a0b2e !important; color: #ffffff !important; 
        border: 1px solid #8a2be2 !important; transition: all 0.3s ease-in-out !important;
        font-weight: 600 !important; white-space: nowrap !important; margin-top: 0 !important;
    }
    div[data-testid="stButton"] button:hover {
        border-color: #d896ff !important; background-color: #3b1361 !important;
        color: #ffffff !important; box-shadow: 0 0 15px rgba(138, 43, 226, 0.8) !important; 
    }

    div[data-baseweb="select"] > div {
        background-color: #1a0b2e !important; border: 1px solid #8a2be2 !important; 
        border-radius: 8px !important; height: 3.5em !important; transition: all 0.3s ease-in-out !important;
    }
    div[data-baseweb="select"] > div > div { color: #ffffff !important; font-weight: 600 !important; }
    div[data-baseweb="popover"] div[role="listbox"] { background-color: #1a0b2e !important; border: 2px solid #8a2be2 !important; border-radius: 8px; }
    li[role="option"] { color: #ffffff !important; font-weight: 600 !important; background-color: #1a0b2e !important; }
    li[role="option"]:hover, li[role="option"][aria-selected="true"] { background-color: #8a2be2 !important; color: #ffffff !important; }

    /* NOVO: STILIZACIJA ZA UNOS TEKSTA I BROJEVA DA PAŠE UZ TAMNU TEMU */
    div[data-baseweb="input"] {
        background-color: #1a0b2e !important; border-radius: 8px !important; border: 1px solid #8a2be2 !important;
    }
    div[data-baseweb="input"] input { color: #ffffff !important; font-weight: bold !important; }
    label { color: #d896ff !important; font-weight: bold !important; }

    .stFileUploader { border: 2px dashed #8a2be2 !important; border-radius: 10px; }
    .veliki-pozdrav { color: #d896ff !important; font-size: 1.2rem !important; font-weight: 700 !important; text-align: center; margin-top: 40px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIJALIZACIJA MEMORIJE ---
if 'uredjena' not in st.session_state: st.session_state.uredjena = None
if 'original' not in st.session_state: st.session_state.original = None
if 'aktivni_alat' not in st.session_state: st.session_state.aktivni_alat = None
if 'zadnji_ai_mod' not in st.session_state: st.session_state.zadnji_ai_mod = "AI: Standardno"

with st.container(border=True):
    st.markdown("""<div class="naslov-kontejner"><div class="naslov-ikona">🎨</div><div class="naslov-tekst">TINČEK DIZAJN<br>PRO EDITOR</div></div>""", unsafe_allow_html=True)
    st.markdown('<div style="font-size: 2rem; color: #ffffff; font-family: Orbitron; text-align: center; margin-bottom: 25px; text-shadow: 0 0 15px #8a2be2;">🛠️ Alati za obradu</div>', unsafe_allow_html=True)

    # Alatna traka - dodali smo Tekst i Veličinu
    c_sel, c1, c2, c3, c4, c5, c6 = st.columns([1.8, 1, 1, 1, 1, 1, 1], gap="small")
    
    with c_sel:
        bg_level = st.selectbox("AI", ["AI: Standardno", "AI: Precizno", "AI: Snažno"], label_visibility="collapsed")
        if bg_level != st.session_state.zadnji_ai_mod and bg_level != "AI: Standardno":
            if st.session_state.uredjena:
                with st.spinner("AI odmah odrađuje radnju..."):
                    try:
                        if "Precizno" in bg_level:
                            st.session_state.uredjena = remove(st.session_state.uredjena, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
                        else:
                            st.session_state.uredjena = remove(st.session_state.uredjena, alpha_matting=True, alpha_matting_foreground_threshold=250, alpha_matting_background_threshold=20, alpha_matting_erode_size=15)
                        st.session_state.zadnji_ai_mod = bg_level
                        st.toast("AI uspješno uklonio pozadinu!")
                    except:
                        st.error("AI trenutno ne može obraditi ovu sliku.")
            else:
                st.warning("⚠️ Prvo učitaj sliku!")

    with c1:
        if st.button("✂️ Izreži"):
            st.session_state.aktivni_alat = "izrezivanje" if st.session_state.aktivni_alat != "izrezivanje" else None
    with c2:
        if st.button("📏 Vel"):
            st.session_state.aktivni_alat = "velicina" if st.session_state.aktivni_alat != "velicina" else None
    with c3:
        if st.button("✍️ Tekst"):
            st.session_state.aktivni_alat = "tekst" if st.session_state.aktivni_alat != "tekst" else None
    with c4:
        btn_rotate = st.button("🔄 Rotiraj")
    with c5:
        btn_cmyk = st.button("🧪 CMYK")
    with c6:
        btn_reset = st.button("↩️ Reset")

    if btn_rotate and st.session_state.uredjena:
        st.session_state.uredjena = st.session_state.uredjena.rotate(-90, expand=True)
    if btn_cmyk and st.session_state.uredjena:
        st.session_state.uredjena = st.session_state.uredjena.convert("RGB").convert("CMYK").convert("RGB")
    if btn_reset:
        st.session_state.uredjena = st.session_state.original
        st.session_state.zadnji_ai_mod = "AI: Standardno"
        st.session_state.aktivni_alat = None
        st.rerun()

    st.markdown("---")
    učitana_datoteka = st.file_uploader("📥 Odaberi sliku za obradu", type=["jpg", "png", "jpeg", "webp"])

    if učitana_datoteka:
        if st.session_state.original is None or učitana_datoteka.name != st.session_state.get('last_name', ''):
            img = Image.open(učitana_datoteka).convert("RGBA")
            st.session_state.original = img
            st.session_state.uredjena = img
            st.session_state.last_name = učitana_datoteka.name

        # === 1. ALAT ZA IZREZIVANJE ===
        if st.session_state.aktivni_alat == "izrezivanje":
            st.info("Podesi okvir za izrezivanje na slici ispod i klikni 'POTVRDI REZ'")
            img_crop = st_cropper(st.session_state.uredjena, realtime_update=True, box_color='#8a2be2', aspect_ratio=None)
            if st.button("✅ POTVRDI REZ", use_container_width=True):
                st.session_state.uredjena = img_crop
                st.session_state.aktivni_alat = None
                st.rerun()
                
        # === 2. ALAT ZA VELIČINU (Tvoj "mali prozor") ===
        elif st.session_state.aktivni_alat == "velicina":
            st.info("Unesi novu širinu i visinu u pikselima:")
            col_w, col_h = st.columns(2)
            with col_w: nova_sirina = st.number_input("Širina", value=st.session_state.uredjena.width, min_value=1)
            with col_h: nova_visina = st.number_input("Visina", value=st.session_state.uredjena.height, min_value=1)
            
            if st.button("✅ PRIMIJENI VELIČINU", use_container_width=True):
                st.session_state.uredjena = st.session_state.uredjena.resize((nova_sirina, nova_visina), Image.Resampling.LANCZOS)
                st.session_state.aktivni_alat = None
                st.rerun()

        # === 3. ALAT ZA TEKST ===
        elif st.session_state.aktivni_alat == "tekst":
            st.info("Unesi tekst koji želiš dodati na sliku:")
            tekst_unos = st.text_input("Tekst", value="Tinček")
            col_t1, col_t2 = st.columns(2)
            with col_t1: velicina_fonta = st.number_input("Veličina fonta", value=40, min_value=10)
            with col_t2: boja_teksta = st.color_picker("Boja", "#FF0000")
            
            if st.button("✅ DODAJ TEKST NA SLIKU", use_container_width=True):
                crtanje = ImageDraw.Draw(st.session_state.uredjena)
                try:
                    font = ImageFont.truetype("arial.ttf", velicina_fonta)
                except:
                    font = ImageFont.load_default() # Sigurnosna mjera ako server nema font
                crtanje.text((20, 20), tekst_unos, font=font, fill=boja_teksta)
                st.session_state.aktivni_alat = None
                st.rerun()
                
        # === GLAVNI PRIKAZ SLIKE (kad nijedan specijalni alat nije aktivan) ===
        else:
            st.markdown("### 🎨 Boje")
            sat = st.slider("Zasićenost", 0.0, 3.0, 1.0, 0.1)
            bright = st.slider("Svjetlina", 0.5, 2.0, 1.0, 0.1)

            img_final = st.session_state.uredjena
            if sat != 1.0: img_final = ImageEnhance.Color(img_final).enhance(sat)
            if bright != 1.0: img_final = ImageEnhance.Brightness(img_final).enhance(bright)

            st.image(img_final, caption="Pregled obrade", use_container_width=True)

            st.markdown("---")
            col_f, col_b = st.columns([1, 1])
            with col_f:
                # DODAN ICO FORMAT OVDJE!
                fmt = st.selectbox("Format", ["PNG", "JPG", "WEBP", "ICO"], label_visibility="collapsed")
            with col_b:
                buf = io.BytesIO()
                mime_type = f"image/{fmt.lower()}"
                ime_fajla = f"tincek_dizajn.{fmt.lower()}"
                
                # --- MAGIJA ZA SPREMANJE U ICO ---
                if fmt == "ICO":
                    img_export = img_final.copy()
                    img_export.thumbnail((256, 256)) # Automatski stisne sliku za ikonu!
                    img_export.save(buf, format="ICO")
                    mime_type = "image/x-icon"
                elif fmt == "JPG": 
                    img_final = img_final.convert("RGB")
                    img_final.save(buf, format="JPEG")
                else:
                    img_final.save(buf, format=fmt)
                    
                st.download_button(label=f"⬇️ SPREMI KAO {fmt}", data=buf.getvalue(), file_name=ime_fajla, mime=mime_type)
    else:
        st.markdown('<p class="veliki-pozdrav">👋 Pozdrav! Učitaj sliku ispod kako bi se otvorila vrata alata na vrhu.</p>', unsafe_allow_html=True)
