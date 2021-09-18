# 🎯스크럼 (항해 1주차 웹개발 미니 프로젝트 20조)
SCRUM! 오늘의 각오와 컨디션을 작성하여 공유하며 오늘 하루를 시작해보세요~!!
다른 사람들의 각오를 보고 동기부여도 받고 스스로 반성하는 시간도 가져봅시다.

## 👥member
*2021년 9월 13일 ~ 21년 9월 17일
#### 안선호(https://github.com/seonhoAn)
#### 정재우(https://github.com/jeongjae95)
#### 최재환(https://github.com/lieblichoi)
#### 하원빈(https://github.com/woodimora)

## 🌊페이지 별 주요기능
- 로그인,회원가입 
  - JWT를 이용해 로그인과 회원가입을 구현하였습니다.
  - 정규화를 이용하여 회원가입 시 필요한 정보들을 필터링 하였습니다.
  - 아이디와 닉네임의 중복확인이 가능합니다.
  - 로그인을 하면 JWT를 발급하여 사용자 인증을 하였습니다.
 
- 게시글 작성
  - 각오를 작성하는 페이지를 따로 만들고 게시글을 저장하는 기능을 구현하였습니다.
  - 하루 한번 게시글을 작성하여야 전체 게시글을 볼 수 있도록 하는 기능을 구현하였습니다.

- 게시글 표시
  - DB에 저장한 ('_id')값을 불러와 게시글을 불러오는 기능을 구현했습니다.
  - 게시글 선택 시 해당 게시물을 작성한 유저의 페이지로 이동할 수 있도록 구현하였습니다.
  - 각각의 포스팅박스에 역동적인 javascript를 추가하였습니다.
  - 게시물을 불러올 때 일정 갯수만 불러오고, 초과하는 게시물은 더보기 버튼으로 불러 올 수 있도록 구현했습니다.
 
- 상세페이지
  - DB에 저장한 ('_id')값에 맞는 게시물을 불러와 나타내고 삭제할 수 있는 기능을 구현했습니다.
  - 사진 업로드 기능으로 프로필 변경을 할 수 있도록 기능을 구현했습니다.

## ⭐️기술 스택
HTML, CSS, javascript, Python, flask

## 📽미니프로젝트 결과물
https://youtu.be/lCG_lE8HfVM

1. 로그인 페이지
<img width="1138" alt="Screen Shot 2021-09-18 at 12 24 31 PM" src="https://user-images.githubusercontent.com/70922665/133871019-b466e06b-9c2a-4dfc-895d-2a33a5d8c4b8.png">
2. 각오 작성 페이지
<img width="1141" alt="Screen Shot 2021-09-18 at 12 25 07 PM" src="https://user-images.githubusercontent.com/70922665/133871029-82079a1a-35e3-4a47-801f-ee94c9224f89.png">
3. 메인 페이지
<img width="1140" alt="Screen Shot 2021-09-18 at 12 24 56 PM" src="https://user-images.githubusercontent.com/70922665/133871039-289bd1c9-5f35-48a0-8f51-47cad17d266f.png">
4. 프로필 페이지
<img width="1141" alt="Screen Shot 2021-09-18 at 12 25 21 PM" src="https://user-images.githubusercontent.com/70922665/133871045-9284aecd-1d8c-4080-b6b2-543cce424d1a.png">
5. 프로필 수정 모달
<img width="1138" alt="Screen Shot 2021-09-18 at 12 27 35 PM" src="https://user-images.githubusercontent.com/70922665/133871079-24e54870-46ea-4b74-8916-4389092dcd95.png">

