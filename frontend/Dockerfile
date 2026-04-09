FROM node:22-alpine

WORKDIR /app

# Install dependencies first
COPY package*.json ./
RUN npm install

# Copy application files
COPY . .

# Expose Vite's default port
EXPOSE 5173

# Run the dev server and expose it
CMD ["npm", "run", "dev"]
