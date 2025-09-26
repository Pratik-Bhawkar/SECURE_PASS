# Secure Pass Frontend

Modern React frontend for the Secure Pass license plate recognition system.

## Features

- React 19 with modern hooks and features
- Responsive design with Tailwind CSS
- Real-time dashboard updates
- Role-based UI components
- Mobile-friendly navigation
- Glass morphism design elements
- Animated components and transitions

## Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env file with your API URL
   ```

## Development

```bash
npm run dev
```

Visit http://localhost:5173

## Building

```bash
npm run build
```

## Project Structure

```
src/
├── assets/           # Static assets (images, icons)
├── components/       # Reusable React components
├── pages/           # Page components
└── styles/          # Global styles
```

## Technologies Used

- React 19
- Vite (build tool)
- Tailwind CSS
- React Router
- Axios
- React Icons+ Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
