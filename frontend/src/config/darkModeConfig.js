// Dark Mode Configuration
export const darkModeConfig = {
  // Storage key for localStorage
  storageKey: 'darkMode',
  
  // CSS class name for dark mode
  darkModeClass: 'dark-mode',
  
  // Default mode (false = light, true = dark)
  defaultMode: false,
  
  // Auto-detect system preference
  autoDetectSystemPreference: true,
  
  // Animation duration for transitions
  transitionDuration: '0.3s',
  
  // Color scheme configuration
  colors: {
    light: {
      background: '#ffffff',
      surface: '#f9fafb',
      text: '#111827',
      textSecondary: '#6b7280',
      primary: '#3b82f6',
      border: '#e5e7eb',
      hover: '#f3f4f6'
    },
    dark: {
      background: '#111827',
      surface: '#1f2937',
      text: '#f9fafb',
      textSecondary: '#e5e7eb',
      primary: '#60a5fa',
      border: '#374151',
      hover: '#374151'
    }
  },
  
  // Components that should be excluded from dark mode
  excludedComponents: [
    '.no-dark-mode',
    '.light-only'
  ],
  
  // Custom CSS variables for dark mode
  cssVariables: {
    '--bg-primary': 'var(--bg-primary-light)',
    '--bg-secondary': 'var(--bg-secondary-light)',
    '--text-primary': 'var(--text-primary-light)',
    '--text-secondary': 'var(--text-secondary-light)',
    '--border-color': 'var(--border-color-light)',
    '--shadow': 'var(--shadow-light)'
  },
  
  // Dark mode CSS variables
  darkCssVariables: {
    '--bg-primary': 'var(--bg-primary-dark)',
    '--bg-secondary': 'var(--bg-secondary-dark)',
    '--text-primary': 'var(--text-primary-dark)',
    '--text-secondary': 'var(--text-secondary-dark)',
    '--border-color': 'var(--border-color-dark)',
    '--shadow': 'var(--shadow-dark)'
  }
};

// Utility function to detect system preference
export const getSystemPreference = () => {
  if (typeof window !== 'undefined' && window.matchMedia) {
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
  return false;
};

// Utility function to apply CSS variables
export const applyCssVariables = (isDarkMode) => {
  if (typeof document !== 'undefined') {
    const root = document.documentElement;
    const variables = isDarkMode 
      ? darkModeConfig.darkCssVariables 
      : darkModeConfig.cssVariables;
    
    Object.entries(variables).forEach(([property, value]) => {
      root.style.setProperty(property, value);
    });
  }
};

export default darkModeConfig;
