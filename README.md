# 파이썬 실습자료

엔코아 AI캠퍼스 「데이터 분석 & AI 머신러닝 캠프」 실습용 주피터 노트북입니다.
수업 진도에 맞춰 자료가 추가됩니다.

---

## ⚠️ 딱 하나만 기억하세요

> ### 배포된 자료는 **읽기 전용**입니다.
> ### 실습은 **`내작업/` 폴더에 복사해서** 하세요.

셀을 실행만 해도 파일이 바뀔 수 있으니, 원본은 건드리지 마세요.

---

## 1. 준비 (처음 한 번만)

```bash
# 자료 내려받기
git clone https://github.com/paircodingofficial-cloud/enkoa-practice-python.git
cd enkoa-practice-python

# uv 설치 — macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows(PowerShell): powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
#  설치 후 터미널을 새로 열어야 합니다.

# 파이썬 3.12 프로젝트로 초기화
uv init --python 3.12

# 주피터 설치 (가상환경 .venv 가 자동으로 만들어집니다)
uv add jupyter
```

앞으로 라이브러리가 필요할 때도 `uv add <이름>` 으로 추가합니다.
`day02`~`day04` 는 **추가 설치 없이** 파이썬 표준 라이브러리만 씁니다.

---

## 2. 실습하기

오늘 자료를 `내작업/` 으로 **복사한 뒤**, 복사본을 열어 작업합니다.

```bash
mkdir -p 내작업/day02
cp day02_파이썬_변수_제어문/*.ipynb 내작업/day02/
```

> Windows: `mkdir 내작업\day02` → `copy day02_파이썬_변수_제어문\*.ipynb 내작업\day02\`
> 파일 탐색기에서 끌어다 복사해도 똑같습니다.

---

## 3. 새 자료 받기

```bash
git pull
```

### 잘 안 될 때

원본을 건드렸다면 아래 같은 메시지가 뜨면서 막힙니다.

```
error: Your local changes would be overwritten by merge
```

이때만 복구 도우미를 실행하세요.

```bash
uv run python 업데이트.py
```

배포 원본을 되돌려 충돌을 없애고 새 자료를 받아옵니다.
`내작업/` 폴더와 여러분이 만든 파일은 **건드리지 않고**, 되돌리기 전 내용은 `.백업/` 에 보관합니다.

---

## 4. 폴더 구성

```
enkoa-practice-python/
├── day02_파이썬_변수_제어문/     ← 배포 원본 (읽기 전용)
│   ├── 교안_01, 교안_02      수업 중 함께 진행
│   └── 과제_LV1 / LV2 / LV3  기초 · 응용 · 통합
├── 내작업/                ← 여기서 실습 (GitHub 에 안 올라감)
└── 업데이트.py            ← git pull 이 막혔을 때만
```

과제의 `# [자가채점]` 셀은 답을 쓴 뒤 실행해 에러가 없으면 통과입니다.
