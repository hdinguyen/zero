# Free/Paid Mode System Guide

## Overview

The application now includes a universal Free/Paid mode toggle that persists across browser sessions using localStorage. This system allows you to conditionally enable/disable features based on the user's selected mode.

## Setup

The mode system is already set up and ready to use:

1. **ModeProvider** wraps the entire application in `src/App.js`
2. **ModeContext** manages the global state in `src/contexts/ModeContext.js`
3. **localStorage** automatically persists the user's choice

## Using the Mode System

### Basic Usage

```jsx
import { useMode } from '../contexts/ModeContext';

function MyComponent() {
  const { mode, isFreeMode, isPaidMode, toggleMode } = useMode();

  return (
    <div>
      <p>Current mode: {mode}</p>
      
      {isPaidMode && (
        <div>🎉 Premium feature available!</div>
      )}
      
      {isFreeMode && (
        <div>⚠️ Upgrade to access premium features</div>
      )}
      
      <button onClick={toggleMode}>
        Switch to {isFreeMode ? 'Paid' : 'Free'} Mode
      </button>
    </div>
  );
}
```

### Available Hook Properties

```jsx
const {
  mode,        // 'free' or 'paid'
  setMode,     // Function to set mode directly
  toggleMode,  // Function to toggle between modes
  isFreeMode,  // Boolean: true if mode === 'free'
  isPaidMode   // Boolean: true if mode === 'paid'
} = useMode();
```

### Conditional Feature Rendering

```jsx
// Feature that's only available in paid mode
{isPaidMode && (
  <AdvancedAnalytics />
)}

// Feature with limited functionality in free mode
<DataExport 
  maxRecords={isFreeMode ? 100 : Infinity}
  formats={isFreeMode ? ['csv'] : ['csv', 'xlsx', 'json']}
/>

// Different UI based on mode
<button 
  className={isPaidMode ? 'btn-premium' : 'btn-standard'}
  disabled={isFreeMode && isAdvancedFeature}
>
  {isFreeMode ? 'Upgrade to Use' : 'Export Data'}
</button>
```

### API Integration

You can also pass the mode to your API calls:

```jsx
const { mode } = useMode();

const apiCall = async () => {
  const response = await fetch('/api/data', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-User-Mode': mode
    },
    body: JSON.stringify({ data: 'example' })
  });
};
```

## UI Components Examples

### Mode-Aware Badge

```jsx
function ModeBadge() {
  const { isPaidMode } = useMode();
  
  return (
    <span className={`px-2 py-1 rounded-full text-xs ${
      isPaidMode 
        ? 'bg-yellow-100 text-yellow-800' 
        : 'bg-gray-100 text-gray-600'
    }`}>
      {isPaidMode ? '👑 Premium' : '🆓 Free'}
    </span>
  );
}
```

### Feature Lock Component

```jsx
function FeatureLock({ children, requiresPaid = false }) {
  const { isPaidMode, toggleMode } = useMode();
  
  if (requiresPaid && !isPaidMode) {
    return (
      <div className="p-4 border border-gray-200 rounded-lg bg-gray-50">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-900">Premium Feature</h3>
          <p className="text-gray-600 mt-1">
            This feature is only available in paid mode.
          </p>
          <button 
            onClick={toggleMode}
            className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Switch to Paid Mode
          </button>
        </div>
      </div>
    );
  }
  
  return children;
}
```

### Usage Example

```jsx
function Dashboard() {
  return (
    <div>
      <h1>Dashboard <ModeBadge /></h1>
      
      <FeatureLock requiresPaid>
        <AdvancedCharts />
      </FeatureLock>
      
      <BasicCharts />
    </div>
  );
}
```

## Styling Conventions

### Colors
- **Free Mode**: Gray colors (`text-gray-500`, `bg-gray-100`)
- **Paid Mode**: Yellow/Gold colors (`text-yellow-600`, `bg-yellow-100`)

### Icons
- **Free Mode**: Basic icons
- **Paid Mode**: Crown icon (👑) or premium styling

### Visual Indicators
- **Status dots**: Gray for free, Yellow for paid
- **Badges**: Different styling based on mode
- **Features**: Disabled/locked appearance for unavailable features

## Storage

The mode preference is automatically saved to localStorage as `chatMode` and will persist across:
- Browser refreshes
- Tab closures
- Browser restarts
- Device restarts

## Testing

To test different modes during development:

```javascript
// In browser console
localStorage.setItem('chatMode', 'paid');   // Set to paid
localStorage.setItem('chatMode', 'free');   // Set to free
localStorage.removeItem('chatMode');        // Reset to default (free)

// Then refresh the page
window.location.reload();
```

## Best Practices

1. **Always check mode before showing premium features**
2. **Provide clear feedback about mode restrictions**
3. **Make the toggle easily accessible**
4. **Use consistent styling for mode indicators**
5. **Gracefully degrade features for free users**
6. **Consider showing upgrade prompts at appropriate times** 