FROM node:22-slim

WORKDIR /app
RUN chown node:node /app

USER node

COPY --chown=node:node package*.json ./
RUN npm install --no-audit --no-fund

COPY --chown=node:node . .

# Compile optimized production Next.js build.
RUN npm run build

EXPOSE 3000

# Start on the port Google Cloud Run injects into $PORT, falling back to 3000.
CMD ["sh", "-c", "npx next start -p ${PORT:-3000}"]
