# AWS Language Chat Buddy - Vite React Frontend

A modern React application built with Vite for interacting with the AWS Language Chat Buddy Flask backend.

## ✨ Features

- 🗣️ **Interactive Chat Interface** - Real-time conversation with AI teacher
- 📚 **Scenario Management** - Load different conversation scenarios
- 🔄 **Session Management** - Persistent conversation state
- 🎯 **Grammar Correction** - Real-time feedback on language usage
- 📊 **Progress Tracking** - Monitor conversation progress
- 🎨 **Modern UI** - Clean, responsive design with gradients and animations
- ⚡ **Fast Development** - Powered by Vite for lightning-fast development

## 🚀 Why Vite?

- **⚡ Lightning Fast** - Instant server start and HMR
- **📦 Optimized Build** - Rollup-based production builds
- **🔧 Modern Tooling** - Native ES modules, TypeScript support
- **🎯 Better DX** - Superior developer experience over Create React App

## 📋 Prerequisites

- Node.js 16+ and npm/yarn
- Running Flask backend (see ../zappa_backend)

## 🛠️ Installation

1. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

2. **Set up environment variables (optional):**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set your API URL:
   ```
   VITE_API_URL=http://localhost:5000
   ```

## 🔧 Development

1. **Start the development server:**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

2. **The app will open at:** `http://localhost:3000`

3. **Hot Module Replacement (HMR)** - Changes appear instantly!

## 🏗️ Building for Production

1. **Create production build:**
   ```bash
   npm run build
   # or
   yarn build
   ```

2. **Preview production build:**
   ```bash
   npm run preview
   # or
   yarn preview
   ```

3. **Build files will be in:** `dist/` directory

## 🎮 Usage

### Starting a Conversation

1. **Check Backend Status** - Green indicator shows connection status
2. **Load a Scenario** - Click on emoji buttons to load scenarios
3. **Start Chatting** - Type responses and get AI feedback
4. **Track Progress** - Monitor conversation state and attempts

### Features Overview

#### 🤖 Chat Interface
- **Real-time messaging** with animated message bubbles
- **Grammar correction** with highlighted suggestions
- **Auto-scroll** to latest messages
- **Loading indicators** for better UX
- **Emoji indicators** for message types

#### 🎯 Scenario Manager
- **Visual scenario cards** with emojis and descriptions
- **Health monitoring** with status indicators
- **Session management** with clear feedback
- **Error handling** with user-friendly messages

## 🔌 API Integration

The frontend communicates with the Flask backend using:
- **Axios** with interceptors for debugging
- **Session cookies** for state persistence
- **CORS** enabled for cross-origin requests
- **Error handling** with user feedback

### API Endpoints

- `GET /health` - Backend health check
- `POST /load_scenario` - Load conversation scenario
- `GET /current_prompt` - Get current conversation prompt
- `POST /student_response` - Submit student response
- `POST /reset` - Reset conversation
- `GET /state` - Get conversation state
- `POST /session/clear` - Clear session
- `GET /session/info` - Get session information

## 🌍 Environment Variables

- `VITE_API_URL` - Backend API URL (default: http://localhost:5000)

## 📁 Project Structure

```
vite_react_frontend/
├── public/
│   └── vite.svg
├── src/
│   ├── components/
│   │   ├── ChatInterface.jsx
│   │   └── ScenarioManager.jsx
│   ├── services/
│   │   └── apiService.js
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── .env.example
├── .gitignore
├── .editorconfig
├── package.json
├── vite.config.js
└── README.md
```

## 🎨 Styling Features

- **Modern CSS** with custom properties
- **Gradient backgrounds** and animations
- **Responsive design** for all devices
- **Smooth transitions** and hover effects
- **Custom scrollbars** for better UX
- **Loading animations** and micro-interactions

## 🚀 Deployment

### Static Hosting

1. **Build the app:**
   ```bash
   npm run build
   ```

2. **Deploy to static hosting:**
   - **Vercel:** `vercel deploy`
   - **Netlify:** Drag & drop `dist/` folder
   - **AWS S3 + CloudFront**
   - **GitHub Pages**

3. **Update API URL:**
   Set `VITE_API_URL` to your production backend URL

### Docker Deployment

```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🔧 Development Tools

- **ESLint** - Code linting
- **Prettier** - Code formatting
- **EditorConfig** - Consistent editor settings
- **Vite DevTools** - Development debugging

## 🐛 Troubleshooting

### Common Issues

1. **Backend Connection Failed:**
   - Check if Flask backend is running on port 5000
   - Verify `VITE_API_URL` in `.env` file
   - Check browser console for CORS errors

2. **Hot Reload Not Working:**
   - Restart Vite dev server
   - Clear browser cache
   - Check file permissions

3. **Build Errors:**
   - Run `npm run lint` to check for errors
   - Clear `node_modules` and reinstall
   - Check Node.js version compatibility

### Performance Tips

- Use React DevTools for component debugging
- Enable Vite's built-in bundle analyzer
- Monitor network requests in browser DevTools
- Use React.memo() for expensive components

## 🆚 Vite vs Create React App

| Feature | Vite | Create React App |
|---------|------|------------------|
| **Start Time** | ~300ms | ~3-5s |
| **HMR Speed** | Instant | 1-3s |
| **Build Tool** | Rollup | Webpack |
| **Bundle Size** | Smaller | Larger |
| **TypeScript** | Native | Requires setup |
| **Modern Features** | Latest | Stable |

## 🤝 Contributing

1. Follow React hooks patterns
2. Use functional components
3. Implement proper error boundaries
4. Add TypeScript types for better DX
5. Write descriptive commit messages
6. Test across different browsers

## 📈 Performance Features

- **Code splitting** with dynamic imports
- **Tree shaking** for optimal bundle size
- **Pre-compression** for faster loading
- **Service worker** support for offline functionality
- **Lazy loading** for images and components

## 🎯 Future Enhancements

- [ ] TypeScript migration
- [ ] PWA support
- [ ] Voice input/output
- [ ] Multi-language support
- [ ] Dark/light theme toggle
- [ ] Advanced analytics
- [ ] Real-time collaboration

---

Built with ❤️ using Vite + React
