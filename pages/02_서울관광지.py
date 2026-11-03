
import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Seoul Travel Map",
    page_icon="🇰🇷",
    layout="wide"
)

# 서울 주요 관광지 TOP 10
places = [
    {
        "rank": 1, "name": "명동", "en": "Myeong-dong",
        "lat": 37.5636, "lon": 126.9850,
        "category": "쇼핑 · K-뷰티",
        "desc": "K-뷰티 매장, 패션 숍, 길거리 음식이 모여 있는 대표 쇼핑 거리예요.",
        "tip": "화장품 쇼핑과 간식 투어를 함께 즐기기 좋아요."
    },
    {
        "rank": 2, "name": "N서울타워", "en": "N Seoul Tower",
        "lat": 37.5512, "lon": 126.9882,
        "category": "전망 · 랜드마크",
        "desc": "남산에서 서울의 도심 풍경을 한눈에 볼 수 있는 전망 명소예요.",
        "tip": "해 질 무렵 방문하면 낮과 밤의 서울을 모두 감상할 수 있어요."
    },
    {
        "rank": 3, "name": "코엑스", "en": "COEX",
        "lat": 37.5116, "lon": 127.0594,
        "category": "쇼핑 · 문화",
        "desc": "대형 쇼핑·전시 복합공간으로 별마당도서관이 유명해요.",
        "tip": "실내에서 쇼핑과 전시, 휴식을 즐겨 보세요."
    },
    {
        "rank": 4, "name": "강남역 일대", "en": "Gangnam Station",
        "lat": 37.4979, "lon": 127.0276,
        "category": "쇼핑 · 트렌드",
        "desc": "패션, 음식점, 카페와 최신 유행을 만날 수 있는 거리예요.",
        "tip": "한국의 도시 라이프스타일을 경험해 보세요."
    },
    {
        "rank": 5, "name": "홍대거리", "en": "Hongdae",
        "lat": 37.5563, "lon": 126.9236,
        "category": "청년문화 · 공연",
        "desc": "개성 있는 상점, 카페, 거리 공연과 음악 문화가 유명해요.",
        "tip": "거리 공연과 독특한 소품 숍을 둘러보세요."
    },
    {
        "rank": 6, "name": "경복궁", "en": "Gyeongbokgung Palace",
        "lat": 37.5796, "lon": 126.9770,
        "category": "역사 · 전통문화",
        "desc": "조선 왕조의 법궁으로 한국 전통 건축을 볼 수 있어요.",
        "tip": "한복 체험과 궁궐 관람을 함께 즐겨 보세요."
    },
    {
        "rank": 7, "name": "북촌한옥마을", "en": "Bukchon Hanok Village",
        "lat": 37.5826, "lon": 126.9830,
        "category": "전통 · 골목",
        "desc": "전통 한옥이 모여 있어 옛 서울의 골목 풍경을 느낄 수 있어요.",
        "tip": "주민 거주 지역이므로 조용히 관람해 주세요."
    },
    {
        "rank": 8, "name": "동대문디자인플라자", "en": "DDP",
        "lat": 37.5669, "lon": 127.0095,
        "category": "건축 · 디자인",
        "desc": "독특한 곡선형 건축물과 전시, 디자인 행사가 열리는 문화 공간이에요.",
        "tip": "건축 사진을 찍거나 전시 일정을 확인해 보세요."
    },
    {
        "rank": 9, "name": "광장시장", "en": "Gwangjang Market",
        "lat": 37.5700, "lon": 126.9997,
        "category": "전통시장 · 먹거리",
        "desc": "빈대떡, 김밥 등 한국 길거리 음식과 전통시장 분위기를 즐길 수 있어요.",
        "tip": "여러 음식을 조금씩 나눠 먹어 보세요."
    },
    {
        "rank": 10, "name": "서울숲·성수", "en": "Seoul Forest & Seongsu",
        "lat": 37.5444, "lon": 127.0374,
        "category": "공원 · 카페문화",
        "desc": "넓은 도심 공원과 개성 있는 카페, 편집숍이 있는 지역이에요.",
        "tip": "공원 산책 후 성수동 카페를 방문해 보세요."
    }
]

# 디자인
st.markdown("""
<style>
.stApp {
    background-color: #F5F7FC;
}
.hero {
    padding: 25px;
    border-radius: 18px;
    background: linear-gradient(115deg, #183B56, #2B6777);
    color: white;
    margin-bottom: 15px;
}
.hero h1 {
    color: white;
}
.hero p {
    color: #EAF4F4;
    font-size: 17px;
}
.place-card {
    background: white;
    border: 1px solid #E7ECF2;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 10px;
}
.place-card h3 {
    color: #183B56;
}
.muted {
    color: #64748B;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# 메인 제목
st.markdown("""
<div class="hero">
    <h1>🇰🇷 Seoul Travel Map</h1>
    <p>
    Discover Seoul's Top 10 Attractions!
    <br>
    서울에서 꼭 방문해야 할 대표 관광지 10곳을 만나보세요.
    </p>
</div>
""", unsafe_allow_html=True)

st.info(
    "🌏 외국인 관광객에게 추천하는 서울의 대표 관광 명소 TOP 10"
)

st.caption(
    "※ 관광지 추천 목록이며 공식 방문객 순위와는 다를 수 있습니다."
)

# 지도 데이터
map_places = [
    {
        "rank": p["rank"],
        "name": p["name"],
        "en": p["en"],
        "lat": p["lat"],
        "lon": p["lon"],
        "category": p["category"],
        "desc": p["desc"]
    }
    for p in places
]

places_json = json.dumps(
    map_places,
    ensure_ascii=False
)

# 지도 HTML
map_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">

<link rel="stylesheet"
href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>

<style>
html, body {
    margin: 0;
    padding: 0;
}
#map {
    width: 100%;
    height: 590px;
    border-radius: 14px;
}
.number-icon {
    background: #174A68;
    color: white;
    border: 2px solid white;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    line-height: 26px;
    text-align: center;
    font-weight: bold;
    font-size: 13px;
    box-shadow: 0 2px 7px rgba(0,0,0,.3);
}
.leaflet-popup-content {
    font-family: Arial, sans-serif;
    line-height: 1.5;
}
</style>
</head>

<body>

<div id="map"></div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>

const places = PLACES_DATA;

const map = L.map('map').setView(
    [37.5665, 126.9780],
    11
);

// OpenStreetMap 지도
L.tileLayer(
    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }
).addTo(map);

// 관광지 마커 표시
const bounds = [];

places.forEach(p => {

    const icon = L.divIcon({
        className: '',
        html: '<div class="number-icon">' + p.rank + '</div>',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });

    const marker = L.marker(
        [p.lat, p.lon],
        {icon: icon}
    ).addTo(map);

    marker.bindPopup(
        '<b>' + p.rank + '. ' + p.name + '</b><br>' +
        p.en + '<br>' +
        '<i>' + p.category + '</i><br>' +
        p.desc
    );

    bounds.push([p.lat, p.lon]);

});

// 관광지 전체가 보이도록 지도 조정
map.fitBounds(
    bounds,
    {padding: [25, 25]}
);

</script>
</body>
</html>
""".replace("PLACES_DATA", places_json)

# 지도 출력
st.subheader("🗺️ Seoul Tourist Map")

st.write(
    "지도 위의 숫자 마커를 클릭하면 "
    "관광지의 이름과 설명을 확인할 수 있어요."
)

components.html(
    map_html,
    height=610,
    scrolling=False
)

# 관광지 설명
st.divider()

st.header("📍 Seoul TOP 10 Attractions")

st.write(
    "서울의 대표 관광지와 여행 팁을 확인해 보세요!"
)

# 2개씩 카드 출력
for start in range(0, len(places), 2):

    cols = st.columns(2)

    for col, p in zip(cols, places[start:start+2]):

        with col:

            st.markdown(f"""
            <div class="place-card">

                <h3>
                {p['rank']:02d}. {p['name']}
                </h3>

                <div class="muted">
                {p['en']} · {p['category']}
                </div>

                <p>{p['desc']}</p>

                <p>
                💡 <b>Travel Tip:</b>
                {p['tip']}
                </p>

            </div>
            """, unsafe_allow_html=True)

            query = p["en"].replace(" ", "+")

            st.markdown(
                f"[📍 Google Maps에서 위치 보기]"
                f"(https://www.google.com/maps/search/?api=1&query={query}+Seoul)"
            )

# 마무리
st.divider()

st.subheader("✈️ Enjoy Your Trip to Seoul!")

st.write(
    "궁궐과 한옥에서 한국의 전통문화를 만나고, "
    "시장과 쇼핑 거리에서 서울의 활기를 느껴보세요!"
)

st.caption(
    "Map data © OpenStreetMap contributors"
)

st.caption(
    "※ 방문 전 관광지의 운영시간과 휴무일을 확인하세요."
)
