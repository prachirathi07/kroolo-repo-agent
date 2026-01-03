import { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertCircle } from 'lucide-react';

interface Props {
    children: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null,
        };
    }

    static getDerivedStateFromError(error: Error): State {
        return {
            hasError: true,
            error,
            errorInfo: null,
        };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('ErrorBoundary caught an error:', error, errorInfo);
        this.setState({
            error,
            errorInfo,
        });
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
                    <div className="max-w-2xl w-full bg-white rounded-xl shadow-lg p-8">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="p-3 bg-red-100 rounded-lg">
                                <AlertCircle className="w-8 h-8 text-red-600" />
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">
                                    Something went wrong
                                </h1>
                                <p className="text-gray-600">
                                    The application encountered an error
                                </p>
                            </div>
                        </div>

                        {this.state.error && (
                            <div className="mb-6">
                                <h2 className="text-lg font-semibold text-gray-900 mb-2">
                                    Error Details:
                                </h2>
                                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                                    <p className="text-red-800 font-mono text-sm">
                                        {this.state.error.toString()}
                                    </p>
                                </div>
                            </div>
                        )}

                        {this.state.errorInfo && (
                            <div className="mb-6">
                                <h2 className="text-lg font-semibold text-gray-900 mb-2">
                                    Component Stack:
                                </h2>
                                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 max-h-64 overflow-auto">
                                    <pre className="text-xs text-gray-700 font-mono whitespace-pre-wrap">
                                        {this.state.errorInfo.componentStack}
                                    </pre>
                                </div>
                            </div>
                        )}

                        <div className="flex gap-4">
                            <button
                                onClick={() => window.location.reload()}
                                className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                            >
                                Reload Page
                            </button>
                            <button
                                onClick={() => window.location.href = '/'}
                                className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
                            >
                                Go to Home
                            </button>
                        </div>

                        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                            <h3 className="font-semibold text-blue-900 mb-2">
                                Troubleshooting Tips:
                            </h3>
                            <ul className="text-sm text-blue-800 space-y-1">
                                <li>• Check the browser console for more details (F12)</li>
                                <li>• Ensure the backend server is running on http://localhost:8000</li>
                                <li>• Verify your database connection is working</li>
                                <li>• Try clearing your browser cache and reloading</li>
                            </ul>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
