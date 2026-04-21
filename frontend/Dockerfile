FROM node:20-alpine

WORKDIR /app

# Copy all files first
COPY . .

# Install dependencies including dev dependencies  
RUN npm install

# Build the app using npx
RUN npx vite build

EXPOSE 5173

CMD ["npx", "vite", "preview", "--port", "5173", "--host"]