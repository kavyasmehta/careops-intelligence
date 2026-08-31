# Development-oriented image: docker-compose mounts source for hot reload.
# (A separate production build is not needed here — the frontend is
# Vercel-deployable directly from the repo; see docs/deployment.md.)
FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
