# WCAG 2.2 Level AA — Auditor Checklist

A working checklist of the success criteria most relevant to web UI audits. Each entry: the
criterion, what to verify, and how it commonly fails.

## Contents
- 1. Perceivable
- 2. Operable
- 3. Understandable
- 4. Robust
- WCAG 2.2 additions

## 1. Perceivable

| SC | Level | Check | Common failure |
| -- | ----- | ----- | -------------- |
| 1.1.1 Non-text Content | A | Images/icons/controls have text alternatives | Missing `alt`; icon button with no label |
| 1.3.1 Info & Relationships | A | Semantic structure (headings, lists, tables, labels) | Styled `<div>` headings; layout tables |
| 1.3.2 Meaningful Sequence | A | DOM order matches reading order | CSS reorders content illogically for AT |
| 1.3.5 Identify Input Purpose | AA | `autocomplete` on personal-data fields | Missing `autocomplete="email"` etc. |
| 1.4.1 Use of Color | A | Color is not the only means of conveying info | Red-only error text; color-only links |
| 1.4.3 Contrast (Minimum) | AA | Text ≥4.5:1 (large ≥3:1) | Light gray text on white |
| 1.4.4 Resize Text | AA | Usable at 200% zoom | Fixed px containers clip text |
| 1.4.10 Reflow | AA | No 2-D scroll at 320px width | Fixed-width layouts |
| 1.4.11 Non-text Contrast | AA | UI components/state ≥3:1 | Invisible input borders; faint focus ring |
| 1.4.12 Text Spacing | AA | No loss when users adjust spacing | Clipped text with `!important` line-height |

## 2. Operable

| SC | Level | Check | Common failure |
| -- | ----- | ----- | -------------- |
| 2.1.1 Keyboard | A | All functionality via keyboard | `div`/`span` click handlers |
| 2.1.2 No Keyboard Trap | A | Focus can leave any component | Modal/widget traps focus permanently |
| 2.4.1 Bypass Blocks | A | Skip link or landmarks | No way past repeated nav |
| 2.4.2 Page Titled | A | Descriptive `<title>` | "Untitled" / same title everywhere |
| 2.4.3 Focus Order | A | Logical focus sequence | Positive `tabindex` scrambles order |
| 2.4.4 Link Purpose | A | Link text makes sense alone | "click here", "read more" ×10 |
| 2.4.6 Headings & Labels | AA | Descriptive headings/labels | Vague or skipped heading levels |
| 2.4.7 Focus Visible | AA | Visible focus indicator | `outline: none` with no replacement |
| 2.4.11 Focus Not Obscured | AA | Focused element not hidden by sticky UI | Sticky header covers focused field |
| 2.5.3 Label in Name | A | Visible label is in the accessible name | Button shows "Search", a11y name "submit" |
| 2.5.8 Target Size (Minimum) | AA | Targets ≥24×24 CSS px (with exceptions) | Tiny icon hit areas |

## 3. Understandable

| SC | Level | Check | Common failure |
| -- | ----- | ----- | -------------- |
| 3.1.1 Language of Page | A | `<html lang>` set | Missing/incorrect `lang` |
| 3.2.1 On Focus | A | Focus doesn't trigger context change | Auto-submit on focus |
| 3.2.2 On Input | A | Changing a value doesn't surprise-navigate | Select onchange auto-navigates |
| 3.3.1 Error Identification | A | Errors described in text | Color-only validation |
| 3.3.2 Labels or Instructions | A | Inputs labeled; format hints given | Placeholder-only labels |
| 3.3.3 Error Suggestion | AA | Tell users how to fix errors | "Invalid input" with no guidance |
| 3.3.7 Redundant Entry | A | Don't re-ask for prior info | Re-typing the same data each step |
| 3.3.8 Accessible Authentication | AA | No cognitive-test-only login | Forced memorization/transcription |

## 4. Robust

| SC | Level | Check | Common failure |
| -- | ----- | ----- | -------------- |
| 4.1.2 Name, Role, Value | A | Custom widgets expose name/role/state | Custom checkbox with no role/state |
| 4.1.3 Status Messages | AA | Async updates announced via live region | Silent toasts / result counts |

## WCAG 2.2 additions (call these out specifically)

- **2.4.11 Focus Not Obscured (Minimum):** check sticky headers/footers and chat widgets.
- **2.5.7 Dragging Movements (AA):** any drag action has a single-pointer alternative.
- **2.5.8 Target Size (Minimum) (AA):** 24×24 CSS px minimum for pointer targets.
- **3.2.6 Consistent Help (A):** help mechanisms appear in a consistent location.
- **3.3.7 Redundant Entry (A):** auto-fill or let users select previously entered info.
- **3.3.8 Accessible Authentication (Minimum) (AA):** allow paste, password managers, and
  avoid requiring users to memorize or transcribe.

## Tooling note

Automated tools (axe-core, Lighthouse, Pa11y) catch roughly 30–40% of issues. Always pair
with: keyboard-only navigation, a screen reader (NVDA on Windows, VoiceOver on macOS/iOS),
200% zoom, and a contrast checker.
