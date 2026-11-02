
# ==========================================
# 4. 메인 화면
# ==========================================

st.markdown(
    '<div class="main-title">📚 MBTI 문화 추천소</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">나의 성격에 어울리는 책과 영화를 찾아보자!</div>',
    unsafe_allow_html=True
)

st.write("")

st.info(
    "💡 MBTI를 선택하면 나의 성향을 참고한 "
    "책 2권과 영화 2편을 추천해 드려요!"
)

# MBTI 선택
selected_mbti = st.selectbox(
    "🧩 나의 MBTI 유형을 선택해 주세요!",
    options=list(recommendations.keys()),
    index=None,
    placeholder="MBTI 유형을 선택하세요!"
)

# ==========================================
# 5. 추천 결과 출력
# ==========================================

if selected_mbti:

    data = recommendations[selected_mbti]

    st.divider()

    st.header(f"✨ {selected_mbti} 유형 추천 결과")

    st.success(data["intro"])

    # 책 추천
    st.subheader("📚 당신을 위한 책 추천 BEST 2")

    book_cols = st.columns(2)

    for i, book in enumerate(data["books"]):

        title, author, year, country, summary, reason = book

        with book_cols[i]:

            st.markdown(f"### 📖 {title}")

            st.caption(f"{year}년 출판 | {country} 작품")

            st.write(f"✍️ **작가:** {author}")

            st.write(f"📝 **줄거리:** {summary}")

            st.info(f"💡 **추천 이유:** {reason}")

    st.divider()

    # 영화 추천
    st.subheader("🎬 당신을 위한 영화 추천 BEST 2")

    movie_cols = st.columns(2)

    for i, movie in enumerate(data["movies"]):

        title, director, year, country, summary, reason = movie

        with movie_cols[i]:

            st.markdown(f"### 🍿 {title}")

            st.caption(f"{year}년 개봉 | {country} 작품")

            st.write(f"🎥 **감독:** {director}")

            st.write(f"📝 **줄거리:** {summary}")

            st.info(f"💡 **추천 이유:** {reason}")

    st.divider()

    # 마무리
    st.subheader("🌈 나만의 문화생활 즐기기!")

    st.write(
        f"오늘의 추천 MBTI는 **{selected_mbti}**! "
        "책과 영화를 통해 새로운 생각과 경험을 만나 보세요."
    )

    st.balloons()

else:

    st.warning("👆 먼저 자신의 MBTI를 선택해 주세요!")

    st.markdown("### 🎁 어떤 작품을 만나게 될까요?")

    st.write(
        "책 속에서 새로운 세상을 발견하고, "
        "영화 속에서 다양한 이야기를 경험해 보세요!"
    )

    st.markdown("""
    | 📚 책 | 🎬 영화 |
    |:---:|:---:|
    | 새로운 지식과 상상력 | 다양한 인물과 이야기 |
    | 감성적인 독서 시간 | 재미있는 영상 경험 |
    """)

# ==========================================
# 6. 하단 안내
# ==========================================

st.divider()

st.caption(
    "📌 본 프로그램은 MBTI 성향을 바탕으로 한 문화 콘텐츠 추천 서비스입니다."
)

st.caption(
    "※ MBTI는 재미있는 성향 탐색 도구이며, "
    "추천 결과가 개인의 취향을 반드시 의미하지는 않습니다."
)

st.caption(
    "※ 모든 추천 작품은 2000년 이후 출판 또는 개봉한 작품입니다."
)
