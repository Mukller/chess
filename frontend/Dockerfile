FROM node:20-alpine AS builder

WORKDIR /app

ARG VITE_API_BASE_URL=/api
ARG VITE_WS_BASE_URL=
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_WS_BASE_URL=$VITE_WS_BASE_URL

COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

COPY tsconfig.json tsconfig.node.json vite.config.ts tailwind.config.js postcss.config.js index.html ./
COPY src ./src

RUN npm run build

FROM nginx:1.27-alpine AS runner

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

RUN useradd -m -u 1000 appuser 2>/dev/null || true
RUN chown -R appuser:appuser /app 2>/dev/null || true
USER appuser
CMD ["nginx", "-g", "daemon off;"]

# Author: Anton Petnitsky
# GitHub: https://github.com/Mukller/chess
# Last modified: 2026-08-13 00:23:16 +0300
