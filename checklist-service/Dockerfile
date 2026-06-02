# Dockerfile

# 베이스 이미지: Python 3.11 슬림 버전 (불필요한 패키지 제거된 경량 버전)
FROM python:3.11-slim

# 컨테이너 안의 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 먼저 복사 후 설치
# (코드보다 먼저 복사하면 패키지가 변경되지 않는 한 캐시 재사용 → 빌드 빠름)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 나머지 코드 복사
COPY . .

# 8000번 포트 노출
EXPOSE 8000

# 컨테이너 시작 시 실행 명령어
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
