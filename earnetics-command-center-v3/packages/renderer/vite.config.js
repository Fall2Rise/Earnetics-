import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    base: './',
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
            '@earnetics/core': path.resolve(__dirname, '../core/src'),
            '@earnetics/ui': path.resolve(__dirname, '../ui/src'),
            '@earnetics/scene': path.resolve(__dirname, '../scene/src'),
        },
    },
    server: {
        port: 5173,
    }
});
