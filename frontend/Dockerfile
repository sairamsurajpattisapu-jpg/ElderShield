# =====================================================================
# ELDERSHIELD PRODUCTION FRONTEND DOCKERFILE
# Multi-stage container build with Vite build and Nginx Alpine
# =====================================================================

FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Nginx Alpine Runtime Stage
FROM nginx:alpine AS runtime

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
