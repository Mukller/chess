# Frontend Development Guide

Complete guide to setting up and developing the React frontend for the Telegram Chess Bot.

## Prerequisites

- Node.js 18+ (includes npm)
- Git
- Backend running (http://localhost:8000)
- Visual Studio Code (recommended)

## Quick Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Browser: http://localhost:5173
```

---

## Project Structure

```
frontend/
├── src/
│   ├── components/           # React components
│   │   ├── Board.tsx        # Chess board display
│   │   ├── GameSelector.tsx # Game mode selection
│   │   ├── Profile.tsx      # User profile & stats
│   │   └── ...
│   ├── pages/               # Page components
│   │   ├── App.tsx          # Main app wrapper
│   │   ├── GamePage.tsx     # In-game view
│   │   └── ...
│   ├── hooks/               # Custom React hooks
│   │   ├── useGame.ts       # Game state management
│   │   ├── useWebSocket.ts  # WebSocket connection
│   │   └── ...
│   ├── store/               # State management (Zustand)
│   │   ├── gameStore.ts     # Game state
│   │   ├── userStore.ts     # User state
│   │   └── ...
│   ├── api/                 # API client functions
│   │   ├── auth.ts          # Authentication
│   │   ├── game.ts          # Game endpoints
│   │   ├── user.ts          # User endpoints
│   │   └── ...
│   ├── types/               # TypeScript types
│   │   ├── game.ts          # Game types
│   │   ├── api.ts           # API response types
│   │   └── ...
│   ├── styles/              # Global styles
│   │   └── tailwind.css     # TailwindCSS imports
│   ├── utils/               # Utility functions
│   │   ├── chess.ts         # Chess logic helpers
│   │   ├── elo.ts           # ELO calculation
│   │   └── ...
│   ├── index.css            # Global styles
│   └── main.tsx             # Entry point
├── public/                  # Static assets
│   └── favicon.svg
├── index.html               # HTML template
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript config
├── tailwind.config.js       # TailwindCSS config
├── postcss.config.js        # PostCSS config
├── vite.config.ts           # Vite config
└── Dockerfile               # Docker build
```

---

## Development Workflow

### Start Dev Server

```bash
npm run dev
```

Vite watches for file changes and hot-reloads the browser.

### Build for Production

```bash
npm run build
```

Creates optimized build in `dist/` directory.

### Preview Build

```bash
npm run preview
```

Preview production build locally.

### Type Checking

```bash
# Check TypeScript
npm run check
```

### Linting

```bash
# Lint code
npm run lint

# Format code
npm run format
```

---

## Key Technologies

### React 18
- Component-based UI
- Hooks for state management
- Strict mode for development

### TypeScript 5
- Type safety for JavaScript
- Better IDE support
- Catch errors at compile time

### Vite 5
- Fast development server
- Instant HMR (hot module reload)
- Optimized production builds
- ES modules

### TailwindCSS
- Utility-first CSS framework
- Responsive design
- Custom theming
- Configuration in `tailwind.config.js`

### Zustand
- Lightweight state management
- No boilerplate
- Perfect for medium-sized apps
- Alternative to Redux/Context

### Telegram WebApp SDK
- Access Telegram user data
- Mini-app features
- Platform-specific APIs

---

## State Management (Zustand)

### Game Store

```typescript
// src/store/gameStore.ts
import { create } from 'zustand';

interface GameState {
  gameId: string | null;
  fen: string;
  moves: string[];
  status: 'active' | 'finished';
  
  startGame: (difficulty: string) => Promise<void>;
  makeMove: (move: string) => Promise<void>;
  setGameId: (id: string) => void;
}

export const useGameStore = create<GameState>((set) => ({
  gameId: null,
  fen: 'starting fen',
  moves: [],
  status: 'active',
  
  startGame: async (difficulty) => {
    // Call API
    // Update state
  },
  
  makeMove: async (move) => {
    // Call API
    // Update state
  },
  
  setGameId: (id) => set({ gameId: id }),
}));
```

### Usage in Components

```typescript
// src/components/Board.tsx
import { useGameStore } from '../store/gameStore';

export function Board() {
  const { fen, makeMove } = useGameStore();
  
  const handleMove = async (move: string) => {
    await makeMove(move);
  };
  
  return <div>{/* Render board with fen */}</div>;
}
```

---

## API Integration

### Client Functions

```typescript
// src/api/game.ts
import { apiClient } from './client';

export async function startGame(difficulty: string) {
  return apiClient.post('/api/game/start', {
    difficulty,
    color: 'white'
  });
}

export async function makeMove(gameId: string, move: string) {
  return apiClient.post(`/api/game/${gameId}/move`, {
    move
  });
}
```

### API Client

```typescript
// src/api/client.ts
import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api';

export const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auto-attach token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

---

## WebSocket Connection

### useWebSocket Hook

```typescript
// src/hooks/useWebSocket.ts
import { useEffect } from 'react';
import { useGameStore } from '../store/gameStore';

export function useWebSocket(gameId: string) {
  const { setGameState } = useGameStore();
  
  useEffect(() => {
    if (!gameId) return;
    
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const url = `${protocol}://${window.location.host}/ws/game/${gameId}`;
    
    const ws = new WebSocket(url);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setGameState(data);
    };
    
    return () => ws.close();
  }, [gameId, setGameState]);
}
```

### Usage

```typescript
// src/pages/GamePage.tsx
import { useWebSocket } from '../hooks/useWebSocket';

export function GamePage() {
  const { gameId } = useGameStore();
  
  useWebSocket(gameId!);
  
  return <Board />;
}
```

---

## Component Examples

### Simple Component

```typescript
// src/components/Button.tsx
interface ButtonProps {
  onClick: () => void;
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
}

export function Button({ onClick, children, variant = 'primary' }: ButtonProps) {
  const styles = {
    primary: 'bg-blue-500 hover:bg-blue-600',
    secondary: 'bg-gray-500 hover:bg-gray-600',
  };
  
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded text-white ${styles[variant]}`}
    >
      {children}
    </button>
  );
}
```

### Component with Hooks

```typescript
// src/components/Board.tsx
import { useState } from 'react';
import { useGameStore } from '../store/gameStore';
import { Square } from './Square';

export function Board() {
  const { fen, makeMove } = useGameStore();
  const [selectedSquare, setSelectedSquare] = useState<string | null>(null);
  
  const handleSquareClick = async (square: string) => {
    if (!selectedSquare) {
      setSelectedSquare(square);
    } else {
      const move = `${selectedSquare}${square}`;
      await makeMove(move);
      setSelectedSquare(null);
    }
  };
  
  return (
    <div className="grid grid-cols-8 gap-1">
      {Array.from({ length: 64 }).map((_, i) => (
        <Square
          key={i}
          square={indexToSquare(i)}
          onClick={() => handleSquareClick(indexToSquare(i))}
          selected={selectedSquare === indexToSquare(i)}
        />
      ))}
    </div>
  );
}
```

---

## Testing

### Unit Tests

```typescript
// src/utils/__tests__/elo.test.ts
import { calculateEloChange } from '../elo';

describe('ELO calculation', () => {
  it('should increase ELO on win', () => {
    const delta = calculateEloChange(1200, 1400, 1.0);
    expect(delta).toBeGreaterThan(0);
  });
  
  it('should decrease ELO on loss', () => {
    const delta = calculateEloChange(1200, 1400, 0.0);
    expect(delta).toBeLessThan(0);
  });
});
```

### Component Tests

```typescript
// src/components/__tests__/Button.test.tsx
import { render, screen } from '@testing-library/react';
import { Button } from '../Button';

describe('Button', () => {
  it('renders correctly', () => {
    render(<Button onClick={() => {}}>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
  
  it('calls onClick handler', () => {
    const onClick = jest.fn();
    render(<Button onClick={onClick}>Click</Button>);
    screen.getByText('Click').click();
    expect(onClick).toHaveBeenCalled();
  });
});
```

Run tests:
```bash
npm test
```

---

## Styling with TailwindCSS

### Utility Classes

```html
<!-- Container -->
<div class="w-full max-w-md mx-auto px-4">
  <!-- Grid -->
  <div class="grid grid-cols-8 gap-2">
    <!-- Item -->
    <div class="bg-blue-500 hover:bg-blue-600 rounded p-4 text-white">
      Square
    </div>
  </div>
</div>
```

### Custom Config

```javascript
// tailwind.config.js
export default {
  theme: {
    extend: {
      colors: {
        'chess-light': '#f0d9b5',
        'chess-dark': '#b58863',
      },
      spacing: {
        'board': 'clamp(200px, 50vw, 500px)',
      },
    },
  },
  plugins: [],
};
```

### CSS Directives

```css
/* src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn {
    @apply px-4 py-2 rounded font-semibold transition;
  }
  
  .btn-primary {
    @apply btn bg-blue-500 hover:bg-blue-600 text-white;
  }
}
```

---

## Environment Variables

Create `.env.local`:

```env
VITE_API_BASE_URL=/api
VITE_WS_BASE_URL=/ws
VITE_TELEGRAM_APP_ID=YOUR_APP_ID
```

Access in code:

```typescript
const apiUrl = import.meta.env.VITE_API_BASE_URL;
const telegramAppId = import.meta.env.VITE_TELEGRAM_APP_ID;
```

---

## Docker Build

```bash
# Build image
docker build -t chess-frontend:latest .

# Run container
docker run -p 3000:80 chess-frontend:latest
```

See [frontend/Dockerfile](frontend/Dockerfile) for details.

---

## Performance Optimization

### Code Splitting

```typescript
import { lazy, Suspense } from 'react';

const GamePage = lazy(() => import('./pages/GamePage'));
const HistoryPage = lazy(() => import('./pages/HistoryPage'));

export function App() {
  return (
    <Suspense fallback={<Loading />}>
      {/* Routes */}
    </Suspense>
  );
}
```

### Memoization

```typescript
import { memo } from 'react';

export const Square = memo(function Square({ piece, onClick }: Props) {
  return <div onClick={onClick}>{piece}</div>;
});
```

### Image Optimization

```typescript
// Use next-gen formats
<img src="piece.webp" fallback="piece.png" />
```

---

## Common Patterns

### Loading State

```typescript
export function GameLoader() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    async function load() {
      try {
        // Fetch data
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        setLoading(false);
      }
    }
    load();
  }, []);
  
  if (loading) return <Spinner />;
  if (error) return <Error message={error} />;
  return <Content />;
}
```

### Form Handling

```typescript
export function GameForm() {
  const [formData, setFormData] = useState({
    difficulty: 'medium',
    color: 'white',
  });
  
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle submission
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <select name="difficulty" value={formData.difficulty} onChange={handleChange}>
        <option value="beginner">Beginner</option>
        <option value="expert">Expert</option>
      </select>
      <button type="submit">Start Game</button>
    </form>
  );
}
```

---

## Troubleshooting

### "Cannot find module" errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules
npm install
```

### Port already in use
```bash
# Vite default: 5173
npm run dev -- --port 3000
```

### Vite not hot-reloading
- Check browser console for errors
- Restart dev server: `Ctrl+C` then `npm run dev`
- Clear browser cache

### TypeScript errors
```bash
# Check all files
npm run check

# Fix auto-fixable issues
npm run lint -- --fix
```

---

## IDE Setup

### VS Code Extensions
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- TypeScript Vue Plugin
- Prettier - Code formatter
- ESLint

### VS Code Settings
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

---

## Resources

- [React Docs](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [TailwindCSS Docs](https://tailwindcss.com/docs)
- [Zustand Docs](https://github.com/pmndrs/zustand)
- [Telegram WebApp SDK](https://core.telegram.org/bots/webapps)

---

## Next Steps

- Start dev server: `npm run dev`
- Open http://localhost:5173
- Make changes to see hot reload
- Check console for errors
- Review existing components in `src/components/`

Happy coding! 🚀
