import streamlit as st
from PIL import Image, ImageEnhance
from rembg import remove
import io
from streamlit_cropper import st_cropper 

# 1. POSTAVKE STRANICE (Ovdje sad vuče tvoju sliku!)
st.set_page_config(
    page_title="TINČEK DIZAJN PRO EDITOR",
    page_icon="ikona.png", 
    layout="centered" 
)

# 2. CSS STILIZACIJA (Popravljen izbornik)
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

    /* --- SVI GUMBI --- */
    div[data-testid="stButton"] button {
        width: 100% !important;
        border-radius: 8px !important;
        height: 3.5em !important;
        background-color: #1a0b2e !important; 
        color: #ffffff !important; 
        border: 1px solid #8a2be2 !important; 
        transition: all 0.3s ease-in-out !important;
        font-weight: 600 !important;
        white-space: nowrap !important;
        margin-top: 0 !important;
        box-shadow: none !important;
    }
    div[data-testid="stButton"] button:hover {
        border-color: #d896ff !important;
        background-color: #3b1361 !important;
        color: #ffffff !important;
        box-shadow: 0 0 15px rgba(138, 43, 226, 0.8) !important; 
    }

    /* --- PADAJUĆI IZBORNIK (Vraćen Neon!) --- */
    div[data-baseweb="select"] > div {
        background-color: #1a0b2e !important; 
        border: 1px solid #8a2be2 !important; 
        border-radius: 8px !important;
        height: 3.5em !important; 
        transition: all 0.3s ease-in-out !important;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: #d896ff !important;
        box-shadow: 0 0 15px rgba(138, 43, 226, 0.8) !important;
    }
    div[data-baseweb="select"] > div > div {
        color: #ffffff !important; 
        font-weight: 600 !important;
    }
    div[data-baseweb="popover"] div[role="listbox"] {
        background-color: #1a0b2e !important;
        border: 2px solid #8a2be2 !important;
        border-radius: 8px;
    }
    li[role="option"] {
        color: #ffffff !important;
        font-weight: 600 !important;
        background-color: #1a0b2e !important; 
    }
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {
        background-color: #8a2be2 !important; 
        color: #ffffff !important;
    }

    .stFileUploader { border: 2px dashed #8a2be2 !important; border-radius: 10px; }
    
    .veliki-pozdrav {
        color: #d896ff !important; font-size: 1.2rem !important;
        font-weight: 700 !important; text-align: center; margin-top: 40px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIJALIZACIJA MEMORIJE ---
if 'uredjena' not in st.session_state:
    st.session_state.uredjena = None
if 'original' not in st.session_state:
    st.session_state.original = None
if 'rezanje_aktivno' not in st.session_state:
    st.session_state.rezanje_aktivno = False
if 'zadnji_ai_mod' not in st.session_state:
    st.session_state.zadnji_ai_mod = "AI: Standardno"

with st.container(border=True):
    st.markdown("""<div class="naslov-kontejner"><div class="naslov-ikona">🎨</div><div class="naslov-tekst">TINČEK DIZAJN<br>PRO EDITOR</div></div>""", unsafe_allow_html=True)
    st.markdown('<div style="font-size: 2rem; color: #ffffff; font-family: Orbitron; text-align: center; margin-bottom: 25px; text-shadow: 0 0 15px #8a2be2;">🛠️ Alati za obradu</div>', unsafe_allow_html=True)

    c_sel, c1, c2, c3, c4 = st.columns([1.8, 1, 1, 1, 1], gap="small")
    
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
        if st.button("✂️ Izreži", use_container_width=True):
            st.session_state.rezanje_aktivno = not st.session_state.rezanje_aktivno
    with c2:
        btn_rotate = st.button("🔄 Rotiraj", use_container_width=True)
    with c3:
        btn_cmyk = st.button("🧪 CMYK", use_container_width=True)
    with c4:
        btn_reset = st.button("↩️ Reset", use_container_width=True)

    # --- LOGIKA ---
    if btn_rotate and st.session_state.uredjena:
        st.session_state.uredjena = st.session_state.uredjena.rotate(-90, expand=True)
    if btn_cmyk and st.session_state.uredjena:
        st.session_state.uredjena = st.session_state.uredjena.convert("RGB").convert("CMYK").convert("RGB")
    if btn_reset:
        st.session_state.uredjena = st.session_state.original
        st.session_state.zadnji_ai_mod = "AI: Standardno"
        st.rerun()

    st.markdown("---")
    učitana_datoteka = st.file_uploader("📥 Odaberi sliku za obradu", type=["jpg", "png", "jpeg", "webp"])

    if učitana_datoteka:
        if st.session_state.original is None or učitana_datoteka.name != st.session_state.get('last_name', ''):
            img = Image.open(učitana_datoteka).convert("RGBA")
            st.session_state.original = img
            st.session_state.uredjena = img
            st.session_state.last_name = učitana_datoteka.name

        # --- ALAT ZA IZREZIVANJE ---
        if st.session_state.rezanje_aktivno:
            st.info("Podesi okvir za izrezivanje na slici ispod i klikni 'POTVRDI REZ'")
            img_crop = st_cropper(st.session_state.uredjena, realtime_update=True, box_color='#8a2be2', aspect_ratio=None)
            if st.button("✅ POTVRDI REZ", use_container_width=True):
                st.session_state.uredjena = img_crop
                st.session_state.rezanje_aktivno = False
                st.rerun()
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
                fmt = st.selectbox("Format", ["PNG", "JPG", "WEBP"], label_visibility="collapsed")
            with col_b:
                buf = io.BytesIO()
                if fmt == "JPG": img_final = img_final.convert("RGB")
                img_final.save(buf, format=fmt)
                st.download_button(label=f"⬇️ SPREMI KAO {fmt}", data=buf.getvalue(), file_name=f"tincek_dizajn.{fmt.lower()}", mime=f"image/{fmt.lower()}")
    else:
        st.markdown('<p class="veliki-pozdrav">👋 Pozdrav! Učitaj sliku ispod kako bi se otvorila vrata alata na vrhu.</p>', unsafe_allow_html=True)
