# Ingatini RAG - Frontend

React + Vite application for Retrieval-Augmented Generation (RAG) with document Q&A capabilities.

## Features

- **Document Upload**: Upload PDF, DOCX, and TXT files
- **AI-Powered Q&A**: Ask questions about your documents using RAG
- **Query History**: Track all your past queries and responses
- **Source Attribution**: See which document chunks contributed to each answer
- **Real-time API Integration**: Connected to FastAPI backend with Gemini API
- **Responsive Design**: Works on desktop and tablet devices

## Tech Stack

- **React 19.2** - UI framework
- **Vite 7.3** - Build tool and dev server
- **Tailwind CSS 4** - Styling
- **Axios** - HTTP client
- **PostCSS** - CSS processing

## Setup

### Prerequisites

- Node.js 18+ and npm
- Backend API running (see [backend README](../backend/README.md))

### Installation

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Update `.env` if your backend is on a different host:
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Features during development:

- Hot module replacement (HMR) for instant code updates
- Automatic browser refresh on save
- Source maps for easier debugging

## Build

Create a production build:
```bash
npm run build
```

Output will be in the `dist/` directory.

### Preview production build:

```bash
npm run preview
```

## Project Structure

```
src/
├── components/
│   ├── DocumentUpload.jsx      # File upload interface
│   ├── ChatInterface.jsx        # Chat/query interface
│   └── QueryHistory.jsx         # Query history view
├── services/
│   └── api.js                   # API client with axios
├── App.jsx                      # Main app component
├── App.css                      # App styles
├── index.css                    # Global + Tailwind styles
└── main.jsx                     # React entry point
```

## Components

### DocumentUpload
Handles file uploads with:
- File selection UI
- Upload progress indication
- Error handling
- Success feedback

### ChatInterface
Full chat interface with:
- Message display (user & assistant)
- Real-time query submission
- Source attribution display
- Loading states

### QueryHistory
Shows past queries with:
- Query text and response
- Timestamps
- Retrieved chunk count
- Auto-refresh capability

### App
Main component that:
- Manages user session
- Checks API health
- Orchestrates all components
- Handles navigation

## API Integration

All API calls go through `src/services/api.js`:

### Available endpoints:

**Users:**
- `createUser(userData)` - Register new user
- `getUser(userId)` - Get user details
- `listUsers(skip, limit)` - List users

**Documents:**
- `uploadDocument(userId, file)` - Upload document
- `getDocuments(userId)` - List user documents
- `getDocument(docId)` - Get document details
- `deleteDocument(docId)` - Delete document

**Queries:**
- `queryDocuments(queryData)` - Ask question (RAG)
- `getQueryHistory(userId)` - View past queries

**Health:**
- `healthCheck()` - Check API status

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000/api` | Backend API URL |

## Styling

Built with Tailwind CSS v4:

- Responsive grid layout
- Blue/indigo color scheme
- Smooth transitions
- Focus states for accessibility
- Dark mode ready

## Troubleshooting

### API Connection Errors

1. Check backend is running: `docker compose up`
2. Verify `VITE_API_BASE_URL` in `.env`
3. Check browser console for CORS errors
4. Ensure backend and frontend are accessible to each other

### Build Issues

1. Clear node_modules and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

2. Clear Vite cache:
```bash
rm -rf node_modules/.vite
```

### Hot Module Replacement Not Working

1. Check `.env` has correct API URL
2. Ensure no other app is using port 5173
3. Try clearing browser cache (Ctrl+Shift+Delete)

## Performance Tips

- Production build is optimized with code splitting
- CSS is minified (4.82 kB → 1.55 kB gzipped)
- JavaScript is tree-shaken to remove unused code
- Assets are hashed for long-term caching

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Future Enhancements

- [ ] User authentication with login
- [ ] Multiple document collections
- [ ] Advanced search filters
- [ ] Export query results
- [ ] Dark mode toggle
- [ ] Mobile app version
- [ ] Real-time collaboration
- [ ] Document analytics dashboard

## Contributing

1. Create a feature branch
2. Make your changes
3. Test with `npm run build`
4. Submit a pull request

## License

Part of the Ingatini RAG project
