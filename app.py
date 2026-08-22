import streamlit as st
import pandas as pd

# 1. SAYFA AYARLARI (Geniş ekran, başlık ve ikon)
st.set_page_config(page_title="Futbol Analiz", page_icon="⚽", layout="wide")

# 2. YAN MENÜ (SIDEBAR) OLUŞTURMA
st.sidebar.header("Filtreleme Menüsü")
st.sidebar.write("Buradan lig ve sezon seçebilirsiniz.")

# Kullanıcıya seçim yaptırıyoruz
secilen_lig = st.sidebar.selectbox("Lig Seçin", ["Süper Lig", "Premier League", "La Liga"])
secilen_sezon = st.sidebar.selectbox("Sezon", ["2023/2024", "2024/2025"])

# 3. ANA SAYFA BAŞLIĞI
st.title("⚽ Gelişmiş Futbol Analitik Panosu")
st.write(f"Şu anda **{secilen_lig}** - **{secilen_sezon}** verilerini görüntülüyorsunuz.")

# 4. SEKMELER (TABS) EKLİYORUZ (Düzenli görünüm için)
tab1, tab2, tab3 = st.tabs(["📊 Puan Durumu", "📈 Oyuncu İstatistikleri", "🔗 Gerçek Veri (API) Nasıl Eklenir?"])

with tab1:
    st.subheader(f"{secilen_lig} Güncel Puan Durumu")
    st.write("Not: Aşağıdaki veri şimdilik manuel eklenmiş bir örnek veridir. 3. sekmede bunu otomatik nasıl çekeceğinizi görebilirsiniz.")
    
    # Örnek Puan Durumu Verisi (Pandas DataFrame oluşturuyoruz)
    puan_durumu_verisi = {
        "Takım": ["Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor", "Başakşehir"],
        "Oynanan": [38, 38, 38, 38, 38],
        "Galibiyet": [33, 31, 16, 21, 18],
        "Beraberlik": [3, 6, 8, 4, 7],
        "Mağlubiyet": [2, 1, 14, 13, 13],
        "Puan": [102, 99, 56, 67, 61]
    }
    df_puan = pd.DataFrame(puan_durumu_verisi)
    
    # Tabloyu ekrana tam genişlikte basıyoruz
    st.dataframe(df_puan, use_container_width=True)

with tab2:
    st.subheader("Gol Krallığı Grafiği")
    
    # Örnek Oyuncu Verisi
    oyuncu_verisi = pd.DataFrame({
        "Oyuncu": ["Mauro Icardi", "Edin Dzeko", "Rey Manaj", "Mame Thiam", "Krzysztof Piatek"],
        "Gol Sayısı": [25, 21, 18, 17, 17]
    })
    
    # Veriyi bar grafiği (sütun grafik) olarak gösteriyoruz
    st.bar_chart(oyuncu_verisi, x="Oyuncu", y="Gol Sayısı", color="#1E90FF")
    
    st.dataframe(oyuncu_verisi, use_container_width=True)

with tab3:
    st.header("Wyscout veya API-Football'dan Veri Çekme")
    st.write("""
    Sitenizin gerçek zamanlı çalışması için (Wyscout, Opta veya API-Football gibi) bir platformdan **API Key (Şifre)** almalısınız. 
    Şifrenizi aldıktan sonra kodunuza aşağıdaki gibi bir bölüm ekleyerek sitenizin verileri otomatik çekmesini sağlayabilirsiniz:
    """)
    
    # API kod örneğini ekranda güzel görünmesi için kod bloğu içine alıyoruz
    st.code("""
import requests
import pandas as pd

# Örnek: API-Football kullanımı
def canli_veri_getir():
    url = "https://v3.football.api-sports.io/standings"
    
    # Hangi lig ve sezonu istediğimizi belirtiyoruz
    querystring = {"league":"39", "season":"2023"} 
    
    # API-Football'dan aldığınız gizli anahtarı buraya yazıyorsunuz
    headers = {
        "x-apisports-key": "BURAYA_SIZIN_GIZLI_SIFRENIZ_GELECEK"
    }
    
    # Veriyi internetten çekiyoruz
    cevap = requests.get(url, headers=headers, params=querystring)
    veri_json = cevap.json()
    
    # Gelen veriyi tabloya çevirip sitemize aktarıyoruz
    # return pd.DataFrame(veri_json...)
    """, language="python")
    
    st.info("İpucu: API anahtarlarınızı doğrudan koda yazmak yerine Streamlit'in 'Secrets' (Gizli Ayarlar) bölümüne eklemek en güvenli yoldur.")
```eof

Bu kodları GitHub'a yapıştırıp kaydettikten sonra sitenizde sekmeler, yan menüler, tablolar ve interaktif bir grafik göreceksiniz. 

**Bundan sonraki adımlar için tavsiyem:** 
1. Sitenizin yeni halini inceleyin.
2. [API-Football](https://www.api-football.com/) sitesine gidip ücretsiz bir üyelik açarak kendinize bir API anahtarı edinin (Wyscout bireysel kullanıcılar için çok pahalıdır, API-Football ise günlük 100 isteğe kadar ücretsizdir ve aynı kalitede veri sunar).
Anahtarınızı aldığınızda, verileri manuel tablodan çıkarıp canlıya bağlamak için bir sonraki adıma geçebiliriz!
