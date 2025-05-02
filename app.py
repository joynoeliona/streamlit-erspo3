import streamlit as st
import tweepy
import pandas as pd
import re
import os
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# --- Load ENV ---
bearer_token = st.secrets["BEARER_TOKEN"]
client = tweepy.Client(bearer_token=bearer_token)

# --- UI ---
st.title("📊 Word Cloud dari Twitter")
st.write("Masukkan kata kunci pencarian (misalnya: 'erspo') untuk mengambil tweet dan membuat Word Cloud.")

keyword = st.text_input("🔍 Kata kunci tweet", value="erspo")
max_tweet = st.slider("Jumlah tweet", min_value=10, max_value=100, step=10, value=50)

if st.button("🔄 Ambil & Buat Word Cloud"):
    with st.spinner("Mengambil tweet..."):
        query = f"{keyword} lang:id -is:retweet"
        response = client.search_recent_tweets(query=query, max_results=max_tweet)
        tweets = response.data or []

    if not tweets:
        st.warning("Tidak ada tweet ditemukan.")
    else:
        teks_asli = [t.text for t in tweets]

        # --- Bersihkan teks ---
        factory = StopWordRemoverFactory()
        stopwords = factory.get_stop_words()

        def bersihkan_teks(teks):
            teks = re.sub(r"http\S+", "", teks)
            teks = re.sub(r"#\S+", "", teks)
            teks = re.sub(r"@\S+", "", teks)
            teks = re.sub(r"[^a-zA-Z\s]", "", teks)
            teks = teks.lower()
            teks = " ".join([t for t in teks.split() if t not in stopwords])
            return teks

        teks_bersih = [bersihkan_teks(t) for t in teks_asli]
        gabungan = " ".join(teks_bersih)

        # --- Word Cloud ---
        st.subheader("☁️ Word Cloud")
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(gabungan)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

        # --- Simpan CSV ---
        df = pd.DataFrame({
            "tweet_mentah": teks_asli,
            "tweet_bersih": teks_bersih
        })

        st.subheader("📁 Data Tweet")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 Download CSV", csv, f"{keyword}_tweet.csv", "text/csv")
    