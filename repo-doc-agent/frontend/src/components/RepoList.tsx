import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Folder, Clock, CheckCircle, XCircle, Loader2, Eye, Trash2 } from 'lucide-react';
import { getRepositories, deleteRepository, type Repository } from '../services/api';

export default function RepoList() {
    const [deletingId, setDeletingId] = useState<string | null>(null);

    const { data, isLoading, error, refetch } = useQuery({
        queryKey: ['repositories'],
        queryFn: getRepositories,
        refetchInterval: 5000, // Refetch every 5 seconds to update status
    });

    const handleDelete = async (repoId: string) => {
        if (!confirm('Are you sure you want to delete this repository?')) {
            return;
        }

        setDeletingId(repoId);
        try {
            await deleteRepository(repoId);
            refetch();
        } catch (error) {
            console.error('Failed to delete repository:', error);
            alert('Failed to delete repository');
        } finally {
            setDeletingId(null);
        }
    };

    const getStatusBadge = (status: Repository['status']) => {
        const badges = {
            pending: { label: 'Pending', class: 'badge badge-info', icon: Clock },
            cloning: { label: 'Cloning', class: 'badge badge-info', icon: Loader2 },
            analyzing: { label: 'Analyzing', class: 'badge badge-warning', icon: Loader2 },
            generating_docs: { label: 'Generating Docs', class: 'badge badge-warning', icon: Loader2 },
            completed: { label: 'Completed', class: 'badge badge-success', icon: CheckCircle },
            failed: { label: 'Failed', class: 'badge badge-error', icon: XCircle },
        };

        const badge = badges[status] || badges.pending;
        const Icon = badge.icon;

        return (
            <span className={badge.class}>
                <Icon className={`w-3 h-3 inline mr-1 ${status.includes('ing') ? 'animate-spin' : ''}`} />
                {badge.label}
            </span>
        );
    };

    const formatDate = (dateString: string | null) => {
        if (!dateString) return 'Never';
        return new Date(dateString).toLocaleString();
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            </div>
        );
    }

    if (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        const isConnectionError = errorMessage.includes('503') || errorMessage.includes('Network Error') || errorMessage.includes('ECONNREFUSED');

        return (
            <div className="card bg-red-50 border-2 border-red-200">
                <div className="text-center py-8">
                    <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-red-800 mb-2">
                        {isConnectionError ? 'Backend Connection Error' : 'Failed to Load Repositories'}
                    </h3>
                    <p className="text-red-700 mb-4">{errorMessage}</p>

                    {isConnectionError && (
                        <div className="bg-white rounded-lg p-4 text-left max-w-2xl mx-auto">
                            <p className="font-semibold text-gray-900 mb-2">🔧 How to fix:</p>
                            <ol className="list-decimal list-inside space-y-1 text-sm text-gray-700">
                                <li>Check if the backend server is running on <code className="bg-gray-100 px-2 py-1 rounded">http://localhost:8000</code></li>
                                <li>Verify your database connection in <code className="bg-gray-100 px-2 py-1 rounded">backend/.env</code></li>
                                <li>Make sure your <code className="bg-gray-100 px-2 py-1 rounded">DATABASE_URL</code> has correct credentials</li>
                                <li>Check backend terminal for error messages</li>
                            </ol>
                        </div>
                    )}

                    <button
                        onClick={() => window.location.reload()}
                        className="btn-primary mt-6"
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    if (!data || data.repositories.length === 0) {
        return (
            <div className="card text-center py-12">
                <Folder className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-700 mb-2">No Repositories Yet</h3>
                <p className="text-gray-500 mb-6">Start by analyzing your first repository</p>
                <a href="/upload" className="btn-primary inline-block">
                    Analyze Repository
                </a>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                    Repositories ({data.total})
                </h2>
                <a href="/upload" className="btn-primary">
                    + New Analysis
                </a>
            </div>

            <div className="grid gap-4">
                {data.repositories.map((repo) => (
                    <div
                        key={repo.id}
                        className="card hover:scale-[1.01] transition-transform duration-200"
                    >
                        <div className="flex items-start justify-between">
                            <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                    <Folder className="w-5 h-5 text-blue-600" />
                                    <h3 className="text-lg font-semibold text-gray-900">
                                        {repo.name || 'Loading...'}
                                    </h3>
                                    {getStatusBadge(repo.status)}
                                </div>

                                <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                                    {repo.description || repo.url}
                                </p>

                                <div className="flex flex-wrap gap-4 text-xs text-gray-500">
                                    <span>Branch: {repo.branch}</span>
                                    <span>Last analyzed: {formatDate(repo.last_analyzed_at)}</span>
                                    {repo.last_commit_hash && (
                                        <span>Commit: {repo.last_commit_hash.substring(0, 7)}</span>
                                    )}
                                </div>

                                {repo.error_message && (
                                    <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-800">
                                        Error: {repo.error_message}
                                    </div>
                                )}
                            </div>

                            <div className="flex gap-2 ml-4">
                                {repo.status === 'completed' && (
                                    <a
                                        href={`/docs/${repo.id}`}
                                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                        title="View Documentation"
                                    >
                                        <Eye className="w-5 h-5" />
                                    </a>
                                )}
                                <button
                                    onClick={() => handleDelete(repo.id)}
                                    disabled={deletingId === repo.id}
                                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                                    title="Delete Repository"
                                >
                                    {deletingId === repo.id ? (
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                    ) : (
                                        <Trash2 className="w-5 h-5" />
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
