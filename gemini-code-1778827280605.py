import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
from io import BytesIO

# 1. 페이지 설정
st.set_page_config(page_title="산업안전 무료 분석기", page_icon="🛡️")

# 2. 무료 사용 안내 UI
st.title("🛡️ 산업안전보건 AI 분석기 (무료 버전)")
st.markdown("""
사용자의 **개인 API 키**를 사용하여 운영되므로, 개발자에게 결제되는 비용이 없는 **완전 무료** 방식입니다.
* 구글 키 발급(무료): [Google AI Studio](https://aistudio.google.com/)
""")

# 3. 사이드바 - 키 입력 (한 번 입력하면 브라우저를 닫기 전까지 유지됨)
with st.sidebar:
    st.header("🔑 API 키 등록")
    g_key = st.text_input("Google Gemini Key", type="password")
    st.caption("※ 이 키는 서버에 저장되지 않고 본인의 브라우저 내에서만 사용됩니다.")

# 4. 메인 로직
uploaded_file = st.file_uploader("현장 사진을 업로드하세요", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="분석 대상 사진", use_container_width=True)

    if st.button("🔍 즉시 분석 시작"):
        if not g_key:
            st.error("왼쪽 사이드바에 Google API Key를 입력해주세요!")
        else:
            try:
                # Gemini 무료 티어 설정
                genai.configure(api_key=g_key)
                # Flash 모델은 무료 티어에서 분당 15회 호출까지 무료입니다.
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                with st.spinner("AI 감사관이 법령 위반 여부를 검토 중입니다..."):
                    prompt = "귀하는 베테랑 산업안전보건지도사입니다. 사진을 보고 [산업안전보건법] 위반 사항, 위험 요인, 즉시 조치 사항을 리포트 형식으로 작성하세요."
                    response = model.generate_content([prompt, img])
                    
                    st.success("✅ 분석 완료")
                    st.markdown("---")
                    st.markdown(response.text)
                    st.markdown("---")
                    
            except Exception as e:
                st.error(f"오류가 발생했습니다. 키가 올바른지 확인하세요: {e}")

st.caption("© 2026 무료 산업안전 툴킷. 본 결과는 법적 효력이 없습니다.")