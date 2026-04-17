FROM node:20-alpine

WORKDIR /app

# Copy frontend files
COPY test_frontend/package*.json ./
COPY test_frontend/vite.config.js ./

# Install dependencies
RUN npm install

# Copy source
COPY test_frontend/src ./src
COPY test_frontend/index.html ./
COPY test_frontend/public ./public

# Expose port
EXPOSE 5173

# Run dev server
CMD ["npm", "run", "dev", "--", "--host"]