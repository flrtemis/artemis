import {defineConfig} from 'vite';
export default defineConfig({build:{outDir:'../web',emptyOutDir:false,target:'es2020',rollupOptions:{output:{manualChunks:{react:['react','react-dom'],presence:['@met4citizen/talkinghead','three']}}}},server:{host:'0.0.0.0',allowedHosts:true}});
