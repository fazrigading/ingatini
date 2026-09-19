FROM node:20-alpine

# Create app directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Install curl for the healthcheck
RUN apk add --no-cache curl

# Copy the rest of the app and build for production
COPY . .
RUN npm run build

# Expose Vite port (dev server and preview both use it)
EXPOSE 5173

# Default: serve the production build.
# For hot-reload development, docker-compose overrides this command with
# `npm run dev -- --host 0.0.0.0`.
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "5173"]
