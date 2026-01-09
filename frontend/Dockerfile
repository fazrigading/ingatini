FROM node:20-alpine

# Create app directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Install curl for the healthcheck
RUN apk add --no-cache curl

# Copy the rest of the app
COPY . .

# Expose Vite dev port
EXPOSE 5173

# Start dev server and listen on all interfaces
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
