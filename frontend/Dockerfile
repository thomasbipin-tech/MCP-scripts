# DealProof frontend image — multi-stage build: compile the Vite/React app,
# then serve the static bundle with nginx.

FROM node:22-alpine AS build
WORKDIR /srv/app

# Wildcard copy so this doesn't fail when package-lock.json isn't committed
# yet. Falls back to `npm install`; once a lockfile exists this will pick it
# up automatically and use `npm ci`.
COPY package*.json ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

COPY . .
RUN npm run build

FROM nginx:alpine AS runtime
COPY --from=build /srv/app/dist /usr/share/nginx/html
# Simple SPA fallback so client-side routing works on refresh/deep links.
RUN printf 'server {\n\
    listen 80;\n\
    server_name _;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
