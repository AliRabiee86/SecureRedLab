# SecureRedLab - Frontend

**Penetration Testing Platform - React + TypeScript + Vite Frontend**

## 🚀 Phase 8.1 - Project Setup COMPLETE

This is the frontend application for SecureRedLab, built with modern web technologies.

---

## 📦 Tech Stack

- **Framework**: React 18+ with TypeScript 5+
- **Build Tool**: Vite 5+ (50-80x faster than Webpack)
- **UI Framework**: TailwindCSS 3+
- **State Management**: Zustand 4+
- **Routing**: React Router 6+
- **Icons**: Lucide React
- **Testing**: Vitest + React Testing Library

---

## 🎯 Features

✅ **Phase 8.1 Complete**:
- ✅ Vite + React + TypeScript setup
- ✅ TailwindCSS with custom security color palette
- ✅ Path aliases configured (`@components`, `@pages`, etc.)
- ✅ Zustand stores (Auth, Dashboard, Theme)
- ✅ React Router with protected routes
- ✅ Sidebar + Header layout
- ✅ Dark theme by default
- ✅ Vitest testing setup
- ✅ Type-safe API with TypeScript

🚧 **Coming Next** (Phase 8.2-8.5):
- Dashboard UI components
- Real-time WebSocket integration
- Data visualization (ECharts + Chart.js)
- Terminal emulation (xterm.js)
- Complete CRUD operations
- E2E testing with Playwright

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/          # Layout components (Sidebar, Header)
│   │   ├── dashboard/       # Dashboard widgets (coming Phase 8.2)
│   │   ├── common/          # Shared components
│   │   ├── charts/          # Data visualization
│   │   └── terminal/        # Terminal emulator
│   ├── pages/
│   │   ├── Dashboard/       # Dashboard page
│   │   ├── Scans/           # Scans page
│   │   ├── Attacks/         # Attacks page
│   │   ├── Reports/         # Reports page
│   │   └── Settings/        # Settings page
│   ├── stores/              # Zustand state stores
│   │   ├── authStore.ts     # Authentication state
│   │   ├── dashboardStore.ts # Dashboard state
│   │   └── themeStore.ts    # Theme state
│   ├── hooks/               # Custom React hooks
│   ├── utils/               # Utility functions
│   ├── types/               # TypeScript type definitions
│   ├── services/            # API services
│   ├── lib/                 # Third-party library configs
│   └── test/                # Test setup
├── public/                  # Static assets
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # TailwindCSS configuration
├── tsconfig.json            # TypeScript configuration
└── package.json             # Dependencies
```

---

## 🛠️ Development

### Prerequisites

- Node.js 18+ (recommended: 20+)
- npm 9+

### Install Dependencies

```bash
npm install
```

### Development Server

```bash
npm run dev
```

Server starts at: `http://localhost:5173`

### Build for Production

```bash
npm run build
```

Output: `dist/` directory

### Preview Production Build

```bash
npm run preview
```

### Run Tests

```bash
# Run tests in watch mode
npm test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

---

## 🎨 Design System

### Color Palette

```typescript
// Severity Levels
critical: '#DC2626'  // Red - Critical vulnerabilities
high:     '#EA580C'  // Orange - High severity
medium:   '#CA8A04'  // Yellow - Medium severity
low:      '#2563EB'  // Blue - Low severity
info:     '#16A34A'  // Green - Informational

// Dark Theme (Default)
dark-900: '#0f172a'  // Background
dark-800: '#1e293b'  // Cards
dark-700: '#334155'  // Borders
dark-600: '#475569'  // Hover
dark-500: '#64748b'  // Disabled
dark-400: '#94a3b8'  // Muted text
dark-300: '#cbd5e1'  // Secondary text
dark-100: '#f1f5f9'  // Primary text
```

### Typography

- **Font Family**: JetBrains Mono (monospace)
- **Headings**: Bold, 2xl-3xl
- **Body**: Regular, sm-base
- **Code**: Monospace, sm

---

## 🔌 API Integration

### Backend URL

Development: `http://localhost:8000`  
Production: Configure in `.env`

### WebSocket

Development: `ws://localhost:8000/ws`  
Production: Configure in `.env`

### Proxy Configuration

Vite is configured to proxy API requests:

```typescript
'/api'  → 'http://localhost:8000'
'/ws'   → 'ws://localhost:8000'
```

---

## 🧪 Testing

### Testing Stack

- **Vitest**: Fast unit test runner (Vite-native)
- **React Testing Library**: Component testing
- **@testing-library/jest-dom**: DOM matchers

### Example Test

```typescript
import { describe, it, expect } from 'vitest'
import { useDashboardStore } from '@stores/dashboardStore'

describe('DashboardStore', () => {
  it('should add a scan', () => {
    const store = useDashboardStore.getState()
    // ... test logic
  })
})
```

---

## 📝 Path Aliases

TypeScript and Vite are configured with path aliases:

```typescript
import Component from '@components/...'
import { useSomething } from '@hooks/...'
import type { User } from '@types'
import api from '@services/api'
```

Available aliases:
- `@/*` → `./src/*`
- `@components/*` → `./src/components/*`
- `@pages/*` → `./src/pages/*`
- `@stores/*` → `./src/stores/*`
- `@hooks/*` → `./src/hooks/*`
- `@utils/*` → `./src/utils/*`
- `@types/*` → `./src/types/*`
- `@services/*` → `./src/services/*`
- `@lib/*` → `./src/lib/*`

---

## 🌐 Environment Variables

Create `.env` file:

```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

Access in code:

```typescript
const apiUrl = import.meta.env.VITE_API_URL
```

---

## 🚢 Deployment

### Build

```bash
npm run build
```

### Deploy to Cloudflare Pages

```bash
# Install Wrangler
npm install -g wrangler

# Deploy
wrangler pages deploy dist
```

---

## 📚 Documentation

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [TailwindCSS Docs](https://tailwindcss.com/docs)
- [Zustand Documentation](https://zustand-demo.pmnd.rs)
- [React Router](https://reactrouter.com)
- [Vitest](https://vitest.dev)

---

## 🎯 Next Steps

**Phase 8.2** - Dashboard UI Implementation (Next)
**Phase 8.3** - Real-time WebSocket Integration  
**Phase 8.4** - Interactive Components & Visualization  
**Phase 8.5** - Testing & Documentation

---

## 📄 License

© 2026 SecureRedLab - All Rights Reserved

---

## 👥 Team

SecureRedLab Development Team

---

**Status**: ✅ Phase 8.1 COMPLETE  
**Version**: 1.0.0-alpha  
**Last Updated**: 2026-01-07
