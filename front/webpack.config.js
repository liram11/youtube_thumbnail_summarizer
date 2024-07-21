const path = require('path');


module.exports = {
  entry: {
    // background: './public/background.js',
    main: './src/index.tsx',
    // contentScript: './src/contentScripts/contentScript.ts',
  },
  devServer: {
    watchFiles: ["src/**/*"],
    port: 3000,
    hot: true,
    compress: true,
    open: "/",
    static: path.join(__dirname, "./public"),
  },
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].js',
    publicPath: '',
  },
  resolve: {
    extensions: ['.ts', '.tsx', '.js'],
  },
  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        exclude: /node_modules/,
        use: 'ts-loader',
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
};
