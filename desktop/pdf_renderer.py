import os
from typing import Dict, Any


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>RealFlip Analysis Report</title>
    <style>
      body { font-family: Arial, Helvetica, sans-serif; color: #222; }
      h1 { margin-bottom: 4px; }
      h2 { margin-top: 28px; border-bottom: 1px solid #ddd; padding-bottom: 4px; }
      table { width: 100%; border-collapse: collapse; margin-top: 8px; }
      th, td { border: 1px solid #eee; padding: 6px 8px; font-size: 12px; }
      th { background: #f7f7f7; text-align: left; }
      .summary { background: #f1f9ff; border: 1px solid #d7ecff; padding: 8px; }
    </style>
  </head>
  <body>
    <h1>RealFlip Analysis Report</h1>
    <div class="summary">
      <div>Generated: {{ timestamp }}</div>
      <div>Total Properties: {{ count }}</div>
    </div>

    {% for item in results %}
    <h2>{{ loop.index }}. {{ item.property.address }}</h2>
    <table>
      <tr><th>Score</th><td>{{ item.analysis.score or 'N/A' }}</td></tr>
      <tr><th>Notes</th><td>{{ item.analysis.notes or '—' }}</td></tr>
      {% if item.analysis.connection_data and item.analysis.connection_data.property_valuation %}
      <tr><th>Current Valuation</th><td>{{ item.analysis.connection_data.property_valuation.current_valuation or 'N/A' }}</td></tr>
      {% endif %}
      {% if item.property.trademe_url %}
      <tr><th>TradeMe URL</th><td>{{ item.property.trademe_url }}</td></tr>
      {% endif %}
    </table>
    {% endfor %}
  </body>
  </html>
"""


def render_html(payload: Dict[str, Any]) -> str:
    """Render HTML string from the results payload using a minimal inline template.
    We avoid external template engines to keep dependencies minimal.
    """
    from jinja2 import Template  # lightweight and common

    template = Template(HTML_TEMPLATE)
    return template.render(**payload)


def html_to_pdf(html: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    # Prefer WeasyPrint if available; otherwise, fall back to a simple HTML save
    try:
        from weasyprint import HTML  # type: ignore
        path = os.path.join(output_dir, "Analysis.pdf")
        HTML(string=html).write_pdf(path)
        return path
    except Exception:
        # Fallback: save the HTML so user still gets an artifact
        path = os.path.join(output_dir, "Analysis.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        return path


class PDFRenderer:
    """PDF renderer for desktop app."""
    
    def __init__(self):
        pass
        
    def render_html_to_pdf(self, html: str, output_path: str) -> bool:
        """Render HTML to PDF file."""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            # Try WeasyPrint first
            try:
                from weasyprint import HTML
                HTML(string=html).write_pdf(output_path)
                return True
            except ImportError:
                # Fallback to HTML file
                html_path = output_path.replace('.pdf', '.html')
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                return False
        except Exception as e:
            print(f"PDF rendering failed: {e}")
            return False
            
    def render_results_to_pdf(self, results: Dict[str, Any], output_dir: str) -> str:
        """Render analysis results to PDF."""
        try:
            import datetime as dt
            
            # Generate HTML
            html = render_html(results)
            
            # Create timestamped filename
            ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_path = os.path.join(output_dir, f"Analysis_{ts}.pdf")
            
            # Convert to PDF
            success = self.render_html_to_pdf(html, pdf_path)
            
            if success:
                return pdf_path
            else:
                # Return HTML path if PDF failed
                return pdf_path.replace('.pdf', '.html')
                
        except Exception as e:
            print(f"Results rendering failed: {e}")
            return ""


