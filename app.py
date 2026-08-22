import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statsbombpy import sb
from mplsoccer import Pitch, Radar

st.set_page_config(page_title="Gelişmiş Scout Panosu", page_icon="🔍", layout="wide")
st.title("🔍 Gelişmiş Oyuncu İstatistikleri ve Kıyaslama")

# --- VERİ ÇEKME FONKSİYONLARI ---
@st.cache_data(show_spinner=False)
def ligleri_getir():
    return sb.competitions()

@st.cache_data(show_spinner=False)
def maclari_getir(comp_id, season_id):
    return sb.matches(competition_id=comp_id, season_id=season_id)

@st.cache_data(show_spinner=False)
def olaylari_getir(match_id):
    return sb.events(match_id=match_id)

# --- YAN MENÜ: FİLTRELEME ---
st.sidebar.header("Veri Seçimi")

try:
    df_ligler = ligleri_getir()
    df_ligler['Lig_Sezon'] = df_ligler['competition_name'] + " (" + df_ligler['season_name'] + ")"
    
    secilen_lig_sezon = st.sidebar.selectbox("Lig ve Sezon Seçin", df_ligler['Lig_Sezon'].unique())
    
    lig_bilgisi = df_ligler[df_ligler['Lig_Sezon'] == secilen_lig_sezon].iloc[0]
    comp_id = lig_bilgisi['competition_id']
    season_id = lig_bilgisi['season_id']
    
    df_maclar = maclari_getir(comp_id, season_id)
    df_maclar['Mac_Adi'] = df_maclar['home_team'] + " vs " + df_maclar['away_team']
    
    secilen_mac_adi = st.sidebar.selectbox("Maç Seçin", df_maclar['Mac_Adi'].unique())
    mac_id = df_maclar[df_maclar['Mac_Adi'] == secilen_mac_adi].iloc[0]['match_id']
    
    with st.spinner("Maç verileri indiriliyor..."):
        df_olaylar = olaylari_getir(mac_id)
        
    oyuncular = df_olaylar['player'].dropna().unique()
    oyuncular.sort()
    
    # --- ANA EKRAN SEKMELERİ ---
    tab1, tab2 = st.tabs(["🗺️ Saha İstatistikleri", "🕸️ Radar (Kıyaslama)"])
    
    with tab1:
        st.subheader("Bireysel Saha Aksiyonları")
        secilen_oyuncu = st.selectbox("Oyuncu Seçin (Saha Çizimi İçin)", oyuncular, key="saha_oyuncu")
        istatistik_turu = st.selectbox(
            "Görmek İstediğiniz İstatistik", 
            ["Tüm Paslar", "Uzun Toplar", "Top Sürme (Dribbling)", "Şutlar ve npXG"]
        )
        
        oyuncu_verisi = df_olaylar[df_olaylar['player'] == secilen_oyuncu]
        
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
        fig, ax = pitch.draw(figsize=(10, 7))
        fig.set_facecolor('#22312b')
        
        if istatistik_turu == "Tüm Paslar":
            paslar = oyuncu_verisi[oyuncu_verisi['type'] == 'Pass']
            for index, row in paslar.iterrows():
                if type(row.get('location')) == list and type(row.get('pass_end_location')) == list:
                    x1, y1 = row['location']
                    x2, y2 = row['pass_end_location']
                    renk = '#00BFFF' if pd.isna(row.get('pass_outcome')) else 'red'
                    pitch.arrows(x1, y1, x2, y2, color=renk, ax=ax, width=2, headwidth=6, alpha=0.8)
                    
        elif istatistik_turu == "Uzun Toplar":
            paslar = oyuncu_verisi[oyuncu_verisi['type'] == 'Pass']
            uzun_toplar = paslar[paslar['pass_length'] >= 35]
            for index, row in uzun_toplar.iterrows():
                if type(row.get('location')) == list and type(row.get('pass_end_location')) == list:
                    x1, y1 = row['location']
                    x2, y2 = row['pass_end_location']
                    renk = '#00FF00' if pd.isna(row.get('pass_outcome')) else 'red'
                    pitch.arrows(x1, y1, x2, y2, color=renk, ax=ax, width=2, headwidth=6, alpha=0.9)
                    
        elif istatistik_turu == "Top Sürme (Dribbling)":
            dribbles = oyuncu_verisi[oyuncu_verisi['type'] == 'Dribble']
            for index, row in dribbles.iterrows():
                if type(row.get('location')) == list:
                    x, y = row['location']
                    renk = '#FFD700' if row.get('dribble_outcome') == 'Complete' else 'red'
                    pitch.scatter(x, y, color=renk, ax=ax, s=150, edgecolors='black', zorder=2)
                    
        elif istatistik_turu == "Şutlar ve npXG":
            sutlar = oyuncu_verisi[oyuncu_verisi['type'] == 'Shot']
            for index, row in sutlar.iterrows():
                if type(row.get('location')) == list:
                    x, y = row['location']
                    xg = row.get('shot_statsbomb_xg')
                    buyukluk = (xg * 1000) if not pd.isna(xg) else 100
                    renk = '#00FF00' if row.get('shot_outcome') == 'Goal' else 'white'
                    pitch.scatter(x, y, color=renk, ax=ax, s=buyukluk, edgecolors='black', alpha=0.7)
                    if not pd.isna(xg):
                        ax.text(x+1, y-1, f"{xg:.2f}", color='white', fontsize=10)

        st.pyplot(fig)
        
    with tab2:
        st.subheader("Oyuncu Kıyaslama (Radar)")
        col1, col2 = st.columns(2)
        
        with col1:
            oyuncu_1 = st.selectbox("1. Oyuncu (Bordo)", oyuncular, key="p1")
        with col2:
            oyuncu_2 = st.selectbox("2. Oyuncu (Mavi)", oyuncular, key="p2")
            
        if st.button("Radarı Çiz"):
            # İki oyuncunun verilerini filtrele
            p1_veri = df_olaylar[df_olaylar['player'] == oyuncu_1]
            p2_veri = df_olaylar[df_olaylar['player'] == oyuncu_2]
            
            # Parametreler (Neleri kıyaslayacağız?)
            parametreler = ['Pas Denemesi', 'Başarılı Pas', 'Şut', 'Dribbling', 'Top Kazanma']
            
            # Oyuncu 1 İstatistiklerini Hesapla
            p1_pas = len(p1_veri[p1_veri['type'] == 'Pass'])
            p1_basarili_pas = len(p1_veri[(p1_veri['type'] == 'Pass') & (pd.isna(p1_veri['pass_outcome']))])
            p1_sut = len(p1_veri[p1_veri['type'] == 'Shot'])
            p1_dribble = len(p1_veri[p1_veri['type'] == 'Dribble'])
            p1_kazanma = len(p1_veri[p1_veri['type'] == 'Ball Recovery'])
            
            p1_degerler = [p1_pas, p1_basarili_pas, p1_sut, p1_dribble, p1_kazanma]
            
            # Oyuncu 2 İstatistiklerini Hesapla
            p2_pas = len(p2_veri[p2_veri['type'] == 'Pass'])
            p2_basarili_pas = len(p2_veri[(p2_veri['type'] == 'Pass') & (pd.isna(p2_veri['pass_outcome']))])
            p2_sut = len(p2_veri[p2_veri['type'] == 'Shot'])
            p2_dribble = len(p2_veri[p2_veri['type'] == 'Dribble'])
            p2_kazanma = len(p2_veri[p2_veri['type'] == 'Ball Recovery'])
            
            p2_degerler = [p2_pas, p2_basarili_pas, p2_sut, p2_dribble, p2_kazanma]
            
            # Radar Grafiği Çizimi
            alt_sinirlar = [0, 0, 0, 0, 0]
            # Üst sınırları oyuncuların maksimum değerlerine göre dinamik belirliyoruz
            ust_sinirlar = [
                max(p1_pas, p2_pas) + 5,
                max(p1_basarili_pas, p2_basarili_pas) + 5,
                max(p1_sut, p2_sut) + 2,
                max(p1_dribble, p2_dribble) + 2,
                max(p1_kazanma, p2_kazanma) + 2
            ]

            radar = Radar(parametreler, alt_sinirlar, ust_sinirlar,
                          round_int=[True]*5, num_rings=4, ring_width=1, center_circle_radius=1)

            # Siyah arka plan ayarları
            fig, ax = radar.setup_axis(facecolor='#121212') 
            fig.set_facecolor('#121212')

            # 1. Oyuncu (Bordo: #800000)
            rings_inner_1, rings_outer_1, vertices_1 = radar.draw_circles(
                ax=ax, values=p1_degerler, facecolor='#800000', edgecolor='#800000', alpha=0.6, lw=2
            )
            
            # 2. Oyuncu (Mavi: #0000FF veya #0047AB)
            rings_inner_2, rings_outer_2, vertices_2 = radar.draw_circles(
                ax=ax, values=p2_degerler, facecolor='#0047AB', edgecolor='#0047AB', alpha=0.6, lw=2
            )

            # Eksen çizgileri ve etiketleri (Beyaz renk)
            radar_poly, rings, vertices = radar.draw_radar_solid(ax, alpha=0)
            ax.vlines(x=vertices[:, 0], ymin=0, ymax=vertices[:, 1], color='white', lw=1, zorder=1)
            radar.draw_range_labels(ax=ax, fontsize=10, color='white')
            radar.draw_param_labels(ax=ax, fontsize=13, color='white')

            # Başlıklar ve İmza
            fig.text(0.15, 0.95, oyuncu_1, fontsize=15, color='#800000', ha='center')
            fig.text(0.5, 0.95, "vs", fontsize=15, color='white', ha='center')
            fig.text(0.85, 0.95, oyuncu_2, fontsize=15, color='#0047AB', ha='center')
            
            # İstediğiniz imza kısmı
            fig.text(0.95, 0.05, "inspired by: @muaythaibetter", fontsize=10, color='gray', ha='right')

            st.pyplot(fig)

except Exception as e:
    st.error(f"Veri yüklenirken bir hata oluştu: {e}")
