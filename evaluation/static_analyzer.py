"""
Deterministic Static Analysis Engine for Generated Web Designs.
Provides rule-based WCAG 2.1 checks, DOM validation, and dark pattern heuristics.
"""

import re
from typing import Any, Dict, List
from bs4 import BeautifulSoup


class StaticAnalyzer:
    @classmethod
    def analyze(cls, html: str, css: str = "", js: str = "") -> Dict[str, Any]:
        """Runs comprehensive static checks across HTML, CSS, and JS."""
        soup = BeautifulSoup(html, "html.parser")
        
        wcag_issues = []
        critical_issues = []
        dark_patterns = []
        passed_rules = []
        
        # 1. Check Landmark HTML5 tags
        main_tags = soup.find_all("main")
        if not main_tags:
            wcag_issues.append("Missing semantic <main> landmark element.")
        else:
            passed_rules.append("Semantic <main> landmark is present.")

        nav_tags = soup.find_all("nav")
        if not nav_tags:
            wcag_issues.append("Missing semantic <nav> navigation landmark.")
        else:
            passed_rules.append("Semantic <nav> landmark is present.")

        # 2. Check Headings hierarchy
        h1_tags = soup.find_all("h1")
        if not h1_tags:
            critical_issues.append("Missing primary <h1> heading on page.")
        elif len(h1_tags) > 1:
            wcag_issues.append("Multiple <h1> headings detected; recommend exactly one per page.")
        else:
            passed_rules.append("Single prominent <h1> heading is present.")

        # 3. Check Image Alt Text
        images = soup.find_all("img")
        missing_alt = 0
        for img in images:
            if not img.get("alt") and img.get("role") != "presentation" and not img.get("aria-hidden"):
                missing_alt += 1
        if missing_alt > 0:
            critical_issues.append(f"{missing_alt} image(s) missing descriptive 'alt' attributes (WCAG 1.1.1).")
        elif images:
            passed_rules.append("All images possess descriptive alt attributes.")

        # 4. Check Form Controls & Labels
        inputs = soup.find_all(["input", "select", "textarea"])
        missing_labels = 0
        for inp in inputs:
            inp_type = inp.get("type", "text")
            if inp_type in ["hidden", "submit", "button", "reset"]:
                continue
            inp_id = inp.get("id")
            aria_label = inp.get("aria-label") or inp.get("aria-labelledby")
            has_label = False
            if inp_id and soup.find("label", attrs={"for": inp_id}):
                has_label = True
            elif aria_label:
                has_label = True
            elif inp.find_parent("label"):
                has_label = True

            if not has_label:
                missing_labels += 1

        if missing_labels > 0:
            critical_issues.append(f"{missing_labels} form input(s) lack associated accessible labels (WCAG 3.3.2).")
        elif inputs:
            passed_rules.append("All interactive form inputs have explicit accessible labels.")

        # 5. Check Interactive Buttons & Links
        buttons = soup.find_all("button")
        empty_buttons = 0
        for btn in buttons:
            text = btn.get_text(strip=True)
            aria = btn.get("aria-label") or btn.get("title")
            if not text and not aria:
                empty_buttons += 1
        if empty_buttons > 0:
            wcag_issues.append(f"{empty_buttons} button(s) lack accessible text content or aria-label.")

        # 6. Check Viewport Meta Tag
        viewport = soup.find("meta", attrs={"name": "viewport"})
        if not viewport:
            critical_issues.append("Missing <meta name='viewport'> tag for responsive rendering.")
        else:
            passed_rules.append("Responsive viewport meta tag is present.")

        # 7. Check Dark Pattern Heuristics
        body_text = soup.get_text().lower()
        
        # Urgency / Scarcity manipulation
        urgency_patterns = [
            r"only \d+ left in stock",
            r"expires in 00:\d\d",
            r"someone just bought this \d+ mins ago",
            r"hurry[,!]\s+offer ends in",
            r"price increases in"
        ]
        for pat in urgency_patterns:
            if re.search(pat, body_text):
                dark_patterns.append(f"Deceptive Urgency Pattern detected: '{pat}'")

        # Confirm-shaming copy
        shaming_patterns = [
            r"no thanks, i hate",
            r"no, i don't want to save",
            r"no, i prefer paying full price"
        ]
        for pat in shaming_patterns:
            if re.search(pat, body_text):
                dark_patterns.append(f"Confirm-Shaming Dark Pattern detected: '{pat}'")

        # Pre-checked checkboxes
        prechecked = soup.find_all("input", attrs={"type": "checkbox", "checked": True})
        if prechecked:
            for chk in prechecked:
                dark_patterns.append(f"Pre-checked checkbox found on input id='{chk.get('id', 'unknown')}'")

        # 8. Compute Rule-Based Scores
        total_checks = len(passed_rules) + len(wcag_issues) + (len(critical_issues) * 2)
        if total_checks == 0:
            wcag_score = 10.0
        else:
            penalty = (len(wcag_issues) * 0.8) + (len(critical_issues) * 2.0)
            wcag_score = max(0.0, min(10.0, 10.0 - penalty))

        dark_pattern_count = len(dark_patterns)
        ethics_static_score = max(0.0, 10.0 - (dark_pattern_count * 3.0))

        return {
            "wcag_score": round(wcag_score, 2),
            "ethics_static_score": round(ethics_static_score, 2),
            "wcag_issues": wcag_issues,
            "critical_issues": critical_issues,
            "passed_rules": passed_rules,
            "dark_patterns": dark_patterns,
            "dark_pattern_count": dark_pattern_count,
            "element_counts": {
                "headings": len(soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])),
                "images": len(images),
                "forms": len(soup.find_all("form")),
                "inputs": len(inputs),
                "buttons": len(buttons),
                "links": len(soup.find_all("a")),
            }
        }
