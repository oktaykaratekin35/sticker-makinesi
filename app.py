import streamlit as st

try:
    from rembg import remove
    from PIL import Image
    import io
    import zipfile
    from datetime import datetime
    
    st.set_page_config(page_title="Sticker Makinesi", page_icon="✂️", layout="wide")
    
    st.title("✂️ Toplu Sticker Makinesi")
    st.markdown("Birden fazla fotoğraf yükle → Arka planları sil → ZIP indir")
    
    # Ayarlar
    with st.sidebar:
        st.header("⚙️ Ayarlar")
        max_files = st.number_input("Max fotoğraf sayısı", 1, 10, 5)
        add_border = st.checkbox("Beyaz kenarlık ekle", False)
        border_size = st.slider("Kenarlık kalınlığı", 5, 30, 10) if add_border else 0
    
    # Dosya yükleme
    uploaded_files = st.file_uploader(
        "Fotoğraf yükle (birden fazla seçebilirsin)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        # Limit kontrol
        if len(uploaded_files) > max_files:
            st.warning(f"⚠️ İlk {max_files} fotoğraf işlenecek")
            uploaded_files = uploaded_files[:max_files]
        
        st.info(f"📁 {len(uploaded_files)} fotoğraf yüklendi")
        
        if st.button("🚀 İşle", type="primary"):
            processed = []
            progress = st.progress(0)
            
            for idx, file in enumerate(uploaded_files):
                with st.spinner(f"İşleniyor: {file.name}"):
                    try:
                        # Görüntüyü aç
                        img = Image.open(file)
                        
                        # Arka planı sil
                        output = remove(img)
                        
                        # Kenarlık ekle
                        if add_border:
                            from PIL import ImageOps
                            output = ImageOps.expand(output, border=border_size, fill='white')
                        
                        # 
