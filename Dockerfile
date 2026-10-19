
FROM python:3.13-slim

# 2) 작업 폴더 /app
WORKDIR /app

# 3) appuser 계정 생성
RUN useradd --create-home appuser

# 4) 필요한 라이브러리 복사하고 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5) app 폴더 복사
COPY app ./app

# 6) appuser로 진행하도록 지정
USER appuser

# 7) 8000번 포트 지정
EXPOSE 8000

# 8) 30초마다 확인하고 3연속 응답 없을 시 "unhealthy"로 표시
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# 9) 컨테이너 실행 시 서버를 켬
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
