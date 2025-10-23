# Development Dockerfile for Next.js with hot reload
FROM node:20.11.0-alpine

WORKDIR /app

# Install dependencies for better build performance
RUN apk add --no-cache libc6-compat

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port 3000
EXPOSE 3000

# Set environment to development
ENV NODE_ENV=development

# Start Next.js in development mode with hot reload
CMD ["npm", "run", "dev"]
