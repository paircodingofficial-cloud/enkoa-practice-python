#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  실습자료 업데이트
#
#  새로 올라온 자료를 받아옵니다.
#  '내작업/' 폴더와 여러분이 만든 파일은 절대 건드리지 않습니다.
# ─────────────────────────────────────────────────────────────
set -u
cd "$(dirname "$0")" || exit 1

if [ ! -d .git ]; then
  echo "❌ 여기는 git 저장소가 아닙니다. 저장소 폴더 안에서 실행하세요."
  exit 1
fi

# 배포된 원본 파일을 수정한 게 있으면 먼저 백업
CHANGED=$(git diff --name-only)
if [ -n "$CHANGED" ]; then
  STAMP=$(date +%m%d_%H%M)
  mkdir -p ".백업/$STAMP"
  echo "⚠️  배포 원본을 수정한 파일이 있어 .백업/$STAMP 로 옮겨 둡니다:"
  echo "$CHANGED" | while IFS= read -r f; do
    [ -f "$f" ] || continue
    echo "    - $f"
    mkdir -p ".백업/$STAMP/$(dirname "$f")"
    cp "$f" ".백업/$STAMP/$f"
  done
  echo "    (앞으로는 '내작업/' 에 복사해서 실습하세요)"
  echo
fi

# 배포 파일만 원상복구 — 추적되지 않는 내 파일은 그대로 남습니다
git checkout -- . 2>/dev/null

echo "📥 새 자료를 받는 중..."
if git pull --ff-only; then
  echo
  echo "✅ 업데이트 완료!"
else
  echo
  echo "❌ 업데이트 실패. 위 메시지를 강사님께 보여주세요."
  exit 1
fi
