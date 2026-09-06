"""
Unit tests for deterministic Static Analysis Engine.
"""

from evaluation.static_analyzer import StaticAnalyzer


def test_static_analyzer_wcag_and_landmarks():
    # Good accessible HTML
    good_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Test</title></head>
    <body>
      <header role="banner"><nav role="navigation"><a href="#home">Home</a></nav></header>
      <main role="main">
        <h1>Accessible Heading</h1>
        <img src="test.jpg" alt="Descriptive test image">
        <form>
          <label for="uname">Username</label>
          <input type="text" id="uname">
          <button type="submit">Submit</button>
        </form>
      </main>
      <footer role="contentinfo"><p>Footer</p></footer>
    </body>
    </html>
    """
    res = StaticAnalyzer.analyze(good_html)
    assert res["wcag_score"] >= 9.0
    assert len(res["critical_issues"]) == 0
    assert res["dark_pattern_count"] == 0


def test_static_analyzer_detects_dark_patterns_and_missing_alt():
    # Flawed HTML with deceptive urgency and missing alt
    bad_html = """
    <!DOCTYPE html>
    <html>
    <body>
      <h2>Skipped H1</h2>
      <img src="banner.jpg">
      <div>Hurry! Offer ends in 00:05 minutes! Only 2 left in stock!</div>
      <input type="checkbox" id="subscribe" checked>
    </body>
    </html>
    """
    res = StaticAnalyzer.analyze(bad_html)
    assert res["wcag_score"] < 8.0
    assert res["dark_pattern_count"] >= 2
    assert any("missing descriptive 'alt'" in issue for issue in res["critical_issues"])
    assert any("Missing primary <h1>" in issue for issue in res["critical_issues"])
