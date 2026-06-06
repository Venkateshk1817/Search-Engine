# Style Documentation

## Theme Variables
```css
:root {
    --mono-bg: #fff;              /* Background color */
    --mono-surface: #f5f5f5;      /* Surface/container background */
    --mono-border: #e0e0e0;       /* Border color */
    --mono-text: #111;            /* Text color */
    --mono-accent: #111;          /* Accent color */
    --mono-radius: 12px;          /* Border radius */
    --mono-shadow: 0 2px 8px rgba(0,0,0,0.04); /* Box shadow */
    --input-height: 3.2rem;       /* Input field height */
}
```

## Dark Theme
```css
[data-theme="dark"] {
    --mono-bg: #111;
    --mono-surface: #222;
    --mono-border: #333;
    --mono-text: #fff;
    --mono-accent: #fff;
}
```

## Key Components

### Container
- Max width: 700px
- Padding: 2.2rem 2rem
- Background: var(--mono-surface)
- Border radius: var(--mono-radius)
- Box shadow: var(--mono-shadow)

### Input Fields
- Height: var(--input-height)
- Padding: 0 1rem
- Border radius: var(--mono-radius)
- Focus state: Border color changes to accent color

### Buttons
- Height: var(--input-height)
- Background: var(--mono-accent)
- Color: var(--mono-accent-dark)
- Border radius: var(--mono-radius)
- Hover: Darker background (#222)

### Theme Toggle
- Position: Fixed (top-right)
- Size: 2.5rem × 2.5rem
- Border radius: 50%
- Background: var(--mono-bg)

### Responsive Design
- Mobile breakpoint: 700px
- Container: 98vw width
- Reduced padding: 1.2rem 0.5rem
- Smaller font sizes: 15px

## Common Elements
- Font: 'Inter', system fonts
- Line height: 1.5
- Transitions: 0.2s-0.3s for color/background changes
- Error states: Red border with light background 