import streamlit as st
from rembg import remove
from PIL import Image
import io
import zipfile
from datetime import datetime

st.set_page_config(page_title="Toplu Sticker Makinesi", page_icon="✂️", layout="wide")

st.title("✂️ Toplu Sticker Makinesi")
st.markdown("**Birden fazla fotoğraf yükle → Hepsinin arka planını sil → ZIP olarak indir**")

with st.sidebar:
    st.header("⚙️ Ayarlar")
    
    quality = st.select_slider(
        "Kalite",
        options=["Hızlı", "Normal", "Yüksek"],
        value="Normal"
    )
    
    add_border = st.checkbox("Beyaz kenarlık ekle (WhatsApp için)", value=False)
    border_size = 0
    if add_border:
        border_size = st.slider("Kenarlık kalınlığı", 5, 50, 10)
    
    resize = st.checkbox("Boyutlandır", value=False)
    size = 512
    if resize:
        size = st.slider("Boyut (px)", 256, 2048, 512, 128)

uploaded_files = st.file_uploader(
    "Fotoğraflarını yükle (birden fazla seçebilirsin)",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"📁 {len(uploaded_files)} adet fotoğraf yüklendi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🖼️ Orijinal Fotoğraflar")
        for i, file in enumerate(uploaded_files[:3]):
            img = Image.open(file)
            st.image(img, caption=f"{i+1}. {file.name}", use_container_width=True)
        if len(uploaded_files) > 3:
            st.caption(f"... ve {len(uploaded_files)-3} fotoğraf daha")
    
    if st.button("🚀 Tüm Fotoğrafları İşle", type="primary", use_container_width=True):
        
        processed_images = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with col2:
            st.subheader("✨ İşlenmiş Sticker'lar")
        
        for idx, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"İşleniyor: {uploaded_file.name} ({idx+1}/{len(uploaded_files)})")
            
            original = Image.open(uploaded_file)
            
            if quality == "Hızlı":
                output = remove(original, alpha_matting=False)
            elif quality == "Yüksek":
                output = remove(
                    original,
                    alpha_matting=True,
                    alpha_matting_foreground_threshold=250,
                    alpha_matting_background_threshold=5,
                    alpha_matting_erode_size=15,
                )
            else:
                output = remove(original, alpha_matting=True)
            
            if resize:
                output.thumbnail((size, size), Image.Resampling.LANCZOS)
            
            if add_border:
                from PIL import ImageOps
                output = ImageOps.expand(output, border=border_size, fill='white')
            
            if idx < 3:
                with col2:
                    st.image(output, caption=f"✅ {uploaded_file.name}", use_container_width=True)
            
            buf = io.BytesIO()
            output.save(buf, format="PNG")
            buf.seek(0)
            
            processed_images.append({
                'name': uploaded_file.name.rsplit('.', 1)[0] + '_sticker.png',
                'data': buf.getvalue()
            })
            
            progress_bar.progress((idx + 1) / len(uploaded_files))
        
        status_text.text("✅ Tüm fotoğraflar işlendi!")
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for img_data in processed_images:
                zip_file.writestr(img_data['name'], img_data['data'])
        
        zip_buffer.seek(0)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label=f"📥 {len(uploaded_files)} Sticker'ı İndir (ZIP)",
            data=zip_buffer.getvalue(),
            file_name=f"stickers_{timestamp}.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True
        )
        
        st.success(f"🎉 {len(uploaded_files)} adet sticker hazır!")
        
        with st.expander("📊 İşlem Detayları"):
            st.write(f"- Toplam işlenen: {len(uploaded_files)} fotoğraf")
            st.write(f"- Kalite ayarı: {quality}")
            st.write(f"- Beyaz kenarlık: {'Evet (' + str(border_size) + 'px)' if add_border else 'Hayır'}")
            st.write(f"- Boyutlandırma: {'Evet (' + str(size) + 'px)' if resize else 'Hayır'}")

else:
    st.info("👆 Yukarıdan fotoğraf yükle (birden fazla seçebilirsin)")
    
    with st.expander("💡 Nasıl Kullanılır?"):
        st.markdown("""
        1. **Toplu Seçim**: `Ctrl` (Windows) veya `Cmd` (Mac) ile birden fazla fotoğraf seç
        2. **Ayarlar**: Sol taraftan kalite, kenarlık ve boyut ayarlarını yap
        3. **İşle**: "Tüm Fotoğrafları İşle" butonuna bas
        4. **İndir**: ZIP dosyası olarak hepsini toplu indir
        
        **İpucu**: WhatsApp sticker için "Beyaz kenarlık ekle" ve "512px boyutlandır" seç!
        """)
