---
name: stitch-skill
description: Stitch Design Taste — Semantic Design System Skill. Generates DESIGN.md files optimized for Google Stitch screen generation with anti-slop frontend engineering directives.
---

# Stitch Design Taste — Semantic Design System Skill

## Overview
This skill generates `DESIGN.md` files optimized for Google Stitch screen generation. It translates anti-slop frontend engineering directives into Stitch's native semantic design language.

The generated `DESIGN.md` serves as the **single source of truth** for prompting Stitch to generate new screens that align with a curated, high-agency design language.

## Prerequisites
- Access to Google Stitch via [labs.google.com/stitch](https://labs.google.com/stitch)
- Optionally: Stitch MCP Server for programmatic integration

## The Goal
Generate a `DESIGN.md` file that encodes:
1. Visual atmosphere — mood, density, design philosophy
2. Color calibration — neutrals, accents, banned patterns with hex codes
3. Typographic architecture — font stacks, scale hierarchy, anti-patterns
4. Component behaviors — buttons, cards, inputs with interaction states
5. Layout principles — grid systems, spacing, responsive strategy
6. Motion philosophy — spring physics, perpetual micro-interactions
7. Anti-patterns — explicit list of banned AI design clichés

## Analysis & Synthesis Instructions

### 1. Define the Atmosphere
- **Density:** "Art Gallery Airy" (1–3) → "Daily App Balanced" (4–7) → "Cockpit Dense" (8–10)
- **Variance:** "Predictable Symmetric" (1–3) → "Offset Asymmetric" (4–7) → "Artsy Chaotic" (8–10)
- **Motion:** "Static Restrained" (1–3) → "Fluid CSS" (4–7) → "Cinematic Choreography" (8–10)
Default baseline: Variance 8, Motion 6, Density 4.

### 2. Map the Color Palette
- Maximum 1 accent color. Saturation below 80%
- "AI Purple/Blue Neon" aesthetic strictly BANNED
- Use absolute neutral bases (Zinc/Slate) with high-contrast singular accents
- Never use pure black (`#000000`)

### 3. Establish Typography Rules
- `Inter` BANNED for premium/creative contexts. Use `Geist`, `Outfit`, `Cabinet Grotesk`, or `Satoshi`
- Generic serif fonts BANNED. If serif needed, use modern serifs: `Fraunces`, `Gambarino`, `Editorial New`
- Dashboard: Sans-Serif pairings exclusively
- High-Density: All numbers must use Monospace

### 4. Define the Hero Section
- **Inline Image Typography:** Embed small photos between words in the headline
- **No Overlapping:** Text never overlaps images or other text
- **No Filler Text:** "Scroll to explore", scroll arrows BANNED
- **Asymmetric Structure:** Centered Hero layouts BANNED when variance > 4
- **CTA Restraint:** Maximum one primary CTA

### 5. Describe Component Stylings
- **Buttons:** Tactile push feedback. No neon outer glows. No custom mouse cursors
- **Cards:** Use ONLY when elevation communicates hierarchy. High-density: replace with dividers
- **Inputs/Forms:** Label above, error below. Standard gap spacing
- **Loading States:** Skeletal loaders matching layout dimensions
- **Empty States:** Composed compositions
- **Error States:** Clear, inline error reporting

### 6. Define Layout Principles
- No overlapping elements — clean spatial separation always
- CSS Grid over Flexbox math
- Max-width constraints (~1400px centered)
- `min-h-[100dvh]` never `h-screen`

### 7. Define Responsive Rules
- **Mobile-First Collapse (< 768px):** All multi-column layouts collapse to single column
- **No Horizontal Scroll** on mobile
- **Touch Targets:** Minimum `44px`
- **Typography Scaling:** Headlines scale via `clamp()`

### 8. Encode Motion Philosophy
- **Spring Physics default:** `stiffness: 100, damping: 20`
- **Perpetual Micro-Interactions:** Every active component has an infinite loop state
- **Staggered Orchestration:** Never mount lists instantly
- **Performance:** Animate via `transform` and `opacity` only

### 9. List Anti-Patterns (AI Tells)
- No emojis anywhere
- No `Inter` font
- No generic serif fonts
- No pure black (`#000000`)
- No neon/outer glow shadows
- No oversaturated accents
- No 3-column equal card layouts
- No generic names ("John Doe", "Acme", "Nexus")
- No fake round numbers
- No AI copywriting clichés
- No filler UI text or scroll arrows
- No broken Unsplash links — use `picsum.photos`

## Best Practices
- **Be Descriptive:** "Deep Charcoal Ink (#18181B)" not just "dark text"
- **Be Functional:** Explain what each element is used for
- **Be Consistent:** Same terminology throughout
- **Be Precise:** Include exact hex codes, rem values
- **Be Opinionated:** Enforce a specific, premium aesthetic

## Common Pitfalls to Avoid
- Using technical jargon without translation
- Omitting hex codes or using only descriptive names
- Forgetting functional roles of design elements
- Being too vague in atmosphere descriptions
- Defaulting to generic "safe" designs
