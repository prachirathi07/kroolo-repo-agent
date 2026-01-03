import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Types
export interface RepositoryCreate {
    url: string;
    auth_token?: string;
    branch?: string;
    monitoring_enabled?: boolean;
}

export interface Repository {
    id: string;
    url: string;
    name: string | null;
    description: string | null;
    status: 'pending' | 'cloning' | 'analyzing' | 'generating_docs' | 'completed' | 'failed';
    last_commit_hash: string | null;
    branch: string;
    monitoring_enabled: boolean;
    error_message: string | null;
    last_analyzed_at: string | null;
    created_at: string;
    updated_at: string | null;
}

export interface Documentation {
    id: string;
    repo_id: string;
    version: number;
    commit_hash: string;
    content: {
        executive_summary: string;
        product_overview: string;
        key_features: string[];
        tech_stack: {
            languages: string[];
            frameworks: string[];
            databases: string[];
        };
        architecture: string;
        use_cases: string[];
        integrations: string[];
        marketing_points: string[];
    };
    file_count: number;
    lines_of_code: number;
    created_at: string;
}

export interface AnalysisResult {
    success: boolean;
    repo_id: string;
    documentation_id: string | null;
    error: string | null;
    duration_seconds: number;
}

// API Functions

export const analyzeRepository = async (data: RepositoryCreate): Promise<AnalysisResult> => {
    const response = await api.post<AnalysisResult>('/api/repos/analyze', data);
    return response.data;
};

export const getRepositories = async (): Promise<{ repositories: Repository[]; total: number }> => {
    const response = await api.get('/api/repos');
    return response.data;
};

export const getRepository = async (repoId: string): Promise<Repository> => {
    const response = await api.get(`/api/repos/${repoId}`);
    return response.data;
};

export const deleteRepository = async (repoId: string): Promise<void> => {
    await api.delete(`/api/repos/${repoId}`);
};

export const getDocumentation = async (repoId: string): Promise<Documentation> => {
    const response = await api.get(`/api/docs/${repoId}`);
    return response.data;
};

export const getDocumentationVersions = async (repoId: string): Promise<{ versions: Documentation[]; total: number }> => {
    const response = await api.get(`/api/docs/${repoId}/versions`);
    return response.data;
};

export const exportMarkdown = async (repoId: string): Promise<Blob> => {
    const response = await api.get(`/api/docs/${repoId}/export/markdown`, {
        responseType: 'blob',
    });
    return response.data;
};

export const exportJSON = async (repoId: string): Promise<any> => {
    const response = await api.get(`/api/docs/${repoId}/export/json`);
    return response.data;
};

export const getMonitoringJobs = async (): Promise<any> => {
    const response = await api.get('/api/monitoring/jobs');
    return response.data;
};

export default api;
