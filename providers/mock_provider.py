"""
High-fidelity Mock LLM Provider for offline research, automated tests, and reproducible benchmarks.
Generates realistic, syntactically valid HTML/CSS/JS and structured JSON for each agent.
"""

import json
import time
from typing import Any, Dict, List, Optional
from providers.base import LLMProvider, LLMResponse, TokenUsage


class MockProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = "mock_key"):
        super().__init__(api_key)

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str = "mock-agent-v1",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format_json: bool = False,
        system_prompt: Optional[str] = None,
    ) -> LLMResponse:
        start_time = time.perf_counter()

        # Combine all prompt text to identify the calling agent context
        all_text = (system_prompt or "") + " " + " ".join([m.get("content", "") for m in messages])
        all_text_lower = all_text.lower()

        parsed_json: Optional[Dict[str, Any]] = None
        content = ""

        # 1. Prompt Structurer Agent
        if "prompt structurer" in all_text_lower or "structured requirements" in all_text_lower or "project_goal" in all_text_lower:
            parsed_json = self._mock_prompt_structurer(all_text)
            content = json.dumps(parsed_json, indent=2)

        # 2. Aesthetic Agent
        elif "aesthetic" in all_text_lower and "score" in all_text_lower:
            parsed_json = self._mock_aesthetic_agent(all_text)
            content = json.dumps(parsed_json, indent=2)

        # 3. Accessibility Agent
        elif "accessibility" in all_text_lower and ("wcag" in all_text_lower or "contrast" in all_text_lower):
            parsed_json = self._mock_accessibility_agent(all_text)
            content = json.dumps(parsed_json, indent=2)

        # 4. Usability Agent
        elif "usability" in all_text_lower and ("cta" in all_text_lower or "navigation" in all_text_lower):
            parsed_json = self._mock_usability_agent(all_text)
            content = json.dumps(parsed_json, indent=2)

        # 5. Ethics & Compliance Agent
        elif "dark_patterns_detected" in all_text_lower or "ethics" in all_text_lower or "compliance" in all_text_lower:
            parsed_json = self._mock_ethics_agent(all_text)
            content = json.dumps(parsed_json, indent=2)

        # 6. Originality & Diversity Agent
        elif "originality" in all_text_lower or "distinctness" in all_text_lower:
            parsed_json = self._mock_originality_agent(all_text)
            content = json.dumps(parsed_json, indent=2)

        # 7. General Critic Agent
        elif "general critic" in all_text_lower or "generalist critique" in all_text_lower:
            parsed_json = self._mock_general_critic_agent(all_text)
            content = json.dumps(parsed_json, indent=2)

        # 8. Feedback Aggregator Agent
        elif "aggregator" in all_text_lower or "priority_issues" in all_text_lower:
            parsed_json = self._mock_aggregator_agent(all_text)
            content = json.dumps(parsed_json, indent=2)

        # 9. Design Refiner Agent
        elif "refiner" in all_text_lower or "revised_html" in all_text_lower:
            parsed_json = self._mock_refiner_agent(all_text)
            content = json.dumps(parsed_json, indent=2)

        # 10. Web Generator Agent (Default generator)
        else:
            parsed_json = self._mock_web_generator(all_text)
            content = json.dumps(parsed_json, indent=2)

        latency_ms = (time.perf_counter() - start_time) * 1000 + 45.0  # realistic simulated latency
        prompt_tokens = len(all_text.split()) * 2
        completion_tokens = len(content.split()) * 2
        total_tokens = prompt_tokens + completion_tokens
        cost = (prompt_tokens * 0.000001) + (completion_tokens * 0.000002)

        return LLMResponse(
            content=content,
            parsed_json=parsed_json if response_format_json or parsed_json else self.extract_json(content),
            token_usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=cost,
            ),
            latency_ms=latency_ms,
            model=model,
            provider="mock",
            finish_reason="stop",
        )

    def _mock_prompt_structurer(self, text: str) -> Dict[str, Any]:
        # Extract title or keyword if possible
        topic = "Modern Sustainable Fashion Brand" if "fashion" in text.lower() else "Modern Interactive Web Platform"
        return {
            "project_goal": f"Design an elegant, highly engaging, and conversion-optimized website for {topic}.",
            "website_type": "E-Commerce / Brand Showcase",
            "target_users": [
                "Eco-conscious consumers seeking ethical apparel",
                "Design enthusiasts valuing clean minimalism",
                "Mobile and desktop shoppers expecting fast, accessible UX"
            ],
            "functional_requirements": [
                "Hero section with dynamic headline and primary Call to Action (CTA)",
                "Featured product catalog with filtering and responsive grid",
                "Sustainability impact metric counters with interactive cards",
                "Newsletter subscription with email validation",
                "Accessible footer with navigation and policy disclosures"
            ],
            "visual_requirements": [
                "Modern earth-tone palette with high contrast (sage green, warm sand, charcoal)",
                "Generous whitespace and clean typography hierarchy (serif headings, sans body)",
                "Card elevation with subtle borders and smooth hover transitions"
            ],
            "accessibility_requirements": [
                "WCAG 2.1 AA compliant color contrast (>= 4.5:1 for normal text)",
                "Descriptive alt text on all imagery",
                "Visible keyboard focus states and logical tab order",
                "Semantic HTML5 landmark tags (header, nav, main, section, footer)"
            ],
            "usability_requirements": [
                "Intuitive sticky navigation bar with clear active states",
                "Prominent primary CTA buttons above the fold",
                "Responsive fluid layout across mobile, tablet, and desktop"
            ],
            "compliance_requirements": [
                "Zero dark patterns (no fake countdowns or preselected checkboxes)",
                "Transparent pricing, shipping details, and clear return policy link",
                "Explicit consent option for newsletter subscription"
            ],
            "originality_requirements": [
                "Distinctive bespoke layout avoiding generic corporate template tropes",
                "Custom interactive sustainability impact calculator badge",
                "Harmonious asymmetrical grid elements"
            ],
            "technical_constraints": [
                "Pure standard HTML5, CSS3, and modern Vanilla JS (ES6+)",
                "No external heavy framework dependencies",
                "Fully self-contained and performant"
            ],
            "content_requirements": [
                "Compelling copy articulating organic sourcing and ethical labor",
                "Accurate product descriptions with materials breakdown",
                "Transparent founder message"
            ],
            "explicit_constraints": [
                "Must load fast and render reliably in sandboxed iframes"
            ],
            "implicit_requirements": [
                "Smooth hover feedback on all interactive elements",
                "Accessible error messaging on form submission"
            ],
            "acceptance_criteria": [
                "Composite evaluation score across all specialized agents >= 8.0/10",
                "Zero critical WCAG accessibility violations",
                "Zero deceptive or coercive dark patterns detected"
            ]
        }

    def _mock_web_generator(self, text: str) -> Dict[str, Any]:
        html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AURA | Sustainable Ethical Fashion</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header class="site-header" role="banner">
    <div class="container nav-wrapper">
      <a href="#home" class="brand-logo" aria-label="Aura Sustainable Fashion Home">AURA<span>.</span></a>
      <nav class="main-nav" role="navigation" aria-label="Main Navigation">
        <ul class="nav-list">
          <li><a href="#catalog" class="nav-link">Collection</a></li>
          <li><a href="#impact" class="nav-link">Sustainability</a></li>
          <li><a href="#story" class="nav-link">Our Story</a></li>
          <li><a href="#contact" class="nav-link">Journal</a></li>
        </ul>
      </nav>
      <div class="header-actions">
        <button class="btn btn-outline" id="cart-btn" aria-label="View Shopping Cart">Cart (<span id="cart-count">0</span>)</button>
        <a href="#catalog" class="btn btn-primary">Shop Now</a>
      </div>
    </div>
  </header>

  <main id="main-content" role="main">
    <!-- Hero Section -->
    <section id="home" class="hero-section" aria-labelledby="hero-title">
      <div class="container hero-grid">
        <div class="hero-content">
          <span class="badge badge-accent">100% Organic & Circular</span>
          <h1 id="hero-title">Timeless Fashion Crafted in Harmony with Nature</h1>
          <p class="hero-subtitle">
            Ethically sourced botanical fibers and zero-waste craftsmanship. Designed to look sublime today, and enrich the Earth tomorrow.
          </p>
          <div class="hero-cta-group">
            <a href="#catalog" class="btn btn-primary btn-lg">Explore Autumn 2026</a>
            <a href="#impact" class="btn btn-secondary btn-lg">Our Eco Impact</a>
          </div>
          <div class="trust-metrics">
            <div class="metric-item">
              <strong>94%</strong>
              <span>Water Recycled</span>
            </div>
            <div class="metric-item">
              <strong>0%</strong>
              <span>Microplastics</span>
            </div>
            <div class="metric-item">
              <strong>100%</strong>
              <span>Fair-Trade</span>
            </div>
          </div>
        </div>
        <div class="hero-visual">
          <div class="visual-card">
            <div class="visual-placeholder" aria-label="Model wearing sustainable linen coat in natural daylight">
              <div class="product-tag">Organic Linen Coat &bull; Autumn Sage</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Catalog Section -->
    <section id="catalog" class="catalog-section" aria-labelledby="catalog-title">
      <div class="container">
        <div class="section-header">
          <h2 id="catalog-title">Curated Essentials</h2>
          <p class="section-desc">Hand-loomed botanic textiles made with regenerative agriculture standards.</p>
          <div class="filter-bar" role="toolbar" aria-label="Product Category Filters">
            <button class="filter-btn active" data-filter="all">All Items</button>
            <button class="filter-btn" data-filter="outerwear">Outerwear</button>
            <button class="filter-btn" data-filter="knitwear">Knitwear</button>
            <button class="filter-btn" data-filter="accessories">Accessories</button>
          </div>
        </div>

        <div class="product-grid" id="product-grid">
          <article class="product-card" data-category="outerwear">
            <div class="product-image-box">
              <span class="card-badge">Zero Waste</span>
              <div class="product-placeholder img-1" role="img" aria-label="Sage Green Organic Trench Coat"></div>
            </div>
            <div class="product-info">
              <span class="product-category">Outerwear</span>
              <h3 class="product-name">Verdant Linen Trench</h3>
              <p class="product-desc">Pure European flax with recycled corozo nut buttons.</p>
              <div class="product-footer">
                <span class="price">$245.00</span>
                <button class="btn btn-sm btn-outline add-to-cart" data-id="1" data-name="Verdant Linen Trench">Add to Cart</button>
              </div>
            </div>
          </article>

          <article class="product-card" data-category="knitwear">
            <div class="product-image-box">
              <span class="card-badge">Organic Cotton</span>
              <div class="product-placeholder img-2" role="img" aria-label="Warm Sand Ribbed Organic Pullover"></div>
            </div>
            <div class="product-info">
              <span class="product-category">Knitwear</span>
              <h3 class="product-name">Earthy Ribbed Pullover</h3>
              <p class="product-desc">GOTS-certified unbleached organic cotton yarn.</p>
              <div class="product-footer">
                <span class="price">$168.00</span>
                <button class="btn btn-sm btn-outline add-to-cart" data-id="2" data-name="Earthy Ribbed Pullover">Add to Cart</button>
              </div>
            </div>
          </article>

          <article class="product-card" data-category="accessories">
            <div class="product-image-box">
              <span class="card-badge">Plant Dyed</span>
              <div class="product-placeholder img-3" role="img" aria-label="Indigo Botanical Silk Scarf"></div>
            </div>
            <div class="product-info">
              <span class="product-category">Accessories</span>
              <h3 class="product-name">Indigo Flora Scarf</h3>
              <p class="product-desc">Peace silk dyed with wild indigo leaf extract.</p>
              <div class="product-footer">
                <span class="price">$85.00</span>
                <button class="btn btn-sm btn-outline add-to-cart" data-id="3" data-name="Indigo Flora Scarf">Add to Cart</button>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- Interactive Impact Section -->
    <section id="impact" class="impact-section" aria-labelledby="impact-title">
      <div class="container">
        <div class="impact-card">
          <div class="impact-text">
            <h2 id="impact-title">Calculate Your Ecological Savings</h2>
            <p>Every AURA garment averts synthetic waste and supports regenerative farmers.</p>
            <div class="calculator-box">
              <label for="garment-slider" class="form-label">Select number of ethical garments purchased:</label>
              <input type="range" id="garment-slider" min="1" max="10" value="3" class="slider" aria-valuemin="1" aria-valuemax="10" aria-valuenow="3">
              <div class="calc-output" aria-live="polite">
                <div class="calc-metric">
                  <span class="calc-num" id="water-saved">4,800</span>
                  <span class="calc-unit">Liters of Clean Water Saved</span>
                </div>
                <div class="calc-metric">
                  <span class="calc-num" id="carbon-saved">18.6</span>
                  <span class="calc-unit">kg CO₂ Emissions Avoided</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Newsletter Section -->
    <section id="newsletter" class="newsletter-section" aria-labelledby="newsletter-title">
      <div class="container newsletter-container">
        <h2 id="newsletter-title">Join the Circular Fashion Movement</h2>
        <p>Subscribe for transparency reports, seasonal release invitations, and ethical styling essays.</p>
        <form id="newsletter-form" class="newsletter-form" novalidate>
          <div class="input-group">
            <label for="email-input" class="sr-only">Email address</label>
            <input type="email" id="email-input" class="form-input" placeholder="Enter your email address" required aria-required="true">
            <button type="submit" class="btn btn-primary">Subscribe</button>
          </div>
          <div id="form-message" class="form-message" role="status" aria-live="polite"></div>
          <p class="privacy-note">We respect your privacy. Unsubscribe anytime with one click. No spam ever.</p>
        </form>
      </div>
    </section>
  </main>

  <footer class="site-footer" role="contentinfo">
    <div class="container footer-grid">
      <div class="footer-col brand-col">
        <span class="footer-logo">AURA<span>.</span></span>
        <p>Radical transparency in clothing. Designed for longevity, circularity, and human dignity.</p>
      </div>
      <div class="footer-col">
        <h4>Navigation</h4>
        <ul>
          <li><a href="#catalog">Collection</a></li>
          <li><a href="#impact">Sustainability Report</a></li>
          <li><a href="#story">Our Artisans</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Policies</h4>
        <ul>
          <li><a href="#privacy">Privacy & Data Rights</a></li>
          <li><a href="#terms">Transparent Terms</a></li>
          <li><a href="#returns">Free Circular Returns</a></li>
        </ul>
      </div>
    </div>
    <div class="container footer-bottom">
      <p>&copy; 2026 AURA Fashion Inc. All rights reserved. B-Corp Certified.</p>
    </div>
  </footer>

  <script src="script.js"></script>
</body>
</html>"""

        css = """/* Base CSS Variables & Theme */
:root {
  --color-bg: #FAF9F6;
  --color-surface: #FFFFFF;
  --color-surface-soft: #F2EFE9;
  --color-text-main: #1C2321;
  --color-text-muted: #4F5D56;
  --color-primary: #2D4F3F;
  --color-primary-hover: #1E372B;
  --color-accent: #C28C59;
  --color-border: #E2DDD5;
  --color-focus: #185ADB;
  --font-serif: "Playfair Display", Georgia, serif;
  --font-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --spacing-xs: 0.5rem;
  --spacing-sm: 1rem;
  --spacing-md: 1.5rem;
  --spacing-lg: 2.5rem;
  --spacing-xl: 4rem;
  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 20px;
  --shadow-sm: 0 2px 8px rgba(28, 35, 33, 0.05);
  --shadow-md: 0 6px 20px rgba(28, 35, 33, 0.08);
}

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: var(--font-sans);
  background-color: var(--color-bg);
  color: var(--color-text-main);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

/* Accessibility Focus States */
a:focus-visible, button:focus-visible, input:focus-visible {
  outline: 3px solid var(--color-focus);
  outline-offset: 2px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

/* Typography */
h1, h2, h3, h4 {
  font-family: var(--font-serif);
  color: var(--color-text-main);
  line-height: 1.25;
  font-weight: 600;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.5rem;
  font-size: 0.95rem;
  font-weight: 500;
  border-radius: var(--radius-sm);
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.btn-primary {
  background-color: var(--color-primary);
  color: #FFFFFF;
}
.btn-primary:hover {
  background-color: var(--color-primary-hover);
}

.btn-secondary {
  background-color: var(--color-surface-soft);
  color: var(--color-text-main);
  border-color: var(--color-border);
}
.btn-secondary:hover {
  background-color: #E6E1D8;
}

.btn-outline {
  background-color: transparent;
  color: var(--color-primary);
  border-color: var(--color-primary);
}
.btn-outline:hover {
  background-color: var(--color-primary);
  color: #FFFFFF;
}

.btn-lg {
  padding: 1rem 2rem;
  font-size: 1.05rem;
}
.btn-sm {
  padding: 0.45rem 0.9rem;
  font-size: 0.85rem;
}

/* Header & Nav */
.site-header {
  background-color: rgba(250, 249, 246, 0.92);
  backdrop-filter: blur(8px);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid var(--color-border);
}

.nav-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 76px;
}

.brand-logo {
  font-family: var(--font-serif);
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-primary);
  text-decoration: none;
  letter-spacing: 0.05em;
}
.brand-logo span {
  color: var(--color-accent);
}

.nav-list {
  display: flex;
  list-style: none;
  gap: var(--spacing-lg);
}

.nav-link {
  color: var(--color-text-main);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.95rem;
  transition: color 0.2s ease;
}
.nav-link:hover {
  color: var(--color-accent);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

/* Hero Section */
.hero-section {
  padding: var(--spacing-xl) 0;
}
.hero-grid {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: var(--spacing-xl);
  align-items: center;
}

.badge-accent {
  display: inline-block;
  background-color: #E8F0EC;
  color: var(--color-primary);
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.35rem 0.75rem;
  border-radius: 50px;
  margin-bottom: var(--spacing-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.hero-content h1 {
  font-size: 2.75rem;
  margin-bottom: var(--spacing-md);
  color: var(--color-text-main);
}
.hero-subtitle {
  font-size: 1.15rem;
  color: var(--color-text-muted);
  margin-bottom: var(--spacing-lg);
  max-width: 540px;
}
.hero-cta-group {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
}

.trust-metrics {
  display: flex;
  gap: var(--spacing-lg);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border);
}
.metric-item strong {
  display: block;
  font-size: 1.5rem;
  color: var(--color-primary);
  font-family: var(--font-serif);
}
.metric-item span {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.visual-card {
  background: var(--color-surface);
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-border);
}
.visual-placeholder {
  height: 380px;
  background: linear-gradient(135deg, #D4DFD8 0%, #B8C7BF 100%);
  border-radius: var(--radius-md);
  display: flex;
  align-items: flex-end;
  padding: var(--spacing-md);
}
.product-tag {
  background: rgba(255, 255, 255, 0.9);
  padding: 0.5rem 1rem;
  border-radius: 50px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-primary);
}

/* Catalog Section */
.catalog-section {
  padding: var(--spacing-xl) 0;
  background-color: var(--color-surface);
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
}
.section-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}
.section-header h2 {
  font-size: 2.25rem;
  margin-bottom: var(--spacing-xs);
}
.section-desc {
  color: var(--color-text-muted);
  margin-bottom: var(--spacing-md);
}

.filter-bar {
  display: flex;
  justify-content: center;
  gap: var(--spacing-xs);
}
.filter-btn {
  background: var(--color-surface-soft);
  border: 1px solid var(--color-border);
  padding: 0.4rem 1rem;
  border-radius: 50px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}
.filter-btn.active, .filter-btn:hover {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-lg);
}
.product-card {
  background: var(--color-bg);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}
.product-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.product-image-box {
  position: relative;
  height: 240px;
}
.product-placeholder {
  width: 100%;
  height: 100%;
}
.img-1 { background: linear-gradient(135deg, #CFD8D3 0%, #9EB0A7 100%); }
.img-2 { background: linear-gradient(135deg, #E6DDD0 0%, #C9BDB0 100%); }
.img-3 { background: linear-gradient(135deg, #D0D8E0 0%, #A8B5C2 100%); }

.card-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(255,255,255,0.92);
  padding: 0.25rem 0.6rem;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-primary);
}

.product-info {
  padding: var(--spacing-md);
}
.product-category {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--color-accent);
  font-weight: 600;
  letter-spacing: 0.05em;
}
.product-name {
  font-size: 1.25rem;
  margin: 0.25rem 0 0.5rem;
}
.product-desc {
  font-size: 0.88rem;
  color: var(--color-text-muted);
  margin-bottom: var(--spacing-md);
}
.product-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.price {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--color-text-main);
}

/* Impact Calculator */
.impact-section {
  padding: var(--spacing-xl) 0;
}
.impact-card {
  background: var(--color-primary);
  color: #FFFFFF;
  padding: var(--spacing-xl);
  border-radius: var(--radius-lg);
}
.impact-card h2 {
  color: #FFFFFF;
  margin-bottom: var(--spacing-xs);
}
.calculator-box {
  margin-top: var(--spacing-lg);
  background: rgba(255,255,255,0.08);
  padding: var(--spacing-lg);
  border-radius: var(--radius-md);
}
.form-label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-weight: 500;
}
.slider {
  width: 100%;
  margin-bottom: var(--spacing-md);
  accent-color: var(--color-accent);
}
.calc-output {
  display: flex;
  gap: var(--spacing-xl);
}
.calc-metric .calc-num {
  display: block;
  font-size: 2.25rem;
  font-family: var(--font-serif);
  font-weight: 700;
  color: var(--color-accent);
}
.calc-metric .calc-unit {
  font-size: 0.9rem;
  color: rgba(255,255,255,0.85);
}

/* Newsletter Section */
.newsletter-section {
  padding: var(--spacing-xl) 0;
  background-color: var(--color-surface-soft);
  text-align: center;
}
.newsletter-container {
  max-width: 600px;
}
.newsletter-section h2 {
  font-size: 2rem;
  margin-bottom: var(--spacing-xs);
}
.newsletter-section p {
  color: var(--color-text-muted);
  margin-bottom: var(--spacing-md);
}
.newsletter-form .input-group {
  display: flex;
  gap: var(--spacing-xs);
}
.form-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  font-family: var(--font-sans);
}
.privacy-note {
  font-size: 0.8rem !important;
  color: var(--color-text-muted);
  margin-top: var(--spacing-xs);
}
.form-message {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
}

/* Footer */
.site-footer {
  background: #151A18;
  color: #D2D8D5;
  padding: var(--spacing-xl) 0 var(--spacing-md);
}
.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: var(--spacing-xl);
  margin-bottom: var(--spacing-lg);
}
.footer-logo {
  font-family: var(--font-serif);
  font-size: 1.5rem;
  color: #FFF;
  font-weight: 700;
  display: block;
  margin-bottom: var(--spacing-xs);
}
.footer-logo span { color: var(--color-accent); }
.footer-col h4 {
  color: #FFF;
  font-size: 1rem;
  margin-bottom: var(--spacing-sm);
}
.footer-col ul {
  list-style: none;
}
.footer-col ul li {
  margin-bottom: 0.4rem;
}
.footer-col a {
  color: #A3AFA8;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;
}
.footer-col a:hover { color: #FFF; }
.footer-bottom {
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: var(--spacing-md);
  font-size: 0.85rem;
  text-align: center;
  color: #7E8C84;
}

/* Responsive */
@media (max-width: 768px) {
  .hero-grid { grid-template-columns: 1fr; }
  .calc-output { flex-direction: column; gap: var(--spacing-sm); }
  .newsletter-form .input-group { flex-direction: column; }
  .footer-grid { grid-template-columns: 1fr; }
}
"""

        js = """// AURA Interactive Experience
document.addEventListener('DOMContentLoaded', () => {
  // 1. Shopping Cart Simulation
  let cartCount = 0;
  const cartBadge = document.getElementById('cart-count');
  const addButtons = document.querySelectorAll('.add-to-cart');

  addButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      cartCount++;
      if (cartBadge) cartBadge.textContent = cartCount;
      const originalText = btn.textContent;
      btn.textContent = 'Added ✓';
      btn.classList.add('btn-primary');
      btn.classList.remove('btn-outline');
      setTimeout(() => {
        btn.textContent = originalText;
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline');
      }, 1200);
    });
  });

  // 2. Interactive Impact Calculator
  const slider = document.getElementById('garment-slider');
  const waterOutput = document.getElementById('water-saved');
  const carbonOutput = document.getElementById('carbon-saved');

  if (slider && waterOutput && carbonOutput) {
    slider.addEventListener('input', (e) => {
      const val = parseInt(e.target.value, 10);
      slider.setAttribute('aria-valuenow', val);
      const waterSaved = (val * 1600).toLocaleString();
      const carbonSaved = (val * 6.2).toFixed(1);
      waterOutput.textContent = waterSaved;
      carbonOutput.textContent = carbonSaved;
    });
  }

  // 3. Category Filter
  const filterBtns = document.querySelectorAll('.filter-btn');
  const productCards = document.querySelectorAll('.product-card');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const category = btn.getAttribute('data-filter');

      productCards.forEach(card => {
        if (category === 'all' || card.getAttribute('data-category') === category) {
          card.style.display = 'block';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });

  // 4. Newsletter Form Validation
  const form = document.getElementById('newsletter-form');
  const emailInput = document.getElementById('email-input');
  const messageBox = document.getElementById('form-message');

  if (form && emailInput && messageBox) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = emailInput.value.trim();
      const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;

      if (!emailRegex.test(email)) {
        messageBox.textContent = 'Please enter a valid email address.';
        messageBox.style.color = '#D32F2F';
      } else {
        messageBox.textContent = 'Thank you for joining our circular community!';
        messageBox.style.color = '#2D4F3F';
        emailInput.value = '';
      }
    });
  }
});
"""

        return {
            "html": html,
            "css": css,
            "javascript": js,
            "component_structure": [
                {"name": "Header", "role": "Navigation & Brand Identity", "tag": "header"},
                {"name": "Hero", "role": "Value Proposition & Primary CTAs", "tag": "section"},
                {"name": "Catalog", "role": "Featured Product Showcase & Filtering", "tag": "section"},
                {"name": "ImpactCalculator", "role": "Interactive Sustainability Proof", "tag": "section"},
                {"name": "Newsletter", "role": "Community Lead Capture", "tag": "section"},
                {"name": "Footer", "role": "Policies & Secondary Navigation", "tag": "footer"}
            ],
            "metadata": {
                "title": "AURA | Sustainable Ethical Fashion",
                "framework": "Vanilla HTML5/CSS3/ES6",
                "responsive": True,
                "color_scheme": "Earth Tones (Sage, Sand, Charcoal)"
            },
            "design_rationale": "Constructed an editorial aesthetic emphasizing sustainability through organic earth tones, serif headlines, clear micro-interactions, full keyboard accessibility, and zero coercive patterns."
        }

    def _mock_aesthetic_agent(self, text: str) -> Dict[str, Any]:
        return {
            "score": 8.4,
            "issues": [
                "Hero section visual weight could balance slightly more symmetrically on wide desktop screens",
                "Product card border contrast could be slightly crispier against off-white background"
            ],
            "severity": ["low", "low"],
            "evidence": [
                ".hero-grid currently uses 1.2fr to 0.8fr column ratio",
                "--color-border uses #E2DDD5 against #FAF9F6 surface"
            ],
            "recommendations": [
                "Refine hero visual alignment to maintain focal hierarchy on ultra-wide viewports",
                "Enhance card border subtlety with refined box shadow"
            ]
        }

    def _mock_accessibility_agent(self, text: str) -> Dict[str, Any]:
        return {
            "score": 8.6,
            "wcag_issues": [
                "Ensure all placeholder icons have explicit aria-hidden or semantic text descriptions",
                "Form feedback element needs aria-live='polite' confirmation"
            ],
            "critical_issues": [],
            "recommendations": [
                "Add explicit aria-live attributes to dynamic calculator outputs",
                "Maintain contrast ratio of at least 4.5:1 across all muted text"
            ]
        }

    def _mock_usability_agent(self, text: str) -> Dict[str, Any]:
        return {
            "score": 8.5,
            "issues": [
                "Cart button click provides subtle feedback but would benefit from badge pulse animation",
                "Product filter buttons could feature active state counter"
            ],
            "severity": ["low", "low"],
            "evidence": [
                "Shopping cart counter increments instantly without micro-interaction animation",
                "Filter bar button list does not display count of matching products"
            ],
            "recommendations": [
                "Add micro-animation keyframes on cart badge increment",
                "Ensure smooth scrolling on anchor link navigation"
            ]
        }

    def _mock_ethics_agent(self, text: str) -> Dict[str, Any]:
        return {
            "score": 9.5,
            "dark_patterns_detected": [],
            "risk_level": "low",
            "evidence": [
                "No deceptive urgency timers or countdown clocks present",
                "No pre-checked newsletter opt-ins or confirm-shaming copy",
                "Clear return policy links and transparent pricing disclosures"
            ],
            "recommendations": [
                "Maintain explicit one-click unsubscribe notice in newsletter disclosure"
            ]
        }

    def _mock_originality_agent(self, text: str) -> Dict[str, Any]:
        return {
            "score": 8.2,
            "issues": [
                "Catalog grid follows standard 3-column e-commerce pattern",
                "Hero section layout is familiar across modern DTC brands"
            ],
            "severity": ["medium", "low"],
            "evidence": [
                "Standard 3-column CSS grid layout for product cards",
                "Split-hero composition with left text and right image"
            ],
            "recommendations": [
                "Incorporate unique botanical texture accents or asymmetrical editorial spacing",
                "Elevate impact calculator presentation with interactive visual gauges"
            ]
        }

    def _mock_general_critic_agent(self, text: str) -> Dict[str, Any]:
        return {
            "score": 8.0,
            "overall_feedback": "The website presents a clean and modern design with good brand alignment. General improvements are needed across visual polish, contrast, and interactive feedback.",
            "issues": [
                "Visual contrast on secondary text could be improved",
                "Cart micro-interactions are minimal",
                "Layout follows conventional template patterns"
            ],
            "recommendations": [
                "Increase text contrast",
                "Add interactive polish",
                "Add distinctive visual accents"
            ]
        }

    def _mock_aggregator_agent(self, text: str) -> Dict[str, Any]:
        return {
            "priority_issues": [
                "Enhance micro-interaction feedback on cart badge updates and slider adjustments",
                "Refine contrast on secondary muted elements to exceed WCAG 2.1 AA benchmarks",
                "Infuse distinctive botanical accent styling into hero and product cards"
            ],
            "blocking_issues": [],
            "conflicts": [
                {
                    "issue": "Aesthetic preference for ultra-minimal muted border vs Accessibility requirement for clear boundary definition",
                    "resolution": "Adopt crisp 1px solid border with subtle #D8D2C6 tone paired with 4px soft ambient shadow to satisfy both aesthetics and visual boundary clarity."
                }
            ],
            "recommended_changes": [
                "Add smooth CSS transitions and keyframe animations for cart updates",
                "Add aria-live attributes and accessible labels to dynamic metrics",
                "Refine hero typography scale and asymmetrical visual element"
            ],
            "preserve": [
                "High-contrast color scheme (Sage green, Sand, Charcoal)",
                "Transparent ethical disclosures and zero dark patterns",
                "Semantic HTML5 structure and clean modular CSS architecture"
            ],
            "refinement_strategy": "Surgically polish typography hierarchy, elevate interactive micro-animations, and strengthen visual distinctness while safeguarding accessibility and ethical standards.",
            "target_scores": {
                "aesthetic": 8.8,
                "accessibility": 9.0,
                "usability": 8.9,
                "ethics": 9.5,
                "originality": 8.5
            }
        }

    def _mock_refiner_agent(self, text: str) -> Dict[str, Any]:
        # Generator base output with targeted refinements
        base = self._mock_web_generator(text)
        
        # Add micro-animation enhancements to CSS
        enhanced_css = base["css"] + """
/* Refined Micro-Animations & Accessibility Polish */
@keyframes cartPulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.25); background-color: var(--color-accent); color: #fff; }
  100% { transform: scale(1); }
}

#cart-count.pulse {
  animation: cartPulse 0.4s ease-in-out;
  display: inline-block;
  padding: 0 4px;
  border-radius: 4px;
}

html {
  scroll-behavior: smooth;
}
"""
        # Refined JS for pulse animation
        enhanced_js = base["javascript"].replace(
            "if (cartBadge) cartBadge.textContent = cartCount;",
            "if (cartBadge) { cartBadge.textContent = cartCount; cartBadge.classList.remove('pulse'); void cartBadge.offsetWidth; cartBadge.classList.add('pulse'); }"
        )

        return {
            "revised_html": base["html"],
            "revised_css": enhanced_css,
            "revised_js": enhanced_js,
            "change_summary": "Refined typography rhythm, added smooth scrolling behavior, enriched cart badge pulse micro-animation, and verified WCAG AA contrast compliance across all cards.",
            "issue_mappings": [
                {
                    "issue": "Cart button click provides subtle feedback but would benefit from badge pulse animation",
                    "action_taken": "Added cartPulse keyframe CSS animation and dynamic DOM class trigger in JS",
                    "files_modified": ["styles.css", "script.js"]
                },
                {
                    "issue": "Aesthetic preference for ultra-minimal muted border vs Accessibility boundary definition",
                    "action_taken": "Harmonized border tone with subtle shadow for crisp definition without visual clutter",
                    "files_modified": ["styles.css"]
                }
            ]
        }
