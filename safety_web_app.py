import streamlit as st
import google.generativeai as genai
from openai import OpenAI
from PIL import Image
import requests
from io import BytesIO
import base64

# 1. 페이지 설정
st.set_page_config(
    page_title="AI 산업안전 감사관 (EHS)",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 커스텀 CSS (UI 개선)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #145a8d;
        border: none;
    }
    .report-container {
        padding: 25px;
        border-radius: 12px;
        background-color: white;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .sidebar-info {
        font-size: 0.9em;
        color: #666;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 사이드바 설정
with st.sidebar:
    st.title("⚙️ 설정")
    st.markdown("---")
    google_key = st.text_input("Google Gemini API Key", type="password", help="Gemini 1.5 Pro/Flash 키")
    openai_key = st.text_input("OpenAI API Key", type="password", help="DALL-E 3 이미지 생성용 키")
    
    st.markdown("---")
    st.markdown("### 🛠️ 가이드")
    st.markdown("""
    1. 왼쪽 설정창에 **API 키**를 입력하세요.
    2. 분석할 현장 사진을 **업로드**하세요.
    3. **[분석 시작]** 버튼을 누르세요.
    4. AI의 법적 검토와 개선 이미지를 확인하세요.
    """)
    st.markdown("---")
    st.caption("v1.0 Powered by Gemini & DALL-E")

# 4. 분석 프롬프트 정의
ANALYSIS_PROMPT = """
# Role
귀하는 20년 경력의 베테랑 '대한민국 산업안전보건지도사'이자 'EHS(환경안전보건) 감사관'입니다. 
제공된 사진을 대한민국 [산업안전보건법] 및 [산업안전보건기준에 관한 규칙]에 근거하여 엄격하고 정밀하게 분석하십시오.

# Analysis Steps
1. 이미지 스캐닝: 사진 내의 모든 작업자, 장비, 시설, 환경적 요소를 식별합니다.
2. 위반 사항 식별: 발견된 상황을 현행 산안법 기준과 대조하여 부적합 사항을 찾습니다.
3. 리포트 작성: 아래의 양식에 맞춰 분석 결과를 출력합니다.

# Output Format
반드시 아래의 구분 태그를 사용하여 출력하십시오.
### REPORT_START
🚩 [종합 안전 등급: 위험/경고/보통]
#### 1. 법적 위반 사항 및 위험 요인
* 위반 항목: 
* 관련 법규: 
* 위험 분석: 
#### 2. 즉시 조치 사항
#### 3. 중장기 개선 대책
### REPORT_END

### PROMPT_START
(이곳에 분석 결과를 바탕으로, 모든 위험 요소가 법규에 맞게 개선된 실사 수준의 현장 사진을 생성하기 위한 상세한 영어 프롬프트를 작성하세요. 원본 사진의 구도와 장비 속성을 유지하되 절연 커버, 경고판, 접지선 등 안전 장치가 완벽히 갖춰진 모습을 묘사해야 합니다.)
### PROMPT_END
"""

# 5. 메인 레이아웃
st.title("🛡️ AI 산업안전 분석 및 시각화 시스템")
st.markdown("##### 대한민국 산업안전보건법 기준 현장 위험성 평가 및 개선 시뮬레이션")
st.divider()

col_orig, col_res = st.columns([1, 1])

with col_orig:
    st.subheader("📸 현장 데이터 입력")
    uploaded_file = st.file_uploader("현장 사진 업로드 (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img_input = Image.open(uploaded_file)
        st.image(img_input, caption="분석 대상 원본 사진", use_container_width=True)

with col_res:
    st.subheader("📋 분석 결과 및 개선 시뮬레이션")
    
    if st.button("🚀 현장 분석 및 개선 이미지 생성") and uploaded_file:
        if not google_key or not openai_key:
            st.error("⚠️ 먼저 사이드바에서 API 키를 입력해 주세요.")
        else:
            try:
                # API 초기화
                genai.configure(api_key=google_key)
                gemini_model = genai.GenerativeModel('gemini-1.5-flash') # 속도 위주 선택
                openai_client = OpenAI(api_key=openai_key)

                # Step 1: 분석 및 프롬프트 생성 (Gemini)
                with st.spinner("⚖️ 산업안전보건법령 대조 분석 중..."):
                    response = gemini_model.generate_content([ANALYSIS_PROMPT, img_input])
                    full_text = response.text
                    
                    # 텍스트 분리
                    report = full_text.split("### REPORT_START")[1].split("### REPORT_END")[0].strip()
                    dalle_prompt = full_text.split("### PROMPT_START")[1].split("### PROMPT_END")[0].strip()
                    
                    st.success("✅ 법적 분석 완료")
                    st.markdown(f'<div class="report-container">{report}</div>', unsafe_allow_html=True)
                
                st.divider()
                
                # Step 2: 개선 이미지 생성 (DALL-E 3)
                with st.spinner("🎨 개선 조치 후의 예상 모습 시뮬레이션 중..."):
                    img_gen_res = openai_client.images.generate(
                        model="dall-e-3",
                        prompt=dalle_prompt,
                        size="1024x1024",
                        quality="standard",
                        n=1
                    )
                    
                    gen_url = img_gen_res.data[0].url
                    gen_img_bytes = requests.get(gen_url).content
                    gen_img = Image.open(BytesIO(gen_img_bytes))
                    
                    st.image(gen_img, caption="✨ AI 추천 안전 개선 시뮬레이션", use_container_width=True)
                    
                    # 결과물 저장/다운로드
                    st.download_button(
                        label="📥 개선 이미지 다운로드",
                        data=gen_img_bytes,
                        file_name="safety_improvement_result.jpg",
                        mime="image/jpeg"
                    )

            except Exception as e:
                st.error(f"❌ 오류 발생: {str(e)}")

st.divider()
st.caption("※ 본 서비스는 AI 분석 결과이며, 최종적인 법적 판단 및 현장 조치는 공인된 안전관리자의 검토가 반드시 필요합니다.")
