import { create } from 'zustand';
import type { Repository, Documentation } from '../services/api';

interface AppState {
    repositories: Repository[];
    currentRepo: Repository | null;
    currentDoc: Documentation | null;
    isLoading: boolean;
    error: string | null;

    setRepositories: (repos: Repository[]) => void;
    setCurrentRepo: (repo: Repository | null) => void;
    setCurrentDoc: (doc: Documentation | null) => void;
    setLoading: (loading: boolean) => void;
    setError: (error: string | null) => void;
    clearError: () => void;
}

export const useAppStore = create<AppState>((set) => ({
    repositories: [],
    currentRepo: null,
    currentDoc: null,
    isLoading: false,
    error: null,

    setRepositories: (repos) => set({ repositories: repos }),
    setCurrentRepo: (repo) => set({ currentRepo: repo }),
    setCurrentDoc: (doc) => set({ currentDoc: doc }),
    setLoading: (loading) => set({ isLoading: loading }),
    setError: (error) => set({ error }),
    clearError: () => set({ error: null }),
}));
