import { useState, useEffect, useCallback } from 'react';
import darkModeConfig, { getSystemPreference, applyCssVariables } from '../config/darkModeConfig';

export const useAdvancedDarkMode = () => {
  // Initialize state from localStorage or system preference
  const [isDarkMode, setIsDarkMode] = useState(() => {
    // Check localStorage first
    const savedMode = localStorage.getItem(darkModeConfig.storageKey);
    if (savedMode !== null) {
      return savedMode === 'true';
    }
    
    // Fall back to system preference if auto-detect is enabled
    if (darkModeConfig.autoDetectSystemPreference) {
      return getSystemPreference();
    }
    
    // Use default mode
    return darkModeConfig.defaultMode;
  });

  // Toggle function
  const toggleDarkMode = useCallback(() => {
    setIsDarkMode(prevMode => {
      const newMode = !prevMode;
      localStorage.setItem(darkModeConfig.storageKey, newMode.toString());
      return newMode;
    });
  }, []);

  // Set specific mode
  const setDarkMode = useCallback((mode) => {
    setIsDarkMode(mode);
    localStorage.setItem(darkModeConfig.storageKey, mode.toString());
  }, []);

  // Reset to system preference
  const resetToSystemPreference = useCallback(() => {
    const systemPreference = getSystemPreference();
    setDarkMode(systemPreference);
  }, [setDarkMode]);

  // Apply dark mode class and CSS variables
  useEffect(() => {
    const bodyElement = document.body;
    
    if (isDarkMode) {
      bodyElement.classList.add(darkModeConfig.darkModeClass);
    } else {
      bodyElement.classList.remove(darkModeConfig.darkModeClass);
    }

    // Apply CSS variables
    applyCssVariables(isDarkMode);

    // Store preference
    localStorage.setItem(darkModeConfig.storageKey, isDarkMode.toString());

    // Dispatch custom event for other components to listen
    const event = new CustomEvent('darkModeChange', { 
      detail: { isDarkMode } 
    });
    window.dispatchEvent(event);

  }, [isDarkMode]);

  // Listen for system preference changes
  useEffect(() => {
    if (darkModeConfig.autoDetectSystemPreference && window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      
      const handleChange = (e) => {
        // Only update if no user preference is stored
        const savedMode = localStorage.getItem(darkModeConfig.storageKey);
        if (savedMode === null) {
          setIsDarkMode(e.matches);
        }
      };

      // Modern browsers
      if (mediaQuery.addEventListener) {
        mediaQuery.addEventListener('change', handleChange);
        return () => mediaQuery.removeEventListener('change', handleChange);
      } 
      // Older browsers
      else if (mediaQuery.addListener) {
        mediaQuery.addListener(handleChange);
        return () => mediaQuery.removeListener(handleChange);
      }
    }
  }, []);

  // Get current theme colors
  const getThemeColors = useCallback(() => {
    return isDarkMode ? darkModeConfig.colors.dark : darkModeConfig.colors.light;
  }, [isDarkMode]);

  // Check if system supports dark mode
  const systemSupportsDarkMode = () => {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').media !== 'not all';
  };

  // Get system preference
  const systemPrefersDark = getSystemPreference();

  return {
    isDarkMode,
    toggleDarkMode,
    setDarkMode,
    resetToSystemPreference,
    getThemeColors,
    systemSupportsDarkMode: systemSupportsDarkMode(),
    systemPrefersDark,
    config: darkModeConfig
  };
};

export default useAdvancedDarkMode;
