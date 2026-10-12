import time
import logging
import re
from typing import List, Dict, Any

from app.providers.base import BaseModelProvider, ProviderResponse, ProviderHealth

logger = logging.getLogger("lenny_growth.providers.mock")

class MockProvider(BaseModelProvider):
    def __init__(self):
        self.model = "mock-deterministic-v2"

    async def health_check(self) -> ProviderHealth:
        return ProviderHealth(
            provider_name="mock",
            healthy=True,
            detail="Deterministic Mock Engine active (zero-cost, resource-efficient testing)."
        )

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1024
    ) -> ProviderResponse:
        start_time = time.perf_counter()
        
        user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                user_msg = m.get("content", "")
                break

        query = user_msg.lower()

        # 1. Ship 30 essay generation
        if "ship 30" in query or "essay" in query or "1,250" in query:
            content = self._generate_ship30_essay(user_msg, system_prompt)
        
        # 2. Interactive Artifact Requests
        elif "ice" in query and ("calculator" in query or "artifact" in query or "html" in query or "component" in query or "matrix" in query):
            content = self._generate_ice_calculator_artifact(user_msg)
        elif "pmf" in query and ("survey" in query or "dashboard" in query or "calculator" in query or "artifact" in query or "html" in query):
            content = self._generate_pmf_dashboard_artifact(user_msg)
        elif "positioning" in query and ("canvas" in query or "artifact" in query or "html" in query or "template" in query):
            content = self._generate_positioning_canvas_artifact(user_msg)
        elif "lno" in query and ("matrix" in query or "planner" in query or "artifact" in query or "html" in query):
            content = self._generate_lno_matrix_artifact(user_msg)
        elif "artifact" in query or "html" in query or "calculator" in query or "component" in query or "landing page" in query:
            content = self._generate_reverse_trial_calculator_artifact(user_msg)
        
        # 3. Topic Grounded Q&A
        elif any(k in query for k in ["elena", "verna", "plg", "freemium", "reverse trial", "pql", "product-led"]):
            content = (
                "Based on Lenny's conversation with **Elena Verna**, here is the strategic breakdown of modern B2B Product-Led Growth:\n\n"
                "### 1. The Real Definition of PLG\n"
                "Elena emphasizes that PLG is not merely a pricing trick or having a free button. It is a fundamental **organizational methodology** where product usage serves as the primary engine of user acquisition, retention, and revenue expansion.\n\n"
                "### 2. The Power of the 'Reverse Trial'\n"
                "Rather than choosing between a strict 14-day free trial (which kicks users out) and pure freemium (which under-monetizes), Elena recommends the **Reverse Trial**:\n"
                "- **Day 1–14**: New users receive full access to enterprise capabilities (SSO, advanced analytics, collaboration).\n"
                "- **Day 15+**: If they don't upgrade, they are gracefully downgraded to a generous free tier rather than being locked out. This preserves the product habit while establishing desire for enterprise features.\n\n"
                "### 3. Product-Qualified Leads (PQLs)\n"
                "Sales teams should never cold-call. A true PQL must meet two conditions:\n"
                "1. **Value Milestone**: The team has activated (e.g., created 3 boards, invited 5 peers).\n"
                "2. **Expansion Signal**: Cross-department adoption or hitting account usage thresholds."
            )
        elif any(k in query for k in ["brian", "balfour", "four fits", "reforge", "loop", "funnel", "product-channel"]):
            content = (
                "According to **Brian Balfour** (Founder of Reforge) on Lenny's Podcast:\n\n"
                "### Why Growth Loops Beat Funnels\n"
                "Traditional pirate funnels (AARRR) operate on a linear model: you spend money to buy traffic, lose users, and must pay again. Sustainable $100M+ businesses compound through **closed growth loops**, where an action taken by a current user automatically produces an output that acquires or re-engages the next user.\n\n"
                "### The Four Fits Framework\n"
                "Product-Market Fit alone is insufficient to build a venture-scale company. You need four interlocking fits:\n"
                "1. **Market-Product Fit**: Solving an urgent, high-value problem for a specific market.\n"
                "2. **Product-Channel Fit**: *Products are built to fit channels; channels do not fit products.* You must engineer your product mechanics to match the rules of SEO, viral sharing, or paid platforms.\n"
                "3. **Channel-Model Fit**: Your monetization model (ARPU) dictates your viable acquisition channels. Low ARPU requires virality/SEO; high ARPU allows enterprise sales teams.\n"
                "4. **Model-Market Fit**: Number of potential customers multiplied by ARPU must equal a $100M+ market opportunity."
            )
        elif any(k in query for k in ["casey", "winters", "marketplace", "cold start", "retention vs"]):
            content = (
                "From Lenny's episode with **Casey Winters** (former CPO at Eventbrite, Growth Lead at Pinterest & Grubhub):\n\n"
                "### 1. Acquisition is a Derivative of Retention\n"
                "Founders mistakenly believe customer acquisition is their biggest challenge. In reality, acquisition is an outcome of great retention. If your 90-day retention curve flattens, users naturally create content, word-of-mouth referrals, and viral loops that drive free acquisition.\n\n"
                "### 2. Solving the Marketplace Cold Start Problem\n"
                "In two-sided marketplaces, always constrain the geographic and category scope. Solve the **supply side first** in a dense hyper-local pocket (e.g., Grubhub signing up 15 pizza restaurants on three blocks in Chicago) before spending money on demand.\n\n"
                "### 3. Feature vs. Product vs. Company\n"
                "- **Feature**: Solves an isolated task.\n"
                "- **Product**: Solves an entire recurring workflow.\n"
                "- **Company**: Creates multi-product compound loops with enduring structural moats."
            )
        elif any(k in query for k in ["sean", "ellis", "ice", "experimentation", "hacking growth"]):
            content = (
                "According to **Sean Ellis** (Author of *Hacking Growth*) on Lenny's Podcast:\n\n"
                "### The ICE Prioritization Framework\n"
                "To rank growth experiments effectively, score each hypothesis from 1 to 10 across:\n"
                "- **Impact (1–10)**: What is the expected upside if this experiment wins?\n"
                "- **Confidence (1–10)**: How strongly is this hypothesis supported by user research or analytics data?\n"
                "- **Ease (1–10)**: How fast and low-effort is this to build and deploy?\n\n"
                "$$\\text{ICE Score} = \\frac{\\text{Impact} + \\text{Confidence} + \\text{Ease}}{3}$$\n\n"
                "### Experimentation Velocity\n"
                "The single strongest predictor of startup growth is experimentation velocity—aiming to launch 3–5 validated growth experiments every week in dedicated growth sprints."
            )
        elif any(k in query for k in ["april", "dunford", "positioning", "obviously awesome", "category", "competitive alternative"]):
            content = (
                "From Lenny's interview with **April Dunford** (Author of *Obviously Awesome*):\n\n"
                "### The 5 Interlocking Components of B2B Positioning\n"
                "Positioning is the foundational context that makes your product's unique value obvious to the right customers:\n"
                "1. **Competitive Alternatives**: What would customers use if you didn't exist? (Often Excel, pen and paper, or manual labor).\n"
                "2. **Unique Differentiated Attributes**: Specific capabilities you have that alternatives lack.\n"
                "3. **Value for Customers**: The concrete business ROI or benefit unlocked by your unique attributes.\n"
                "4. **Target Customer Segment**: The specific customer profile that cares most about that value.\n"
                "5. **Market Category**: The market frame of reference that makes your value instantly intuitive.\n\n"
                "### The 'All-in-One' Trap\n"
                "Never position your product as the 'All-in-One Platform for Everyone'. When you try to be everything to everybody, you become the best choice for nobody."
            )
        elif any(k in query for k in ["shreyas", "doshi", "lno", "high agency", "prioritization", "good pm"]):
            content = (
                "From Lenny's episode with **Shreyas Doshi**, here is the core guidance on High Agency PM leadership and prioritization:\n\n"
                "### The LNO Framework\n"
                "To prevent burnout and maximize strategic impact, categorize your work into three buckets:\n"
                "- **L — Leverage Tasks (10x ROI)**: Asymmetric bets like product vision, customer discovery insights, or core strategy memos. Dedicate 60% of creative energy and aim for an **A+ grade**.\n"
                "- **N — Neutral Tasks (1x ROI)**: Routine operational tasks (sprint planning, status updates). Aim for a solid **B grade** and do not over-polish.\n"
                "- **O — Overhead Tasks (<0.1x ROI)**: Admin, expense reports, compliance. Complete with **C/D grade** effort or automate.\n\n"
                "### High Agency Leadership\n"
                "High agency is the refusal to accept standard constraints as fixed barriers. When an average PM encounters blocked dependencies, they stop. A high-agency PM finds a path forward—sketching wireframes, redlining agreements directly with legal, or re-scoping requirements to preserve outcome velocity."
            )
        elif any(k in query for k in ["rahul", "vohra", "pmf", "superhuman", "40%", "disappointed"]):
            content = (
                "According to **Rahul Vohra** (Founder & CEO of Superhuman) on Lenny's Podcast, Product-Market Fit can be engineered systematically:\n\n"
                "### The 40% Disappointment Metric\n"
                "Ask your users: *'How would you feel if you could no longer use the product?'*\n"
                "- Very disappointed\n"
                "- Somewhat disappointed\n"
                "- Not disappointed\n\n"
                "Benchmark: Companies with durable growth consistently score **40% or higher** in the 'Very disappointed' group. Superhuman started at 22% and engineered it to 58% in six months.\n\n"
                "### The 4-Step PMF Engine\n"
                "1. **Segment for High-Expectation Customers (HXC)**: Double down on the archetype that answered 'Very disappointed' and ignore feedback from 'Not disappointed'.\n"
                "2. **Analyze Feedback**: Discover why HXCs love the product and what holds back the 'Somewhat disappointed' cohort.\n"
                "3. **50% of Roadmap**: Make core superpowers even faster and more delightful.\n"
                "4. **50% of Roadmap**: Overcome the top 2-3 blockers cited by somewhat disappointed HXCs."
            )
        else:
            content = (
                "I searched the indexed Lenny's Podcast transcript knowledge base for your query, but could not find sufficient grounded evidence to answer authoritatively.\n\n"
                "The current knowledge base covers:\n"
                "- **Elena Verna**: B2B Product-Led Growth, Reverse Trials, PQLs, and Monetization Loops.\n"
                "- **Brian Balfour**: The Four Fits Framework, Growth Loops vs. Funnels, and Retention.\n"
                "- **Casey Winters**: Retention Loops, Marketplace Cold Start, and Scaling.\n"
                "- **Sean Ellis**: The ICE Prioritization Scoring Framework and 40% PMF Test.\n"
                "- **April Dunford**: The 5 Components of B2B Product Positioning.\n"
                "- **Shreyas Doshi**: High Agency Product Management, LNO Task Prioritization, and Strategy.\n"
                "- **Rahul Vohra**: Superhuman's PMF Engine, the 40% Disappointment Rule, and High-Expectation Customers.\n\n"
                "Please ask a question related to these topics or product growth frameworks!"
            )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return ProviderResponse(
            content=content,
            provider_name="mock",
            model_name=self.model,
            latency_ms=round(elapsed_ms, 2)
        )

    def _generate_ship30_essay(self, user_msg: str, system_prompt: str) -> str:
        return (
            "# The Compound Growth Engine: Why Modern B2B Winners Replace Funnels with Loops\n\n"
            "**By Lenny Growth Assistant (Ship 30 for 30 Framework)**\n\n"
            "> **The 1-Sentence Takeaway**: Sustainable enterprise growth is not built on linear ad funnels, but on closed self-reinforcing product loops where usage directly generates the next cohort of activated users.\n\n"
            "---\n\n"
            "### The Hook: Why 90% of Growth Teams Are Trapped in a Leaky Bucket\n"
            "Every Monday morning, growth teams gather to stare at their Pirate Funnel (AARRR). They pour thousands of marketing dollars into the top, watch 95% of users vanish before day 30, celebrate the remaining 5%, and repeat the madness next week.\n\n"
            "As **Brian Balfour** (Founder of Reforge) famously outlined on Lenny's Podcast, the funnel mental model is fundamentally broken for scaling $100M+ businesses. If your acquisition requires linear marketing spend, your growth will instantly stall the moment CAC rises.\n\n"
            "---\n\n"
            "### Pillar 1: The Anatomy of a Closed Growth Loop\n"
            "A growth loop is a closed compound system where:\n"
            "1. **Input**: User signs up and takes a high-value core action.\n"
            "2. **Action**: User creates an artifact (a dashboard in Amplitude, a board in Miro, an email snippet in Superhuman).\n"
            "3. **Output**: The artifact is exposed to external stakeholders or indexed by search engines.\n"
            "4. **Reinvestment**: New prospects discover the product organically and become the next cohort's input.\n\n"
            "---\n\n"
            "### Pillar 2: The Elena Verna Reverse Trial Playbook\n"
            "How do you activate this loop without massive friction? According to **Elena Verna**, the answer is the **Reverse Trial**:\n"
            "- Give new signups 14 days of unrestricted enterprise capabilities.\n"
            "- Hook them on collaboration features (team seats, unlimited canvases, advanced analytics).\n"
            "- When the trial expires, **never lock them out**. Gracefully downgrade them to a generous freemium plan to preserve the daily habit.\n\n"
            "---\n\n"
            "### Pillar 3: Engineering Quantitative Product-Market Fit\n"
            "Growth loops are useless if retention is broken. **Rahul Vohra** (Superhuman) and **Sean Ellis** established the gold standard:\n"
            "- Target at least **40%** of survey respondents answering they would be *'Very disappointed'* without your product.\n"
            "- Dedicate **50% of your engineering sprint** to amplifying what enthusiasts love, and **50%** to knocking down objections for the 'Somewhat disappointed' high-expectation users.\n\n"
            "---\n\n"
            "### Transcript Evidence vs. Strategic Inference\n\n"
            "| Principle | Grounded Transcript Evidence | Actionable Strategic Inference |\n"
            "| :--- | :--- | :--- |\n"
            "| **Growth Loops** | Brian Balfour: *'Sustainable $100M+ businesses grow through closed loops.'* | Audit your product for natural viral touchpoints and UGC indexing opportunities. |\n"
            "| **Reverse Trial** | Elena Verna: *'Hook them on enterprise features, then downgrade to free.'* | Replace hard 14-day paywalls with seamless freemium fallback. |\n"
            "| **ICE Scoring** | Sean Ellis: *'ICE Score = (Impact + Confidence + Ease) / 3.'* | Rank growth backlog weekly to eliminate subjective prioritization bias. |\n"
            "| **PMF Benchmark** | Rahul Vohra: *'The 40% Sean Ellis threshold benchmarks durable PMF.'* | Measure your disappointment score monthly before scaling paid acquisition. |\n\n"
            "---\n\n"
            "### The 24-Hour Action Checklist for Growth Leads\n"
            "- [ ] **Step 1**: Map your product's primary acquisition loop from user action to peer invite.\n"
            "- [ ] **Step 2**: Check your 30-day cohort retention curve; ensure it flattens parallel to the x-axis.\n"
            "- [ ] **Step 3**: Implement the 40% disappointment survey across activated users this week."
        )

    def _generate_ice_calculator_artifact(self, query: str) -> str:
        html = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Sean Ellis ICE Prioritization Matrix</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b0f19; color: #f1f5f9; padding: 20px; }
    .container { max-width: 650px; margin: 0 auto; background: #131d2e; border: 1px solid #24354f; border-radius: 12px; padding: 20px; }
    h2 { color: #38bdf8; font-size: 1.25rem; margin-bottom: 4px; }
    p.sub { color: #94a3b8; font-size: 0.8rem; margin-bottom: 16px; }
    .form-row { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr auto; gap: 8px; margin-bottom: 16px; }
    input, button { background: #1a273d; border: 1px solid #24354f; color: #fff; padding: 8px 10px; border-radius: 6px; font-size: 0.825rem; }
    button.add { background: #2563eb; cursor: pointer; font-weight: bold; border: none; }
    button.add:hover { background: #38bdf8; }
    table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 0.825rem; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid #24354f; }
    th { color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; }
    .score-badge { background: rgba(56, 189, 248, 0.2); color: #38bdf8; font-weight: bold; padding: 3px 8px; border-radius: 4px; }
  </style>
</head>
<body>
  <div class="container">
    <h2>⚡ Sean Ellis ICE Growth Prioritization Matrix</h2>
    <p class="sub">Rank growth experiments by (Impact + Confidence + Ease) / 3 to maximize sprint velocity.</p>
    
    <div class="form-row">
      <input type="text" id="expName" placeholder="Experiment Name (e.g. Reverse Trial Onboarding)" />
      <input type="number" id="expI" min="1" max="10" placeholder="Impact (1-10)" />
      <input type="number" id="expC" min="1" max="10" placeholder="Conf (1-10)" />
      <input type="number" id="expE" min="1" max="10" placeholder="Ease (1-10)" />
      <button class="add" onclick="addExp()">+ Add</button>
    </div>

    <table id="iceTable">
      <thead>
        <tr>
          <th>Experiment</th>
          <th>I</th>
          <th>C</th>
          <th>E</th>
          <th>ICE Score</th>
        </tr>
      </thead>
      <tbody id="tableBody">
        <tr>
          <td><strong>Reverse Trial with SAML SSO Gating</strong></td>
          <td>9</td><td>8</td><td>7</td>
          <td><span class="score-badge">8.0</span></td>
        </tr>
        <tr>
          <td><strong>Sean Ellis 40% In-App PMF Survey</strong></td>
          <td>8</td><td>9</td><td>9</td>
          <td><span class="score-badge">8.7</span></td>
        </tr>
        <tr>
          <td><strong>Double-Sided Viral Referral Loop</strong></td>
          <td>9</td><td>7</td><td>6</td>
          <td><span class="score-badge">7.3</span></td>
        </tr>
      </tbody>
    </table>
  </div>

  <script>
    let exps = [
      { name: "Sean Ellis 40% In-App PMF Survey", i: 8, c: 9, e: 9, score: 8.7 },
      { name: "Reverse Trial with SAML SSO Gating", i: 9, c: 8, e: 7, score: 8.0 },
      { name: "Double-Sided Viral Referral Loop", i: 9, c: 7, e: 6, score: 7.3 }
    ];

    function render() {
      exps.sort((a,b) => b.score - a.score);
      const tbody = document.getElementById('tableBody');
      tbody.innerHTML = '';
      exps.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td><strong>${item.name}</strong></td><td>${item.i}</td><td>${item.c}</td><td>${item.e}</td><td><span class="score-badge">${item.score.toFixed(1)}</span></td>`;
        tbody.appendChild(tr);
      });
    }

    function addExp() {
      const name = document.getElementById('expName').value;
      const i = parseFloat(document.getElementById('expI').value);
      const c = parseFloat(document.getElementById('expC').value);
      const e = parseFloat(document.getElementById('expE').value);
      if(!name || isNaN(i) || isNaN(c) || isNaN(e)) return;
      const score = (i + c + e) / 3;
      exps.push({ name, i, c, e, score });
      document.getElementById('expName').value = '';
      document.getElementById('expI').value = '';
      document.getElementById('expC').value = '';
      document.getElementById('expE').value = '';
      render();
    }
  </script>
</body>
</html>"""
        return f"Here is the interactive **Sean Ellis ICE Prioritization Matrix** component:\n\n```html\n{html}\n```\n\nUse this tool to rank growth experiments dynamically."

    def _generate_pmf_dashboard_artifact(self, query: str) -> str:
        html = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Superhuman PMF Engine & 40% Rule Dashboard</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b0f19; color: #f1f5f9; padding: 20px; }
    .card { max-width: 620px; margin: 0 auto; background: #131d2e; border: 1px solid #24354f; border-radius: 12px; padding: 24px; }
    h2 { color: #38bdf8; font-size: 1.25rem; margin-bottom: 6px; }
    p.sub { color: #94a3b8; font-size: 0.8rem; margin-bottom: 20px; }
    .survey-box { background: #1a273d; border-radius: 8px; padding: 16px; margin-bottom: 20px; }
    .bar-row { margin-bottom: 12px; }
    .bar-label { display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px; }
    .bar-track { background: #0d131f; height: 12px; border-radius: 6px; overflow: hidden; }
    .bar-fill { height: 100%; border-radius: 6px; transition: width 0.3s ease; }
    .fill-green { background: #10b981; }
    .fill-yellow { background: #f59e0b; }
    .fill-red { background: #ef4444; }
    .target-line { font-size: 0.75rem; color: #10b981; font-weight: bold; margin-top: 8px; }
  </style>
</head>
<body>
  <div class="card">
    <h2>🎯 Superhuman Product-Market Fit Engine (40% Rule)</h2>
    <p class="sub">Benchmark Sean Ellis PMF score and segment High-Expectation Customers (HXC).</p>

    <div class="survey-box">
      <div style="font-size: 0.85rem; font-weight: 600; margin-bottom: 12px; color: #fff;">
        "How would you feel if you could no longer use this product tomorrow?"
      </div>

      <div class="bar-row">
        <div class="bar-label">
          <span>🚀 Very Disappointed (Target: ≥40%)</span>
          <strong style="color: #10b981;">54%</strong>
        </div>
        <div class="bar-track"><div class="bar-fill fill-green" style="width: 54%;"></div></div>
      </div>

      <div class="bar-row">
        <div class="bar-label">
          <span>⚠️ Somewhat Disappointed</span>
          <strong style="color: #f59e0b;">32%</strong>
        </div>
        <div class="bar-track"><div class="bar-fill fill-yellow" style="width: 32%;"></div></div>
      </div>

      <div class="bar-row">
        <div class="bar-label">
          <span>🛑 Not Disappointed (Filter out)</span>
          <strong style="color: #ef4444;">14%</strong>
        </div>
        <div class="bar-track"><div class="bar-fill fill-red" style="width: 14%;"></div></div>
      </div>

      <div class="target-line">✓ Status: DURABLE PRODUCT-MARKET FIT ACHIEVED (54% > 40%)</div>
    </div>
  </div>
</body>
</html>"""
        return f"Here is the interactive **Superhuman PMF Engine & 40% Rule Dashboard** artifact:\n\n```html\n{html}\n```"

    def _generate_positioning_canvas_artifact(self, query: str) -> str:
        html = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>April Dunford 5-Step Positioning Canvas</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b0f19; color: #f1f5f9; padding: 20px; }
    .canvas { max-width: 650px; margin: 0 auto; background: #131d2e; border: 1px solid #24354f; border-radius: 12px; padding: 20px; }
    h2 { color: #38bdf8; font-size: 1.25rem; margin-bottom: 4px; }
    p.sub { color: #94a3b8; font-size: 0.8rem; margin-bottom: 16px; }
    .step { background: #1a273d; border-left: 4px solid #38bdf8; border-radius: 6px; padding: 12px; margin-bottom: 10px; }
    .step-num { font-size: 0.7rem; text-transform: uppercase; color: #38bdf8; font-weight: bold; }
    .step-title { font-size: 0.85rem; font-weight: bold; margin: 2px 0 6px 0; }
    .step-content { font-size: 0.8rem; color: #cbd5e1; }
  </style>
</head>
<body>
  <div class="canvas">
    <h2>📐 April Dunford 5-Step Positioning Canvas</h2>
    <p class="sub">Define your product's category, differentiated value, and target segment.</p>
    
    <div class="step">
      <div class="step-num">Component 1</div>
      <div class="step-title">Competitive Alternatives</div>
      <div class="step-content">What would customers do if you didn't exist? (e.g. Messy Google Sheets + Manual Zapier scripts).</div>
    </div>

    <div class="step">
      <div class="step-num">Component 2</div>
      <div class="step-title">Unique Differentiated Attributes</div>
      <div class="step-content">What features do you have that alternatives lack? (e.g. Instant sub-100ms keyboard-first search).</div>
    </div>

    <div class="step">
      <div class="step-num">Component 3</div>
      <div class="step-title">Value for Customers</div>
      <div class="step-content">What business ROI does that unlock? (e.g. Saves executives 4 hours per week on inbox triage).</div>
    </div>

    <div class="step">
      <div class="step-num">Component 4</div>
      <div class="step-title">Target Customer Segment</div>
      <div class="step-content">Who cares the most about that value? (e.g. Fast-paced VC investors and C-suite leaders).</div>
    </div>

    <div class="step">
      <div class="step-num">Component 5</div>
      <div class="step-title">Market Category Frame</div>
      <div class="step-content">Context that makes your value obvious: "The Superhuman Email Engine for Founders".</div>
    </div>
  </div>
</body>
</html>"""
        return f"Here is the interactive **April Dunford 5-Step Positioning Canvas**:\n\n```html\n{html}\n```"

    def _generate_lno_matrix_artifact(self, query: str) -> str:
        html = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Shreyas Doshi LNO Task Matrix</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b0f19; color: #f1f5f9; padding: 20px; }
    .matrix { max-width: 650px; margin: 0 auto; background: #131d2e; border: 1px solid #24354f; border-radius: 12px; padding: 20px; }
    h2 { color: #38bdf8; font-size: 1.25rem; margin-bottom: 4px; }
    p.sub { color: #94a3b8; font-size: 0.8rem; margin-bottom: 16px; }
    .grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
    .col { background: #1a273d; border-radius: 8px; padding: 12px; border-top: 4px solid #38bdf8; }
    .col.n { border-top-color: #f59e0b; }
    .col.o { border-top-color: #64748b; }
    .col-title { font-size: 0.85rem; font-weight: bold; margin-bottom: 4px; }
    .col-roi { font-size: 0.7rem; color: #38bdf8; margin-bottom: 8px; font-weight: bold; }
    .task { background: #0d131f; padding: 8px; border-radius: 4px; font-size: 0.775rem; margin-bottom: 6px; color: #cbd5e1; }
  </style>
</head>
<body>
  <div class="matrix">
    <h2>⚡ Shreyas Doshi LNO Task Allocation Matrix</h2>
    <p class="sub">Allocate creative energy based on Leverage (10x), Neutral (1x), and Overhead (0.1x).</p>

    <div class="grid">
      <div class="col">
        <div class="col-title">Leverage (L)</div>
        <div class="col-roi">10x ROI • Aim for A+</div>
        <div class="task">🎯 Core Product Strategy Memo</div>
        <div class="task">💡 Key Customer Discovery Interviews</div>
        <div class="task">📈 Reverse Trial Pricing Model</div>
      </div>
      <div class="col n">
        <div class="col-title">Neutral (N)</div>
        <div class="col-roi" style="color: #f59e0b;">1x ROI • Aim for B</div>
        <div class="task">📋 Weekly Sprint Planning</div>
        <div class="task">✉️ Stakeholder Status Email</div>
        <div class="task">📊 Routine Metric Dashboards</div>
      </div>
      <div class="col o">
        <div class="col-title">Overhead (O)</div>
        <div class="col-roi" style="color: #94a3b8;"><0.1x ROI • Aim for C/D</div>
        <div class="task">📝 Expense Reports</div>
        <div class="task">📑 Compliance Forms</div>
        <div class="task">🔄 Calendar Rescheduling</div>
      </div>
    </div>
  </div>
</body>
</html>"""
        return f"Here is the interactive **Shreyas Doshi LNO Task Allocation Matrix** artifact:\n\n```html\n{html}\n```"

    def _generate_reverse_trial_calculator_artifact(self, user_msg: str) -> str:
        html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>PLG Reverse Trial & PQL Revenue Modeler</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    body { background: #0b0f19; color: #f1f5f9; padding: 24px; display: flex; justify-content: center; }
    .card { background: #131d2e; border: 1px solid #23334d; border-radius: 12px; max-width: 580px; width: 100%; padding: 24px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5); }
    h2 { font-size: 1.25rem; color: #38bdf8; margin-bottom: 8px; }
    p.sub { font-size: 0.85rem; color: #94a3b8; margin-bottom: 20px; }
    .input-group { margin-bottom: 16px; }
    label { display: block; font-size: 0.8rem; font-weight: 600; color: #cbd5e1; margin-bottom: 6px; }
    input[type="range"] { width: 100%; accent-color: #38bdf8; margin-bottom: 4px; }
    .range-val { font-size: 0.8rem; color: #38bdf8; font-weight: bold; float: right; }
    .metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 24px; border-top: 1px solid #23334d; padding-top: 16px; }
    .metric-box { background: #1a273d; padding: 14px; border-radius: 8px; border-left: 4px solid #38bdf8; }
    .metric-box.green { border-left-color: #10b981; }
    .metric-title { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; }
    .metric-value { font-size: 1.4rem; font-weight: bold; color: #fff; margin-top: 4px; }
  </style>
</head>
<body>
  <div class="card">
    <h2>🚀 Elena Verna Reverse Trial Modeler</h2>
    <p class="sub">Model monthly revenue from enterprise trial downgrades and PQL expansion.</p>

    <div class="input-group">
      <label>Monthly Free Signups <span class="range-val" id="valSignups">5,000</span></label>
      <input type="range" id="inputSignups" min="500" max="25000" step="500" value="5000" oninput="calculate()" />
    </div>

    <div class="input-group">
      <label>14-Day Activation / PQL Rate <span class="range-val" id="valActivation">35%</span></label>
      <input type="range" id="inputActivation" min="10" max="80" step="5" value="35" oninput="calculate()" />
    </div>

    <div class="input-group">
      <label>Enterprise Conversion Rate <span class="range-val" id="valEnterpriseConv">8%</span></label>
      <input type="range" id="inputEnterpriseConv" min="1" max="25" step="1" value="8" oninput="calculate()" />
    </div>

    <div class="input-group">
      <label>Average Contract Value (ACV / year) <span class="range-val" id="valACV">$4,800</span></label>
      <input type="range" id="inputACV" min="1200" max="24000" step="600" value="4800" oninput="calculate()" />
    </div>

    <div class="metrics-grid">
      <div class="metric-box">
        <div class="metric-title">Monthly PQLs</div>
        <div class="metric-value" id="resPQLs">1,750</div>
      </div>
      <div class="metric-box green">
        <div class="metric-title">New Enterprise ARR</div>
        <div class="metric-value" id="resARR">$56,000</div>
      </div>
    </div>
  </div>

  <script>
    function calculate() {
      const signups = parseInt(document.getElementById('inputSignups').value);
      const actRate = parseInt(document.getElementById('inputActivation').value) / 100;
      const convRate = parseInt(document.getElementById('inputEnterpriseConv').value) / 100;
      const acv = parseInt(document.getElementById('inputACV').value);

      document.getElementById('valSignups').innerText = signups.toLocaleString();
      document.getElementById('valActivation').innerText = Math.round(actRate * 100) + '%';
      document.getElementById('valEnterpriseConv').innerText = Math.round(convRate * 100) + '%';
      document.getElementById('valACV').innerText = '$' + acv.toLocaleString();

      const pqls = Math.round(signups * actRate);
      const customers = Math.round(pqls * convRate);
      document.getElementById('resPQLs').innerText = pqls.toLocaleString();
      document.getElementById('resARR').innerText = '$' + (customers * acv).toLocaleString() + ' / yr';
    }
  </script>
</body>
</html>"""
        return f"Here is the interactive **PLG Reverse Trial & PQL Revenue Modeler** artifact:\n\n```html\n{html}\n```"

