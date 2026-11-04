# ── Stage 1: build the React app ─────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (cached unless package.json changes)
COPY package.json ./
RUN npm install 

# Copy source and build
COPY . .

# VITE_API_URL is empty so the browser uses relative paths,
# which Nginx will proxy to the API service
ARG VITE_API_URL=""
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build


# ── Stage 2: serve with Nginx ─────────────────────────────────────────────────
FROM nginx:1.25-alpine

# Remove default Nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built React app
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://127.0.0.1/health/live || exit 1

CMD ["nginx", "-g", "daemon off;"]
