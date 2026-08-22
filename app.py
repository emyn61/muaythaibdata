import streamlit as st
import pandas as pd
import numpy as np
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
    div.stDownloadButton > button { background-color: #10b981; color: white; font-weight: bold; border-radius: 8px; border: none; width: 100%; }
    div.stDownloadButton > button:hover { background-color: #059669; }
</style>
""", unsafe_allow_html=True)

# --- YARDIMCI FONKSİYONLAR ---
def add_watermark(fig):
    fig.text(0.99, 0.01, 'Scouting Report | Muhammed Emin (@pressxresistant)', 
             color='#8b949e', fontsize=9, ha='right', va='bottom', alpha=0.6, weight='bold')

def draw_stat(title, value, percentile):
    # NaN veya eksik veri kontrolü
    if pd.isna(value): value = 0.0
    if pd.isna(percentile): percentile = 0

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

# --- SOL MENÜ: DOSYA YÜKLEME VE FİLTRELEME ---
st.sidebar.title("🔍 Kapsamlı Scout Paneli")
st.sidebar.markdown("---")
st.sidebar.subheader("📁 Veritabanı Yükle")
st.sidebar.info("Excel (.xlsx) veya CSV dosyanızı yükleyin. (Örn: FBref/Wyscout export)")

uploaded_file = st.sidebar.file_uploader("", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Kullanıcının yüklediği veriyi oku
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.sidebar.success(f"✅ Veri yüklendi! ({len(df)} Oyuncu)")
        
        # Gerekli sütunların kontrolü (Kendi veritabanını hazırlarken bu başlıkları kullanmalısın)
        required_columns = ['Sezon', 'Lig', 'Takim', 'Oyuncu', 'Pozisyon', 'Yas', 'Dakika', 'Ulke_Bayrak', 'Takim_Logo']
        missing_cols = [col for col in required_columns if col not in df.columns]
        
        if missing_cols:
            st.sidebar.warning(f"⚠️ Dosyanızda şu temel sütunlar eksik olabilir: {', '.join(missing_cols)}. Hata almamak için sütun isimlerini kontrol edin.")
            st.stop()

        # DİNAMİK FİLTRELEME AĞACI
        sezonlar = sorted(df['Sezon'].astype(str).unique().tolist(), reverse=True)
        secilen_sezon = st.sidebar.selectbox("📅 Sezon Seçin", sezonlar)
        df_sezon = df[df['Sezon'].astype(str) == secilen_sezon]

        ligler = sorted(df_sezon['Lig'].unique().tolist())
        secilen_lig = st.sidebar.selectbox("🌍 Lig Seçin", ligler)

        takimlar = sorted(df_sezon[df_sezon['Lig'] == secilen_lig]['Takim'].unique().tolist())
        secilen_takim = st.sidebar.selectbox("🏠 Takım Seçin", takimlar)

        oyuncular = sorted(df_sezon[(df_sezon['Lig'] == secilen_lig) & (df_sezon['Takim'] == secilen_takim)]['Oyuncu'].unique().tolist())
        secilen_oyuncu = st.sidebar.selectbox("👤 Oyuncu Seçin", oyuncular)

        oyuncu_verisi = df_sezon[df_sezon['Oyuncu'] == secilen_oyuncu].iloc[0]

        st.sidebar.markdown("---")
        menu = st.sidebar.radio("📌 Navigasyon", ["Player Stats", "Stat Radar Comparison", "Pizza Chart"])

        # --- ANA EKRAN İÇERİKLERİ ---
        if menu == "Player Stats":
            st.markdown(f"""
            <div class="header-box">
                <div style="display: flex; align-items: center;">
                    <img src="{oyuncu_verisi.get('Takim_Logo', 'https://cdn-icons-png.flaticon.com/512/53/53283.png')}" width="65" style="margin-right: 20px; object-fit: contain;">
                    <div>
                        <h1 style="margin:0; font-size: 32px;">{secilen_oyuncu} <span style="font-size: 24px;">{oyuncu_verisi.get('Ulke_Bayrak', '🏳️')}</span></h1>
                        <p style="margin:5px 0 0 0; color: #8b949e; font-size: 14px;">{secilen_sezon} Sezonu | {secilen_lig} | Percentile rank vs. positional peers</p>
                    </div>
                </div>
                <div style="text-align: right; font-size: 13px; color: #d1d5db;">
                    <div style="margin-bottom: 8px;">
                        <span style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 15px; margin-right: 5px;">{secilen_takim}</span> 
                        <span style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 15px; color:#10b981;">{oyuncu_verisi['Pozisyon']}</span>
                    </div>
                    <div>
                        <span style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 15px; margin-right: 5px;">Age: {oyuncu_verisi.get('Yas', '-')}</span> 
                        <span style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 15px;">{oyuncu_verisi['Dakika']} min.</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2, gap="large")

            # Gerçek veritabanındaki sütun adlarına göre verileri çekme mantığı
            # Excel'inde 'Goals_p90' ve 'Goals_percentile' gibi sütunlar olmalı.
            def get_val(col_name): return oyuncu_verisi.get(f"{col_name}_p90", 0.0)
            def get_perc(col_name): return oyuncu_verisi.get(f"{col_name}_percentile", 0)

            with col1:
                st.markdown('<div class="category-card"><div class="category-title">OUTPUT</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(draw_stat("Goals", get_val("Goals"), get_perc("Goals")), unsafe_allow_html=True)
                    st.markdown(draw_stat("Shots On Target", get_val("SoT"), get_perc("SoT")), unsafe_allow_html=True)
                with c2:
                    st.markdown(draw_stat("npxG", get_val("npxG"), get_perc("npxG")), unsafe_allow_html=True)
                    st.markdown(draw_stat("Touches In Opp. Box", get_val("Touches_Box"), get_perc("Touches_Box")), unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="category-card"><div class="category-title">PLAYMAKING</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(draw_stat("Assists", get_val("Assists"), get_perc("Assists")), unsafe_allow_html=True)
                    st.markdown(draw_stat("Key Passes", get_val("Key_Passes"), get_perc("Key_Passes")), unsafe_allow_html=True)
                with c2:
                    st.markdown(draw_stat("xA", get_val("xA"), get_perc("xA")), unsafe_allow_html=True)
                    st.markdown(draw_stat("Prog. Passes", get_val("Prog_Passes"), get_perc("Prog_Passes")), unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        elif menu == "Pizza Chart":
            st.subheader(f"🍕 {secilen_oyuncu} - Yüzdelik Grafiği ({secilen_sezon})")
            
            # Seçilen pozisyona göre Excel'den çekilecek metrik listesi
            if oyuncu_verisi['Pozisyon'] in ["FW", "ST", "AM", "RW", "LW"]:
                params = ["Goals", "npxG", "Shots", "Touches_Box", "xA", "Succ_Dribbles"]
            elif oyuncu_verisi['Pozisyon'] in ["CM", "DM"]:
                params = ["Prog_Passes", "Key_Passes", "Pass_Acc", "Tackles", "Interceptions", "xT"]
            elif oyuncu_verisi['Pozisyon'] in ["CB", "FB"]:
                params = ["Aerials_Won", "Tackles_Won", "Interceptions", "Clearances", "Prog_Carries", "Pass_Acc"]
            else:
                params = ["Saves", "Save_Pct", "Crosses_Stopped", "Def_Actions_Out", "Long_Pass_Acc", "Pass_Acc"]
            
            # Görüntülenecek başlıklar (Alt tireleri kaldırıp güzelleştirelim)
            param_labels = [p.replace("_", " ") for p in params]
            # Değerleri Excel'den çek
            values = [oyuncu_verisi.get(f"{p}_percentile", 50) for p in params]
            
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
            add_watermark(fig)
            st.pyplot(fig)
            
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=300, bbox_inches="tight", facecolor='#0b101c')
            buf.seek(0)
            st.download_button(label="📸 Pizza Grafiğini İndir", data=buf, file_name=f"{secilen_oyuncu}_pizza.png", mime="image/png")

    except Exception as e:
        st.error(f"Dosya okunurken bir hata oluştu: {e}. Lütfen sütun isimlerinizi kontrol edin.")

else:
    # DOSYA YÜKLENMEDİĞİNDE ÇIKACAK EKRAN
    st.markdown("""
    <div style="text-align: center; margin-top: 50px;">
        <h2>🛠️ Veritabanı Bekleniyor...</h2>
        <p style="color: #8b949e;">Lütfen sol menüden oyuncu verilerinizi içeren <b>Excel (.xlsx)</b> veya <b>CSV</b> dosyanızı yükleyin.</p>
        <p style="color: #8b949e;">Dosyanızda olması gereken zorunlu sütun isimleri:</p>
        <code style="color: #10b981; background: #121927; padding: 10px; border-radius: 8px;">
        Sezon | Lig | Takim | Oyuncu | Pozisyon | Yas | Dakika | Ulke_Bayrak | Takim_Logo
        </code><br><br>
        <p style="color: #8b949e;">Ve istatistikleriniz için (Örnek):</p>
        <code style="color: #3b82f6; background: #121927; padding: 10px; border-radius: 8px;">
        Goals_p90 | Goals_percentile | npxG_p90 | npxG_percentile
        </code>
    </div>
    """, unsafe_allow_html=True)
