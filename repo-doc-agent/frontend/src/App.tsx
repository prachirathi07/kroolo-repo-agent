import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { FileCode, Github } from 'lucide-react';
import RepoList from './components/RepoList';
import RepoUpload from './components/RepoUpload';
import DocumentationViewer from './components/DocumentationViewer';
import ErrorBoundary from './components/ErrorBoundary';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <a href="/" className="flex items-center gap-3 group">
              <div className="p-2 bg-gray-900 rounded-lg group-hover:bg-gray-800 transition-colors">
                <FileCode className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">RepoDocAgent</h1>
                <p className="text-xs text-gray-500">AI Documentation</p>
              </div>
            </a>

            <nav className="flex items-center gap-3">
              <a
                href="/"
                className="text-gray-600 hover:text-gray-900 font-medium text-sm transition-colors px-3 py-2"
              >
                Dashboard
              </a>
              <a
                href="/upload"
                className="btn-primary text-sm"
              >
                New Analysis
              </a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <p>© 2025 RepoDocAgent</p>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 hover:text-gray-900 transition-colors"
            >
              <Github className="w-4 h-4" />
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<RepoList />} />
              <Route path="/upload" element={<RepoUpload />} />
              <Route path="/docs/:repoId" element={<DocumentationViewer />} />
            </Routes>
          </Layout>
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
