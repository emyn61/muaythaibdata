import streamlit as st
import pandas as pd
import numpy as np

# Sayfa ayarlarını yapıyoruz (Geniş ekran ve koyu tema hissi)
st.set_page_config(page_title="Scout Dashboard - Per90 Style", page_icon="⚽", layout="wide")

# --- ÖZEL CSS İLE GÖRSELDEKİ ARAYÜZÜ YARATMA ---
# Streamlit'in arka planını koyu lacivert/gri yapıp kutuları şekillendiriyoruz
st.markdown("""
<style>
    /* Ana arka plan (Görseldeki gibi koyu lacivert tonu) */
    .stApp {
        background-color: #0b101c;
    }
    
    /* Üst taraftaki oyuncu başlık alanı */
    .header-box {
        background-color: #121927;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #1f2937;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Kategori Kartları (OUTPUT, PLAYMAKING vb.) */
    .category-card {
        background-color: #121927;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #1f2937;
        color: #8b949e;
    }
    
    .category-title {
        font-size: 12px;
        letter-spacing: 2px;
        margin-bottom: 20px;
        color: #8b949e;
        font-weight: 600;
        text-transform: uppercase;
    }

    /* Tekil İstatistik Kutusu */
    .stat-container {
        margin-bottom: 15px;
    }
    
    .stat-header {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        color: white;
        margin-bottom: 5px;
    }

    /* İlerleme Çubuğu (Percentile Bar) */
    .bar-bg {
        width: 100%;
        height: 6px;
        background-color: #1f2937;
        border-radius: 3px;
        overflow: hidden;
        margin-bottom: 5px;
    }
    
    .bar-fill {
        height: 100%;
        border-radius: 3px;
    }

    /* Etiketler (Elite, Above Avg, Poor vb.) */
    .badge {
        font-size: 10px;
        padding: 2px 6px;
        border-radius: 12px;
        border: 1px solid;
        letter-spacing: 0.5px;
    }
    
    /* Renk Sınıfları */
    .elite-color { background-color: #00ff00; }
    .elite-badge { color: #00ff00; border-color: #00ff00; }
    
    .above-color { background-color: #1e90ff; }
    .above-badge { color: #1e90ff; border-color: #1e90ff; }
    
    .avg-color { background-color: #808080; }
    .avg-badge { color: #808080; border-color: #808080; }
    
    .below-color { background-color: #ffa500; }
    .below-badge { color: #ffa500; border-color: #ffa500; }
    
    .poor-color { background-color: #ff0000; }
    .poor-badge { color: #ff0000; border-color: #ff0000; }
</style>
""", unsafe_allow_html=True)

# --- YARDIMCI HTML FONKSİYONU ---
def draw_stat_bar(title, value_per_90, percentile):
    """Görseldeki istatistik barını HTML/CSS ile çizer"""
    
    # Yüzdeliğe göre renk ve rozet (Badge) belirleme
    if percentile >= 85:
        bar_class = "elite-color"
        badge_class = "elite-badge"
        badge_text = "ELITE"
    elif percentile >= 65:
        bar_class = "above-color"
        badge_class = "above-badge"
        badge_text = "ABOVE AVG"
    elif percentile >= 35:
        bar_class = "avg-color"
        badge_class = "avg-badge"
        badge_text = "AVERAGE"
    elif percentile >= 15:
        bar_class = "below-color"
        badge_class = "below-badge"
        badge_text = "BELOW AVG"
    else:
        bar_class = "poor-color"
        badge_class = "poor-badge"
        badge_text = "POOR"

    # HTML Çıktısı
    html = f"""
    <div class="stat-container">
        <div style="text-align: center; color: white; font-size: 13px; margin-bottom: 5px;">{title}</div>
        <div class="bar-bg">
            <div class="bar-fill {bar_class}" style="width: {percentile}%;"></div>
        </div>
        <div class="stat-header">
            <span>{value_per_90:.2f}/90 <span style="color:#8b949e; font-size:11px;">({percentile}%)</span></span>
            <span class="badge {badge_class}">{badge_text}</span>
        </div>
    </div>
    """
    return html

# --- SAHTE VERİ (Gerçek veri yerine tasarımı göstermek için) ---
oyuncu_adi = "Muhammed Emin Küçükkaya" # Aapo Boström tarzı başlık
oyuncu_takim = "Trabzonspor"
oyuncu_pozisyon = "DM/CM"
oyuncu_yas = "20 y/o"
oyuncu_dakika = "1450 min. played"

# --- ÜST BAŞLIK ALANI (HEADER) ---
st.markdown(f"""
<div class="header-box">
    <div>
        <h1 style="margin:0; font-size: 32px;">{oyuncu_adi}</h1>
        <p style="margin:0; color: #8b949e; font-size: 14px;">Percentile rank vs. league's positional peers</p>
    </div>
    <div style="text-align: right; font-size: 12px;">
        <div style="margin-bottom: 5px;"><span style="border: 1px solid #30363d; padding: 4px 10px; border-radius: 15px; margin-right: 5px;">{oyuncu_takim}</span> <span style="border: 1px solid #30363d; padding: 4px 10px; border-radius: 15px;">{oyuncu_pozisyon}</span></div>
        <div><span style="border: 1px solid #30363d; padding: 4px 10px; border-radius: 15px; margin-right: 5px;">{oyuncu_yas}</span> <span style="border: 1px solid #30363d; padding: 4px 10px; border-radius: 15px;">{oyuncu_dakika}</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 2 KOLONLU IZGARA (GRID) YAPISI ---
col1, col2 = st.columns(2, gap="large")

with col1:
    # --- OUTPUT KUTUSU ---
    st.markdown('<div class="category-card">', unsafe_allow_html=True)
    st.markdown('<div class="category-title">OUTPUT</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(draw_stat_bar("Goals", 0.00, 18), unsafe_allow_html=True)
        st.markdown(draw_stat_bar("Shots On Target", 0.30, 41), unsafe_allow_html=True)
        st.markdown(draw_stat_bar("Shots Inside Box", 0.30, 24), unsafe_allow_html=True)
    with c2:
        st.markdown(draw_stat_bar("npxG", 0.06, 28), unsafe_allow_html=True)
        st.markdown(draw_stat_bar("Created Own Shot", 0.40, 57), unsafe_allow_html=True)
        st.markdown(draw_stat_bar("Touches In Opp. Box", 0.79, 19), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- PASSING KUTUSU ---
    st.markdown('<div class="category-card">', unsafe_allow_html=True)
    st.markdown('<div class="category-title">PASSING</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(draw_stat_bar("Accurate Passes", 48.92, 80), unsafe_allow_html=True)
        st.markdown(draw_stat_bar("Accurate Crosses", 0.30, 48), unsafe_allow_html=True)
        st.markdown(draw_stat_bar("Long Ball Accuracy %", 52.50, 59), unsafe_allow_html=True)
    with c2:
        st.markdown(draw_stat_bar("Accurate Long Balls", 2.08, 61), unsafe_allow_html=True)
        st.markdown(draw_stat_bar("Pass Accuracy %", 87.41, 76), unsafe_allow_html=True)
        st.markdown(draw_stat_bar("Cross Accuracy %", 15.79, 28), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- DEFENDING / DUELS KUTUSU ---
    st.markdown('<div class="category-card">', unsafe_allow_html=True)
    st.markdown('<div class="category-title">DEFENDING/DUELS</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(draw_stat_bar("Tackles Won %", 63.89, 69), unsafe_allow_html=True)
        st.markdown(draw_stat_bar("Duels Won %", 57.66, 91), unsafe_allow_html=True)
    with c2:
        st.markdown(draw_stat_bar("Aerials Won %", 53.85, 80), unsafe_allow_html=True)
        st.markdown(draw_stat_bar("Tackles Won", 2.28, 98), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # --- PLAYMAKING KUTUSU ---
    st.markdown('<div class="category-card">', unsafe_allow_html=True)
    st.markdown('<div class="category-title">PLAYMAKING</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(draw_stat_bar("Assists", 0.00, 21), unsafe_allow_html=True)
        st.markdown(draw_stat_bar("Key Passes", 1.19, 61), unsafe_allow_html=True)
        st.markdown(draw_stat_bar("Progressive Passes", 5.36, 78), unsafe_allow_html=True)
    with c2:
        st.markdown(draw_stat_bar("xA", 0.08, 54), unsafe_allow_html=True)
        st.markdown(draw_stat_bar("xT via Live Passes", 0.15, 74), unsafe_allow_html=True)
        st.markdown(draw_stat_bar("Passes Into Final 3rd", 4.86, 78), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- POSSESSION KUTUSU ---
    st.markdown('<div class="category-card">', unsafe_allow_html=True)
    st.markdown('<div class="category-title">POSSESSION</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(draw_stat_bar("Successful Dribbles", 0.69, 67), unsafe_allow_html=True)
        st.markdown(draw_stat_bar("Dribble Success %", 50.00, 62), unsafe_allow_html=True)
        st.markdown(draw_stat_bar("xT via Progressive Carries", 0.03, 39), unsafe_allow_html=True)
    with c2:
        st.markdown(draw_stat_bar("Dribble Attempts", 1.39, 63), unsafe_allow_html=True)
        st.markdown(draw_stat_bar("Progressive Carries", 1.59, 48), unsafe_allow_html=True)
        st.markdown(draw_stat_bar("Carries Into Final 1/3", 0.89, 67), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- OTHER KUTUSU ---
    st.markdown('<div class="category-card">', unsafe_allow_html=True)
    st.markdown('<div class="category-title">OTHER</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(draw_stat_bar("Interceptions", 0.60, 28), unsafe_allow_html=True)
        st.markdown(draw_stat_bar("Passes in Opp. Half", 26.49, 81), unsafe_allow_html=True)
    with c2:
        st.markdown(draw_stat_bar("Fouls Drawn", 1.39, 61), unsafe_allow_html=True)
        st.markdown(draw_stat_bar("Forward Passes", 25.01, 89), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
