// background.ts

// Add your background script logic here
// This script runs in the background and handles events and communication between the extension and the browser

// Example code:
chrome.runtime.onInstalled.addListener(() => {
  console.log('Video clickbait extension installed');
});

// chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
//   console.log('Message received:', message);
//   // Handle the message and send a response if needed
// });

// You can also import and use other modules or files as needed
// For example:
// import { someFunction } from './utils/api';

// someFunction();
