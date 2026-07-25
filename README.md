# 데이터 직무 채용공고 알림 봇

사람인 / 인크루트 / 자소설닷컴에서 신입 및 경력무관 데이터 분석·데이터
관련 채용공고를 주기적으로 수집해서 이메일로 알려주는 봇입니다.
GitHub Actions로 하루 2번(08:00, 18:00 KST) 자동 실행됩니다.

## 사이트별 수집 방식과 한계

- **사람인**: 검색 기능으로 "데이터" 키워드 검색 후 제목을 다시 필터링합니다.
  경력 조건(신입/경력무관)이 공고에 명시되어 있어 정확하게 필터링됩니다.
- **인크루트**: 검색 결과 페이지에서 "데이터" 키워드로 검색 후 제목/경력
  조건을 필터링합니다. EUC-KR 인코딩 사이트이고, 명시적인 페이지네이션
  파라미터를 찾지 못해 한 번의 요청으로 오는 기본 결과(첫 페이지)만
  가져옵니다.
- **자소설닷컴**: 채용 목록 페이지가 키워드 검색을 지원하지 않는 캘린더형
  위젯이라, 사이트맵에서 최근 등록된 공고 ID를 가져와 상세 페이지 제목으로
  필터링합니다. 실행마다 최대 80건의 신규 공고만 확인합니다.

## 제외한 사이트와 이유

- **잡코리아**: robots.txt가 키워드 검색 페이지(`/Search/`)를 모든 크롤러
  대상으로 명시적으로 금지합니다. 대안으로 허용된 `/recruit/joblist` 직무별
  목록 페이지를 시도해봤지만, 이 페이지의 직무 필터 폼도 결국 내부적으로
  `/Search/`로 제출되는 구조라 필터 파라미터가 서버에서 무시되고 데이터와
  무관한 일반 추천 공고만 반환되는 것을 확인했습니다. 크롤러에게 허용된
  경로만으로는 키워드/직무 필터링이 불가능해서 제외했습니다.
- **인디스워크(inthiswork.com)**: robots.txt가 `anthropic-ai`, `ClaudeBot`을
  사이트 전체에서 명시적으로 차단하고 있어서, Claude로 작성된 이 봇에
  포함시키지 않았습니다.
- **원티드**: `/robots.txt` 요청 자체를 CDN(CloudFront)이 403으로 차단해서
  크롤링 정책을 확인할 수 없는 상태로 한 번 추가했었으나, 실제로 GitHub
  Actions에서 실행해보니 채용정보 API 요청도 403으로 차단되는 것을 확인하고
  제외했습니다. 클라우드/서버 IP 대역을 막는 정책으로 보입니다.

사이트 페이지/API 구조가 바뀌면 스크래퍼가 깨질 수 있습니다. 실행 로그에
수집 실패 메시지가 보이면 `scrapers/` 안의 선택자를 다시 확인해야 합니다.

## 사전 준비

### 1. Gmail 앱 비밀번호 발급

1. Google 계정 > 보안 > 2단계 인증을 켭니다 (필수).
2. https://myaccount.google.com/apppasswords 에서 앱 비밀번호를 생성합니다.
3. 생성된 16자리 비밀번호를 복사해둡니다 (`EMAIL_PASSWORD`로 사용).

### 2. GitHub 저장소 만들고 코드 올리기

```bash
cd job-alert-bot
git init
git add .
git commit -m "init: data job alert bot"
git branch -M main
git remote add origin https://github.com/<your-id>/<repo-name>.git
git push -u origin main
```

### 3. GitHub Secrets 등록

저장소 Settings > Secrets and variables > Actions 에서 다음 3개를 등록합니다.

| Secret 이름 | 값 |
|---|---|
| `EMAIL_ADDRESS` | 발신용 Gmail 주소 |
| `EMAIL_PASSWORD` | 위에서 발급한 앱 비밀번호 (16자리) |
| `EMAIL_TO` | 알림 받을 이메일 주소 (본인과 같아도 됨) |

### 4. 실행 확인

저장소의 Actions 탭 > "Data Job Alert" 워크플로 > "Run workflow" 를 눌러
수동으로 한 번 실행해봅니다. 정상 동작하면 이후 매일 08:00, 18:00(KST)에
자동 실행됩니다.

## 로컬에서 테스트하기

```bash
pip install -r requirements.txt
EMAIL_ADDRESS=you@gmail.com EMAIL_PASSWORD=xxxxxxxxxxxxxxxx EMAIL_TO=you@gmail.com python main.py
```

## 알림 주기/키워드 조정

- 알림 시각: `.github/workflows/job-alert.yml`의 `cron` 값 수정
- 검색 키워드: `config.py`의 `DATA_KEYWORDS` 수정
- 사이트당 이메일에 담기는 최대 공고 수: `config.py`의 `MAX_ITEMS_PER_SITE`

## 최초 실행 관련 안내

`data/seen.json`이 초기 상태(빈 리스트)이기 때문에 첫 실행 시 그 시점에
조건에 맞는 공고들이 한꺼번에 신규로 잡혀 이메일로 발송됩니다. 이후부터는
새로 올라온 공고만 알려줍니다.
