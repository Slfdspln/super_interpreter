"""
Calculator automation using your proven click-calc.jxa script
This is the working solution that actually clicks Calculator buttons
"""

import subprocess
import json
from typing import List, Dict, Any

class JXACalculatorController:
    """Calculator controller using your proven JXA script"""

    def __init__(self):
        self.jxa_script = '''
// click-calc.jxa
// Usage examples:
//   osascript -l JavaScript click-calc.jxa 2 0 9 "*" 3 9 0 9 "="
//   osascript -l JavaScript click-calc.jxa expr "209*3909" "="
//   osascript -l JavaScript click-calc.jxa --dump   (lists button labels it sees)

function run(argv) {
  const se = Application("System Events");
  const calc = Application("Calculator");
  calc.activate();
  delay(0.2);

  const proc = se.processes["Calculator"];
  if (!proc.exists()) return "Calculator process not found (grant Accessibility in System Settings → Privacy & Security → Accessibility).";
  const win = proc.windows.length ? proc.windows[0] : null;
  if (!win) return "No Calculator window.";

  // Helpers
  const normOp = (s) => ({ "*":"×", "/":"÷", "-":"−", "+":"+", "=":"=" }[s] || s);
  const isDigit = (s) => /^\\d$/.test(s);

  function strFields(el){
    const out = [];
    try{ const v = el.name(); if (v) out.push(String(v)); }catch(_){}
    try{ const v = el.title(); if (v) out.push(String(v)); }catch(_){}
    try{ const v = el.description(); if (v) out.push(String(v)); }catch(_){}
    try{ const v = el.value(); if (v) out.push(String(v)); }catch(_){}
    return out.filter(Boolean);
  }

  function findUI(root, pred, maxDepth=7) {
    const q = [{el: root, d: 0}];
    while (q.length) {
      const {el, d} = q.shift();
      if (d > maxDepth) continue;
      let role="", subrole="";
      try{ role = String(el.role()).toLowerCase(); }catch(_){}
      try{ subrole = String(el.subrole()).toLowerCase(); }catch(_){}
      const fields = strFields(el);
      try {
        if (pred({el, role, subrole, fields})) return el;
      } catch(_) {}
      let kids = [];
      try{ kids = el.uiElements(); }catch(_){}
      for (let i=0;i<kids.length;i++) q.push({el:kids[i], d: d+1});
    }
    return null;
  }

  function clickButton(label){
    const want = normOp(String(label));
    const synonyms = new Set([want]);
    if (want === "=") synonyms.add("equals");
    if (want === "×") synonyms.add("*");
    if (want === "÷") synonyms.add("/");
    if (want === "−") synonyms.add("-");

    const target = findUI(win, ({role, fields})=>{
      if (!role.includes("button")) return false;
      const joined = fields.join(" ").trim();
      if (!joined) return false;

      // exact match first
      for (const s of synonyms) if (fields.some(f => f === s)) return true;
      // then contains
      for (const s of synonyms) if (joined.includes(s)) return true;

      // digits sometimes appear as "digit 7" or similar
      if (isDigit(want) && new RegExp(`\\\\b(?:digit|key|number)\\\\s*${want}\\\\b`, "i").test(joined)) return true;
      // plain digit in fields
      if (isDigit(want) && fields.some(f => f.trim() === want)) return true;

      return false;
    });

    if (!target) throw new Error(`Button not found for "${label}"`);
    target.click();  // AXPress
  }

  // Dump mode to see what the app exposes (helps localize labels)
  if (argv.length === 1 && argv[0] === "--dump") {
    const seen = [];
    function dumpButtons(root, depth=0){
      if (depth > 6) return;
      let kids=[];
      try{ kids = root.uiElements(); }catch(_){}
      for (const k of kids) {
        let role=""; try{ role=String(k.role()).toLowerCase(); }catch(_){}
        if (role.includes("button")) {
          const f = strFields(k);
          seen.push(f.join(" | "));
        }
        dumpButtons(k, depth+1);
      }
    }
    dumpButtons(win);
    return ["Buttons I see:", ...seen].join("\\n");
  }

  // Parse args: either explicit sequence or "expr <string> [=]"
  let sequence = [];
  if (argv.length >= 1 && argv[0] === "expr") {
    const expr = (argv[1] || "").replace(/\\s+/g,"");
    for (const ch of expr) sequence.push(ch);
    for (let i=2;i<argv.length;i++) sequence.push(argv[i]); // allow trailing "=" etc.
  } else {
    sequence = argv.length ? argv : ["2","2","8","="]; // default tiny demo
  }

  // Do the clicks
  for (const tok of sequence) {
    clickButton(tok);
    delay(0.08);
  }
  return "OK";
}
'''

    def click_buttons(self, button_sequence: List[str]) -> Dict[str, Any]:
        """Click Calculator buttons using proven JXA script"""
        try:
            # Run the JXA script with button sequence
            cmd = ["osascript", "-l", "JavaScript", "-e", self.jxa_script, "--"] + button_sequence
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                return {
                    "ok": True,
                    "method": "jxa_button_clicking",
                    "sequence": button_sequence,
                    "output": result.stdout.strip()
                }
            else:
                return {
                    "ok": False,
                    "error": result.stderr.strip() or "JXA script failed",
                    "method": "jxa_button_clicking"
                }

        except Exception as e:
            return {"ok": False, "error": str(e), "method": "jxa_button_clicking"}

    def calculate_expression(self, expression: str) -> Dict[str, Any]:
        """Calculate expression using expr mode"""
        try:
            # Use expr mode: expr "209*3909" "="
            cmd = ["osascript", "-l", "JavaScript", "-e", self.jxa_script, "--", "expr", expression, "="]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                return {
                    "ok": True,
                    "method": "jxa_expression",
                    "expression": expression,
                    "output": result.stdout.strip()
                }
            else:
                return {
                    "ok": False,
                    "error": result.stderr.strip() or "JXA expression failed",
                    "method": "jxa_expression"
                }

        except Exception as e:
            return {"ok": False, "error": str(e), "method": "jxa_expression"}

    def calculate_209_x_3909(self) -> Dict[str, Any]:
        """Specific method for 209 × 3909 calculation"""
        return self.click_buttons(["2", "0", "9", "*", "3", "9", "0", "9", "="])

    def dump_buttons(self) -> Dict[str, Any]:
        """Dump available Calculator buttons for debugging"""
        try:
            cmd = ["osascript", "-l", "JavaScript", "-e", self.jxa_script, "--", "--dump"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                return {
                    "ok": True,
                    "method": "jxa_dump",
                    "buttons": result.stdout.strip()
                }
            else:
                return {
                    "ok": False,
                    "error": result.stderr.strip() or "JXA dump failed",
                    "method": "jxa_dump"
                }

        except Exception as e:
            return {"ok": False, "error": str(e), "method": "jxa_dump"}

# Create global instance
jxa_calc = JXACalculatorController()

# Convenience functions for easy use
def click_calc_buttons(buttons: List[str]) -> Dict[str, Any]:
    """Click Calculator buttons: click_calc_buttons(['2','0','9','*','3','9','0','9','='])"""
    return jxa_calc.click_buttons(buttons)

def calc_expression(expression: str) -> Dict[str, Any]:
    """Calculate expression: calc_expression('209*3909')"""
    return jxa_calc.calculate_expression(expression)

def calc_209_x_3909() -> Dict[str, Any]:
    """Calculate 209 × 3909 specifically"""
    return jxa_calc.calculate_209_x_3909()