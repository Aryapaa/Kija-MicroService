FROM node:14

WORKDIR /app

COPY package*.json /app

RUN npm install

COPY app.js /app

EXPOSE 5000

CMD ["node", "app.js"]