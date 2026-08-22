import streamlit as st
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
from mplsoccer import PyPizza, Radar

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pro Scout Dashboard", page_icon="📊", layout="wide")

# --- CSS (KUSURSUZ SİMETRİ VE KARANLIK TEMA) ---
st.markdown("""
<style>
    .stApp { background-color: #0b101c; color: white; }
    
    .header-box {
        background-color: #121927; padding: 20px; border-radius: 12px; 
        margin-bottom: 20px; border: 1px solid #1f2937;
        display: flex; justify-content: space-between; align-items: center;
    }
    
    .category-card {
        background-color: #121927; border-radius: 12px; padding: 25px 20px; 
        margin-bottom: 25px; border: 1px solid #1f2937; height: 100%;
    }
    
    .category-title {
        font-size: 13px; letter-spacing: 2px; margin-bottom: 25px; 
        color: #8b949e; font-weight: 600; text-transform: uppercase; text-align: left;
    }

    .stat-container { margin-bottom: 22px; }
    
    .stat-title {
        text-align: center; color: #e5e7eb; font-size: 12px; margin-bottom: 8px; font-weight: 500;
    }
    
    .bar-bg {
        width: 100%; height: 6px; background-color: #1f2937; 
        border-radius: 3px; margin-bottom: 8px;
    }
    
    .bar-fill { height: 100%; border-radius: 3px; }
    
    .stat-values {
        display: flex; justify-content: space-between; align-items: center; font-size: 11px;
    }
    
    .badge {
        padding: 3px 8px; border-radius: 12px; border: 1px solid; 
        font-weight: 600; font-size: 9px; letter-spacing: 0.5px;
    }

    /* Renk Paleti */
    .elite-color { background-color: #10b981; } .elite-badge { color: #10b981; border-color: #10b981; }
    .above-color { background-color: #3b82f6; } .above-badge { color: #3b82f6; border-color: #3b82f6; }
    .avg-color { background-color: #6b7280; } .avg-badge { color: #6b7280; border-color: #6b7280; }
    .below-color { background-color: #f59e0b; } .below-badge { color: #f59e0b; border-color: #f59e0b; }
    .poor-color { background-color: #ef4444; } .poor-badge { color: #ef4444; border-color: #ef4444; }
</style>
""", unsafe_allow_html=True)

# --- VERİTABANI SİMÜLASYONU (Bunu ileride kendi Excel'in ile değiştirebilirsin) ---
@st.cache_data
def load_database():
    # Bu veritabanı mantığı sayesinde Lig -> Takım -> Oyuncu filtrelemesi kusursuz çalışır
    data = {
        "Lig": ["Turkish Super Lig", "Turkish Super Lig", "English Premier League", "English Premier League", "Veikkausliiga"],
        "Takim": ["Trabzonspor", "Trabzonspor", "Liverpool", "Liverpool", "SJK"],
        "Oyuncu": ["Uğurcan Çakır", "Batagov", "Mohamed Salah", "Alexis Mac Allister", "Aapo Boström"],
        "Pozisyon": ["GK", "CB", "FW", "CM", "CM"],
        "Ulke": ["🇹🇷", "🇺🇦", "🇪🇬", "🇦🇷", "🇫🇮"],
        "Sezon": ["2025/2026", "2025/2026", "2025/2026", "2025/2026", "2024"],
        "Dakika": [2150, 1800, 2400, 2100, 907],
        "Logo": [
            "https://upload.wikimedia.org/wikipedia/tr/a/ab/TrabzonsporAmblemi.png",
            "https://upload.wikimedia.org/wikipedia/tr/a/ab/TrabzonsporAmblemi.png",
            "https://upload.wikimedia.org/wikipedia/en/0/0c/Liverpool_FC.svg",
            "https://upload.wikimedia.org/wikipedia/en/0/0c/Liverpool_FC.svg",
            "https://upload.wikimedia.org/wikipedia/en/c/c5/SJK_logo.png"
        ]
    }
    return pd.DataFrame(data)

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

# --- SOL MENÜ (DİNAMİK FİLTRELEME) ---
st.sidebar.title("🔍 Kapsamlı Scout Paneli")
st.sidebar.markdown("---")

# 1. Lig Seçimi
ligler = df['Lig'].unique().tolist()
secilen_lig = st.sidebar.selectbox("🌍 Lig Seçin", ligler)

# 2. Seçilen Lige Göre Takım Seçimi
takimlar = df[df['Lig'] == secilen_lig]['Takim'].unique().tolist()
secilen_takim = st.sidebar.selectbox("🏠 Takım Seçin", takimlar)

# 3. Seçilen Takıma Göre Oyuncu Seçimi
oyuncular = df[(df['Lig'] == secilen_lig) & (df['Takim'] == secilen_takim)]['Oyuncu'].unique().tolist()
secilen_oyuncu = st.sidebar.selectbox("👤 Oyuncu Seçin", oyuncular)

# Seçilen oyuncunun bilgilerini DataFrame'den çekme
oyuncu_verisi = df[df['Oyuncu'] == secilen_oyuncu].iloc[0]

st.sidebar.markdown("---")
menu = st.sidebar.radio("📌 Navigasyon", ["Player Stats", "Stat Radar Comparison", "Pizza Chart"])

# Demoluk rastgele ama tutarlı istatistik üreteci (Gerçek veriye bağlayana kadar güzel görünmesi için)
random.seed(len(secilen_oyuncu)) 
p = lambda: random.randint(10, 99)
v = lambda: round(random.uniform(0.1, 5.0), 2)

# --- ANA EKRAN İÇERİKLERİ ---
if menu == "Player Stats":
    # PROFESYONEL VE SİMETRİK ÜST BİLGİ KARTI
    st.markdown(f"""
    <div class="header-box">
        <div style="display: flex; align-items: center;">
            <img src="{oyuncu_verisi['Logo']}" width="65" style="margin-right: 20px; object-fit: contain;">
            <div>
                <h1 style="margin:0; font-size: 32px;">{secilen_oyuncu} <span style="font-size: 24px;">{oyuncu_verisi['Ulke']}</span></h1>
                <p style="margin:5px 0 0 0; color: #8b949e; font-size: 14px;">{oyuncu_verisi['Sezon']} Sezonu | {oyuncu_verisi['Lig']} | Percentile rank vs. positional peers</p>
            </div>
        </div>
        <div style="text-align: right; font-size: 13px; color: #d1d5db;">
            <div style="margin-bottom: 8px;">
                <span style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 15px; margin-right: 5px;">{oyuncu_verisi['Takim']}</span> 
                <span style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 15px; color:#10b981;">{oyuncu_verisi['Pozisyon']}</span>
            </div>
            <div>
                <span style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 15px; margin-right: 5px;">Age: 20</span> 
                <span style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 15px;">{oyuncu_verisi['Dakika']} min.</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2 KOLONLU NİZAMİ YAPI (Her satır eşit yükseklikte)
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

    with col2:
        st.markdown('<div class="category-card"><div class="category-title">PLAYMAKING</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(draw_stat("Assists", v(), p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Key Passes", v(), p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Progressive Passes", v()*2, p()), unsafe_allow_html=True)
        with c2:
            st.markdown(draw_stat("xA", v(), p()), unsafe_allow_html=True)
            st.markdown(draw_stat("xT via Live Passes", v(), p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Passes Into Final 3rd", v()*2, p()), unsafe_allow_html=True)
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

        st.markdown('<div class="category-card"><div class="category-title">OTHER</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(draw_stat("Interceptions", v(), p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Passes in Opp. Half", v()*10, p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Total Shots", v(), p()), unsafe_allow_html=True)
        with c2:
            st.markdown(draw_stat("Fouls Drawn", v(), p()), unsafe_allow_html=True)
            st.markdown(draw_stat("Forward Passes", v()*5, p()), unsafe_allow_html=True)
            st.markdown(draw_stat("On Target %", p(), p()), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


elif menu == "Stat Radar Comparison":
    st.subheader(f"🕸️ {secilen_oyuncu} - Radar Kıyaslaması")
    st.write("Radar grafiği hatası çözüldü, veriler sorunsuz çiziliyor.")
    
    params = ['npxG', 'xA', 'Prog. Passes', 'Prog. Carries', 'Tackles', 'Int']
    p1_vals = [0.25, 0.20, 6.5, 3.2, 2.8, 1.5]
    p2_vals = [0.12, 0.15, 4.1, 2.1, 1.5, 1.1]
    low =  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    high = [0.5, 0.5, 10.0, 6.0, 5.0, 3.0]
    
    radar = Radar(params, low, high, round_int=[False]*6, num_rings=4, ring_width=1, center_circle_radius=1)
    fig, ax = radar.setup_axis(facecolor='#0b101c')
    
    # HATA DÜZELTİLDİ: draw_circles tek başına çağrıldı, values beklenmiyor.
    radar.draw_circles(ax=ax, facecolor='#121927', edgecolor='#1f2937')
    radar.draw_radar(p1_vals, ax=ax, kwargs_radar={'facecolor': '#3b82f6', 'alpha': 0.6}, kwargs_rings={'alpha': 0})
    radar.draw_radar(p2_vals, ax=ax, kwargs_radar={'facecolor': '#ef4444', 'alpha': 0.6}, kwargs_rings={'alpha': 0})
    radar.draw_range_labels(ax=ax, fontsize=10, color='white')
    radar.draw_param_labels(ax=ax, fontsize=11, color='white')
    
    fig.text(0.15, 0.95, secilen_oyuncu, fontsize=14, color='#3b82f6', ha='center', weight='bold')
    fig.text(0.5, 0.95, "vs", fontsize=14, color='white', ha='center')
    fig.text(0.85, 0.95, "Lig Ortalaması", fontsize=14, color='#ef4444', ha='center', weight='bold')
    fig.patch.set_facecolor('#0b101c')
    
    st.pyplot(fig)


elif menu == "Pizza Chart":
    st.subheader(f"🍕 {secilen_oyuncu} - Yüzdelik (Percentile) Grafiği")
    st.write(f"Mevki ({oyuncu_verisi['Pozisyon']}) tabanlı önemli KPI metrikleri.")
    
    # MEVKİYE GÖRE DİNAMİK KPI METRİKLERİ (Pizza chart için)
    if oyuncu_verisi['Pozisyon'] in ["FW", "ST", "AM"]:
        params = ["Goals", "npxG", "Shots", "Touches Box", "xA", "Succ. Dribbles"]
        values = [85, 80, 75, 90, 60, 70]
    elif oyuncu_verisi['Pozisyon'] in ["CM", "DM"]:
        params = ["Prog. Passes", "Key Passes", "Pass Acc %", "Tackles", "Interceptions", "xT"]
        values = [88, 75, 92, 60, 55, 80]
    elif oyuncu_verisi['Pozisyon'] in ["CB", "FB"]:
        params = ["Aerials Won %", "Tackles Won", "Interceptions", "Clearances", "Prog. Carries", "Pass Acc %"]
        values = [90, 85, 80, 75, 60, 70]
    else: # Kaleci vs için
        params = ["Saves", "Save %", "Crosses Stopped", "Def. Actions Outside Box", "Long Pass Acc", "Pass Acc"]
        values = [80, 85, 70, 65, 75, 60]
    
    # GRAFİK BOYUTU BÜYÜTÜLDÜ: figsize=(12, 12) yapıldı
    baker = PyPizza(
        params=params,                  
        background_color="#0b101c",     
        straight_line_color="#1f2937",  
        straight_line_lw=1,             
        last_circle_lw=1,               
        last_circle_color="#1f2937",    
        other_circle_ls="-.",           
        other_circle_lw=1               
    )
    
    fig, ax = baker.make_pizza(
        values,              
        figsize=(10, 10),  # Daha büyük ve okunaklı
        param_location=110,  
        kwargs_slices=dict(facecolor="#10b981", edgecolor="#0b101c", zorder=2, linewidth=1),
        kwargs_params=dict(color="white", fontsize=12, va="center", weight='bold'),
        kwargs_values=dict(
            color="white", fontsize=11, zorder=3,
            bbox=dict(edgecolor="white", facecolor="#121927", boxstyle="round,pad=0.2", lw=1)
        )
    )
    
    fig.patch.set_facecolor('#0b101c')
    st.pyplot(fig)
