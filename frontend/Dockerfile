# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built app - UTILISEZ /app/build au lieu de /app/dist
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy .env file
COPY .env /usr/share/nginx/html/.env

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]