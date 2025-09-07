import React from 'react';
import { useDarkMode } from '../contexts/DarkModeContext';
import { Moon, Sun } from 'lucide-react';
import './DarkModeToggle.css';

const DarkModeToggle = () => {
  const { isDarkMode, toggleDarkMode } = useDarkMode();

  return (
    <button
      className="dark-mode-toggle"
      onClick={toggleDarkMode}
      aria-label={isDarkMode ? 'تفعيل الوضع العادي' : 'تفعيل الوضع المظلم'}
      title={isDarkMode ? 'تفعيل الوضع العادي' : 'تفعيل الوضع المظلم'}
    >
      {isDarkMode ? (
        <Sun size={20} className="toggle-icon" />
      ) : (
        <Moon size={20} className="toggle-icon" />
      )}
    </button>
  );
};

export default DarkModeToggle;
