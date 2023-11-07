const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true
})

const path = require('path')
const basePath = '/chat-pdf'

module.exports = {
  devServer: {
    port: 3051,
    allowedHosts: "all",
  },
  publicPath: process.env.NODE_ENV !== 'development' ? basePath : '/',
  configureWebpack: {
    resolve: {
      symlinks: false,
      alias: {
        vue: path.resolve(`./node_modules/vue`)
      }
    }
  }
}