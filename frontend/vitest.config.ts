import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    include: ['src/**/*.functional.test.ts', 'src/**/*.functional.test.tsx'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json-summary', 'html'],
      reportsDirectory: './coverage/unit',
      exclude: [
        '.next/**',
        'tests/**',
        'src/**/__tests__/**',
        'src/coverage-tests/**',
        '**/*.spec.ts',
        '**/*.test.ts',
        '**/*.test.tsx',
        'next-env.d.ts',
        '**/*.config.*',
        'next.config.js',
        'src/lib/types.ts',
      ],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
