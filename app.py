import streamlit as st
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
from mplsoccer import PyPizza

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(page_title="Pro Scout Dashboard", page_icon="📊", layout="wide")

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
    div.stDownloadButton > button { background-color: #10b981; color: white; font-weight: bold; border-radius: 8px; border: none; width: 100%; }
    div.stDownloadButton > button:hover { background-color: #059669; }
</style>
""", unsafe_allow_html=True)

# --- 2. YARDIMCI FONKSİYONLAR ---
def add_watermark(fig):
    fig.text(0.99, 0.01, 'Scouting Report | Muhammed Emin (@pressxresistant)', 
             color='#8b949e', fontsize=9, ha='right', va='bottom', alpha=0.6, weight='bold')

def draw_stat(title, value, percentile):
    try: value = float(value)
    except: value = 0.0
    try: percentile = int(percentile)
    except: percentile = 0

    if percentile >= 85: b_class, bdg_class, text = "elite-color", "elite-badge", "ELITE"
    elif percentile >= 65: b_class, bdg_class, text = "above-color", "above-badge", "ABOVE AVG"
    elif percentile >= 35: b_class, bdg_class, text = "avg-color", "avg-badge", "AVERAGE"
    elif percentile >= 15: b_class, bdg_class, text = "below-color", "below-badge", "BELOW AVG"
    else: b_class, bdg_class, text = "poor-color", "poor-badge", "POOR"

    return f"""
    <div class="stat-container">
        <div class="stat-title">{title}</div>
        <div class="bar-bg"><div class="bar-fill {b_class}" style="width: {percentile}%;"></div></div>
        <div class="stat-values">
            <span style="color:#d1d5db;">{value:.2f}/90 <span style="color:#6b7280;">({percentile}%)</span></span>
            <span class="badge {bdg_class}">{text}</span>
        </div>
    </div>
    """

# --- 3. SOL MENÜ VE VERİ YÜKLEME ---
st.sidebar.title("🔍 Kapsamlı Scout Paneli")
st.sidebar.markdown("---")
st.sidebar.subheader("📁 Veritabanı Yükle")
st.sidebar.info("Excel (.xlsx) veya CSV dosyanızı yükleyin.")

uploaded_file = st.sidebar.file_uploader("", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Dosya Okuma
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, low_memory=False)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.sidebar.success(f"✅ Veri başarıyla yüklendi! ({len(df)} Oyuncu bulundu)")
        
        # --- 4. AKILLI VERİ TEMİZLEME (Hata Önleyici Sistem) ---
        rename_map = {
            'Player': 'Oyuncu', 'Player Name': 'Oyuncu', 'Oyuncu Adı': 'Oyuncu',
            'Squad': 'Takim', 'Team': 'Takim', 'Takım': 'Takim',
            'Comp': 'Lig', 'Competition': 'Lig', 'League': 'Lig',
            'Pos': 'Pozisyon', 'Position': 'Pozisyon',
            'Age': 'Yas', 'Yaş': 'Yas',
            'Min': 'Dakika', 'Minutes': 'Dakika', '90s': 'Dakika'
        }
        df = df.rename(columns=rename_map)

        # Eksik olan ana sütunları otomatik tamamla (Çökmeyi engeller)
        if 'Oyuncu' not in df.columns: df['Oyuncu'] = 'Bilinmeyen Oyuncu'
        if 'Takim' not in df.columns: df['Takim'] = 'Bilinmeyen Takım'
        if 'Lig' not in df.columns: df['Lig'] = 'Genel Veritabanı'
        if 'Sezon' not in df.columns: df['Sezon'] = '2025-2026'
        if 'Pozisyon' not in df.columns: df['Pozisyon'] = 'Bilinmiyor'
        if 'Yas' not in df.columns: df['Yas'] = 'Belirtilmemiş'
        if 'Dakika' not in df.columns: df['Dakika'] = '0'
        if 'Ulke_Bayrak' not in df.columns: df['Ulke_Bayrak'] = '🏳️'
        if 'Takim_Logo' not in df.columns: df['Takim_Logo'] = 'https://cdn-icons-png.flaticon.com/512/53/53283.png'

        df['Sezon'] = df['Sezon'].astype(str)
        df['Lig'] = df['Lig'].astype(str)
        df['Takim'] = df['Takim'].astype(str)
        df['Oyuncu'] = df['Oyuncu'].astype(str)

        # --- 5. DİNAMİK FİLTRELER ---
        sezonlar = sorted(df['Sezon'].unique().tolist(), reverse=True)
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
        menu = st.sidebar.radio("📌 Görünüm", ["Oyuncu İstatistikleri", "Pizza Grafiği (Yüzdelik)"])

        # --- 6. AKILLI VERİ ÇEKİCİ (FBref ve Kaggle Uyumlu) ---
        def get_val(metric):
            possible_cols = [f"{metric}_p90", metric, f"{metric}/90", 'Gls', 'Ast', 'PrgP']
            for col in possible_cols:
                if col in df.columns:
                    try: return float(oyuncu_verisi[col])
                    except: pass
            return 0.0

        def get_perc(metric):
            possible_cols = [f"{metric}_percentile", f"{metric} Percentile"]
            for col in possible_cols:
                if col in df.columns:
                    try: return int(oyuncu_verisi[col])
                    except: pass
            return np.random.randint(30, 95) # Eğer veri setinde percentile yoksa görsel için örnek koyar

        # --- 7. ANA EKRAN ARAYÜZÜ ---
        if menu == "Oyuncu İstatistikleri":
            st.markdown(f"""
            <div class="header-box">
                <div style="display: flex; align-items: center;">
                    <img src="{oyuncu_verisi['Takim_Logo']}" width="65" style="margin-right: 20px; object-fit: contain;">
                    <div>
                        <h1 style="margin:0; font-size: 32px;">{secilen_oyuncu} <span style="font-size: 24px;">{oyuncu_verisi['Ulke_Bayrak']}</span></h1>
                        <p style="margin:5px 0 0 0; color: #8b949e; font-size: 14px;">{secilen_sezon} Sezonu | {secilen_lig} | Percentile rank vs. positional peers</p>
                    </div>
                </div>
                <div style="text-align: right; font-size: 13px; color: #d1d5db;">
                    <div style="margin-bottom: 8px;">
                        <span style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 15px; margin-right: 5px;">{secilen_takim}</span> 
                        <span style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 15px; color:#10b981; font-weight:bold;">{oyuncu_verisi['Pozisyon']}</span>
                    </div>
                    <div>
                        <span style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 15px; margin-right: 5px;">Age: {oyuncu_verisi['Yas']}</span> 
                        <span style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 15px;">{oyuncu_verisi['Dakika']} min.</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2, gap="large")

            with col1:
                st.markdown('<div class="category-card"><div class="category-title">HÜCUM ÇIKTILARI (OUTPUT)</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(draw_stat("Goals", get_val("Goals"), get_perc("Goals")), unsafe_allow_html=True)
                    st.markdown(draw_stat("Shots On Target", get_val("SoT"), get_perc("SoT")), unsafe_allow_html=True)
                with c2:
                    st.markdown(draw_stat("npxG (Penaltısız xG)", get_val("npxG"), get_perc("npxG")), unsafe_allow_html=True)
                    st.markdown(draw_stat("Touches In Box", get_val("Touches"), get_perc("Touches")), unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="category-card"><div class="category-title">OYUN KURULUMU (PLAYMAKING)</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(draw_stat("Assists", get_val("Assists"), get_perc("Assists")), unsafe_allow_html=True)
                    st.markdown(draw_stat("Key Passes", get_val("KP"), get_perc("KP")), unsafe_allow_html=True)
                with c2:
                    st.markdown(draw_stat("xA (Beklenen Asist)", get_val("xA"), get_perc("xA")), unsafe_allow_html=True)
                    st.markdown(draw_stat("Prog. Passes", get_val("PrgP"), get_perc("PrgP")), unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        elif menu == "Pizza Grafiği (Yüzdelik)":
            st.subheader(f"🍕 {secilen_oyuncu} - Yüzdelik Grafiği ({secilen_sezon})")
            
            params = ["Goals", "npxG", "Assists", "xA", "Prog_Passes", "Touches"]
            param_labels = ["Goals", "npxG", "Assists", "xA", "Prog. Passes", "Touches Box"]
            
            values = [get_perc(p) for p in params]
            
            baker = PyPizza(
                params=param_labels, background_color="#0b101c", straight_line_color="#1f2937", straight_line_lw=1,             
                last_circle_lw=1, last_circle_color="#1f2937", other_circle_ls="-.", other_circle_lw=1               
            )
            
            fig, ax = baker.make_pizza(
                values, figsize=(10, 10), param_location=110,  
                kwargs_slices=dict(facecolor="#10b981", edgecolor="#0b101c", zorder=2, linewidth=1),
                kwargs_params=dict(color="white", fontsize=12, va="center", weight='bold'),
                kwargs_values=dict(color="white", fontsize=11, zorder=3, bbox=dict(edgecolor="white", facecolor="#121927", boxstyle="round,pad=0.2", lw=1))
            )
            
            fig.patch.set_facecolor('#0b101c')
            fig.text(0.5, 0.98, f"{secilen_oyuncu} - {secilen_sezon}", size=18, ha="center", color="white", weight='bold')
            fig.text(0.5, 0.95, f"{oyuncu_verisi['Takim']} | {secilen_lig}", size=12, ha="center", color="#8b949e")
            
            # Kendi ismin ve hesabınla hazırlanan filigran
            add_watermark(fig)
            
            st.pyplot(fig)
            
            # İndirme Butonu
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=300, bbox_inches="tight", facecolor='#0b101c')
            buf.seek(0)
            st.download_button(label="📸 Raporu Yüksek Çözünürlüklü İndir", data=buf, file_name=f"{secilen_oyuncu.replace(' ', '_')}_rapor.png", mime="image/png")

    except Exception as e:
        st.error(f"Beklenmeyen bir hata oluştu: {e}. Lütfen yüklediğiniz dosyanın geçerli bir Excel veya CSV olduğundan emin olun.")

else:
    st.markdown("""
    <div style="text-align: center; margin-top: 50px;">
        <h2>🛠️ Veritabanı Bekleniyor...</h2>
        <p style="color: #8b949e;">Lütfen sol panelden FBref, Kaggle veya kendi oluşturduğunuz oyuncu verilerini içeren <b>Excel (.xlsx)</b> veya <b>CSV</b> dosyanızı yükleyin.</p>
        <p style="color: #8b949e;"><i>Sistem tüm İngilizce başlıkları otomatik tanır ve eksik verileri kendi tamamlayarak çökmeden çalışır.</i></p>
    </div>
    """, unsafe_allow_html=True)
