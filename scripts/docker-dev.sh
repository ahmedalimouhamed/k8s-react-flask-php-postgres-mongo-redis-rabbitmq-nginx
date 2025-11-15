#!/bin/bash

set -e

echo "Starting Docker development environment..."

cd ./scripts

case "$1" in

    "up")
        echo "Starting all services..."
        docker-compose up -d

        echo "waiting for services to be healthy..."
        ./wait-for-services.sh

        echo "Services are ready!"
        echo ""
        echo "Servie URLS:"
        echo "  Frontend:           http://localhost:3000"
        echo "  Backend API:        http://localhost:5000"
        echo "  RabbitMQ MGMT:      http://localhost:15672 (guest/guest)"
        echo "  Redis Commander:    http://localhost:8081"
        echo "  Mongo Express:      htto://localhost:8082"
        ;;

    "down")
        echo "Stopping all services..."
        docker-compose down
        ;;
    
    "logs")
        echo "Showing logs..."
        docker-compose logs -f
        ;;

    "build")
        echo "Rebuild images..."
        docker-compose build --no-cache
        ;;

    "status")
        echo "Service status:"
        docker-compose ps
        ;;

    "clean")
        echo "Cleaning up..."
        docker-compos down -v
        docker system prune -f
        ;;

    *)
        echo "Usage : $0 {up|down|logs|build|restart|status|clean}"
        exit 1
        ;;

esac