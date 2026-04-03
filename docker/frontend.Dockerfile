FROM node:20-alpine AS builder

WORKDIR /app/frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend /app/frontend
RUN npm run build

FROM nginx:1.27-alpine
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/frontend/dist /usr/share/nginx/html
