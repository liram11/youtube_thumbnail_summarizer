import pluginQuery from '@tanstack/eslint-plugin-query'

module.exports = {
  "parser": "@typescript-eslint/parser",
  "extends": [
    ...pluginQuery.configs['flat/recommended'],
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:@typescript-eslint/recommended",
  ],
  "parserOptions": {
    "ecmaVersion": 2020,
    "sourceType": "module",
    "ecmaFeatures": {
      "jsx": true
    }
  },
  "rules": {
    "react/react-in-jsx-scope": "off"
  },
  "settings": {
    "react": {
      "version": "detect"
    }
  }
}
