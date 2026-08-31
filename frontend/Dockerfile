FROM node:22-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build -- --configuration=production

FROM alpine:3.20

RUN apk add --no-cache darkhttpd

COPY --from=build /app/dist/incident-response/browser /usr/share/nginx/html

EXPOSE 80

CMD ["darkhttpd", "/usr/share/nginx/html", "--port", "80"]
