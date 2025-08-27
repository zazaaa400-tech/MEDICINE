import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# PENGATURAN HALAMAN STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Gemini Chatbot (Streamlit)",
    page_icon="🤖"
)

st.title("🤖 Gemini Chatbot Sederhana")
st.markdown("---")

# ==============================================================================
# KONTEKS AWAL CHATBOT (INI BAGIAN YANG BISA ANDA MODIFIKASI!)
# ==============================================================================
# Definisikan peran chatbot Anda di sini.
INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Saya adalah ahli tenaga medis. Tuliskan penyakit yang perlu di diaknosis. Jawaban singkat dan jelas. Tolak pertanyaan selain tentang penyakit."]
    },
    {
        "role": "model",
        "parts": ["Baik! Tuliskan penyakit yang perlu di diagnosis."]
    }
]

# ==============================================================================
# KONFIGURASI API KEY DAN MODEL
# ==============================================================================
# Coba ambil API key dari st.secrets (untuk deployment di Streamlit Community Cloud)
# Jika tidak ada, fallback ke variabel lingkungan atau input pengguna.
API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

# Jika API key belum ditemukan, minta pengguna untuk memasukkannya.
if not API_KEY:
    st.warning("API Key belum ditemukan. Harap masukkan API Key Gemini Anda di bawah.")
    API_KEY = st.text_input("Masukkan API Key Gemini Anda:", type="password")

# Setelah API key dimasukkan, inisialisasi model.
if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        # Nama model Gemini yang akan digunakan.
        MODEL_NAME = 'gemini-1.5-flash'
        
        # Inisialisasi model
        model = genai.GenerativeModel(
            MODEL_NAME,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4, # Kontrol kreativitas
                max_output_tokens=500 # Batas maksimal panjang jawaban
            )
        )
        
        # Inisialisasi riwayat chat di session_state jika belum ada
        if "messages" not in st.session_state:
            st.session_state.messages = INITIAL_CHATBOT_CONTEXT
            
    except Exception as e:
        st.error(f"❌ Terjadi kesalahan saat mengkonfigurasi API Key atau menginisialisasi model: {e}")
        st.stop() # Hentikan eksekusi script jika ada error

# ==============================================================================
# TAMPILKAN RIWAYAT CHAT
# ==============================================================================
for message in st.session_state.messages:
    # Cek peran (role) untuk menentukan ikon chat
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["parts"][0])
    elif message["role"] == "model":
        with st.chat_message("assistant"):
            st.markdown(message["parts"][0])

# ==============================================================================
# HANDLE INPUT PENGGUNA BARU
# ==============================================================================
if prompt := st.chat_input("Tulis pertanyaan Anda di sini..."):
    # Tambahkan pesan pengguna ke riwayat chat
    st.session_state.messages.append({"role": "user", "parts": [prompt]})
    
    # Tampilkan pesan pengguna di UI
    with st.chat_message("user"):
        st.markdown(prompt)

    # Dapatkan respons dari model
    with st.chat_message("assistant"):
        # Buat sesi chat baru dengan riwayat dari session_state
        chat_session = model.start_chat(history=st.session_state.messages[:-1])
        
        # Kirim pesan terbaru dari pengguna
        response = chat_session.send_message(prompt, stream=True)
        
        # Tuliskan respons secara bertahap (seperti mengetik)
        full_response = st.write_stream(response)

    # Tambahkan respons model ke riwayat chat
    st.session_state.messages.append({"role": "model", "parts": [full_response]})
