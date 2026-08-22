import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import matplotlib.pyplot as plt
from mplsoccer import PyPizza, Radar

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pro Scout Dashboard", page_icon="📊", layout="wide")

# --- CSS (KUSURSUZ SİMETRİ VE KARANLIK TEMA) ---
st.markdown("""
<style>
    .stApp { background-color: #0b101c; color: white; }
    .header-box { background-color: #121927; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #1f2937; display: flex; justify-content: space-between; align-items: center; }
    .category-card { background-color: #121927; border-radius: 12px; padding: 25px 20px; margin-bottom: 25px; border: 1px solid #1f2937; height: 100%; }
    .category-title { font-size: 13px; letter-spacing: 2px; margin-bottom: 25px; color: #8b949e; font-weight: 600; text-transform: uppercase; text-align: left; }
    .stat-container { margin-bottom: 22px; }
    .stat-title { text-align: center; color: #e5e7eb; font-size: 12px; margin-bottom: 8px; font-weight: 500; }
    .bar-bg { width: 100%; height: 6px; background-color: #1f2937; border-radius: 3px; margin-bottom: 8px; }
    .bar-fill { height: 100%; border-radius: 3px; }
    .stat-values { display: flex; justify-content: space-between; align-items: center; font-size: 11px; }
    .badge { padding: 3px 8px; border-radius: 12px; border: 1px solid; font-weight: 600; font-size: 9px; letter-spacing: 0.5px; }
    .elite-color { background-color: #10b981; } .elite-badge { color: #10b981; border-color: #10b981; }
    .above-color { background-color: #3b82f6; } .above-badge { color: #3b82f6; border-color: #3b82f6; }
    .avg-color { background-color: #6b7280; } .avg-badge { color: #6b7280; border-color: #6b7280; }
    .below-color { background-color: #f59e0b; } .below-badge { color: #f59e0b; border-color: #f59e0b; }
    .poor-color { background-color: #ef4444; } .poor-badge { color: #ef4444; border-color: #ef4444; }
    div.stDownloadButton > button { background-color: #10b981; color: white; font-weight: bold; border-radius: 8px; border: none; }
    div.stDownloadButton > button:hover { background-color: #059669; }
</style>
""", unsafe_allow_html=True)

# --- BÜYÜK VERİTABANI YÜKLEME / OLUŞTURMA YÖNETİMİ ---
@st.cache_data
def load_database():
    try:
        # Eğer sistemde scout_data.csv adında kendi gerçek dosyan varsa, onu saniyeler içinde okur.
        # Bu dosya 30 lig ve 100.000 satır olsa bile Pandas anında yükler.
        df = pd.read_csv("scout_data.csv")
        return df
    except FileNotFoundError:
        # Gerçek dosyan yoksa, sistemin gücünü test etmen için 10.000+ oyunculuk veri simüle ediliyor.
        ligler = [f"Lig {i}" for i in range(1, 31)]
        ligler[0], ligler[1] = "Turkish Super Lig", "English Premier League"
        
        takimlar = {}
        for lig in ligler:
            takimlar[lig] = [f"{lig} Takım {j}" for j in range(1, 21)]
        
        takimlar["Turkish Super Lig"][0] = "Trabzonspor"
        takimlar["English Premier League"][0] = "Liverpool"

        ulkeler = ["🇹🇷", "🇪🇬", "🇺🇦", "🇦🇷", "🇫🇮", "🇧🇷", "🇫🇷", "🇩🇪", "🇪🇸", "🇮🇹"]
        pozisyonlar = ["GK", "CB", "FB", "DM", "CM", "AM", "RW", "LW", "ST"]
        sezonlar = ["2025/2026", "2026/2027"]

        data = []
        # Trabzonspor ve Liverpool için bazı gerçek isimler ekleyelim
        ozel_oyuncular = {
            "Trabzonspor": [("Uğurcan Çakır", "GK", "🇹🇷"), ("Batagov", "CB", "🇺🇦")],
            "Liverpool": [("Mohamed Salah", "RW", "🇪🇬"), ("Alexis Mac Allister", "CM", "🇦🇷")]
        }

        # 30 Lig, her ligde 20 takım, her takımda 25 oyuncu = ~15.000 oyuncu
        # İki sezon (25/26 ve 26/27) için veri = ~30.000 satır
        for lig in ligler:
            for takim in takimlar[lig]:
                for sezon in sezonlar:
                    for k in range(25):
                        oyuncu_ismi = f"Oyuncu {random.randint(1000, 99999)}"
                        poz = random.choice(pozisyonlar)
                        ulke = random.choice(ulkeler)
                        logo = "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                        
                        if takim in ozel_oyuncular and k < len(ozel_oyuncular[takim]):
                            oyuncu_ismi, poz, ulke = ozel_oyuncular[takim][k]
                            logo = "https://upload.wikimedia.org/wikipedia/tr/a/ab/TrabzonsporAmblemi.png" if takim == "Trabzonspor" else "https://upload.wikimedia.org/wikipedia/en/0/0c/Liverpool_FC.svg"
                        elif takim in ozel_oyuncular:
                            continue # Özel oyuncular eklendiği için atla

                        data.append([lig, takim, oyuncu_ismi, poz, ulke, sezon, random.randint(300, 3420), logo])
        
        df = pd.DataFrame(data, columns=["Lig", "Takim", "Oyuncu", "Pozisyon", "Ulke", "Sezon", "Dakika", "Logo"])
        return df

df = load_database()

# --- YARDIMCI FONKSİYON: STAT BAR ---
def draw_stat(title, value, percentile):
    if percentile >= 85: b_class, bdg_class, text = "elite-color", "elite-badge", "ELITE"
    elif percentile >= 65: b_class, bdg_class, text = "above-color", "above-badge", "ABOVE AVG"
    elif percentile >= 35: b_class, bdg_class, text = "avg-color", "avg-badge", "AVERAGE"
    elif percentile >= 15: b_class, bdg_class, text = "below-color", "below-badge", "BELOW AVG"
    else: b_class, bdg_class, text = "poor-color", "poor-badge", "POOR"

    val_str = f"{value:.2f}" if isinstance(value, float) else f"{value}"
    return f"""
    <div class="stat-container">
        <div class="stat-title">{title}</div>
        <div class="bar-bg"><div class="bar-fill {b_class}" style="width: {percentile}%;"></div></div>
        <div class="stat-values">
            <span style="color:#d1d5db;">{val_str}/90 <span style="color:#6b7280;">({percentile}%)</span></span>
            <span class="badge {bdg_class}">{text}</span>
        </div>
    </div>
    """

# --- SOL MENÜ (DİNAMİK FİLTRELEME 30.000 SATIR İÇİN) ---
st.sidebar.title("🔍 Kapsamlı Scout Paneli")
st.sidebar.markdown("---")

sezonlar = sorted(df['Sezon'].unique().tolist())
secilen_sezon = st.sidebar.selectbox("📅 Sezon Seçin", sezonlar)

df_sezon = df[df['Sezon'] == secilen_sezon]

ligler = sorted(df_sezon['Lig'].unique().tolist())
secilen_lig = st.sidebar.selectbox("🌍 Lig Seçin", ligler)

takimlar = sorted(df_sezon[df_sezon['Lig'] == secilen_lig]['Takim'].unique().tolist())
secilen_takim = st.sidebar.selectbox("🏠 Takım Seçin", takimlar)

oyuncular = sorted(df_sezon[(df_sezon['Lig'] == secilen_lig) & (df_sezon['Takim'] == secilen_takim)]['Oyuncu'].unique().tolist())
secilen_oyuncu = st.sidebar.selectbox("👤 Oyuncu Seçin", oyuncular)

oyuncu_verisi = df_sezon[df_sezon['Oyuncu'] == secilen_oyuncu].iloc[0]

st.sidebar.markdown("---")
menu = st.sidebar.radio("📌 Navigasyon", ["Player Stats", "Stat Radar Comparison", "Pizza Chart"])

# Veri simülasyonu için rastgelelik tohumu (oyuncuya özel sabit kalsın diye)
random.seed(hash(secilen_oyuncu + secilen_sezon)) 
p = lambda: random.randint(10, 99)
v = lambda: round(random.uniform(0.1, 5.0), 2)

# Ortak Watermark Fonksiyonu (Grafiklere profesyonel marka eklemek için)
def add_watermark(fig):
    fig.text(0.99, 0.01, 'Scouting Report | Muhammed Emin (@pressxresistant)', 
             color='#8b949e', fontsize=9, ha='right', va='bottom', alpha=0.6, weight='bold')

# --- ANA EKRAN İÇERİKLERİ ---
if menu == "Player Stats":
    st.markdown(f"""
    <div class="header-box">
        <div style="display: flex; align-items: center;">
            <img src="{oyuncu_verisi['Logo']}" width="65" style="margin-right: 20px; object-fit: contain;">
            <div>
                <h1 style="margin:0; font-size: 32px;">{secilen_oyuncu} <span style="font-size: 24px;">{oyuncu_verisi['Ulke']}</span></h1>
                <p style="margin:5px 0 0 0; color: #8b949e; font-size: 14px;">{secilen_sezon} Sezonu | {secilen_lig} | Percentile rank vs. positional peers</p>
            </div>
        </div>
        <div style="text-align: right; font-size: 13px; color: #d1d5db;">
            <div style="margin-bottom: 8px;">
                <span style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 15px; margin-right: 5px;">{secilen_takim}</span> 
                <span style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 15px; color:#10b981;">{oyuncu_verisi['Pozisyon']}</span>
            </div>
            <div>
                <span style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 15px; margin-right: 5px;">Age: 20</span> 
                <span style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 15px;">{oyuncu_verisi['Dakika']} min.</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="category-card"><div class="category-title">OUTPUT</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(draw_stat("Goals", v(), p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Shots On Target", v(), p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Shots Inside Box", v(), p()), unsafe_allow_html=True)
        with c2:
            st.markdown(draw_stat("npxG", v(), p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Created Own Shot", v(), p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Touches In Opp. Box", v(), p()), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="category-card"><div class="category-title">PASSING</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(draw_stat("Accurate Passes", v()*10, p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Accurate Crosses", v(), p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Long Ball Acc. %", p(), p()), unsafe_allow_html=True)
        with c2:
            st.markdown(draw_stat("Accurate Long Balls", v(), p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Pass Accuracy %", p(), p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Cross Accuracy %", p(), p()), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="category-card"><div class="category-title">DEFENDING / DUELS</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(draw_stat("Tackles Won %", p(), p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Duels Won %", p(), p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Aerials Won", v(), p()), unsafe_allow_html=True)
        with c2:
            st.markdown(draw_stat("Aerials Won %", p(), p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Tackles Won", v(), p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Duels Won", v()*2, p()), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="category-card"><div class="category-title">POSSESSION</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(draw_stat("Successful Dribbles", v(), p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Dribble Success %", p(), p()), unsafe_allow_html=True)
            st.markdown(draw_stat("xT via Prog. Carries", v(), p()), unsafe_allow_html=True)
        with c2:
            st.markdown(draw_stat("Dribble Attempts", v(), p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Progressive Carries", v()*2, p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Carries Into Final ⅓", v(), p()), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


elif menu == "Stat Radar Comparison":
    st.subheader(f"🕸️ {secilen_oyuncu} - Radar Kıyaslaması ({secilen_sezon})")
    
    params = ['npxG', 'xA', 'Prog. Passes', 'Prog. Carries', 'Tackles', 'Int']
    p1_vals = [round(random.uniform(0.1, 0.5), 2) for _ in range(2)] + [round(random.uniform(2.0, 10.0), 1) for _ in range(4)]
    p2_vals = [round(random.uniform(0.1, 0.5), 2) for _ in range(2)] + [round(random.uniform(2.0, 10.0), 1) for _ in range(4)]
    low =  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    high = [0.6, 0.6, 12.0, 8.0, 6.0, 4.0]
    
    radar = Radar(params, low, high, round_int=[False]*6, num_rings=4, ring_width=1, center_circle_radius=1)
    fig, ax = radar.setup_axis(facecolor='#0b101c')
    
    radar.draw_circles(ax=ax, facecolor='#121927', edgecolor='#1f2937')
    radar.draw_radar(p1_vals, ax=ax, kwargs_radar={'facecolor': '#3b82f6', 'alpha': 0.6}, kwargs_rings={'alpha': 0})
    radar.draw_radar(p2_vals, ax=ax, kwargs_radar={'facecolor': '#ef4444', 'alpha': 0.6}, kwargs_rings={'alpha': 0})
    radar.draw_range_labels(ax=ax, fontsize=10, color='white')
    radar.draw_param_labels(ax=ax, fontsize=11, color='white')
    
    fig.text(0.15, 0.95, secilen_oyuncu, fontsize=14, color='#3b82f6', ha='center', weight='bold')
    fig.text(0.5, 0.95, "vs", fontsize=14, color='white', ha='center')
    fig.text(0.85, 0.95, "Lig Ortalaması", fontsize=14, color='#ef4444', ha='center', weight='bold')
    fig.patch.set_facecolor('#0b101c')
    
    add_watermark(fig)
    st.pyplot(fig)
    
    # Fotoğraf İndirme Butonu
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight", facecolor='#0b101c')
    buf.seek(0)
    st.download_button(label="📸 Radar Grafiğini İndir (Yüksek Çözünürlük)", data=buf, file_name=f"{secilen_oyuncu}_radar.png", mime="image/png")

elif menu == "Pizza Chart":
    st.subheader(f"🍕 {secilen_oyuncu} - Yüzdelik Grafiği ({secilen_sezon})")
    
    if oyuncu_verisi['Pozisyon'] in ["FW", "ST", "AM", "RW", "LW"]:
        params = ["Goals", "npxG", "Shots", "Touches Box", "xA", "Succ. Dribbles"]
        values = [p() for _ in range(6)]
    elif oyuncu_verisi['Pozisyon'] in ["CM", "DM"]:
        params = ["Prog. Passes", "Key Passes", "Pass Acc %", "Tackles", "Interceptions", "xT"]
        values = [p() for _ in range(6)]
    elif oyuncu_verisi['Pozisyon'] in ["CB", "FB"]:
        params = ["Aerials Won %", "Tackles Won", "Interceptions", "Clearances", "Prog. Carries", "Pass Acc %"]
        values = [p() for _ in range(6)]
    else:
        params = ["Saves", "Save %", "Crosses Stopped", "Def. Actions Outside Box", "Long Pass Acc", "Pass Acc"]
        values = [p() for _ in range(6)]
    
    baker = PyPizza(
        params=params, background_color="#0b101c", straight_line_color="#1f2937", straight_line_lw=1,             
        last_circle_lw=1, last_circle_color="#1f2937", other_circle_ls="-.", other_circle_lw=1               
    )
    
    fig, ax = baker.make_pizza(
        values, figsize=(10, 10), param_location=110,  
        kwargs_slices=dict(facecolor="#10b981", edgecolor="#0b101c", zorder=2, linewidth=1),
        kwargs_params=dict(color="white", fontsize=12, va="center", weight='bold'),
        kwargs_values=dict(color="white", fontsize=11, zorder=3, bbox=dict(edgecolor="white", facecolor="#121927", boxstyle="round,pad=0.2", lw=1))
    )
    
    fig.patch.set_facecolor('#0b101c')
    
    # Grafik başlığı (Oyuncu ismi ve metrik türü) grafiğin kendisine yazdırılıyor ki indirilen resimde görünsün
    fig.text(0.5, 0.98, f"{secilen_oyuncu} - {secilen_sezon}", size=18, ha="center", color="white", weight='bold')
    fig.text(0.5, 0.95, f"{oyuncu_verisi['Takim']} | {secilen_lig}", size=12, ha="center", color="#8b949e")
    
    add_watermark(fig)
    st.pyplot(fig)
    
    # Fotoğraf İndirme Butonu
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight", facecolor='#0b101c')
    buf.seek(0)
    st.download_button(label="📸 Pizza Grafiğini İndir (Yüksek Çözünürlük)", data=buf, file_name=f"{secilen_oyuncu}_pizza.png", mime="image/png")
