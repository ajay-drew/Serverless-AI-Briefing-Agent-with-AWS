# AI Briefing Agent - Frontend

React + TypeScript + Vite frontend for the AI Briefing Agent.

## Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Environment Variables

Create a `.env` file:

```
VITE_API_URL=http://localhost:8000
```

For production deployment, set `VITE_API_URL` to your backend URL.

## Development

The app runs on `http://localhost:3000` and proxies API requests to `http://localhost:8000`.

## Deployment

### Vercel

1. Connect your GitHub repository
2. Set root directory to `frontend`
3. Build command: `npm run build`
4. Output directory: `dist`
5. Add environment variable: `VITE_API_URL=https://your-backend.onrender.com`

### Netlify

1. Connect your GitHub repository
2. Base directory: `frontend`
3. Build command: `npm run build`
4. Publish directory: `frontend/dist`
5. Add environment variable: `VITE_API_URL=https://your-backend.onrender.com`
