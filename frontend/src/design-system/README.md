# Design-System für Dev-Server-Workflow

Dieses Design-System bietet eine Sammlung von wiederverwendbaren Komponenten, Tokens und Utilities für die Entwicklung der Dev-Server-Workflow-Anwendung. Es wurde mit Fokus auf Konsistenz, Barrierefreiheit und Benutzerfreundlichkeit entwickelt.

## Inhaltsverzeichnis

1. [Einführung](#einführung)
2. [Struktur](#struktur)
3. [Tokens](#tokens)
4. [Theme](#theme)
5. [Komponenten](#komponenten)
6. [Hooks](#hooks)
7. [Styles](#styles)
8. [Verwendung](#verwendung)
9. [Barrierefreiheit](#barrierefreiheit)

## Einführung

Das Design-System ist die Grundlage für ein konsistentes Erscheinungsbild und Verhalten der Anwendung. Es bietet:

- **Design-Tokens**: Grundlegende Designelemente wie Farben, Abstände, Typografie, etc.
- **Theme-System**: Unterstützung für Light- und Dark-Mode
- **Komponenten-Bibliothek**: Wiederverwendbare UI-Komponenten
- **Hooks**: Nützliche React-Hooks für häufige Aufgaben
- **Globale Styles**: Grundlegende Styles für die gesamte Anwendung

## Struktur

Das Design-System ist wie folgt strukturiert:

```
design-system/
├── components/       # UI-Komponenten
├── hooks/            # React-Hooks
├── styles/           # Globale Styles
├── tokens/           # Design-Tokens
├── theme.ts          # Theme-Definitionen
├── ThemeProvider.tsx # Theme-Provider
└── index.ts          # Haupt-Export
```

## Tokens

Design-Tokens sind die kleinsten Designelemente, die in der Anwendung verwendet werden. Sie bilden die Grundlage für das gesamte Design-System.

### Farben

```typescript
const colors = {
  primary: {
    50: '#e3f2fd',
    100: '#bbdefb',
    // ...
    900: '#0d47a1',
  },
  // ...
};
```

### Abstände

```typescript
const spacing = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  // ...
};
```

### Typografie

```typescript
const typography = {
  fontFamily: {
    primary: '"Roboto", "Helvetica", "Arial", sans-serif',
    code: '"Source Code Pro", monospace',
  },
  fontSize: {
    xs: '0.75rem',
    sm: '0.875rem',
    // ...
  },
  // ...
};
```

## Theme

Das Theme-System unterstützt sowohl Light- als auch Dark-Mode und kann zur Laufzeit gewechselt werden.

```typescript
// Light-Theme verwenden
<ThemeProvider initialTheme="light">
  <App />
</ThemeProvider>

// Dark-Theme verwenden
<ThemeProvider initialTheme="dark">
  <App />
</ThemeProvider>

// System-Einstellung verwenden
<ThemeProvider initialTheme="system">
  <App />
</ThemeProvider>
```

### Theme wechseln

```typescript
import { useTheme } from './design-system';

const MyComponent = () => {
  const { theme, toggleTheme, setTheme } = useTheme();
  
  return (
    <div>
      <p>Aktuelles Theme: {theme.mode}</p>
      <button onClick={toggleTheme}>Theme wechseln</button>
      <button onClick={() => setTheme('light')}>Light-Mode</button>
      <button onClick={() => setTheme('dark')}>Dark-Mode</button>
      <button onClick={() => setTheme('system')}>System-Einstellung</button>
    </div>
  );
};
```

## Komponenten

Das Design-System bietet eine Reihe von wiederverwendbaren UI-Komponenten.

### Button

```typescript
import { Button } from './design-system';

// Primärer Button
<Button variant="primary">Klick mich</Button>

// Sekundärer Button
<Button variant="secondary">Klick mich</Button>

// Outlined Button
<Button variant="outlined">Klick mich</Button>

// Text-Button
<Button variant="text">Klick mich</Button>

// Error-Button
<Button variant="error">Löschen</Button>

// Größen
<Button size="sm">Klein</Button>
<Button size="md">Mittel</Button>
<Button size="lg">Groß</Button>

// Volle Breite
<Button fullWidth>Volle Breite</Button>

// Deaktiviert
<Button disabled>Deaktiviert</Button>

// Loading
<Button isLoading>Loading</Button>

// Mit Icons
<Button startIcon={<Icon />}>Mit Icon</Button>
<Button endIcon={<Icon />}>Mit Icon</Button>
```

### Card

```typescript
import { Card } from './design-system';

// Einfache Card
<Card>
  <p>Inhalt</p>
</Card>

// Card mit Titel
<Card title="Meine Card">
  <p>Inhalt</p>
</Card>

// Card mit Footer
<Card
  title="Meine Card"
  footer={
    <div>
      <Button>Abbrechen</Button>
      <Button variant="primary">Speichern</Button>
    </div>
  }
>
  <p>Inhalt</p>
</Card>

// Card-Varianten
<Card variant="default">Default</Card>
<Card variant="outlined">Outlined</Card>
<Card variant="elevated">Elevated</Card>
```

### Input

```typescript
import { Input } from './design-system';

// Einfacher Input
<Input placeholder="Eingabe" />

// Input mit Label
<Input label="Name" placeholder="Max Mustermann" />

// Input mit Hilfetext
<Input
  label="E-Mail"
  placeholder="max@example.com"
  helperText="Wir werden Ihre E-Mail niemals weitergeben."
/>

// Input mit Fehler
<Input
  label="Passwort"
  type="password"
  error="Das Passwort muss mindestens 8 Zeichen lang sein."
/>

// Input-Varianten
<Input variant="outlined" label="Outlined" />
<Input variant="filled" label="Filled" />
<Input variant="standard" label="Standard" />

// Input-Größen
<Input size="sm" label="Klein" />
<Input size="md" label="Mittel" />
<Input size="lg" label="Groß" />

// Input mit Icons
<Input startIcon={<Icon />} label="Mit Icon" />
<Input endIcon={<Icon />} label="Mit Icon" />
```

### Grid

```typescript
import { GridContainer, GridItem } from './design-system';

<GridContainer spacing={{ xs: 1, md: 2 }}>
  <GridItem xs={12} md={6} lg={4}>
    <Card>Item 1</Card>
  </GridItem>
  <GridItem xs={12} md={6} lg={4}>
    <Card>Item 2</Card>
  </GridItem>
  <GridItem xs={12} md={6} lg={4}>
    <Card>Item 3</Card>
  </GridItem>
</GridContainer>
```

### Container

```typescript
import { Container } from './design-system';

// Standard-Container
<Container>
  <p>Inhalt</p>
</Container>

// Container-Größen
<Container size="sm">Klein</Container>
<Container size="md">Mittel</Container>
<Container size="lg">Groß</Container>
<Container size="xl">Extra Groß</Container>
<Container size="fluid">Fluid</Container>
```

### Modal

```typescript
import { Modal, Button } from './design-system';
import { useState } from 'react';

const MyComponent = () => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <>
      <Button onClick={() => setIsOpen(true)}>Modal öffnen</Button>
      
      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="Mein Modal"
        footer={
          <div>
            <Button onClick={() => setIsOpen(false)}>Abbrechen</Button>
            <Button variant="primary">Speichern</Button>
          </div>
        }
      >
        <p>Modal-Inhalt</p>
      </Modal>
    </>
  );
};
```

## Hooks

Das Design-System bietet nützliche React-Hooks für häufige Aufgaben.

### useFocusTrap

```typescript
import { useFocusTrap } from './design-system';

const MyComponent = () => {
  const { containerRef } = useFocusTrap(true);
  
  return (
    <div ref={containerRef}>
      <button>Button 1</button>
      <button>Button 2</button>
      <button>Button 3</button>
    </div>
  );
};
```

### useKeyboardNavigation

```typescript
import { useKeyboardNavigation } from './design-system';

const MyComponent = () => {
  const items = ['Item 1', 'Item 2', 'Item 3'];
  
  const { containerRef, activeIndex, handleKeyDown } = useKeyboardNavigation(
    items.length,
    {
      vertical: true,
      loop: true,
      onSelect: (index) => console.log(`Selected: ${items[index]}`),
    }
  );
  
  return (
    <div
      ref={containerRef}
      onKeyDown={handleKeyDown}
      tabIndex={0}
    >
      {items.map((item, index) => (
        <div
          key={index}
          style={{
            background: activeIndex === index ? 'lightblue' : 'transparent',
          }}
        >
          {item}
        </div>
      ))}
    </div>
  );
};
```

### useAnnouncer

```typescript
import { useAnnouncer } from './design-system';

const MyComponent = () => {
  const { announce } = useAnnouncer();
  
  const handleAction = () => {
    // Aktion ausführen
    announce('Aktion erfolgreich ausgeführt');
  };
  
  return (
    <button onClick={handleAction}>
      Aktion ausführen
    </button>
  );
};
```

## Styles

Das Design-System bietet globale Styles für die gesamte Anwendung.

```typescript
import { GlobalStyles } from './design-system';

// In der App-Komponente
<ThemeProvider>
  <GlobalStyles />
  <App />
</ThemeProvider>
```

## Verwendung

Um das Design-System in einer Komponente zu verwenden, importieren Sie die benötigten Teile:

```typescript
import { 
  Button, 
  Card, 
  Input, 
  useTheme 
} from './design-system';

const MyComponent = () => {
  const { theme } = useTheme();
  
  return (
    <Card title="Meine Komponente">
      <Input label="Name" placeholder="Max Mustermann" />
      <div style={{ marginTop: theme.spacing.md }}>
        <Button variant="primary">Speichern</Button>
      </div>
    </Card>
  );
};
```

## Barrierefreiheit

Das Design-System wurde mit Fokus auf Barrierefreiheit entwickelt. Alle Komponenten:

- Unterstützen Tastatur-Navigation
- Haben semantisch korrekte HTML-Elemente
- Verwenden ARIA-Attribute
- Haben ausreichende Farbkontraste
- Unterstützen Screenreader

Zusätzlich bietet das Design-System Hilfsmittel für die Verbesserung der Barrierefreiheit:

- `useFocusTrap`: Verhindert, dass der Fokus aus einem bestimmten Bereich entweicht
- `useKeyboardNavigation`: Ermöglicht die Navigation durch Elemente mit Pfeiltasten
- `useAnnouncer`: Ermöglicht das Ankündigen von Nachrichten für Screenreader
- `GlobalStyles`: Enthält Barrierefreiheits-Verbesserungen für die gesamte Anwendung