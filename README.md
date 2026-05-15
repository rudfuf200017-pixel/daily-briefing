# 가시제거연구소 데일리 브리핑

매일 09:00 KST에 RSS를 수집하여 노션 페이지를 자동 생성하는 시스템입니다.

---

## 사전 준비

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env` 파일을 프로젝트 루트에 생성하고 아래 값을 입력합니다.  
(`.env`는 `.gitignore`에 포함되어 있으므로 커밋되지 않습니다.)

```
NOTION_API_KEY=secret_xxxxxxxxxxxx
NOTION_PARENT_PAGE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

또는 Claude 클라우드 환경 설정 → Secrets에 위 두 변수를 등록합니다.

### 3. Notion Integration 설정

1. [Notion Integrations](https://www.notion.so/my-integrations)에서 Integration을 생성합니다.
2. 생성된 `Internal Integration Secret`을 `NOTION_API_KEY`에 입력합니다.
3. 브리핑 페이지가 생성될 부모 페이지를 열고, 우상단 `...` → `Add connections` → 생성한 Integration을 연결합니다.
4. 부모 페이지 URL에서 페이지 ID를 복사합니다.  
   예: `https://notion.so/가시제거연구소-xxxxxxxxxxxx` → ID: `xxxxxxxxxxxx`

### 4. 수동 실행 테스트

```bash
python main.py
```

### 5. 자동 실행 설정

Claude 클라우드의 `/schedule` 기능을 사용하여 매일 09:00 KST에 `python main.py`를 실행하도록 등록합니다.

---

## RSS 피드 목록

### 시장 뉴스 (검증 완료 ✅)

| 매체명 | RSS URL | 도메인 | 검증 |
|--------|---------|--------|------|
| 식품저널 foodnews | http://www.foodnews.co.kr/rss/allArticle.xml | foodnews.co.kr | ✅ 200 + RSS 2.0 |
| 식품외식경제 | https://www.foodbank.co.kr/rss/allArticle.xml | foodbank.co.kr | ✅ 200 + RSS 2.0 |
| 식품음료신문 | https://www.thinkfood.co.kr/rss/allArticle.xml | thinkfood.co.kr | ✅ 200 + RSS 2.0 |

### 경쟁사 네이버 블로그 (수동 확인 필요 ⚠️)

> **[주의]** Naver는 외부 봇의 `blog.naver.com` 및 `rss.blog.naver.com` 접근을 차단합니다.  
> 자동 검증이 불가능하므로 **아래 URL을 직접 브라우저에서 열어 유효 여부를 확인**한 후 `feeds.py`를 수정해 주세요.  
> 잘못된 URL은 feedparser가 자동으로 무시하므로 시스템 오류는 발생하지 않습니다.

| 브랜드 | RSS URL | 확인 방법 |
|--------|---------|-----------|
| 비비고 (CJ제일제당) | https://rss.blog.naver.com/cjcheiljedang.xml | 브라우저에서 직접 열기 |
| 동원F&B | https://rss.blog.naver.com/dongwonfnb.xml | 브라우저에서 직접 열기 |
| 오뚜기 | https://rss.blog.naver.com/ottogirecipe.xml | 브라우저에서 직접 열기 |
| 청정원 | https://rss.blog.naver.com/chungjungone.xml | 브라우저에서 직접 열기 |

**Naver 블로그 RSS URL 교체 방법:**
1. 경쟁사 Naver 블로그 주소 확인 (예: `blog.naver.com/브랜드ID`)
2. RSS URL: `https://rss.blog.naver.com/브랜드ID.xml`
3. 브라우저에서 직접 열어 XML이 표시되면 유효
4. `feeds.py`의 `NAVER_BLOG_FEEDS` 리스트에 URL 입력 후 `"verified": True`로 변경

### 경쟁사 유튜브 (검증 완료 ✅)

| 채널명 | YouTube RSS URL | 도메인 | 검증 |
|--------|----------------|--------|------|
| 비비고 (bibigo) | https://www.youtube.com/feeds/videos.xml?channel_id=UCGmLtNZFTL6PiKsz3Vpdgbw | youtube.com | ✅ Atom |
| 동원F&B(Dongwon) | https://www.youtube.com/feeds/videos.xml?channel_id=UCs_L1_g_MeTHhuRhJEkF_xA | youtube.com | ✅ Atom |
| 청정원 | https://www.youtube.com/feeds/videos.xml?channel_id=UCni5yuiUB59rF5h3eGrhqJg | youtube.com | ✅ Atom |

---

## 허용 도메인 목록

Claude 클라우드 원격 루틴 실행 시 아래 도메인에만 네트워크 접근이 허용됩니다.

| 도메인 | 용도 |
|--------|------|
| api.notion.com | 노션 페이지 생성 API |
| pypi.org | 패키지 설치 |
| files.pythonhosted.org | 패키지 다운로드 |
| foodnews.co.kr | 시장뉴스 RSS |
| foodbank.co.kr | 시장뉴스 RSS |
| thinkfood.co.kr | 시장뉴스 RSS |
| rss.blog.naver.com | 경쟁사 네이버 블로그 RSS |
| www.youtube.com | 경쟁사 유튜브 RSS (Atom) |

---

## 노션 페이지 구조

```
[가시제거연구소 데일리 브리핑] YYYY-MM-DD
├── 1. 시장 핵심 뉴스 🆕 24시간 내 신규 N건  (또는 📚 폴백)
│   ├── [이미지 블록 - 있을 경우]
│   ├── 기사 제목 (링크)
│   ├── 요약 (description 앞 110자, 원본 그대로)
│   └── 매체명 · 발행시각 (회색)
├── 2. 경쟁사 블로그 동향 🆕 / 📚
│   └── (이미지 + 제목 + 매체명·발행시각, 요약 없음)
└── 3. 경쟁사 유튜브 동향 🆕 / 📚
    └── (썸네일 + 제목 + 채널명·발행시각, 요약 없음)
```

---

## 파일 구조

```
daily-briefing/
├── main.py              # 메인 실행 스크립트
├── feeds.py             # RSS 피드 URL 목록
├── notion_publisher.py  # 노션 페이지 생성 로직
├── requirements.txt     # 의존 패키지
├── .gitignore           # .env 포함
├── CLAUDE.md            # 원격 루틴 작업 지시서
└── README.md            # 이 파일
```
