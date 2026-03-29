FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# 🚨 关键一步：安装 Playwright 需要的系统依赖和 Chromium 浏览器内核
RUN playwright install --with-deps chromium

COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]