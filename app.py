import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import PyPizza, Radar

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pro Scout Dashboard", page_icon="📊", layout="wide")

# --- CSS (GÖRSELDEKİ KARANLIK TEMA VE KUTU TASARIMLARI) ---
st.markdown("""
<style>
    .stApp { background-color: #0b101c; color: white; }
    
    .header-box {
        background-color: #121927; padding: 20px; border-radius: 10px; 
        margin-bottom: 20px; border: 1px solid #1f2937;
        display: flex; justify-content: space-between; align-items: center;
    }
    
    .category-card {
        background-color: #121927; border-radius: 12px; padding: 20px; 
        margin-bottom: 20px; border: 1px solid #1f2937;
    }
    
    .category-title {
        font-size: 13px; letter-spacing: 2px; margin-bottom: 25px; 
        color: #8b949e; font-weight: 600; text-transform: uppercase;
    }

    .stat-container { margin-bottom: 20px; }
    
    .stat-title {
        text-align: center; color: #e5e7eb; font-size: 12px; margin-bottom: 8px;
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
        padding: 2px 8px; border-radius: 12px; border: 1px solid; 
        font-weight: 600; font-size: 9px; letter-spacing: 0.5px;
    }

    .elite-color { background-color: #10b981; }
    .elite-badge { color: #10b981; border-color: #10b981; }
    
    .above-color { background-color: #3b82f6; }
    .above-badge { color: #3b82f6; border-color: #3b82f6; }
    
    .avg-color { background-color: #6b7280; }
    .avg-badge { color: #6b7280; border-color: #6b7280; }
    
    .below-color { background-color: #f59e0b; }
    .below-badge { color: #f59e0b; border-color: #f59e0b; }
    
    .poor-color { background-color: #ef4444; }
    .poor-badge { color: #ef4444; border-color: #ef4444; }
</style>
""", unsafe_allow_html=True)

# --- STAT BAR ÇİZİCİ FONKSİYON ---
def draw_stat(title, value, percentile):
    if percentile >= 85:
        b_class, bdg_class, text = "elite-color", "elite-badge", "ELITE"
    elif percentile >= 65:
        b_class, bdg_class, text = "above-color", "above-badge", "ABOVE AVG"
    elif percentile >= 35:
        b_class, bdg_class, text = "avg-color", "avg-badge", "AVERAGE"
    elif percentile >= 15:
        b_class, bdg_class, text = "below-color", "below-badge", "BELOW AVG"
    else:
        b_class, bdg_class, text = "poor-color", "poor-badge", "POOR"

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

# --- SOL MENÜ (SIDEBAR) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/53/53283.png", width=50) # Opsiyonel logo
st.sidebar.title("Scout Paneli")

top_30_leagues = [
    "English Premier League", "Spanish La Liga", "Italian Serie A", "German Bundesliga", "French Ligue 1",
    "Turkish Super Lig", "Dutch Eredivisie", "Portuguese Primeira Liga", "Belgian Pro League", "Brazilian Serie A",
    "Argentine Primera", "Championship (ENG)", "MLS (USA)", "Liga MX (MEX)", "Russian Premier League",
    "Scottish Premiership", "Austrian Bundesliga", "Swiss Super League", "Danish Superliga", "Swedish Allsvenskan",
    "Norwegian Eliteserien", "Serbian SuperLiga", "Croatian HNL", "Greek Super League", "Czech First League",
    "Polish Ekstraklasa", "Colombian Primera A", "Uruguayan Primera", "J1 League (JPN)", "K League 1 (KOR)"
]

secilen_lig = st.sidebar.selectbox("🌍 Lig Seçimi (Top 30)", top_30_leagues, index=21) # Sırbistan varsayılan
secilen_takim = st.sidebar.text_input("🏠 Takım:", "First Team")
secilen_oyuncu = st.sidebar.text_input("👤 Oyuncu Ara:", "Andrej Vasovic")

st.sidebar.markdown("---")
# İSTENİLEN SEKMELER
menu = st.sidebar.radio("📌 Navigasyon", ["Player Stats", "Stat Radar Comparison", "Pizza Chart"])

# --- ANA EKRAN İÇERİKLERİ ---
if menu == "Player Stats":
    # GÖRSELDEKİ ÜST BİLGİ KARTININ AYNISI
    st.markdown(f"""
    <div class="header-box">
        <div>
            <div style="display:flex; align-items:center;">
                <h1 style="margin:0; font-size: 36px;">{secilen_oyuncu}</h1>
            </div>
            <p style="margin:2px 0 0 0; color: #8b949e; font-size: 13px;">Percentile rank vs. league's positional peers</p>
        </div>
        <div style="text-align: right; font-size: 12px; color: #d1d5db;">
            <div style="margin-bottom: 8px;">
                <span style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 15px; margin-right: 5px;">{secilen_lig}</span> 
                <span style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 15px;">DM/CM</span>
            </div>
            <div>
                <span style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 15px; margin-right: 5px;">20 y/o</span> 
                <span style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 15px;">907 min. played</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2 KOLONLU YAPI
    col1, col2 = st.columns(2, gap="large")

    with col1:
        # 1. OUTPUT
        st.markdown('<div class="category-card"><div class="category-title">OUTPUT</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(draw_stat("Goals", 0.00, 18), unsafe_allow_html=True)
            st.markdown(draw_stat("Shots On Target", 0.30, 41), unsafe_allow_html=True)
            st.markdown(draw_stat("Shots Inside Box", 0.30, 24), unsafe_allow_html=True)
        with c2:
            st.markdown(draw_stat("npxG", 0.06, 28), unsafe_allow_html=True)
            st.markdown(draw_stat("Created Own Shot", 0.40, 57), unsafe_allow_html=True)
            st.markdown(draw_stat("Touches In Opp. Box", 0.79, 19), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 3. PASSING
        st.markdown('<div class="category-card"><div class="category-title">PASSING</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(draw_stat("Accurate Passes", 48.92, 80), unsafe_allow_html=True)
            st.markdown(draw_stat("Accurate Crosses", 0.30, 48), unsafe_allow_html=True)
            st.markdown(draw_stat("Long Ball Accuracy %", 52.50, 59), unsafe_allow_html=True)
        with c2:
            st.markdown(draw_stat("Accurate Long Balls", 2.08, 61), unsafe_allow_html=True)
            st.markdown(draw_stat("Pass Accuracy %", 87.41, 76), unsafe_allow_html=True)
            st.markdown(draw_stat("Cross Accuracy %", 15.79, 28), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 5. DEFENDING/DUELS
        st.markdown('<div class="category-card"><div class="category-title">DEFENDING/DUELS</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(draw_stat("Tackles Won %", 63.89, 69), unsafe_allow_html=True)
            st.markdown(draw_stat("Duels Won %", 57.66, 91), unsafe_allow_html=True)
            st.markdown(draw_stat("Aerials Won", 0.69, 61), unsafe_allow_html=True)
        with c2:
            st.markdown(draw_stat("Aerials Won %", 53.85, 80), unsafe_allow_html=True)
            st.markdown(draw_stat("Tackles Won", 2.28, 100), unsafe_allow_html=True)
            st.markdown(draw_stat("Duels Won", 6.35, 96), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # 2. PLAYMAKING
        st.markdown('<div class="category-card"><div class="category-title">PLAYMAKING</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(draw_stat("Assists", 0.00, 21), unsafe_allow_html=True)
            st.markdown(draw_stat("Key Passes", 1.19, 61), unsafe_allow_html=True)
            st.markdown(draw_stat("Progressive Passes", 5.36, 78), unsafe_allow_html=True)
        with c2:
            st.markdown(draw_stat("xA", 0.08, 54), unsafe_allow_html=True)
            st.markdown(draw_stat("xT via Live Passes", 0.15, 74), unsafe_allow_html=True)
            st.markdown(draw_stat("Passes Into Final 3rd", 4.86, 78), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 4. POSSESSION
        st.markdown('<div class="category-card"><div class="category-title">POSSESSION</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(draw_stat("Successful Dribbles", 0.69, 67), unsafe_allow_html=True)
            st.markdown(draw_stat("Dribble Success %", 50.00, 62), unsafe_allow_html=True)
            st.markdown(draw_stat("xT via Progressive Carries", 0.03, 39), unsafe_allow_html=True)
        with c2:
            st.markdown(draw_stat("Dribble Attempts", 1.39, 63), unsafe_allow_html=True)
            st.markdown(draw_stat("Progressive Carries", 1.59, 48), unsafe_allow_html=True)
            st.markdown(draw_stat("Carries Into Final ⅓", 0.89, 67), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 6. OTHER
        st.markdown('<div class="category-card"><div class="category-title">OTHER</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(draw_stat("Interceptions", 0.60, 28), unsafe_allow_html=True)
            st.markdown(draw_stat("Passes in Opp. Half", 26.49, 81), unsafe_allow_html=True)
            st.markdown(draw_stat("Total Shots", 0.69, 20), unsafe_allow_html=True)
        with c2:
            st.markdown(draw_stat("Fouls Drawn", 1.39, 61), unsafe_allow_html=True)
            st.markdown(draw_stat("Forward Passes", 25.01, 89), unsafe_allow_html=True)
            st.markdown(draw_stat("On Target %", 42.86, 84), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


elif menu == "Stat Radar Comparison":
    st.subheader("🕸️ Radar Comparison")
    st.write("İki oyuncunun metriklerini kıyaslayın.")
    
    # Radar grafiği parametreleri
    params = ['npxG', 'xA', 'Prog. Passes', 'Prog. Carries', 'Tackles Won', 'Int']
    p1_vals = [0.06, 0.08, 5.36, 1.59, 2.28, 0.60]
    p2_vals = [0.12, 0.15, 6.10, 2.10, 1.50, 1.10]
    
    low =  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    high = [0.3, 0.3, 10.0, 5.0, 4.0, 2.5]
    
    radar = Radar(params, low, high, round_int=[False]*6, num_rings=4, ring_width=1, center_circle_radius=1)
    
    fig, ax = radar.setup_axis(facecolor='#0b101c')
    rings_inner, rings_outer = radar.draw_circles(ax=ax, facecolor='#121927', edgecolor='#1f2937')
    radar.draw_radar(p1_vals, ax=ax, kwargs_radar={'facecolor': '#3b82f6', 'alpha': 0.6}, kwargs_rings={'alpha': 0})
    radar.draw_radar(p2_vals, ax=ax, kwargs_radar={'facecolor': '#ef4444', 'alpha': 0.6}, kwargs_rings={'alpha': 0})
    radar.draw_range_labels(ax=ax, fontsize=10, color='white')
    radar.draw_param_labels(ax=ax, fontsize=11, color='white')
    
    # Başlıklar
    fig.text(0.15, 0.95, secilen_oyuncu, fontsize=14, color='#3b82f6', ha='center')
    fig.text(0.5, 0.95, "vs", fontsize=14, color='white', ha='center')
    fig.text(0.85, 0.95, "Rakip Oyuncu", fontsize=14, color='#ef4444', ha='center')
    
    fig.patch.set_facecolor('#0b101c')
    st.pyplot(fig)


elif menu == "Pizza Chart":
    st.subheader("🍕 Percentile Pizza Chart")
    st.write("Oyuncunun yüzdelik dilimlerini (Percentile) görselleştirin.")
    
    params = ["npxG", "xA", "Key Passes", "Prog. Passes", "Succ. Dribbles", "Duels Won %"]
    values = [28, 54, 61, 78, 67, 91] # Görseldeki yüzdelik (percentile) değerleri
    
    # Pizza Chart çizimi
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
        figsize=(8, 8),      
        param_location=110,  
        kwargs_slices=dict(
            facecolor="#3b82f6", edgecolor="#0b101c", zorder=2, linewidth=1
        ),
        kwargs_params=dict(
            color="white", fontsize=11, va="center"
        ),
        kwargs_values=dict(
            color="white", fontsize=11, zorder=3,
            bbox=dict(edgecolor="white", facecolor="#121927", boxstyle="round,pad=0.2", lw=1)
        )
    )
    
    fig.patch.set_facecolor('#0b101c')
    st.pyplot(fig)
