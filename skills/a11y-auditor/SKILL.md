---
name: a11y-auditor
description: Audits HTML, JSX, and UI components for accessibility (a11y) problems against WCAG 2.2 AA, reporting each issue with severity, the success criterion, and a concrete code fix. Use when the user asks to check accessibility, mentions a11y, WCAG, screen readers, keyboard navigation, color contrast, ARIA, or alt text, or shares markup to review.
license: MIT
metadata:
  author: ATOM00blue
  version: "1.0.0"
  category: frontend
---

# Accessibility (a11y) Auditor

Find accessibility barriers in markup or components and give a fix for each, mapped to
[WCAG 2.2](https://www.w3.org/TR/WCAG22/) Level AA. Prioritize by real user impact.

## Workflow

```
- [ ] 1. Identify the document/component type and interactive elements
- [ ] 2. Run the checklist below, top to bottom
- [ ] 3. Report each issue: severity, WCAG criterion, location, fix
- [ ] 4. Provide corrected code
- [ ] 5. Note what still needs manual/AT testing
```

## The first rule of ARIA

**No ARIA is better than bad ARIA.** Prefer a native element (`<button>`, `<a href>`,
`<input>`, `<nav>`, `<label>`) over a `<div>` plus `role` plus JavaScript. Native elements
come with focus, keyboard behavior, and semantics for free.

## Audit checklist

### 1. Images and non-text content (WCAG 1.1.1)
- Every `<img>` has an `alt`. Informative images describe content; **decorative images use
  `alt=""`** (empty, not missing) so screen readers skip them.
- Icon-only buttons/links have an accessible name (`aria-label` or visually-hidden text).
- Complex images (charts) have a longer description nearby or via `aria-describedby`.

### 2. Text alternatives & headings (1.3.1, 2.4.6)
- Headings are nested in order (`h1` → `h2` → `h3`), not chosen for size. One `h1` per page.
- Use real lists (`<ul>/<ol>`), `<table>` with `<th scope>` for tabular data — not layout.

### 3. Color and contrast (1.4.3, 1.4.11)
- Text contrast ≥ **4.5:1** (≥ **3:1** for large text ≥24px or 18.66px bold).
- UI components and graphical objects (icons, input borders, focus rings) ≥ **3:1**.
- **Color is never the only signal** — pair it with text, an icon, or underline (1.4.1).

### 4. Keyboard and focus (2.1.1, 2.4.7, 2.4.11)
- Every interactive element is reachable and operable by keyboard; no keyboard trap.
- A **visible focus indicator** exists; never `outline: none` without a replacement.
- Logical tab order (DOM order); avoid positive `tabindex`.
- Custom widgets follow the [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
  keyboard pattern (e.g. arrow keys in a menu/tablist).

### 5. Forms (1.3.5, 3.3.1, 3.3.2, 4.1.2)
- Every input has a programmatic `<label>` (or `aria-label`/`aria-labelledby`).
- Required fields and formats are stated in text, not just color/placeholder.
- Errors are announced (`aria-live`/`role="alert"`), tied to the field (`aria-describedby`),
  and say how to fix them.
- Don't use placeholder text as the only label — it disappears on input.

### 6. Dynamic content & ARIA (4.1.2, 4.1.3)
- Live regions (`aria-live="polite"` / `role="status"`) announce async updates (toasts,
  loading, search results count).
- Modals: focus moves in on open, is trapped inside, returns to the trigger on close;
  `role="dialog"` + `aria-modal="true"` + an accessible name; `Esc` closes.
- State is exposed: `aria-expanded`, `aria-pressed`, `aria-current`, `aria-selected`.

### 7. Structure & navigation (2.4.1, 1.3.1)
- Landmarks present (`<header> <nav> <main> <footer>`); one `<main>`.
- A "skip to content" link is the first focusable element.
- Page has a descriptive `<title>` and `lang` on `<html>`.

### 8. Motion & resize (1.4.4, 1.4.10, 2.3.3)
- Text reflows and remains usable at 200% zoom / 320px width without horizontal scroll.
- Respect `prefers-reduced-motion`; avoid content that flashes more than 3×/second.

## Report format

For each finding:

```
[SEVERITY] WCAG <criterion> — <short title>
Where: <selector / line>
Problem: <one sentence>
Fix:
<corrected code>
```

Severity: **Critical** (blocks a task for AT users), **Serious** (major barrier),
**Moderate** (workaround exists), **Minor** (polish).

## Example

**Input:**
```html
<div onclick="submit()" style="color:#9b9b9b">Send</div>
<img src="chart.png">
```

**Findings:**
```
[Critical] WCAG 2.1.1 / 4.1.2 — clickable div is not keyboard or AT operable
Where: <div onclick="submit()">
Fix:
<button type="button" onclick="submit()">Send</button>

[Serious] WCAG 1.4.3 — "Send" text contrast ~2.8:1 on white (needs 4.5:1)
Fix: use #595959 or darker on #ffffff.

[Serious] WCAG 1.1.1 — image has no text alternative
Fix:
<img src="chart.png" alt="Q2 revenue rose 18% to $4.2M">
```

## What still needs manual testing

Automated review catches ~30–40% of issues. Flag that the following require a human or
assistive tech: actual screen-reader announcements (NVDA/VoiceOver), keyboard-only walk-throughs,
focus order with real content, and contrast over images/gradients.

## Additional resources

- For the full per-criterion checklist with pass/fail notes, see
  [references/wcag-2.2-aa-checklist.md](references/wcag-2.2-aa-checklist.md).
