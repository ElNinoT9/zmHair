const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true
      }
    }
  },
  css: {
    loaderOptions: {
      sass: {
        additionalData: `@import "@/styles/variables.scss";`
      }
    }
  }
})
