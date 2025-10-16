from typing import Tuple
from .models import DataPoints, ScoringBreakdown
import os
from datetime import datetime

def generate_scoring_html_report(dp: DataPoints, score: float, notes: str, breakdown: ScoringBreakdown, debug_data: dict) -> str:
    """Generate HTML report with all scoring calculations and explanations"""
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RealFlip Scoring Analysis - {dp.address}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
        }}
        .header .timestamp {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        .score-summary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
        }}
        .score-summary .final-score {{
            font-size: 4em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .score-summary .score-label {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .section {{
            margin-bottom: 30px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
        }}
        .section-header {{
            background: #34495e;
            color: white;
            padding: 15px 20px;
            font-size: 1.3em;
            font-weight: bold;
        }}
        .section-content {{
            padding: 20px;
        }}
        .variable-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .variable-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }}
        .variable-name {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        .variable-value {{
            font-size: 1.1em;
            color: #27ae60;
            font-weight: bold;
        }}
        .variable-description {{
            font-size: 0.9em;
            color: #7f8c8d;
            margin-top: 5px;
        }}
        .calculation-step {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
        }}
        .calculation-step .step-title {{
            font-weight: bold;
            color: #856404;
            margin-bottom: 8px;
        }}
        .calculation-step .step-formula {{
            font-family: 'Courier New', monospace;
            background: #f8f9fa;
            padding: 8px;
            border-radius: 3px;
            margin: 5px 0;
        }}
        .breakdown-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            margin: 8px 0;
            background: #f8f9fa;
            border-radius: 5px;
            border-left: 4px solid #e74c3c;
        }}
        .breakdown-item .criteria {{
            font-weight: bold;
            color: #2c3e50;
        }}
        .breakdown-item .score {{
            font-size: 1.2em;
            font-weight: bold;
            color: #27ae60;
        }}
        .notes {{
            background: #e8f4f8;
            border: 1px solid #bee5eb;
            border-radius: 5px;
            padding: 15px;
            margin-top: 20px;
        }}
        .notes h3 {{
            color: #0c5460;
            margin-top: 0;
        }}
        .highlight {{
            background: #fff3cd;
            padding: 2px 6px;
            border-radius: 3px;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 RealFlip Scoring Analysis</h1>
            <div class="timestamp">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="score-summary">
            <div class="final-score">{score:.1f}/10.0</div>
            <div class="score-label">Overall Viability Score</div>
            <div style="margin-top: 15px; font-size: 1.1em;">Property: {dp.address}</div>
        </div>
        
        <div class="section">
            <div class="section-header">📊 Input Variables & Data Points</div>
            <div class="section-content">
                <div class="variable-grid">
                    <div class="variable-item">
                        <div class="variable-name">Purchase Price</div>
                        <div class="variable-value">{f'${dp.est_purchase_price:,.0f}' if dp.est_purchase_price else 'N/A'}</div>
                        <div class="variable-description">Estimated purchase price of the property</div>
                    </div>
                    <div class="variable-item">
                        <div class="variable-name">Rehab Cost</div>
                        <div class="variable-value">{f'${dp.est_rehab_cost:,.0f}' if dp.est_rehab_cost else 'N/A'}</div>
                        <div class="variable-description">Estimated renovation/repair costs</div>
                    </div>
                    <div class="variable-item">
                        <div class="variable-name">After Repair Value (ARV)</div>
                        <div class="variable-value">{f'${dp.est_after_repair_value:,.0f}' if dp.est_after_repair_value else 'N/A'}</div>
                        <div class="variable-description">Estimated value after renovations</div>
                    </div>
                    <div class="variable-item">
                        <div class="variable-name">Days on Market</div>
                        <div class="variable-value">{dp.days_on_market_avg if dp.days_on_market_avg is not None else 'N/A'}</div>
                        <div class="variable-description">Average days properties stay on market</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-header">🧮 Profit Margin Calculation (60% of total score)</div>
            <div class="section-content">
                <div class="calculation-step">
                    <div class="step-title">Step 1: Calculate Total Investment</div>
                    <div class="step-formula">Total Cost = Purchase Price + Rehab Cost</div>
                    <div class="step-formula">Total Cost = {f'${dp.est_purchase_price:,.0f}' if dp.est_purchase_price else 'N/A'} + {f'${dp.est_rehab_cost:,.0f}' if dp.est_rehab_cost else 'N/A'} = {f'${debug_data.get("total_cost", 0):,.0f}' if debug_data.get('total_cost') else 'N/A'}</div>
                </div>
                
                <div class="calculation-step">
                    <div class="step-title">Step 2: Calculate Net Sale Proceeds</div>
                    <div class="step-formula">Net Sale = ARV × (1 - Transaction Costs)</div>
                    <div class="step-formula">Net Sale = {f'${dp.est_after_repair_value:,.0f}' if dp.est_after_repair_value else 'N/A'} × 0.94 = {f'${debug_data.get("net_sale", 0):,.0f}' if debug_data.get('net_sale') else 'N/A'}</div>
                    <div class="variable-description">Transaction costs in NZ are typically 6% (legal, agent fees, etc.)</div>
                </div>
                
                <div class="calculation-step">
                    <div class="step-title">Step 3: Calculate Profit</div>
                    <div class="step-formula">Profit = Net Sale - Total Cost</div>
                    <div class="step-formula">Profit = {f'${debug_data.get("net_sale", 0):,.0f}' if debug_data.get('net_sale') else 'N/A'} - {f'${debug_data.get("total_cost", 0):,.0f}' if debug_data.get('total_cost') else 'N/A'} = {f'${debug_data.get("profit", 0):,.0f}' if debug_data.get('profit') else 'N/A'}</div>
                </div>
                
                <div class="calculation-step">
                    <div class="step-title">Step 4: Calculate Profit Margin</div>
                    <div class="step-formula">Margin Ratio = Profit ÷ Total Cost</div>
                    <div class="step-formula">Margin Ratio = {f'${debug_data.get("profit", 0):,.0f}' if debug_data.get('profit') else 'N/A'} ÷ {f'${debug_data.get("total_cost", 0):,.0f}' if debug_data.get('total_cost') else 'N/A'} = {f'{debug_data.get("margin_ratio", 0):.1%}' if debug_data.get('margin_ratio') else 'N/A'}</div>
                </div>
                
                <div class="calculation-step">
                    <div class="step-title">Step 5: Score Assignment</div>
                    <div class="step-formula">If margin ≥ 20%: Full 6.0 points</div>
                    <div class="step-formula">If margin < 20%: Proportional scoring (6.0 × margin ÷ 0.20)</div>
                    <div class="step-formula">Score = {f'{breakdown.margin_score:.1f}' if breakdown.margin_score is not None else 'N/A'} points</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-header">📈 Scoring Breakdown by Criteria</div>
            <div class="section-content">
                <div class="breakdown-item">
                    <div class="criteria">💰 Profit Margin</div>
                    <div class="score">{f'{breakdown.margin_score:.1f}' if breakdown.margin_score is not None else 'N/A'}/6.0</div>
                </div>
                <div class="breakdown-item">
                    <div class="criteria">⏱️ Days on Market</div>
                    <div class="score">{f'{breakdown.dom_score:.1f}' if breakdown.dom_score is not None else 'N/A'}/1.5</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-header">📝 Detailed Scoring Logic</div>
            <div class="section-content">
                <div class="calculation-step">
                    <div class="step-title">Days on Market Scoring</div>
                    <div class="step-formula">≤ 15 days: 1.5 points (fast market)</div>
                    <div class="step-formula">15-90 days: Linear scaling</div>
                    <div class="step-formula">≥ 90 days: 0 points (slow market)</div>
                    <div class="variable-description">{breakdown.dom_details or 'No data available'}</div>
                </div>
            </div>
        </div>
        
        <div class="notes">
            <h3>📋 Analysis Notes</h3>
            <p><strong>Overall Assessment:</strong> {notes}</p>
            <p><strong>Key Insights:</strong></p>
            <ul>
                <li>Profit margin of <span class="highlight">{f'{debug_data.get("margin_ratio", 0):.1%}' if debug_data.get('margin_ratio') else 'N/A'}</span> {'exceeds' if debug_data.get('margin_ratio', 0) >= 0.20 else 'is below'} the 20% threshold for optimal returns</li>
                <li>Total investment required: <span class="highlight">{f'${debug_data.get("total_cost", 0):,.0f}' if debug_data.get('total_cost') else 'N/A'}</span></li>
                <li>Expected profit: <span class="highlight">{f'${debug_data.get("profit", 0):,.0f}' if debug_data.get('profit') else 'N/A'}</span></li>
                <li>This property {'meets' if score >= 7.0 else 'does not meet'} the criteria for a high-viability flip (≥7.0 score)</li>
            </ul>
        </div>
    </div>
</body>
</html>
    """
    
    return html_content

def score_datapoints(dp: DataPoints) -> Tuple[float, str, ScoringBreakdown]:
    """
    Score datapoints for New Zealand real estate flip viability.
    Enhanced with NZ-specific factors and market conditions.
    """
    subs = []
    score = 0.0
    breakdown = ScoringBreakdown()
    debug_data = {}  # Store all debug information

    if dp.est_purchase_price and dp.est_rehab_cost and dp.est_after_repair_value:
        total_cost = dp.est_purchase_price + dp.est_rehab_cost
        # NZ market typically has lower transaction costs than US (around 4-6%)
        net_sale = dp.est_after_repair_value * 0.94
        profit = net_sale - total_cost
        
        # Store debug data
        debug_data.update({
            'total_cost': total_cost,
            'net_sale': net_sale,
            'profit': profit
        })
        
        print(f"🔍 DEBUG SCORING: est_purchase_price = {dp.est_purchase_price}")
        print(f"🔍 DEBUG SCORING: est_rehab_cost = {dp.est_rehab_cost}")
        print(f"🔍 DEBUG SCORING: est_after_repair_value = {dp.est_after_repair_value}")
        print(f"🔍 DEBUG SCORING: total_cost = {total_cost}")
        print(f"🔍 DEBUG SCORING: net_sale = {net_sale}")
        print(f"🔍 DEBUG SCORING: profit = {profit}")
        if total_cost > 0:
            margin_ratio = profit / total_cost
            debug_data['margin_ratio'] = margin_ratio
            print(f"🔍 DEBUG SCORING: margin_ratio = {margin_ratio}")
            # NZ market typically requires lower margins due to different market dynamics
            if margin_ratio <= 0:
                sub = 0.0
            elif margin_ratio >= 0.20:  # Lower threshold for NZ market
                sub = 6.0
            else:
                sub = 6.0 * (margin_ratio / 0.20)
            score += sub
            subs.append(f"Margin {margin_ratio:.1%} -> {sub:.1f}")
            breakdown.margin_score = sub
            breakdown.margin_details = f"Profit margin: {margin_ratio:.1%}, Total cost: ${total_cost:,.0f}, Net sale: ${net_sale:,.0f}"
        else:
            subs.append("No cost basis")
            breakdown.margin_details = "No cost basis available"
    else:
        subs.append("Missing price/rehab/ARV")
        breakdown.margin_details = "Missing price, rehab cost, or ARV data"

    if dp.days_on_market_avg is not None:
        dom = dp.days_on_market_avg
        # NZ market typically moves faster than US market
        if dom <= 15:  # Faster threshold for NZ
            sub = 1.5
        elif dom >= 90:  # Shorter maximum for NZ
            sub = 0.0
        else:
            sub = 1.5 * (1 - (dom - 15) / 75)
        final_dom_score = max(0.0, min(1.5, sub))
        score += final_dom_score
        subs.append(f"DOM {dom} -> {final_dom_score:.1f}")
        breakdown.dom_score = final_dom_score
        breakdown.dom_details = f"Days on market: {dom} days (NZ market threshold: 15-90 days)"
    else:
        subs.append("Missing DOM")
        breakdown.dom_details = "Missing days on market data"

    final_score = round(min(10.0, max(0.0, score)), 1)
    notes = "; ".join(subs)
    
    # Generate HTML report (temporarily disabled to fix errors)
    try:
        html_report = generate_scoring_html_report(dp, final_score, notes, breakdown, debug_data)
        
        # Save HTML report to file
        safe_address = "".join(c for c in dp.address if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_address = safe_address.replace(' ', '_')[:50]  # Limit length
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"scoring_report_{safe_address}_{timestamp}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_report)
        print(f"📄 HTML scoring report saved: {filename}")
    except Exception as e:
        print(f"❌ Error generating HTML report: {e}")
        # Continue without HTML report
    
    return final_score, notes, breakdown