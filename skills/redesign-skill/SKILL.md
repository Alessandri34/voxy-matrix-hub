---
name: redesign-skill
description: Systematic design audit and upgrade skill. Scan, diagnose, and fix generic patterns in existing projects without rewriting from scratch.
---

# Redesign Skill

## How This Works
When applied to an existing project, follow this sequence:
1. **Scan** — Read the codebase. Identify the framework, styling method, and current design patterns.
2. **Diagnose** — Run through the audit below. List every generic pattern, weak point, and missing state.
3. **Fix** — Apply targeted upgrades working with the existing stack. Do not rewrite from scratch.

## Design Audit

### Typography
- **Browser default fonts or Inter everywhere.** Replace with `Geist`, `Outfit`, `Cabinet Grotesk`, `Satoshi`.
- **Headlines lack presence.** Increase size, tighten letter-spacing, reduce line-height.
- **Body text too wide.** Limit to ~65 characters. Increase line-height.
- **Only Regular (400) and Bold (700).** Introduce Medium (500) and SemiBold (600).
- **Numbers in proportional font.** Use monospace or `font-variant-numeric: tabular-nums`.
- **Missing letter-spacing adjustments.** Negative tracking for headers, positive for labels.
- **Orphaned words.** Fix with `text-wrap: balance` or `text-wrap: pretty`.

### Color and Surfaces
- **Pure `#000000` background.** Replace with off-black (`#0a0a0a`, `#121212`).
- **Oversaturated accent colors.** Keep saturation below 80%.
- **More than one accent color.** Pick one. Remove the rest.
- **Mixing warm and cool grays.** Stick to one gray family.
- **Purple/blue "AI gradient" aesthetic.** Replace with neutral bases and a single accent.
- **Generic `box-shadow`.** Tint shadows to match the background hue.
- **Flat design with zero texture.** Add subtle noise, grain, or micro-patterns.
- **Random dark sections in a light mode page.** Keep consistent background tone.
- **Empty, flat sections.** Add background imagery, subtle patterns, or ambient gradients.

### Layout
- **Everything centered and symmetrical.** Break symmetry with offset margins or mixed aspect ratios.
- **Three equal card columns as feature row.** Replace with 2-column zig-zag, asymmetric grid, or masonry.
- **Using `height: 100vh`.** Replace with `min-height: 100dvh`.
- **No max-width container.** Add ~1200-1440px constraint with auto margins.
- **No overlap or depth.** Use negative margins to create layering.
- **Buttons not bottom-aligned in card groups.** Pin buttons to card bottoms.
- **Mathematical alignment that looks optically wrong.** Add 1-2px optical adjustments.

### Interactivity and States
- **No hover states on buttons.** Add background shift, slight scale, or translate.
- **No active/pressed feedback.** Add `scale(0.98)` or `translateY(1px)`.
- **No loading states.** Replace spinners with skeleton loaders.
- **No empty states.** Design a composed "getting started" view.
- **No error states.** Add clear, inline error messages.

### Content
- **Generic names like "John Doe".** Use diverse, realistic-sounding names.
- **Fake round numbers.** Use organic, messy data.
- **AI copywriting clichés.** Never use "Elevate", "Seamless", "Unleash", "Next-Gen".
- **Lorem Ipsum.** Never use. Write real draft copy.

### Component Patterns
- **Generic card look.** Remove border, or use only background color, or only spacing.
- **Three-card carousel testimonials.** Replace with masonry wall or embedded social posts.
- **Pricing table with 3 towers.** Highlight recommended tier with emphasis.

### Code Quality
- **Div soup.** Use semantic HTML.
- **Missing alt text.** Describe image content.
- **Arbitrary z-index values.** Establish a clean z-index scale.
- **Import hallucinations.** Check that every import exists in dependencies.

## Upgrade Techniques

### Typography Upgrades
- Variable font animation. Outlined-to-fill transitions. Text mask reveals.

### Layout Upgrades
- Broken grid / asymmetry. Whitespace maximization. Parallax card stacks. Split-screen scroll.

### Motion Upgrades
- Smooth scroll with inertia. Staggered entry. Spring physics. Scroll-driven reveals.

### Surface Upgrades
- True glassmorphism with inner borders and inner shadows. Spotlight borders. Grain overlays. Colored, tinted shadows.

## Fix Priority
1. **Font swap** — biggest instant improvement
2. **Color palette cleanup** — remove clashing colors
3. **Hover and active states** — makes it feel alive
4. **Layout and spacing** — proper grid, max-width, consistent padding
5. **Replace generic components** — swap cliché patterns
6. **Add loading, empty, and error states** — feels finished
7. **Polish typography scale** — the premium final touch

## Rules
- Work with the existing tech stack. Do not migrate frameworks.
- Do not break existing functionality.
- Before importing any new library, check the dependency file.
- Keep changes reviewable and focused.
