import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import {
    FileText,
    Download,
    Loader2,
    ArrowLeft,
    Sparkles,
    Code,
    Target,
    Plug,
    MessageSquare,
} from 'lucide-react';
import { getDocumentation, getRepository, exportMarkdown, exportJSON, exportDOCX } from '../services/api';
import mermaid from 'mermaid';

// Initialize Mermaid
mermaid.initialize({ startOnLoad: true, theme: 'default' });

export default function DocumentationViewer() {
    const { repoId } = useParams<{ repoId: string }>();
    const [activeTab, setActiveTab] = useState<'overview' | 'features' | 'tech' | 'architecture'>('overview');

    const { data: repo, isLoading: repoLoading } = useQuery({
        queryKey: ['repository', repoId],
        queryFn: () => getRepository(repoId!),
        enabled: !!repoId,
    });

    const { data: doc, isLoading: docLoading, error } = useQuery({
        queryKey: ['documentation', repoId],
        queryFn: () => getDocumentation(repoId!),
        enabled: !!repoId,
    });

    // Render Mermaid diagram
    useEffect(() => {
        if (doc?.content.architecture && activeTab === 'architecture') {
            mermaid.contentLoaded();
        }
    }, [doc, activeTab]);

    const handleExportMarkdown = async () => {
        try {
            const blob = await exportMarkdown(repoId!);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${repo?.name || 'documentation'}.md`;
            a.click();
        } catch (error) {
            alert('Failed to export Markdown');
        }
    };

    const handleExportJSON = async () => {
        try {
            const data = await exportJSON(repoId!);
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${repo?.name || 'documentation'}.json`;
            a.click();
        } catch (error) {
            alert('Failed to export JSON');
        }
    };

    const handleExportDOCX = async () => {
        try {
            const blob = await exportDOCX(repoId!);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${repo?.name || 'documentation'}.docx`;
            a.click();
        } catch (error) {
            alert('Failed to export DOCX');
        }
    };

    if (repoLoading || docLoading) {
        return (
            <div className="flex items-center justify-center py-20">
                <Loader2 className="w-12 h-12 animate-spin text-blue-600" />
            </div>
        );
    }

    if (error || !doc) {
        return (
            <div className="card bg-red-50 border border-red-200">
                <p className="text-red-800">Documentation not found or still being generated</p>
                <a href="/" className="text-blue-600 hover:underline mt-2 inline-block">
                    ← Back to Dashboard
                </a>
            </div>
        );
    }

    const tabs = [
        { id: 'overview', label: 'Overview', icon: FileText },
        { id: 'features', label: 'Features', icon: Sparkles },
        { id: 'tech', label: 'Tech Stack', icon: Code },
        { id: 'architecture', label: 'Architecture', icon: Target },
    ];

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="card">
                <div className="flex items-start justify-between">
                    <div className="flex-1">
                        <a
                            href="/"
                            className="text-blue-600 hover:text-blue-700 font-medium mb-3 inline-flex items-center gap-2"
                        >
                            <ArrowLeft className="w-4 h-4" />
                            Back to Dashboard
                        </a>
                        <h1 className="text-3xl font-bold text-gray-900 mb-2">{repo?.name}</h1>
                        <p className="text-gray-600 mb-4">{repo?.description}</p>
                        <div className="flex flex-wrap gap-3 text-sm text-gray-500">
                            <span>📁 {doc.file_count} files</span>
                            <span>📝 {doc.lines_of_code.toLocaleString()} lines of code</span>
                            <span>🔖 Version {doc.version}</span>
                            <span>📅 {new Date(doc.created_at).toLocaleDateString()}</span>
                        </div>
                    </div>

                    <div className="flex gap-2">
                        <button
                            onClick={handleExportMarkdown}
                            className="btn-secondary flex items-center gap-2"
                        >
                            <Download className="w-4 h-4" />
                            Markdown
                        </button>
                        <button
                            onClick={handleExportJSON}
                            className="btn-secondary flex items-center gap-2"
                        >
                            <Download className="w-4 h-4" />
                            JSON
                        </button>
                        <button
                            onClick={handleExportDOCX}
                            className="btn-secondary flex items-center gap-2 bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100"
                        >
                            <FileText className="w-4 h-4" />
                            Word
                        </button>
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="card">
                <div className="flex gap-2 border-b border-gray-200 pb-4 mb-6">
                    {tabs.map((tab) => {
                        const Icon = tab.icon;
                        return (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id as any)}
                                className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${activeTab === tab.id
                                    ? 'bg-blue-600 text-white shadow-md'
                                    : 'text-gray-600 hover:bg-gray-100'
                                    }`}
                            >
                                <Icon className="w-4 h-4" />
                                {tab.label}
                            </button>
                        );
                    })}
                </div>

                {/* Tab Content */}
                <div className="prose max-w-none">
                    {activeTab === 'overview' && (
                        <div className="space-y-6">
                            <div>
                                <h2 className="text-2xl font-bold text-gray-900 mb-4">Executive Summary</h2>
                                <p className="text-gray-700 leading-relaxed">
                                    {doc.content.executive_summary}
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-bold text-gray-900 mb-4">Product Overview</h2>
                                <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                                    {doc.content.product_overview}
                                </p>
                            </div>

                            {doc.content.use_cases.length > 0 && (
                                <div>
                                    <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                                        <Target className="w-6 h-6 text-blue-600" />
                                        Use Cases
                                    </h2>
                                    <ul className="space-y-3">
                                        {doc.content.use_cases.map((useCase, index) => (
                                            <li key={index} className="flex gap-3">
                                                <span className="text-blue-600 font-semibold">{index + 1}.</span>
                                                <span className="text-gray-700">{useCase}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {doc.content.marketing_points.length > 0 && (
                                <div>
                                    <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                                        <MessageSquare className="w-6 h-6 text-blue-600" />
                                        Marketing Talking Points
                                    </h2>
                                    <div className="grid gap-3">
                                        {doc.content.marketing_points.map((point, index) => (
                                            <div
                                                key={index}
                                                className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg"
                                            >
                                                <p className="text-gray-800 font-medium">{point}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'features' && (
                        <div>
                            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                                <Sparkles className="w-6 h-6 text-blue-600" />
                                Key Features
                            </h2>
                            <div className="grid gap-4">
                                {doc.content.key_features.map((feature, index) => (
                                    <div
                                        key={index}
                                        className="p-5 bg-white border-2 border-blue-100 rounded-xl hover:border-blue-300 hover:shadow-md transition-all"
                                    >
                                        <div className="flex gap-4">
                                            <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center text-white font-bold">
                                                {index + 1}
                                            </div>
                                            <p className="text-gray-800 leading-relaxed flex-1">{feature}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {activeTab === 'tech' && (
                        <div className="space-y-8">
                            <div>
                                <h3 className="text-xl font-bold text-gray-900 mb-4">Languages</h3>
                                <div className="flex flex-wrap gap-2">
                                    {doc.content.tech_stack.languages.map((lang) => (
                                        <span
                                            key={lang}
                                            className="px-4 py-2 bg-gradient-to-r from-green-100 to-green-200 text-green-800 rounded-full font-medium"
                                        >
                                            {lang}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            {doc.content.tech_stack.frameworks.length > 0 && (
                                <div>
                                    <h3 className="text-xl font-bold text-gray-900 mb-4">Frameworks & Libraries</h3>
                                    <div className="flex flex-wrap gap-2">
                                        {doc.content.tech_stack.frameworks.map((fw) => (
                                            <span
                                                key={fw}
                                                className="px-4 py-2 bg-gradient-to-r from-blue-100 to-blue-200 text-blue-800 rounded-full font-medium"
                                            >
                                                {fw}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {doc.content.tech_stack.databases.length > 0 && (
                                <div>
                                    <h3 className="text-xl font-bold text-gray-900 mb-4">Databases</h3>
                                    <div className="flex flex-wrap gap-2">
                                        {doc.content.tech_stack.databases.map((db) => (
                                            <span
                                                key={db}
                                                className="px-4 py-2 bg-gradient-to-r from-orange-100 to-orange-200 text-orange-800 rounded-full font-medium"
                                            >
                                                {db}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {doc.content.integrations.length > 0 && (
                                <div>
                                    <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                                        <Plug className="w-5 h-5" />
                                        Integrations
                                    </h3>
                                    <div className="grid grid-cols-2 gap-3">
                                        {doc.content.integrations.map((integration) => (
                                            <div
                                                key={integration}
                                                className="p-3 bg-purple-50 border border-purple-200 rounded-lg text-purple-800 font-medium"
                                            >
                                                {integration}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'architecture' && (
                        <div>
                            <h2 className="text-2xl font-bold text-gray-900 mb-6">System Architecture</h2>
                            <div className="bg-white p-6 rounded-xl border-2 border-gray-200">
                                <div className="mermaid">{doc.content.architecture}</div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
