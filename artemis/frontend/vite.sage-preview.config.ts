import {defineConfig} from 'vite';

// A labelled static interaction lab, reusing the real helper component.
// No runtime proxy, model, credentials, source inbox, or public-directory copy.
export default defineConfig({
  base: './',
  publicDir: false,
  build: {
    outDir: '../../docs', emptyOutDir: false, target: 'es2020',
    rollupOptions: {
      input: 'sage-preview.html',
      output: {
        entryFileNames: 'assets/sage-preview-[hash].js',
        chunkFileNames: 'assets/sage-preview-chunk-[hash].js',
        assetFileNames: 'assets/sage-preview-[hash][extname]',
      },
    },
  },
});
