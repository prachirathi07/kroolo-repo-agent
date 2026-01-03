import { useState } from 'react';
import { Upload, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { analyzeRepository } from '../services/api';
import { useAppStore } from '../store/appStore';

export default function RepoUpload() {
    const [url, setUrl] = useState('');
    const [authToken, setAuthToken] = useState('');
    const [branch, setBranch] = useState('main');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

    const { setError } = useAppStore();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!url.trim()) {
            setError('Please enter a repository URL');
            return;
        }

        setIsSubmitting(true);
        setResult(null);
        setError(null);

        try {
            const response = await analyzeRepository({
                url: url.trim(),
                auth_token: authToken.trim() || undefined,
                branch: branch.trim() || 'main',
                monitoring_enabled: true,
            });

            if (response.success) {
                setResult({
                    success: true,
                    message: `Analysis started! Repository ID: ${response.repo_id}`,
                });

                // Clear form
                setUrl('');
                setAuthToken('');
                setBranch('main');

                // Redirect to dashboard after 2 seconds
                setTimeout(() => {
                    window.location.href = '/';
                }, 2000);
            } else {
                setResult({
                    success: false,
                    message: response.error || 'Analysis failed',
                });
            }
        } catch (error: any) {
            setResult({
                success: false,
                message: error.response?.data?.detail || error.message || 'Failed to start analysis',
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto animate-fade-in">
            <div className="card">
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg">
                        <Upload className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900">Analyze Repository</h2>
                        <p className="text-gray-600">Enter a GitHub or GitLab repository URL to get started</p>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                    {/* Repository URL */}
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                            Repository URL *
                        </label>
                        <input
                            type="url"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            placeholder="https://github.com/username/repository"
                            className="input-field"
                            required
                            disabled={isSubmitting}
                        />
                        <p className="text-xs text-gray-500 mt-1">
                            Supports both public and private repositories
                        </p>
                    </div>

                    {/* Branch */}
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                            Branch
                        </label>
                        <input
                            type="text"
                            value={branch}
                            onChange={(e) => setBranch(e.target.value)}
                            placeholder="main"
                            className="input-field"
                            disabled={isSubmitting}
                        />
                    </div>

                    {/* Auth Token (Optional) */}
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                            Personal Access Token (Optional)
                        </label>
                        <input
                            type="password"
                            value={authToken}
                            onChange={(e) => setAuthToken(e.target.value)}
                            placeholder="ghp_... or glpat_..."
                            className="input-field"
                            disabled={isSubmitting}
                        />
                        <p className="text-xs text-gray-500 mt-1">
                            Required only for private repositories
                        </p>
                    </div>

                    {/* Result Message */}
                    {result && (
                        <div
                            className={`p-4 rounded-lg flex items-start gap-3 ${result.success
                                    ? 'bg-green-50 border border-green-200'
                                    : 'bg-red-50 border border-red-200'
                                }`}
                        >
                            {result.success ? (
                                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                            ) : (
                                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                            )}
                            <p
                                className={`text-sm font-medium ${result.success ? 'text-green-800' : 'text-red-800'
                                    }`}
                            >
                                {result.message}
                            </p>
                        </div>
                    )}

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={isSubmitting}
                        className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isSubmitting ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                Starting Analysis...
                            </>
                        ) : (
                            <>
                                <Upload className="w-5 h-5" />
                                Analyze Repository
                            </>
                        )}
                    </button>
                </form>

                {/* Info Box */}
                <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h4 className="text-sm font-semibold text-blue-900 mb-2">What happens next?</h4>
                    <ul className="text-xs text-blue-800 space-y-1">
                        <li>• Repository will be cloned and analyzed</li>
                        <li>• AI will extract features and generate documentation</li>
                        <li>• Marketing-friendly content will be created</li>
                        <li>• You'll be redirected to view the results</li>
                    </ul>
                </div>
            </div>
        </div>
    );
}
