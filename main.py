import streamlit as st
st.title('나의 첫 웹 서비스 만들기!')
a=st.text_input('이름을 입력하세요!')
st.selectbox('좋아하는 음식을 선택하세요!',['밥','빵','면'])
if st.button('인사말 생성'):
  st.write('반갑습니다.')
  st.info(a+'님, 안녕하세요!')
  st.warning(b+'를 좋아하시는 군요!')
  st.error('잘부탁드립니다!')
