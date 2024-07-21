# YouTube Summary Extension

This is a Chrome extension that generates summaries of YouTube videos and displays a tooltip with the summary near every video preview.

## Project Structure

```
youtube-summary-extension
├── public
│   ├── manifest.json
│   ├── background.js
│   └── popup.html
├── src
│   ├── components
│   │   ├── App.tsx
│   │   └── Tooltip.tsx
│   ├── contentScripts
│   │   └── contentScript.ts
│   ├── utils
│   │   └── api.ts
│   ├── styles
│   │   └── tooltip.css
│   ├── background.ts
│   ├── popup.tsx
│   └── types
│       └── index.ts
├── package.json
├── tsconfig.json
├── webpack.config.js
└── README.md
```

## Files

- `public/manifest.json`: The manifest file for the Chrome extension.
- `public/background.js`: The background script for the Chrome extension.
- `public/popup.html`: The HTML file for the extension's popup.
- `src/components/App.tsx`: The main component of the extension.
- `src/components/Tooltip.tsx`: The tooltip component.
- `src/contentScripts/contentScript.ts`: The content script for the extension.
- `src/utils/api.ts`: Utility functions for making API requests.
- `src/styles/tooltip.css`: CSS styles for the tooltip component.
- `src/background.ts`: TypeScript file for the background script.
- `src/popup.tsx`: TypeScript file for the popup component.
- `src/types/index.ts`: TypeScript type definitions.
- `tsconfig.json`: TypeScript configuration file.
- `webpack.config.js`: Webpack configuration file.
- `package.json`: npm configuration file.

## Usage

1. Install the extension in Chrome.
2. Click on the extension icon to open the popup.
3. Hover over a video preview to see the summary tooltip.

## Development

1. Clone the repository.
2. Install dependencies with `npm install`.
3. Build the project with `npm run build`.
4. Load the extension in Chrome using the `public` folder.
5. Make changes to the code and rebuild as needed.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```

Please note that this is a basic README file and you may need to update it with more specific information about your project.