
import streamlit as st

# ---------------------------------
# 1. 페이지 기본 설정
# ---------------------------------
st.set_page_config(
    page_title="MBTI 진로 탐색소",
    page_icon="🎯",
    layout="wide"
)

# ---------------------------------
# 2. 디자인
# ---------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #F5F7FB;
}
.main-title {
    text-align: center;
    color: #384B75;
    font-size: 38px;
    font-weight: bold;
}
.sub-title {
    text-align: center;
    color: #777777;
    font-size: 17px;
}
.job-card {
    background-color: white;
    padding: 22px;
    border-radius: 15px;
    border: 1px solid #E2E7F0;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------
# 3. MBTI별 진로 데이터
# 연봉은 국내 예상 연봉 범위 (세전)
# ---------------------------------
career_data = {
    "ISTJ": {
        "intro": "체계적이고 책임감이 강한 현실주의자 📚",
        "jobs": [
            {
                "name": "회계사 💰",
                "major": "경영학과, 회계학과, 경제학과",
                "personality": "꼼꼼하고 논리적이며 숫자를 정확하게 분석하는 사람",
                "salary": "4,000~7,000만 원"
            },
            {
                "name": "공무원 🏛️",
                "major": "행정학과, 법학과, 정치외교학과",
                "personality": "책임감이 강하고 규칙을 잘 지키며 꾸준한 사람",
                "salary": "3,000~5,000만 원"
            }
        ]
    },
    "ISFJ": {
        "intro": "배려심이 깊고 주변 사람을 잘 챙기는 수호자 🌷",
        "jobs": [
            {
                "name": "간호사 🏥",
                "major": "간호학과",
                "personality": "세심하고 공감 능력이 뛰어나며 책임감 있는 사람",
                "salary": "3,500~5,000만 원"
            },
            {
                "name": "초등학교 교사 🍎",
                "major": "초등교육과",
                "personality": "인내심이 있고 다른 사람의 성장을 돕는 사람",
                "salary": "4,000~6,000만 원"
            }
        ]
    },
    "INFJ": {
        "intro": "통찰력이 있고 타인의 성장을 돕는 옹호자 🌱",
        "jobs": [
            {
                "name": "심리상담사 🧠",
                "major": "심리학과, 상담심리학과",
                "personality": "공감 능력이 뛰어나고 깊이 있게 생각하는 사람",
                "salary": "3,000~5,000만 원"
            },
            {
                "name": "작가 ✍️",
                "major": "문예창작학과, 국어국문학과",
                "personality": "상상력이 풍부하고 생각을 글로 표현하는 사람",
                "salary": "2,500~5,000만 원"
            }
        ]
    },
    "INTJ": {
        "intro": "분석적이고 전략적인 계획을 세우는 전략가 ♟️",
        "jobs": [
            {
                "name": "소프트웨어 개발자 💻",
                "major": "컴퓨터공학과, 소프트웨어학과",
                "personality": "논리적이고 문제 해결 능력이 뛰어난 사람",
                "salary": "4,000~7,000만 원"
            },
            {
                "name": "연구원 🔬",
                "major": "자연과학계열, 공학계열",
                "personality": "탐구심이 강하고 분석과 연구를 즐기는 사람",
                "salary": "3,500~6,000만 원"
            }
        ]
    },
    "ISTP": {
        "intro": "실용적이고 문제 해결에 능숙한 장인 🔧",
        "jobs": [
            {
                "name": "기계공학 기술자 ⚙️",
                "major": "기계공학과, 자동차공학과",
                "personality": "손재주가 좋고 기계와 원리를 이해하는 사람",
                "salary": "3,500~6,000만 원"
            },
            {
                "name": "항공정비사 ✈️",
                "major": "항공정비학과, 항공기계공학과",
                "personality": "집중력이 높고 세밀한 작업을 잘하는 사람",
                "salary": "3,500~5,500만 원"
            }
        ]
    },
    "ISFP": {
        "intro": "감각적이고 자신만의 감성을 가진 예술가 🎨",
        "jobs": [
            {
                "name": "시각디자이너 🖌️",
                "major": "시각디자인학과, 산업디자인학과",
                "personality": "창의적이고 색감과 디자인 감각이 좋은 사람",
                "salary": "3,000~5,000만 원"
            },
            {
                "name": "셰프 👨‍🍳",
                "major": "호텔조리학과, 외식조리학과",
                "personality": "감각적이고 섬세하며 새로운 요리를 만드는 것을 좋아하는 사람",
                "salary": "3,000~5,000만 원"
            }
        ]
    },
    "INFP": {
        "intro": "상상력이 풍부하고 자신만의 가치를 추구하는 중재자 🌈",
        "jobs": [
            {
                "name": "콘텐츠 기획자 🎬",
                "major": "미디어학과, 광고홍보학과",
                "personality": "창의적이고 새로운 아이디어를 떠올리는 사람",
                "salary": "3,000~5,000만 원"
            },
            {
                "name": "일러스트레이터 🖼️",
                "major": "회화과, 디자인학과",
                "personality": "예술적 감각과 풍부한 상상력을 가진 사람",
                "salary": "2,500~4,500만 원"
            }
        ]
    },
    "INTP": {
        "intro": "호기심이 많고 지식을 탐구하는 논리술사 🔍",
        "jobs": [
            {
                "name": "데이터 분석가 📊",
                "major": "통계학과, 데이터사이언스학과",
                "personality": "논리적이고 데이터를 분석하는 것을 좋아하는 사람",
                "salary": "4,000~6,500만 원"
            },
            {
                "name": "과학 연구원 🧪",
                "major": "물리학과, 화학과, 생명과학과",
                "personality": "탐구심이 강하고 복잡한 원리를 이해하는 사람",
                "salary": "3,500~6,000만 원"
            }
        ]
    },
    "ESTP": {
        "intro": "활동적이고 도전을 즐기는 사업가 🚀",
        "jobs": [
            {
                "name": "영업 전문가 🤝",
                "major": "경영학과, 마케팅학과",
                "personality": "적극적이고 순발력이 있으며 소통을 잘하는 사람",
                "salary": "3,000~6,000만 원"
            },
            {
                "name": "스포츠 트레이너 🏋️",
                "major": "체육학과, 스포츠과학과",
                "personality": "활동적이고 도전 정신이 강한 사람",
                "salary": "2,800~4,500만 원"
            }
        ]
    },
    "ESFP": {
        "intro": "사교적이고 즐거움을 만드는 연예인 🎉",
        "jobs": [
            {
                "name": "방송인 🎤",
                "major": "방송연예과, 미디어학과",
                "personality": "표현력이 좋고 사람들과 어울리는 것을 좋아하는 사람",
                "salary": "2,500~6,000만 원"
            },
            {
                "name": "이벤트 기획자 🎪",
                "major": "이벤트학과, 광고홍보학과",
                "personality": "활발하고 현장 대응 능력이 뛰어난 사람",
                "salary": "3,000~5,000만 원"
            }
        ]
    },
    "ENFP": {
        "intro": "열정적이고 새로운 가능성을 발견하는 활동가 🌟",
        "jobs": [
            {
                "name": "광고 기획자 📢",
                "major": "광고홍보학과, 미디어학과",
                "personality": "아이디어가 풍부하고 소통 능력이 뛰어난 사람",
                "salary": "3,500~5,500만 원"
            },
            {
                "name": "창업가 🏢",
                "major": "경영학과, 창업학과",
                "personality": "도전 정신이 강하고 새로운 사업을 구상하는 사람",
                "salary": "소득 편차가 큼"
            }
        ]
    },
    "ENTP": {
        "intro": "창의적이고 새로운 아이디어를 즐기는 변론가 💡",
        "jobs": [
            {
                "name": "사업 전략 기획자 📈",
                "major": "경영학과, 경제학과",
                "personality": "분석력과 창의력이 뛰어나고 새로운 전략을 만드는 사람",
                "salary": "4,000~7,000만 원"
            },
            {
                "name": "마케팅 전문가 📱",
                "major": "마케팅학과, 광고홍보학과",
                "personality": "트렌드에 민감하고 설득력과 기획력이 좋은 사람",
                "salary": "3,500~6,000만 원"
            }
        ]
    },
    "ESTJ": {
        "intro": "리더십이 강하고 조직을 이끄는 경영자 👔",
        "jobs": [
            {
                "name": "경영 관리자 🏢",
                "major": "경영학과, 산업경영학과",
                "personality": "결단력이 있고 목표를 체계적으로 관리하는 사람",
                "salary": "4,500~8,000만 원"
            },
            {
                "name": "경찰관 🚔",
                "major": "경찰행정학과, 법학과",
                "personality": "책임감이 강하고 판단력과 실행력이 좋은 사람",
                "salary": "3,500~5,500만 원"
            }
        ]
    },
    "ESFJ": {
        "intro": "친절하고 사람들과 협력하는 사교적인 외교관 💕",
        "jobs": [
            {
                "name": "인사 담당자 👥",
                "major": "경영학과, 심리학과",
                "personality": "대인관계 능력이 좋고 다른 사람을 배려하는 사람",
                "salary": "3,500~5,500만 원"
            },
            {
                "name": "호텔 서비스 매니저 🏨",
                "major": "호텔경영학과, 관광학과",
                "personality": "친절하고 서비스 정신과 소통 능력이 뛰어난 사람",
                "salary": "3,000~5,000만 원"
            }
        ]
    },
    "ENFJ": {
        "intro": "타인에게 영감을 주고 성장을 돕는 선도자 🌻",
        "jobs": [
            {
                "name": "교사 📖",
                "major": "교육학과, 사범대학 관련 학과",
                "personality": "리더십이 있고 다른 사람을 가르치는 것을 좋아하는 사람",
                "salary": "4,000~6,000만 원"
            },
            {
                "name": "기업 교육 전문가 🎓",
                "major": "교육학과, 경영학과",
                "personality": "소통 능력이 좋고 사람의 성장을 돕는 사람",
                "salary": "3,500~5,500만 원"
            }
        ]
    },
    "ENTJ": {
        "intro": "목표 지향적이고 강한 추진력을 가진 통솔자 👑",
        "jobs": [
            {
                "name": "기업 경영 컨설턴트 📊",
                "major": "경영학과, 경제학과",
                "personality": "전략적 사고와 문제 해결 능력이 뛰어난 사람",
                "salary": "4,500~8,000만 원"
            },
            {
                "name": "프로젝트 매니저 🗂️",
                "major": "산업공학과, 경영학과",
                "personality": "리더십이 강하고 계획을 실행으로 옮기는 사람",
                "salary": "4,000~7,000만 원"
            }
        ]
    }
}

# ---------------------------------
# 4. 메인 화면
# ---------------------------------
st.markdown(
    '<div class="main-title">🎯 MBTI 진로 탐색소</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">나의 성격 유형으로 찾아보는 특별한 미래 직업!</div>',
    unsafe_allow_html=True
)

st.write("")
st.info("💡 나의 MBTI를 선택하고 나에게 어울리는 진로를 찾아보세요!")

# MBTI 선택
mbti_list = list(career_data.keys())

selected_mbti = st.selectbox(
    "🧩 나의 MBTI 유형을 선택해 주세요!",
    mbti_list,
    index=None,
    placeholder="MBTI를 선택하세요"
)

# ---------------------------------
# 5. 결과 화면
# ---------------------------------
if selected_mbti:

    data = career_data[selected_mbti]

    st.divider()

    st.subheader(f"✨ 당신은 {selected_mbti} 유형!")

    st.write(data["intro"])

    st.success("당신의 성향을 참고한 추천 진로 2가지를 소개합니다!")

    col1, col2 = st.columns(2)

    for i, job in enumerate(data["jobs"]):

        target_col = col1 if i == 0 else col2

        with target_col:

            st.markdown(
                f"""
                <div class="job-card">
                    <h3>{job['name']}</h3>
                    <p><b>🎓 추천 학과</b></p>
                    <p>{job['major']}</p>
                    <p><b>✨ 적합한 성격과 특성</b></p>
                    <p>{job['personality']}</p>
                    <p><b>💰 예상 연봉</b></p>
                    <h4 style="color:#4267B2;">{job['salary']}</h4>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.divider()

    st.subheader("🌈 나만의 진로 탐색 TIP")

    st.write("""
    - MBTI는 나의 성향을 이해하는 참고 자료예요.
    - 추천 직업이 반드시 나에게 가장 적합하다는 뜻은 아니에요.
    - 실제 진로를 결정할 때는 관심 분야, 능력, 가치관도 함께 고려해 보세요!
    """)

    st.caption(
        "※ 연봉은 국내 직업의 대략적인 세전 참고 범위이며, "
        "경력·기업 규모·지역·근무 형태에 따라 달라질 수 있습니다."
    )

else:
    st.warning("👆 먼저 MBTI 유형을 선택해 주세요!")
    st.markdown("### 어떤 미래가 기다리고 있을까요? 🚀")
    st.write("나의 MBTI를 선택하면 추천 직업과 학과를 확인할 수 있어요!")
