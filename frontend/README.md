# NET-EST Frontend

This is the React frontend for the NET-EST linguistic analysis tool.

## Quick Start

```bash
# Install dependencies
npm ci

# Start development server
npm run dev
```

The development server will start at http://localhost:3000 by default.

## Available Scripts

- **`npm run dev`**: Starts the development server with hot reloading
- **`npm run build`**: Builds the application for production
- **`npm run preview`**: Serves the production build for preview
- **`npm run test`**: Runs the test suite
- **`npm run lint`**: Runs ESLint to check code quality

## Project Structure

```
frontend/
├── public/            # Static assets
├── src/
│   ├── components/    # React components
│   │   ├── common/    # Shared UI components
│   │   └── layout/    # Layout components
│   ├── services/      # API and service integrations
│   ├── utils/         # Utility functions
│   ├── App.jsx        # Main application component
│   └── main.jsx       # Application entry point
├── package.json       # Dependencies and scripts
└── vite.config.js     # Vite configuration
```

## Documentation

For comprehensive documentation on the frontend architecture, component structure, and development guidelines, please refer to:

- [Central Documentation Hub](../DOCUMENTATION.md)
- [Architecture Documentation](../ARCHITECTURE.md)
- [Development Guide](../DEVELOPMENT.md)
- [State Management](./STATE_MANAGEMENT.md)
- [Dependencies](./DEPENDENCIES.md)

## API Integration

The frontend communicates with the backend API using Axios. The base configuration is defined in `src/services/api.js`.

Ensure the backend server is running at the URL specified in your environment variables (default: http://localhost:8000) for the frontend to function properly.

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
