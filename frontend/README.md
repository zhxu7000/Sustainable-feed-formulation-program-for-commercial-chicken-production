
📚 Install README for React Services


📚 Install README for React Services
🎯 1. Introduction:
This document provides a step-by-step guide on setting up the necessary React services and launching them.

📋 2. Pre-requisites:
Ensure you have Node.js, NPM, and NVM installed on your machine. If not, you can download and install them from their official websites.

🛠️ 3. Installing the Necessary React Services:
To set up your React application, the following packages are essential:

3.1 Install react-scripts package:
`npm install react-scripts --save`

3.2 Install ESLint plugin for React:
Helpful for linting your React code for potential issues.
`npm install eslint-plugin-react@latest --save-dev`

3.3 Install react-highlight-words:
For highlighting functionalities within your React app.
`npm install react-highlight-words --save`

⚙️ 4. Setting Up the 'Serve' Package:
Serve is a simple static server with pushstate.

4.1 Installing Serve Globally:
If there's an existing global installation of serve, remove it first:
`npm uninstall -g serve`
Then, reinstall:
`npm install -g serve`

🔀 5. Switching Node.js Version:
For compatibility, use Node.js version 14:
`nvm install 14.21.3`
`nvm use 14`

🧹 6. Cleaning Up:
Clean any residual files or directories to prevent conflicts:
`rm -rf node_modules package-lock.json`

🔧 7. Installation & Updates:
7.1 Update outdated packages:
`npm update`
7.2 Install project dependencies:
`npm install`
7.3 Fix potential vulnerabilities:
`npm audit fix`

🚀 8. Building and Running the React App:
8.1 Build the application:
This step creates a build directory with production-ready files.
`npm run build`

8.2 Start the React application:
`npm start`

8.3 Serve the built files on port 3000:
`serve -s build -l 3000`
For background running:
`setsid serve -s build -l 3000 > output.log 2>&1`

✅ 9. Testing:
Run the associated tests for your React project:
`npm test`

Feel free to reach out with any questions or if further assistance is required! Happy coding! 🌟
