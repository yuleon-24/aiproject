
import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(
    page_title="서울 1박 2일 여행 지도",
    page_icon="🗺️",
    layout="wide"
)

places = [
    {
        "id": 1, "name": "경복궁", "en": "Gyeongbokgung Palace",
        "lat": 37.5796, "lon": 126.9770, "day": 1, "order": 1,
        "time": "09:30", "duration": "약 1시간 30분",
        "category": "역사·문화",
        "desc": "조선 왕조의 대표 궁궐로 근정전과 전통 건축의 아름다움을 볼 수 있습니다.",
        "tip": "한복 체험을 곁들이기 좋으며, 휴궁일과 관람 시간을 확인하세요."
    },
    {
        "id": 2, "name": "북촌한옥마을", "en": "Bukchon Hanok Village",
        "lat": 37.5826, "lon": 126.9830, "day": 1, "order": 2,
        "time": "11:20", "duration": "약 1시간",
        "category": "전통·거리",
        "desc": "전통 한옥이 모여 있어 서울의 옛 주거 풍경과 골목길을 경험할 수 있습니다.",
        "tip": "주민이 거주하는 곳이므로 조용히 관람하고 출입 제한 구역을 지켜주세요."
    },
    {
        "id": 3, "name": "광장시장", "en": "Gwangjang Market",
        "lat": 37.5700, "lon": 126.9997, "day": 1, "order": 3,
        "time": "12:40", "duration": "약 1시간",
        "category": "시장·음식",
        "desc": "빈대떡과 김밥, 전통 간식 등 다양한 한국 길거리 음식을 맛볼 수 있습니다.",
        "tip": "점심시간에는 혼잡할 수 있으니 여유 있게 둘러보세요."
    },
    {
        "id": 4, "name": "동대문디자인플라자(DDP)",
        "en": "Dongdaemun Design Plaza",
        "lat": 37.5669, "lon": 127.0095, "day": 1, "order": 4,
        "time": "14:10", "duration": "약 1시간",
        "category": "건축·전시",
        "desc": "독특한 곡선형 건축물과 전시·디자인 공간으로 유명한 랜드마크입니다.",
        "tip": "전시 일정에 따라 관람 가능한 공간이 달라질 수 있습니다."
    },
    {
        "id": 5, "name": "명동", "en": "Myeongdong",
        "lat": 37.5636, "lon": 126.9850, "day": 1, "order": 5,
        "time": "16:00", "duration": "약 1시간 30분",
        "category": "쇼핑·먹거리",
        "desc": "화장품과 패션 상점, 길거리 음식이 모여 있는 대표 번화가입니다.",
        "tip": "저녁 무렵 길거리 음식과 쇼핑을 함께 즐기기 좋습니다."
    },
    {
        "id": 6, "name": "N서울타워", "en": "N Seoul Tower",
        "lat": 37.5512, "lon": 126.9882, "day": 1, "order": 6,
        "time": "18:00", "duration": "약 1시간 30분",
        "category": "전망·야경",
        "desc": "남산에서 서울 도심의 전경과 야경을 감상할 수 있는 전망 명소입니다.",
        "tip": "일몰 전후에 방문하면 낮 풍경과 야경을 모두 즐기기 좋습니다."
    },
    {
        "id": 7, "name": "홍대거리", "en": "Hongdae Street",
        "lat": 37.5563, "lon": 126.9236, "day": 2, "order": 1,
        "time": "10:00", "duration": "약 1시간 30분",
        "category": "문화·쇼핑",
        "desc": "개성 있는 상점과 카페, 거리 공연 등 젊고 활기찬 문화를 느낄 수 있습니다.",
        "tip": "주말에는 거리 공연과 팝업 행사를 만날 수 있습니다."
    },
    {
        "id": 8, "name": "서울숲·성수동",
        "en": "Seoul Forest & Seongsu",
        "lat": 37.5444, "lon": 127.0374, "day": 2, "order": 2,
        "time": "12:00", "duration": "약 2시간",
        "category": "공원·카페",
        "desc": "서울숲의 녹지와 성수동의 개성 있는 카페·편집숍을 함께 즐길 수 있습니다.",
        "tip": "공원 산책 후 성수동 카페와 편집숍을 둘러보세요."
    },
    {
        "id": 9, "name": "코엑스·별마당도서관",
        "en": "COEX & Starfield Library",
        "lat": 37.5116, "lon": 127.0594, "day": 2, "order": 3,
        "time": "15:00", "duration": "약 1시간 30분",
        "category": "쇼핑·문화",
        "desc": "대형 복합 쇼핑 공간과 높은 서가가 인상적인 별마당도서관을 둘러볼 수 있습니다.",
        "tip": "실내에서 쇼핑과 휴식을 함께 즐기기 좋습니다."
    },
    {
        "id": 10, "name": "강남역 일대", "en": "Gangnam",
        "lat": 37.4979, "lon": 127.0276, "day": 2, "order": 4,
        "time": "17:00", "duration": "약 1시간 30분",
        "category": "도심·쇼핑",
        "desc": "대형 상점과 음식점, 카페가 밀집한 현대적인 서울의 번화가입니다.",
        "tip": "여행 마지막 일정으로 식사와 쇼핑을 즐기기 좋습니다."
    }
]

st.title("🗺️ 서울 1박 2일 여행 지도")
st.caption(
    "외국인 관광객에게 잘 알려진 서울 대표 명소 10곳을 둘러보는 추천 코스"
)

a, b, c = st.columns(3)
a.metric("여행 기간", "1박 2일")
b.metric("관광지", "10곳")
c.metric("일정", "전통 도심 + 트렌디 서울")

st.info(
    "관광지 목록은 공식 방문객 순위가 아니라 "
    "대표 명소를 바탕으로 구성한 추천 목록입니다. "
    "운영 시간과 휴무일은 방문 전에 확인하세요."
)

st.subheader("📍 지도에서 관광지와 이동 순서 확인하기")

map_data = json.dumps(places, ensure_ascii=False)

html = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<link rel="stylesheet"
href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>

<style>
html, body {
    margin: 0;
    padding: 0;
}

#map {
    height: 610px;
    width: 100%;
    border-radius: 12px;
}

.num {
    background: white;
    border: 2px solid #243447;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    line-height: 26px;
    text-align: center;
    font-weight: bold;
    color: #17202a;
    box-shadow: 0 1px 5px #777;
}

.legend {
    background: white;
    padding: 10px 12px;
    border-radius: 8px;
    line-height: 1.8;
    box-shadow: 0 1px 6px #aaa;
    font: 13px Arial;
}

.dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 6px;
}
</style>
</head>

<body>
<div id="map"></div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
const places = __DATA__;

const map = L.map('map').setView(
    [37.556, 126.991], 12
);

L.tileLayer(
    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }
).addTo(map);

const colors = {
    1: '#2563eb',
    2: '#e05a35'
};

// 관광지 마커 표시
places.forEach(p => {

    const color = colors[p.day];

    const icon = L.divIcon({
        className: '',
        html: `
            <div class="num"
            style="border-color:${color}">
            ${p.id}
            </div>
        `,
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });

    L.marker(
        [p.lat, p.lon],
        {icon: icon}
    )
    .addTo(map)
    .bindPopup(`
        <b>${p.id}. ${p.name}</b><br>
        ${p.en}<br>
        <b>${p.day}일 차 · ${p.time}</b><br>
        ${p.category}<br><br>
        ${p.desc}
    `);
});

// 날짜별 이동 경로 표시
[1, 2].forEach(day => {

    const pts = places
        .filter(p => p.day === day)
        .sort((x, y) => x.order - y.order);

    L.polyline(
        pts.map(p => [p.lat, p.lon]),
        {
            color: colors[day],
            weight: 4,
            opacity: 0.8,
            dashArray: '8,7'
        }
    ).addTo(map);

});

// 지도 범례
const legend = L.control({
    position: 'bottomright'
});

legend.onAdd = function() {

    const d = L.DomUtil.create(
        'div',
        'legend'
    );

    d.innerHTML = `
        <b>이동 순서</b><br>
        <span class="dot"
        style="background:${colors[1]}"></span>
        1일 차<br>

        <span class="dot"
        style="background:${colors[2]}"></span>
        2일 차<br>

        숫자 마커를 누르면 설명 표시
    `;

    return d;
};

legend.addTo(map);

// 모든 관광지가 보이도록 지도 크기 조정
map.fitBounds(
    L.latLngBounds(
        places.map(p => [p.lat, p.lon])
    ),
    {padding: [25, 25]}
);

</script>
</body>
</html>
"""

html = html.replace("__DATA__", map_data)

components.html(
    html,
    height=625,
    scrolling=False
)

# 날짜별 일정과 관광지 설명
schedule = [
    (
        1,
        "📅 1일 차 — 서울의 전통과 야경",
        "궁궐과 전통 골목, 시장을 둘러본 뒤 "
        "명동 쇼핑과 남산 야경으로 마무리합니다."
    ),
    (
        2,
        "📅 2일 차 — 트렌디한 서울",
        "홍대에서 시작해 성수의 카페 거리, "
        "코엑스와 강남을 둘러봅니다."
    )
]

for day, title, intro in schedule:

    st.markdown("---")
    st.header(title)
    st.write(intro)

    day_places = sorted(
        [p for p in places if p["day"] == day],
        key=lambda x: x["order"]
    )

    for p in day_places:

        with st.container(border=True):

            left, right = st.columns([1, 5])

            left.markdown(f"### {p['order']}")

            right.markdown(
                f"**{p['time']} · {p['name']}**"
            )

            right.caption(
                f"{p['en']} | {p['duration']} | {p['category']}"
            )

            right.write(p["desc"])
            right.write(f"💡 여행 팁: {p['tip']}")

            right.markdown(
                f"[Google 지도에서 위치 보기]"
                f"(https://www.google.com/maps/search/?api=1"
                f"&query={p['lat']},{p['lon']})"
            )

st.markdown("---")

st.subheader("🚇 이동 안내")

st.write(
    "- 지도 선은 관광지 방문 순서를 보여주는 개략 경로이며 "
    "실제 도로·대중교통 경로는 아닙니다."
)

st.write(
    "- 실시간 대중교통과 길찾기는 네이버 지도, "
    "카카오맵 또는 Google 지도에서 확인하세요."
)

st.write(
    "- 지도 타일은 OpenStreetMap을 사용하므로 "
    "인터넷 연결이 필요합니다."
)

st.caption(
    "추천 일정은 이동·혼잡·개인 취향에 따라 조정할 수 있습니다."
)
