# 3d_forest — Riverside Forest

강가의 오두막, 호수, 마을과 숲을 걸어 다니며 낚시도 하는 몰입형 3D 자연 탐험 (three.js, 단일 HTML).
**플레이:** https://sandboxwork.github.io/3d_forest/ (첫 로딩에 약 58MB를 받습니다)

## 조작
WASD 이동 · Shift 달리기 · Space 점프 · E 문 열기/주민과 대화 · R 낚싯대(클릭: 던지기/챔질/감기) · M 미니맵 · N 지도 방향 · T 시간대 · Esc 설정(스위치로 꽃/동물/마을/조명/미니맵 끄기)

## 구성
- `index.html` — 빌드 결과물. 지형·하늘·물 셰이더 등 원본 월드 코드 + Blender 에셋(압축 임베드) + 런타임 모듈이 한 파일에 들어 있습니다.
- `source/` — 소스
  - `riverside_forest.html` — 에셋이 비어 있는 템플릿(월드/렌더링 코드)
  - `assets/*.js` — 런타임 모듈: `assetlib`(번들 디코더), `village_core`/`village`(마을·주민), `fauna`, `flora`, `cabin`(오두막), `fishing`, `minimap`
  - `assets/build_assets.py` — 에셋 번들을 양자화·gzip 하여 HTML 에 주입하고 모듈을 삽입
  - `assets/blender/*.py` — 모든 3D 모델을 만드는 Blender(5.1) 파이썬 스크립트 (동물 `deer.py` 등, 집 `hs_*`, 실내 `lv_/kt_/bd_*`, 마을 `vh_/vl_/vp_*`, 꽃 `meadow_*` …), 공용 헬퍼 `bl_common.py`
  - `assets/tex/` — 절차적으로 만든 PBR 텍스처(JPEG)
  - `assets/out/*.meta.json` — 에셋 메타(피벗, 충돌, 서식지 등)

## 다시 만들기
1. Blender 로 `assets/blender/` 스크립트를 실행하면 `assets/out/<이름>.json` 지오메트리 번들이 생성됩니다 (용량이 커서(≈240MB) 이 레포에는 포함하지 않았습니다. 예: `blender -b --python assets/blender/deer.py`).
2. `uv run --with numpy python3 source/assets/build_assets.py` → `source/riverside_forest.html` 이 갱신됩니다.
3. 결과 파일을 `index.html` 로 복사해 호스팅합니다.

모든 모델과 텍스처는 Blender/numpy 코드로 직접 생성했고 외부 에셋은 사용하지 않았습니다. 예외로 three.js r128 은 cdnjs 에서 불러옵니다.
