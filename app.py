import streamlit as st
from PIL import Image, ImageEnhance
from rembg import remove
import io

# 1. POSTAVKE STRANICE MORAJU BITI NA SAMOM VRHU! 
st.set_page_config(
    page_title="TINČEK DIZAJN PRO EDITOR",
    page_icon="🎨",
    layout="centered" 
)

# 2. CSS STILIZACIJA (Dark Card & Banner Tema)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&display=swap');

    /* Apsolutno najtamnija crna za pozadinu cijele stranice (oko aplikacije) */
    .stApp {
        background-color: #050505; 
    }
    
    /* --- DODANO: FIKSIRANA ŠIRINA DA APLIKACIJA BUDE USKA KAO PRIJE --- */
    .block-container {
        max-width: 700px !important; 
        padding-top: 2rem !important;
    }
    
    /* =======================================================
       ŠAH-MAT ZA STREAMLIT: Bez okvira, samo svjetlija pozadina!
       ======================================================= */
    html body div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #121212 !important; /* Malo svjetlija crna za "karticu" */
        border: none !important; /* UKINUTI SVI OKVIRI! */
        border-radius: 15px !important;
        box-shadow: 0 10px 40px rgba(138, 43, 226, 0.15) !important; /* Vrlo blagi ljubičasti odsjaj iza kartice */
        padding: 30px 20px !important;
        overflow: hidden !important; 
    }
    /* Poništavamo sivi Streamlit okvir ako se pokuša sakriti unutra */
    html body div[data-testid="stVerticalBlockBorderWrapper"] > div {
        border: none !important;
        box-shadow: none !important;
    }

    /* --- VRAĆENI I POBOLJŠANI HEADER BANNER --- */
    .naslov-kontejner {
        display: flex;
        align-items: center; 
        justify-content: center; 
        gap: 20px; 
        
        /* Gradient koji kreće od ljubičaste i stapa se u našu novu #121212 pozadinu */
        background: linear-gradient(180deg, #2a0a4a 0%, #121212 100%);
        margin: -30px -20px 30px -20px; /* Rasteže ga od ruba do ruba "kartice" */
        padding: 40px 20px;
        
        border-bottom: 1px solid rgba(138, 43, 226, 0.3); /* Jako suptilna linija odvajanja */
    }
    .naslov-ikona {
        font-size: 5.5rem; 
        line-height: 1;
        text-shadow: 0 0 25px rgba(138, 43, 226, 0.7); 
    }
    .naslov-tekst {
        color: #ffffff !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900;
        text-align: left; 
        letter-spacing: 3px;
        text-shadow: 0 0 10px #8a2be2, 0 0 20px #8a2be2, 0 0 40px #d896ff !important;
        font-size: 2.6rem !important; 
        line-height: 1.2 !important;
        margin: 0;
    }
    .prvi-red {
        white-space: nowrap !important;
    }

    .alati-naslov {
        font-size: 2rem;
        color: #ffffff;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        text-align: center;
        margin-bottom: 25px;
        text-shadow: 0 0 15px #8a2be2;
    }

    p:not(.veliki-pozdrav), span:not(.veliki-pozdrav), label, div[data-testid="stMarkdownContainer"] > p {
        color: #ffffff !important;
    }

    /* --- RAZMACI IZMEĐU STUPACA --- */
    div[data-testid="stHorizontalBlock"] {
        gap: 8px !important; 
    }
    div[data-testid="column"] {
        padding: 0 !important; 
    }

    /* --- GUMBI --- */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em !important; 
        padding: 0 5px !important; 
        font-size: 1rem !important; 
        background-color: #1a0b2e; 
        color: #ffffff !important;
        border: 1px solid #8a2be2 !important; 
        transition: all 0.3s ease-in-out;
        font-weight: 600;
        margin-top: 0 !important;
        white-space: nowrap !important; 
    }
    .stButton>button:hover {
        border-color: #d896ff !important;
        background-color: #3b1361 !important; 
        box-shadow: 0 0 6px #8a2be2, 0 0 12px #d896ff !important; 
        color: #ffffff !important;
    }

    .stDownloadButton>button {
        background-color: #8a2be2 !important;
        color: white !important;
        border: 2px solid #d896ff !important;
        font-weight: 800;
        width: 100%;
        height: 3em !important; 
        border-radius: 8px;
        transition: all 0.3s ease-in-out;
        font-size: 1rem !important;
    }
    .stDownloadButton>button:hover {
        background-color: #a020f0 !important;
        box-shadow: 0 0 10px #8a2be2, 0 0 20px #d896ff !important; 
        color: white !important;
    }

    /* --- PADAJUĆI IZBORNIK --- */
    div[data-baseweb="select"] > div {
        background-color: #1a0b2e !important; 
        border: 1px solid #8a2be2 !important; 
        border-radius: 8px;
        height: 3.5em !important; 
        align-items: center;
        padding: 0 5px !important;
    }
    div[data-baseweb="select"] > div > div {
        color: #ffffff !important; 
        font-weight: 700 !important;
        font-size: 0.95rem !important; 
        text-shadow: none !important; 
    }
    div[data-baseweb="popover"] div[role="listbox"] {
        background-color: #1a0b2e !important;
        border: 2px solid #8a2be2 !important;
        border-radius: 8px;
        padding: 0 !important; 
    }
    li[role="option"] {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        background-color: #1a0b2e !important; 
        opacity: 1 !important; 
    }
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {
        background-color: #8a2be2 !important; 
        color: #ffffff !important;
        opacity: 1 !important; 
    }

    .stFileUploader {
        border: 2px dashed #8a2be2 !important;
        border-radius: 10px;
        padding: 10px;
        background-color: #0b0b0b; /* Uploader ima mrvicu tamniju pozadinu da se istakne */
        box-shadow: 0 0 6px rgba(138, 43, 226, 0.2) !important;
    }
    div[data-testid="stFileUploadDropzone"] small {
        display: none !important;
    }

    .stSlider div[data-testid="stThumbValue"] {
        color: #d896ff !important;
        font-weight: bold;
    }
    div[data-baseweb="slider"] div[data-testid="stTickBar"] > div {
        background-color: #3b1361 !important;
    }
    div[data-baseweb="slider"] div[role="slider"] {
        background-color: #d896ff !important;
        border: 3px solid #8a2be2 !important;
        box-shadow: 0 0 8px #8a2be2 !important; 
    }
    div[data-baseweb="slider"] > div > div > div {
        background-color: #8a2be2 !important;
    }

    hr {
        border-color: #8a2be2 !important;
        opacity: 0.3 !important; /* Još blaže linije unutar same aplikacije */
    }

    .veliki-pozdrav {
        color: #d896ff !important; 
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        text-align: center;
        margin-top: 40px;
        text-shadow: 0 0 8px #8a2be2; 
    }

    /* --- DODANO: PRAVILA KOJA SPAŠAVAJU MOBITEL (Naslov i Gumbi) --- */
    @media (max-width: 650px) {
        .naslov-kontejner {
            flex-direction: column; /* Stavlja paletu iznad teksta */
            gap: 5px;
            padding: 30px 10px;
        }
        .naslov-ikona {
            font-size: 4rem; 
        }
        .naslov-tekst {
            font-size: 1.8rem !important; /* Smanjuje tekst da ne curi van okvira */
            text-align: center;
        }
        .prvi-red {
            white-space: normal !important; /* Gasi zabranu prelaska u novi red na mobitelu */
        }
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important; /* Dozvoljava gumbima da idu u novi red */
        }
        div[data-testid="column"] {
            min-width: 45% !important; /* Na mobitelu gumbi postaju kockasti i idu 2x2 */
            flex: 1 1 auto !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIJALIZACIJA MEMORIJE ---
if 'uredjena' not in st.session_state:
    st.session_state.uredjena = None
if 'original' not in st.session_state:
    st.session_state.original = None

# =======================================================
# KARTICA SA SVJETLIJOM POZADINOM BEZ IKAKVIH OKVIRA
# =======================================================
with st.container(border=True):

    # VRAĆENI HEADER
    st.markdown("""
        <div class="naslov-kontejner">
            <div class="naslov-ikona">🎨</div>
            <div class="naslov-tekst"><span class="prvi-red">TINČEK DIZAJN</span><br>PRO EDITOR</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="alati-naslov">🛠️ Alati za obradu</div>', unsafe_allow_html=True)

    c_sel, c1, c2, c3, c4 = st.columns([1.8, 1, 1, 1, 1], gap="small")
    
    with c_sel:
        bg_level = st.selectbox(
            "Razina AI brisanja", 
            ["AI: Standardno", "AI: Precizno", "AI: Snažno"], 
            label_visibility="collapsed"
        )

    with c1:
        btn_bg = st.button("🪄 Ukloni", use_container_width=True)
    with c2:
        btn_rotate = st.button("🔄 Rotiraj", use_container_width=True)
    with c3:
        btn_cmyk = st.button("🧪 CMYK", use_container_width=True)
    with c4:
        btn_reset = st.button("↩️ Reset", use_container_width=True)

    if btn_bg:
        if st.session_state.uredjena:
            with st.spinner("AI pažljivo analizira rubove..."):
                if "Standardno" in bg_level:
                    st.session_state.uredjena = remove(st.session_state.uredjena)
                elif "Precizno" in bg_level:
                    st.session_state.uredjena = remove(st.session_state.uredjena, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
                else:
                    st.session_state.uredjena = remove(st.session_state.uredjena, alpha_matting=True, alpha_matting_foreground_threshold=250, alpha_matting_background_threshold=20, alpha_matting_erode_size=15)
        else:
            st.warning("⚠️ Prvo učitaj sliku ispod da bi koristila alate!")

    if btn_rotate:
        if st.session_state.uredjena:
            st.session_state.uredjena = st.session_state.uredjena.rotate(-90, expand=True)
        else:
            st.warning("⚠️ Prvo učitaj sliku ispod da bi koristila alate!")

    if btn_cmyk:
        if st.session_state.uredjena:
            temp = st.session_state.uredjena.convert("RGB")
            st.session_state.uredjena = temp.convert("CMYK").convert("RGB")
            st.toast("Prikazan CMYK profil za print profiling!")
        else:
            st.warning("⚠️ Prvo učitaj sliku ispod da bi koristila alate!")

    if btn_reset:
        if st.session_state.original:
            st.session_state.uredjena = st.session_state.original
            st.rerun()
        else:
            st.warning("⚠️ Nema slike za resetiranje.")

    st.markdown("---")

    učitana_datoteka = st.file_uploader("📥 Odaberi sliku za obradu (Maksimalno 10 MB)", type=["jpg", "png", "jpeg", "webp"])

    if učitana_datoteka:
        if učitana_datoteka.size > 10 * 1024 * 1024:
            st.error("🚨 Slika koju si pokušala učitati je prevelika! Maksimalna dozvoljena veličina je 10 MB. Molim te odaberi manju sliku.")
        else:
            if st.session_state.original is None or učitana_datoteka.name != st.session_state.get('last_name', ''):
                img = Image.open(učitana_datoteka).convert("RGBA")
                st.session_state.original = img
                st.session_state.uredjena = img
                st.session_state.last_name = učitana_datoteka.name

            st.markdown("### 🎨 Boje")
            sat = st.slider("Zasićenost (Saturation)", 0.0, 3.0, 1.0, 0.1)
            bright = st.slider("Svjetlina (Brightness)", 0.5, 2.0, 1.0, 0.1)

            img_mod = st.session_state.uredjena
            if sat != 1.0:
                img_mod = ImageEnhance.Color(img_mod).enhance(sat)
            if bright != 1.0:
                img_mod = ImageEnhance.Brightness(img_mod).enhance(bright)

            st.image(img_mod, caption="Pregled obrade", use_container_width=True)

            st.markdown("---")
            col_format, col_btn = st.columns([1, 1], gap="small")
            with col_format:
                format_izbora = st.selectbox("Format", ["PNG", "JPG", "WEBP"], label_visibility="collapsed")
            with col_btn:
                buf = io.BytesIO()
                final_save = img_mod
                if format_izbora == "JPG":
                    final_save = final_save.convert("RGB")
                
                final_save.save(buf, format=format_izbora)
                
                st.download_button(
                    label=f"⬇️ SPREMI KAO {format_izbora}",
                    data=buf.getvalue(),
                    file_name=f"tincek_dizajn.{format_izbora.lower()}",
                    mime=f"image/{format_izbora.lower()}"
                )

    else:
        st.markdown("""
            <p class="veliki-pozdrav">👋 Pozdrav! Učitaj sliku ispod kako bi se otvorila vrata alata na vrhu.</p>
        """, unsafe_allow_html=True)
