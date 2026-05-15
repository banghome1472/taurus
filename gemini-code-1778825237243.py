import streamlit as st
import google.generativeai as genai
from openai import OpenAI
from PIL import Image
import requests
from io import BytesIO

# ==========================================
# 🔑 [필독] 여기에 본인의 API 키를 입력하세요
# ==========================================
MY_GOOGLE_API_KEY = "여기에_구글_키를_넣으세요"
MY_OPENAI_API_KEY = "여기에_오픈AI_키를_넣으세요"
# ==========================================

# 1. 웹 페이지 기본 설정
st.set_page_config(
    page_title="AI 산업안전 감사관",
    page_icon="🛡️",
    layout="wide"
)

# 2. 스타일 커스텀 (CSS)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; border: none; }
    .stButton>button:hover { background-color: #0056b3; }
    .report-box { padding: 20px; border-radius: 10px; background-color: white; border: 1px solid #ddd; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ 스마트 산업안전보건(EHS) 분석 시스템")
st.info("현장 사진을 업로드하고 버튼을 누르시면 AI 분석 리포트와 개선 이미지가 생성됩니다.")

# 3. 사이드바 (정보 표시용으로 변경)
with st.sidebar:
    st.header("📋 시스템 상태")
    st.success("✅ API 연결 완료 (자동 로그인)")
    st.divider()
    st.markdown("""
    ### 📌 사용 방법
    1. 분석할 현장 사진을 업로드합니다.
    2. **[분석 및 이미지 생성]** 버튼을 누릅니다.
    3. 결과 리포트와 이미지를 확인합니다.
    """)

# 4. 분석 프롬프트
ANALYSIS_PROMPT = """
귀하는 20년 경력의 베테랑 '대한민국 산업안전보건지도사'입니다.
제공된 사진을 대한민국 [산업안전보건법] 및 [산업안전보건기준에 관한 규칙]에 근거하여 분석하고, 
반드시 지정된 태그(### REPORT_START/END, ### PROMPT_START/END)를 사용하여 결과물(리포트와 영어 이미지 생성 프롬프트)을 제출하십시오.
"""

# 5. 메인 레이아웃
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📤 현장 사진 업로드")
    uploaded_file = st.file_uploader("이미지 파일 (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        source_img = Image.open(uploaded_file)
        st.image(source_img, caption="원본 현장 데이터", use_container_width=True)

with col_right:
    st.subheader("🔍 AI 분석 리포트 & 개선안")
    
    if st.button("🚀 분석 및 개선 이미지 생성 시작"):
        # 키가 설정되어 있는지 확인
        if "여기에" in MY_GOOGLE_API_KEY or "여기에" in MY_OPENAI_API_KEY:
            st.error("⚠️ 코드 상단의 API 키 설정이 필요합니다.")
        elif uploaded_file is None:
            st.warning("분석할 사진을 업로드해 주세요.")
        else:
            try:
                # API 초기화 (미리 설정된 키 사용)
                genai.configure(api_key=MY_GOOGLE_API_KEY)
                gemini = genai.GenerativeModel('gemini-1.5-pro-latest')
                openai_client = OpenAI(api_key=MY_OPENAI_API_KEY)

                # 단계 1: 분석 리포트 생성
                with st.spinner("법령 위반 사항을 대조 분석 중입니다..."):
                    response = gemini.generate_content([ANALYSIS_PROMPT, source_img])
                    full_text = response.text
                    
                    report_content = full_text.split("### REPORT_START")[1].split("### REPORT_END")[0].strip()
                    dalle_prompt = full_text.split("### PROMPT_START")[1].split("### PROMPT_END")[0].strip()
                    
                    st.success("✅ 법적 검토 완료")
                    st.markdown(f"<div class='report-box'>{report_content}</div>", unsafe_allow_html=True)

                # 단계 2: 개선 이미지 생성
                with st.spinner("개선 조치 후의 가상 이미지를 렌더링 중입니다..."):
                    img_gen_res = openai_client.images.generate(
                        model="dall-e-3",
                        prompt=dalle_prompt,
                        size="1024x1024",
                        n=1
                    )
                    
                    gen_img_url = img_gen_res.data[0].url
                    gen_img_data = requests.get(gen_img_url).content
                    gen_img = Image.open(BytesIO(gen_img_data))
                    
                    st.image(gen_img, caption="✨ AI 추천 개선 완료 모습", use_container_width=True)
                    
                    # 다운로드 버튼
                    st.download_button(
                        label="💾 개선 이미지 다운로드",
                        data=gen_img_data,
                        file_name="safety_improvement.jpg",
                        mime="image/jpeg"
                    )

            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")

st.divider()
st.caption("© 2026 Smart EHS Solutions. 본 시스템은 참고용이며 법적 증거로 사용될 수 없습니다.")