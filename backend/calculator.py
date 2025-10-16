from config import Config

class PropertyFlipCalculator:
    """
    Calculate profit for property flipping with GST considerations.
    
    Formulas:
    - GST Claimable = GST on PP + RB + LE
    - GST Payable = GST on TV (sale price)
    - Gross Profit = TV - PP - RB - LE - CR - INS - COM
    - Pre-tax Profit = Gross Profit + GST Claimable - GST Payable
    - Post-tax Profit = Pre-tax Profit * (1 - TAX_RATE)
    """
    
    def __init__(self):
        self.gst_rate = Config.GST_RATE
        self.tax_rate = Config.TAX_RATE
        self.commission_rate = Config.COMMISSION_RATE
        self.min_profit = Config.MIN_PROFIT_THRESHOLD
        self.target_profit_min = Config.TARGET_PROFIT_MIN
        self.target_profit_max = Config.TARGET_PROFIT_MAX
    
    def calculate(self, pp, tv, rv=None, cv=None, ins=None, rb=None, le=None, cr=None, int_rate=None, renovation_months=None):
        """
        Calculate profit and recommendations.
        
        Args:
            pp: Purchase Price
            tv: Target Value (estimated sale price)
            rv: Rateable Value (optional)
            cv: Capital Value (optional)
            ins: Insurance cost (defaults to Config.DEFAULT_INSURANCE)
            rb: Renovation Budget (defaults to Config.DEFAULT_RENOVATION_BUDGET)
            le: Legal Expenses (defaults to Config.DEFAULT_LEGAL_EXPENSES)
            cr: Council Rates (defaults to Config.DEFAULT_COUNCIL_RATES)
            int_rate: Interest rate for financing (defaults to 7.5% annually)
            renovation_months: Duration of renovation in months (defaults to 6 months)
        
        Returns:
            dict with all calculations and recommendations
        """
        # Apply defaults
        if ins is None:
            ins = Config.DEFAULT_INSURANCE
        if rb is None:
            rb = Config.DEFAULT_RENOVATION_BUDGET
        if le is None:
            le = Config.DEFAULT_LEGAL_EXPENSES
        if cr is None:
            cr = Config.DEFAULT_COUNCIL_RATES
        if int_rate is None:
            int_rate = 0.075  # 7.5% annual interest rate
        if renovation_months is None:
            renovation_months = 6  # 6 months renovation period
        
        # Calculate commission (on sale price)
        com = tv * self.commission_rate
        
        # Calculate interest cost (INT)
        # Interest on purchase price + renovation budget during renovation period
        total_financed = pp + rb
        monthly_interest_rate = int_rate / 12
        int_cost = total_financed * monthly_interest_rate * renovation_months
        
        # GST Calculations
        # GST entity can claim GST on: purchase, renovations, legal fees
        gst_claimable = (pp + rb + le) * (self.gst_rate / (1 + self.gst_rate))
        
        # GST payable on sale (TV includes GST for registered entity)
        gst_payable = tv * (self.gst_rate / (1 + self.gst_rate))
        
        # Net GST position
        net_gst = gst_payable - gst_claimable
        
        # Profit Calculations
        gross_profit = tv - pp - rb - le - cr - ins - com - int_cost
        pre_tax_profit = gross_profit - net_gst  # Net GST reduces profit
        post_tax_profit = pre_tax_profit * (1 - self.tax_rate)
        
        # Determine if viable
        is_viable = post_tax_profit >= self.min_profit
        
        # Calculate recommended PP if not viable
        recommended_pp = None
        if not is_viable:
            # Target post-tax profit in the middle of desired range
            target_post_tax = (self.target_profit_min + self.target_profit_max) / 2
            # Work backwards to find required PP
            recommended_pp = self._calculate_recommended_pp(tv, target_post_tax, ins, rb, le, cr, int_rate, renovation_months)
        
        return {
            'pp': round(pp, 2),
            'tv': round(tv, 2),
            'rv': round(rv, 2) if rv else None,
            'cv': round(cv, 2) if cv else None,
            'ins': round(ins, 2),
            'rb': round(rb, 2),
            'le': round(le, 2),
            'cr': round(cr, 2),
            'com': round(com, 2),
            'int_cost': round(int_cost, 2),
            'int_rate': round(int_rate * 100, 2),  # Convert to percentage
            'renovation_months': renovation_months,
            'gst_claimable': round(gst_claimable, 2),
            'gst_payable': round(gst_payable, 2),
            'net_gst': round(net_gst, 2),
            'gross_profit': round(gross_profit, 2),
            'pre_tax_profit': round(pre_tax_profit, 2),
            'post_tax_profit': round(post_tax_profit, 2),
            'is_viable': is_viable,
            'recommended_pp': round(recommended_pp, 2) if recommended_pp else None,
        }
    
    def _calculate_recommended_pp(self, tv, target_post_tax, ins, rb, le, cr, int_rate, renovation_months):
        """
        Calculate the recommended purchase price to achieve target post-tax profit.
        
        This involves solving for PP in the profit equation:
        post_tax_profit = (TV - PP - RB - LE - CR - INS - COM - INT - net_GST) * (1 - TAX_RATE)
        
        Where:
        - COM = TV * commission_rate
        - INT = (PP + RB) * monthly_interest_rate * renovation_months
        - net_GST involves PP in the calculation
        
        Simplified approach: iterative approximation
        """
        com = tv * self.commission_rate
        monthly_interest_rate = int_rate / 12
        
        # Start with a guess
        pp_guess = tv * 0.5  # Start at 50% of TV
        
        # Iterate to find optimal PP
        for _ in range(100):  # Max 100 iterations
            # Calculate interest cost for this PP guess
            total_financed = pp_guess + rb
            int_cost = total_financed * monthly_interest_rate * renovation_months
            
            gst_claimable = (pp_guess + rb + le) * (self.gst_rate / (1 + self.gst_rate))
            gst_payable = tv * (self.gst_rate / (1 + self.gst_rate))
            net_gst = gst_payable - gst_claimable
            
            gross_profit = tv - pp_guess - rb - le - cr - ins - com - int_cost
            pre_tax_profit = gross_profit - net_gst
            post_tax_profit = pre_tax_profit * (1 - self.tax_rate)
            
            # Check if we're close enough
            if abs(post_tax_profit - target_post_tax) < 100:  # Within $100
                return pp_guess
            
            # Adjust pp_guess based on difference
            diff = post_tax_profit - target_post_tax
            adjustment = diff * 0.8  # Damping factor for stability
            pp_guess = pp_guess + adjustment
            
            # Ensure PP stays positive and reasonable
            if pp_guess < 0:
                pp_guess = tv * 0.1
            elif pp_guess > tv:
                pp_guess = tv * 0.9
        
        return pp_guess

