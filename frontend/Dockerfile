FROM node:20-alpine

WORKDIR /app

# package*.json копируем отдельно, чтобы кеш Docker работал эффективно
COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]