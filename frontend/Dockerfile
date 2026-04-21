FROM node:20-alpine

WORKDIR /app

# Copy package files first for better caching
COPY package*.json tsconfig*.json vite.config.ts ./

# Install ALL dependencies including dev
RUN npm install

# Copy source code
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "--port", "5173"]