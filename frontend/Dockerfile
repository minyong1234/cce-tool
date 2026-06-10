FROM node:20-slim AS builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 빌드 결과물을 nginx로 서빙
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html

# nginx 설정 (React Router 새로고침 대응)
RUN echo 'server { \
  listen 80; \
  location / { \
    root /usr/share/nginx/html; \
    index index.html; \
    try_files $uri $uri/ /index.html; \
  } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
