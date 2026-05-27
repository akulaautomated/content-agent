FROM node:20-alpine

WORKDIR /app

# Copy package files first (better layer caching)
COPY package.json ./

# npm install creates node_modules AND generates package-lock.json automatically
RUN npm install

# Copy the rest of the source code
COPY . .

EXPOSE 3000

# Run Next.js in development mode (hot reload enabled)
CMD ["npm", "run", "dev"]
