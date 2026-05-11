import streamlit as st
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
from rembg import remove
import io
import base64
from streamlit_cropper import st_cropper 

# --- MAGIČNI KOD ZA UGRADNJU IKONE ---
def get_base64_of_image(filename):
    try:
        with open(filename, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except:
        return None 

image_base64 = get_base64_of_image("ikona.png")
page_icon_final = Image.open("ikona.png") if image_base64 else "🎨" 

st.set_page_config(page_title="TINČEK DIZAJN PRO EDITOR", page_icon=page_icon_final, layout="centered")

# --- CSS STILIZACIJA ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&display=swap');
    header, [data-testid="stHeader"], .stAppHeader { display: none !important; height: 0px !important; }
    [data-testid="stToolbar"], [data-testid="stDecoration"], .stDeployButton, #MainMenu, footer { display: none !important; }
    .stApp { background-color: #050505 !important; }
    .block-container { max-width: 800px !important; padding-top: 2rem !important; }
    
    html body div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #121212 !important; border: none !important; border-radius: 15px !important;
        box-shadow: 0 10px 40px rgba(138, 43, 226, 0.15) !important; padding: 20px 15px !important;
    }

    .naslov-kontejner { text-align: center; background: linear-gradient(180deg, #2a0a4a 0%, #121212 100%); padding: 25px 10px; border-radius: 15px; margin-bottom: 25px; border: 1px solid rgba(138, 43, 226, 0.3); }
    .naslov-ikona { max-width: 90px; margin: 0 auto 15px auto; display: block; filter: drop-shadow(0 0 15px rgba(138, 43, 226, 0.7)); }
    .naslov-tekst { color: #ffffff !important; font-family: 'Orbitron', sans-serif !important; font-weight: 900; letter-spacing: 1px; text-shadow: 0 0 10px #8a2be2, 0 0 20px #8a2be2 !important; font-size: 1.6rem !important; line-height: 1.3 !important; margin: 0; }
    @media (min-width: 600px) { .naslov-tekst { font-size: 2.3rem !important; } .naslov-ikona { max-width: 120px; } }

    div[data-testid="stButton"] button { width: 100% !important; border-radius: 8px !important; height: 3.5em !important; background-color: #1a0b2e !important; color: #ffffff !important; border: 1px solid #8a2be2 !important; font-weight: 600 !important; white-space: nowrap !important; margin-top: 0 !important; }
    div[data-testid="stButton"] button:hover { border-color: #d896ff !important; background-color: #3b1361 !important; color: #ffffff !important; box-shadow: 0 0 15px rgba(138, 43, 226, 0.8) !important; }
    
    .stSlider > div { background-color: transparent !important; }
    div[data-baseweb="select"] > div, div[data-baseweb="input"] { background-color: #1a0b2e !important; border: 1px solid #8a2be2 !important; border-radius: 8px !important; }
    div[data-baseweb="input"] input { color: #ffffff !important; font-weight: bold !important; }
    label { color: #d896ff !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIJALIZACIJA MEMORIJE ---
if 'original' not in st.session_state: st.session_state.original = None
if 'uredjena' not in st.session_state: st.session_state.uredjena = None
if 'aktivni_alat' not in st.session_state: st.session_state.aktivni_alat = None
if 'zadnji_ai_mod' not in st.session_state: st.session_state.zadnji_ai_mod = "AI: Standardno"
if 'tekst_slojevi' not in st.session_state: st.session_state.tekst_slojevi = [] 

# --- FUNKCIJA ZA ISCRTAVANJE (Pravi Live Preview) ---
def render_sliku():
    if st.session_state.uredjena is None: return None
    radna_slika = st.session_state.uredjena.copy()
    crtanje = ImageDraw.Draw(radna_slika)
    
    for sloj in st.session_state.tekst_slojevi:
        try: font = ImageFont.truetype("arial.ttf", sloj['velicina'])
        except: font = ImageFont.load_default()
        
        if sloj['stil'] == "Oblačić":
            bbox = crtanje.textbbox((sloj['x'], sloj['y']), sloj['tekst'], font=font)
            padding = 15
            rect_coords = [bbox[0]-padding, bbox[1]-padding, bbox[2]+padding, bbox[3]+padding]
            crtanje.rounded_rectangle(rect_coords, radius=10, fill="white", outline="#8a2be2", width=3)
            crtanje.text((sloj['x'], sloj['y']), sloj['tekst'], font=font, fill="black")
        else:
            crtanje.text((sloj['x'], sloj['y']), sloj['tekst'], font=font, fill=sloj['boja'])
            
    return radna_slika

with st.container(border=True):
    # NASLOV
    logo_html = f'<img src="data:image/png;base64,{image_base64}" alt="Logo" class="naslov-ikona">' if image_base64 else '<div style="font-size: 4rem; text-align: center; margin-bottom: 10px;">🎨</div>'
    st.markdown(f'<div class="naslov-kontejner">{logo_html}<div class="naslov-tekst">TINČEK DIZAJN<br>PRO EDITOR</div></div>', unsafe_allow_html=True)
    
    st.markdown('<div style="font-size: 1.5rem; color: #ffffff; font-family: Orbitron; text-align: center; margin-bottom: 25px; text-shadow: 0 0 15px #8a2be2;">🛠️ Alati za obradu</div>', unsafe_allow_html=True)

    # --- NOVI GRID RASPORED (2 PO 2) ZA SAVRŠEN MOBILNI PRIKAZ ---
    bg_level = st.selectbox("AI", ["AI: Standardno", "AI: Precizno", "AI: Snažno"], label_visibility="collapsed")
    if bg_level != st.session_state.zadnji_ai_mod and bg_level != "AI: Standardno":
        if st.session_state.uredjena:
            with st.spinner("AI radi..."):
                if "Precizno" in bg_level:
                    st.session_state.uredjena = remove(st.session_state.uredjena, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
                else:
                    st.session_state.uredjena = remove(st.session_state.uredjena, alpha_matting=True, alpha_matting_foreground_threshold=250, alpha_matting_background_threshold=20, alpha_matting_erode_size=15)
                st.session_state.zadnji_ai_mod = bg_level
                st.rerun()
        else:
            st.warning("⚠️ Prvo učitaj sliku!")

    st.markdown("<br>", unsafe_allow_html=True) # Mali razmak

    c1, c2 = st.columns(2)
    with c1: 
        if st.button("✂️ Izreži", use_container_width=True): st.session_state.aktivni_alat = "izrezivanje" if st.session_state.aktivni_alat != "izrezivanje" else None
    with c2: 
        if st.button("📏 Veličina", use_container_width=True): st.session_state.aktivni_alat = "velicina" if st.session_state.aktivni_alat != "velicina" else None

    c3, c4 = st.columns(2)
    with c3: 
        if st.button("✍️ Tekst", use_container_width=True): st.session_state.aktivni_alat = "tekst" if st.session_state.aktivni_alat != "tekst" else None
    with c4:
        if st.button("🎬 GIF", use_container_width=True): st.session_state.aktivni_alat = "gif" if st.session_state.aktivni_alat != "gif" else None

    c5, c6 = st.columns(2)
    with c5: 
        if st.button("🔄 Rotiraj", use_container_width=True): 
            if st.session_state.uredjena: st.session_state.uredjena = st.session_state.uredjena.rotate(-90, expand=True)
    with c6:
        if st.button("🧪 CMYK", use_container_width=True):
            if st.session_state.uredjena: st.session_state.uredjena = st.session_state.uredjena.convert("RGB").convert("CMYK").convert("RGB")
            
    if st.button("↩️ Resetiraj Sve", use_container_width=True): 
        st.session_state.uredjena = st.session_state.original
        st.session_state.tekst_slojevi = []
        st.session_state.aktivni_alat = None
        st.rerun()

    st.markdown("---")

    # === ALAT ZA GIF ANIMACIJE ===
    if st.session_state.aktivni_alat == "gif":
        st.markdown('<h3 style="color:#d896ff; text-align:center;">🎬 Kreator GIF Animacija</h3>', unsafe_allow_html=True)
        st.info("Ovdje učitaj više slika koje želiš spojiti u animirani GIF!")
        gif_slike = st.file_uploader("Učitaj sličice (okvire)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        
        if gif_slike and len(gif_slike) > 1:
            brzina = st.slider("Brzina animacije (ms po slici)", 50, 1500, 500, 50)
            
            if st.button("Generiraj GIF i Prikaži", use_container_width=True):
                okviri = [Image.open(slika) for slika in gif_slike]
                buf_gif = io.BytesIO()
                okviri[0].save(buf_gif, format='GIF', append_images=okviri[1:], save_all=True, duration=brzina, loop=0)
                
                st.image(buf_gif.getvalue(), caption="Tvoja Animacija")
                st.download_button(label="⬇️ SPREMI OVO KAO GIF", data=buf_gif.getvalue(), file_name="tincek_animacija.gif", mime="image/gif")
        elif gif_slike:
            st.warning("Učitaj barem 2 slike da bi napravila animaciju!")
            
    # === GLAVNI EDITOR (ZA OBIČNE SLIKE) ===
    else:
        učitana_datoteka = st.file_uploader("📥 Odaberi sliku za obradu", type=["jpg", "png", "jpeg", "webp"])

        if učitana_datoteka:
            if st.session_state.original is None or učitana_datoteka.name != st.session_state.get('last_name', ''):
                img = Image.open(učitana_datoteka).convert("RGBA")
                st.session_state.original = img
                st.session_state.uredjena = img.copy()
                st.session_state.tekst_slojevi = [] 
                st.session_state.last_name = učitana_datoteka.name

            # --- ALAT ZA REZANJE ---
            if st.session_state.aktivni_alat == "izrezivanje":
                st.info("Podesi okvir za izrezivanje na slici ispod i klikni 'POTVRDI REZ'")
                img_crop = st_cropper(render_sliku(), realtime_update=True, box_color='#8a2be2', aspect_ratio=None)
                if st.button("✅ POTVRDI REZ", use_container_width=True):
                    st.session_state.uredjena = img_crop
                    st.session_state.tekst_slojevi = [] 
                    st.session_state.aktivni_alat = None
                    st.rerun()

            # --- ALAT ZA VELIČINU ---
            elif st.session_state.aktivni_alat == "velicina":
                col_w, col_h = st.columns(2)
                with col_w: nova_sirina = st.number_input("Nova Širina", value=st.session_state.uredjena.width, min_value=1)
                with col_h: nova_visina = st.number_input("Nova Visina", value=st.session_state.uredjena.height, min_value=1)
                if st.button("✅ PRIMIJENI VELIČINU", use_container_width=True):
                    st.session_state.uredjena = st.session_state.uredjena.resize((nova_sirina, nova_visina), Image.Resampling.LANCZOS)
                    st.session_state.aktivni_alat = None
                    st.rerun()

            # --- ALAT ZA TEKST (SLOJEVI I OBLAČIĆI) ---
            elif st.session_state.aktivni_alat == "tekst":
                st.markdown("### ✍️ Uređivač teksta")
                
                if st.session_state.tekst_slojevi:
                    st.write("Tvoji trenutni tekstovi (Live pomicanje):")
                    for i, sloj in enumerate(st.session_state.tekst_slojevi):
                        with st.expander(f"Tekst: {sloj['tekst']}", expanded=True):
                            sloj['tekst'] = st.text_input("Izmijeni tekst", value=sloj['tekst'], key=f"t_{i}")
                            col_1, col_2 = st.columns(2)
                            with col_1: sloj['x'] = st.slider("Lijevo/Desno (X)", 0, st.session_state.uredjena.width, sloj['x'], key=f"x_{i}")
                            with col_2: sloj['y'] = st.slider("Gore/Dolje (Y)", 0, st.session_state.uredjena.height, sloj['y'], key=f"y_{i}")
                            
                            col_3, col_4, col_5 = st.columns(3)
                            with col_3: sloj['velicina'] = st.number_input("Vel.", value=sloj['velicina'], min_value=10, key=f"v_{i}")
                            with col_4: sloj['boja'] = st.color_picker("Boja", sloj['boja'], key=f"b_{i}")
                            with col_5: sloj['stil'] = st.selectbox("Stil", ["Samo tekst", "Oblačić"], index=0 if sloj['stil']=="Samo tekst" else 1, key=f"s_{i}")
                            
                            if st.button(f"🗑️ Obriši ovaj tekst", key=f"del_{i}", use_container_width=True):
                                st.session_state.tekst_slojevi.pop(i)
                                st.rerun()

                st.markdown("#### Dodaj novi tekst")
                novi_tekst = st.text_input("Unesi novi tekst", value="Novi tekst")
                if st.button("➕ DODAJ NA SLIKU", use_container_width=True):
                    st.session_state.tekst_slojevi.append({'tekst': novi_tekst, 'x': 50, 'y': 50, 'velicina': 40, 'boja': '#ff0000', 'stil': 'Samo tekst'})
                    st.rerun()

            # --- GLAVNI PREGLED I SPREMANJE ---
            st.markdown("### 🎨 Živi Pregled")
            
            if st.session_state.aktivni_alat not in ["izrezivanje", "tekst", "velicina"]:
                sat = st.slider("Zasićenost (Boje)", 0.0, 3.0, 1.0, 0.1)
                bright = st.slider("Svjetlina", 0.5, 2.0, 1.0, 0.1)
                
                if sat != 1.0: st.session_state.uredjena = ImageEnhance.Color(st.session_state.uredjena).enhance(sat)
                if bright != 1.0: st.session_state.uredjena = ImageEnhance.Brightness(st.session_state.uredjena).enhance(bright)

            konacna_slika = render_sliku()
            st.image(konacna_slika, use_container_width=True)

            # --- OPCIJE ZA SPREMANJE ---
            st.markdown("---")
            col_f, col_ico, col_btn = st.columns([1, 1, 1.5])
            with col_f:
                fmt = st.selectbox("Format", ["PNG", "JPG", "WEBP", "ICO"], label_visibility="collapsed")
            
            ico_velicina = 256
            if fmt == "ICO":
                with col_ico:
                    ico_velicina = st.selectbox("Dim. (px)", [512, 256, 128, 64, 32, 16], label_visibility="collapsed")
            
            with col_btn:
                buf = io.BytesIO()
                mime_type = f"image/{fmt.lower()}"
                ime_fajla = f"tincek_dizajn.{fmt.lower()}"
                
                slika_za_export = konacna_slika.copy()
                if fmt == "ICO":
                    slika_za_export.thumbnail((ico_velicina, ico_velicina))
                    slika_za_export.save(buf, format="ICO")
                    mime_type = "image/x-icon"
                elif fmt == "JPG": 
                    slika_za_export.convert("RGB").save(buf, format="JPEG")
                else:
                    slika_za_export.save(buf, format=fmt)
                    
                st.download_button(label=f"⬇️ SPREMI", data=buf.getvalue(), file_name=ime_fajla, mime=mime_type, use_container_width=True)
        else:
            st.markdown('<p style="color:#d896ff;text-align:center;margin-top:20px;font-size:1.2rem;font-weight:bold;">👋 Učitaj sliku ili otvori 🎬 Kreator GIF-ova na vrhu!</p>', unsafe_allow_html=True)
