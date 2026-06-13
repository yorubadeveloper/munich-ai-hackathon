FROM node:22-slim

WORKDIR /app
RUN chown node:node /app

USER node

COPY --chown=node:node package*.json ./
RUN npm ci --no-audit --no-fund

COPY --chown=node:node . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
