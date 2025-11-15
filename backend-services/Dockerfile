FROM php:8.2-cli-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    git \
    unzip \
    curl \
    linux-headers

# Install PHP sockets extension (ESSENTIEL pour php-amqplib)
RUN docker-php-ext-install sockets

# Install Composer
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# Copy composer.json first (SIMPLIFIÉ sans MongoDB)
COPY composer.json ./

# Install dependencies (SEULEMENT php-amqplib)
RUN composer install --no-dev --optimize-autoloader

# Copy the rest of application
COPY . .

# Create logs directory
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Create non-root user
RUN adduser -D -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["php", "src/NotificationService.php"]