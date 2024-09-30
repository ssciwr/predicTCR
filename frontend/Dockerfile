FROM node:22-slim AS builder

LABEL org.opencontainers.image.source=https://github.com/ssciwr/predicTCR
LABEL org.opencontainers.image.description="predicTCR frontend production image"
LABEL org.opencontainers.image.licenses=MIT

WORKDIR /app

COPY package*.json ./

RUN npm install -g pnpm

RUN pnpm install

COPY . .

RUN echo "VITE_REST_API_LOCATION=/api" > .env

RUN pnpm run build-only

FROM nginx

COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf
