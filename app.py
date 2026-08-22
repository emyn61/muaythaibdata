import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statsbombpy import sb
from mplsoccer import Pitch

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Futbol Analiz", page_icon="⚽", layout="wide")

st.sidebar.header("Filtreleme Menüsü")
st.sidebar.write("Buradan lig ve sezon seçebilirsiniz.")
secilen_lig = st.sidebar.selectbox("Lig Seçin", ["Süper Lig", "Premier League", "La Liga"])
secilen_sezon = st.sidebar.selectbox("Sezon", ["2023/2024", "2024/2025"])

st.title("⚽ Gelişmiş Futbol Analitik Panosu")
st.write(f"Şu anda **{secilen_lig}** - **{secilen_sezon}** verilerini görüntülüyorsunuz.")

# 4. SEKMELER
tab1, tab2, tab3 = st.tabs(["📊 Puan Durumu", "📈 Oyuncu İstatistikleri", "🔥 StatsBomb Pas Haritası (Gerçek Veri)"])

with tab1:
    st.subheader(f"{secilen_lig} Güncel Puan Durumu")
    puan_durumu_verisi = {
        "Takım": ["Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor", "Başakşehir"],
        "Oynanan": [38, 38, 38, 38, 38],
        "Galibiyet": [33, 31, 16, 21, 18],
        "Beraberlik": [3, 6, 8, 4, 7],
        "Mağlubiyet": [2, 1, 14, 13, 13],
        "Puan": [102, 99, 56, 67, 61]
    }
    st.dataframe(pd.DataFrame(puan_durumu_verisi), use_container_width=True)

with tab2:
    st.subheader("Gol Krallığı Grafiği")
    oyuncu_verisi = pd.DataFrame({
        "Oyuncu": ["Mauro Icardi", "Edin Dzeko", "Rey Manaj", "Mame Thiam", "Krzysztof Piatek"],
        "Gol Sayısı": [25, 21, 18, 17, 17]
    })
    st.bar_chart(oyuncu_verisi, x="Oyuncu", y="Gol Sayısı", color="#1E90FF")

with tab3:
    st.header("StatsBomb Ücretsiz Veritabanı - Pas Haritası")
    st.write("Aşağıdaki veri, **2022 Dünya Kupası Finali (Arjantin vs Fransa)** maçından StatsBomb açık veritabanı kullanılarak anlık çekilmektedir.")
    
    # 1. Veriyi çekmek için bir buton ekleyelim (Site her açıldığında ağırlaşmasın diye)
    if st.button("Dünya Kupası Finali Verilerini Çek ve Çiz"):
        with st.spinner("StatsBomb sunucularına bağlanılıyor... Lütfen bekleyin."):
            try:
                # Arjantin - Fransa finalinin StatsBomb'daki maç ID'si: 3869685
                mac_olaylari = sb.events(match_id=3869685)
                
                # Sadece pasları filtreliyoruz ve Arjantin takımını seçiyoruz
                paslar = mac_olaylari[mac_olaylari['type'] == 'Pass']
                arjantin_paslari = paslar[paslar['team'] == 'Argentina']
                
                # Sadece Messi'nin paslarını alıyoruz
                messi_paslari = arjantin_paslari[arjantin_paslari['player'] == 'Lionel Andrés Messi Cuccittini']
                
                st.success("Veri başarıyla çekildi! Lionel Messi'nin pas haritası oluşturuluyor...")
                
                # 2. Saha Çizimi (mplsoccer kütüphanesi ile)
                pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
                fig, ax = pitch.draw(figsize=(10, 7))
                fig.set_facecolor('#22312b')
                
                # 3. Pasları sahaya oklar halinde yerleştirme
                for index, row in messi_paslari.iterrows():
                    # X ve Y koordinatları 'location' ve 'pass_end_location' içindedir
                    x_baslangic = row['location'][0]
                    y_baslangic = row['location'][1]
                    x_bitis = row['pass_end_location'][0]
                    y_bitis = row['pass_end_location'][1]
                    
                    # Eğer pas başarılıysa mavi, hatalıysa kırmızı ok çiz
                    if pd.isna(row.get('pass_outcome')): # StatsBomb'da boş (NaN) ise pas başarılıdır
                        pitch.arrows(x_baslangic, y_baslangic, x_bitis, y_bitis, width=2,
                                     headwidth=10, headlength=10, color='#00BFFF', ax=ax, label='Başarılı')
                    else:
                        pitch.arrows(x_baslangic, y_baslangic, x_bitis, y_bitis, width=2,
                                     headwidth=10, headlength=10, color='red', ax=ax, label='Hatalı')

                plt.title("Lionel Messi - 2022 Dünya Kupası Finali Pas Haritası", color='white', size=16)
                
                # Çizilen grafiği Streamlit sitesine aktar
                st.pyplot(fig)
                
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")
