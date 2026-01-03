# 🎨 RepoDocAgent Frontend

Modern React dashboard for the RepoDocAgent - AI-powered repository documentation generator.

## ✨ Features

- 📊 **Repository Dashboard** - View all analyzed repositories with real-time status updates
- 📤 **Upload Interface** - Analyze new repositories with a beautiful form
- 📖 **Documentation Viewer** - Tabbed interface for viewing generated documentation
- 🎨 **Premium UI** - Gradient backgrounds, smooth animations, modern design
- 📥 **Export Functionality** - Download documentation as Markdown or JSON
- 🔄 **Real-time Updates** - Auto-refresh repository status every 5 seconds

## 🛠️ Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Query** - Data fetching & caching
- **Zustand** - State management
- **React Router** - Routing
- **Axios** - HTTP client
- **Mermaid** - Architecture diagrams
- **Lucide React** - Icons

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
VITE_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

Visit: http://localhost:5173

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── RepoList.tsx           # Repository dashboard
│   │   ├── RepoUpload.tsx         # Upload form
│   │   └── DocumentationViewer.tsx # Doc viewer
│   ├── services/
│   │   └── api.ts                 # API client
│   ├── store/
│   │   └── appStore.ts            # Zustand store
│   ├── App.tsx                    # Main app with routing
│   ├── main.tsx                   # Entry point
│   └── index.css                  # Tailwind styles
├── package.json
├── tailwind.config.js
├── vite.config.ts
└── .env.example
```

## 🎯 Pages

### 1. Dashboard (`/`)
- Lists all repositories
- Shows analysis status with badges
- Real-time status updates
- Delete repositories
- Navigate to documentation

### 2. Upload (`/upload`)
- Repository URL input
- Branch selection
- Optional auth token for private repos
- Form validation
- Success/error messages

### 3. Documentation Viewer (`/docs/:repoId`)
- **Overview Tab**: Executive summary, product overview, use cases, marketing points
- **Features Tab**: Key features with numbered cards
- **Tech Stack Tab**: Languages, frameworks, databases, integrations
- **Architecture Tab**: Mermaid diagram visualization
- Export buttons (Markdown, JSON)

## 🎨 Design System

### Colors
- **Primary**: Blue gradient (`from-blue-600 to-blue-700`)
- **Success**: Green (`bg-green-100 text-green-800`)
- **Warning**: Yellow (`bg-yellow-100 text-yellow-800`)
- **Error**: Red (`bg-red-100 text-red-800`)
- **Info**: Blue (`bg-blue-100 text-blue-800`)

### Components
- `.card` - White card with shadow
- `.btn-primary` - Blue gradient button
- `.btn-secondary` - White button with border
- `.input-field` - Styled input with focus states
- `.badge` - Status badges

### Animations
- `animate-fade-in` - Fade in on load
- `animate-slide-up` - Slide up on load
- `animate-spin` - Loading spinners

## 📦 Build for Production

```bash
npm run build
```

Output will be in `dist/` folder.

## 🚀 Deployment (Vercel)

### Option 1: Vercel CLI

```bash
npm install -g vercel
vercel
```

### Option 2: GitHub Integration

1. Push code to GitHub
2. Import project in Vercel
3. Set environment variable: `VITE_API_URL=https://your-backend-url.com`
4. Deploy

## 🔧 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |

## 📝 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## 🎓 Key Features Explained

### Real-time Status Updates
Uses React Query with `refetchInterval: 5000` to poll repository status every 5 seconds.

### Mermaid Diagram Rendering
Automatically renders architecture diagrams using the Mermaid library when viewing the Architecture tab.

### Export Functionality
Downloads documentation as Markdown or JSON files using Blob URLs.

### Responsive Design
Fully responsive with Tailwind CSS breakpoints for mobile, tablet, and desktop.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License

---

**Built with ❤️ using React, TypeScript, and Tailwind CSS**
