# Dockerfile for Next.js (supports both dev and prod mode)
FROM node:20.11.0-alpine

WORKDIR /app

# Install dependencies for better build performance
RUN apk add --no-cache libc6-compat

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port 3000
EXPOSE 3000

# Build Next.js for production (will be skipped in dev mode)
RUN npm run build || true

# Default to development mode (can be overridden in docker-compose)
ENV NODE_ENV=development

# Start command (can be overridden in docker-compose)
CMD ["npm", "run", "dev"]
