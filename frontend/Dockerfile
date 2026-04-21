FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

EXPOSE 5173

# Dev mode: hot reload без пересборки
CMD ["npx", "vite", "--host"]