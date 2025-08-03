# Frontend Dependency Management

## Overview

The frontend uses npm with exact version locking via `package-lock.json` to ensure reproducible builds.

## Key Files

- **`package.json`**: Defines dependencies with semantic versioning
- **`package-lock.json`**: Locks exact versions of all dependencies and sub-dependencies
- **`.npmrc`**: npm configuration (if present)

## Management Commands

### Install Dependencies
```bash
# Install all dependencies from package-lock.json
npm ci

# Or install and update package-lock.json
npm install
```

### Update Dependencies
```bash
# Check for outdated packages
npm outdated

# Update all dependencies to latest compatible versions
npm update

# Update specific package
npm install package-name@latest
```

### Security Management
```bash
# Check for security vulnerabilities
npm audit

# Fix automatically fixable vulnerabilities
npm audit fix

# Check production dependencies only
npm audit --omit=dev
```

### Development Workflow
```bash
# Development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Lint code
npm run lint

# Preview production build
npm run preview
```

## Best Practices

1. **Always commit `package-lock.json`** to version control
2. **Use `npm ci` in CI/CD** for faster, reliable installs
3. **Regularly run `npm audit`** to check for security issues
4. **Pin exact versions** for critical dependencies when needed
5. **Keep dependencies updated** but test thoroughly

## Dependency Categories

### Production Dependencies
- `react`: UI framework
- `react-dom`: React DOM renderer
- `axios`: HTTP client
- `lucide-react`: Icon library

### Development Dependencies
- `vite`: Build tool and dev server
- `@vitejs/plugin-react`: React plugin for Vite
- `eslint`: Code linting
- `vitest`: Testing framework
- TypeScript definitions for React
