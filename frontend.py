"""
MacroManager — Notebook-aesthetic Streamlit frontend
PCOS-focused nutrition tracking interface.
Connects to FastAPI backend at API_URL (default: http://localhost:8000).
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
import base64
import time
import math
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
API_URL   = "http://localhost:8000"
RING_R    = 40
RING_CIRC = 2 * math.pi * RING_R

PALETTE = {
    "protein": {"fill": "#7F77DD", "track": "#E1DEFC", "dark": "#3C3489", "mid": "#534AB7"},
    "carbs":   {"fill": "#EF9F27", "track": "#FCE8BE", "dark": "#633806", "mid": "#854F0B"},
    "fat":     {"fill": "#1D9E75", "track": "#B5EDD8", "dark": "#085041", "mid": "#0F6E56"},
}

_DIV = '<hr style="border:none;border-top:1px solid rgba(42,31,16,0.12);margin:8px 0;"/>'

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MacroManager",
    page_icon="📓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Courier+Prime:ital,wght@0,400;0,700;1,400;1,700&display=swap');

/* ── Notebook paper background ── */
[data-testid="stAppViewContainer"] {
    background-color: #F8FAFB;
    background-image: 
        linear-gradient(to right, rgba(100, 116, 139, 0.06) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(100, 116, 139, 0.06) 1px, transparent 1px);
    background-size: 26px 26px;
}
[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stSidebar"] { display: none !important; }

/* ── Main column: clean layout ── */
.block-container {
    max-width:  460px !important;
    padding:    1.5rem 1.5rem 3rem 1.5rem !important;
    border-left: none !important;
    background:  transparent !important;
}

/* ── Base font ── */
* { font-family: 'Courier Prime', monospace !important; }
h1, h2, h3 { color: #2a1f10 !important; }

/* ── Restore Streamlit Icons ── */
[data-testid="stIcon"],
[data-testid="stIconMaterial"],
[data-testid="stExpanderToggleIcon"],
[class*="MaterialSymbols"],
[class*="material-icons"] {
    font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
}

/* ── Text inputs ── */
.stTextInput  > div > div > input,
.stTextArea   > div > div > textarea,
.stNumberInput > div > div > input {
    background:    rgba(255, 255, 255, 0.88) !important;
    border:        1px solid rgba(42, 31, 16, 0.26) !important;
    font-size:     16px !important;
    color:         #2a1f10 !important;
    border-radius: 4px !important;
    caret-color:   #7F77DD;
}
textarea::placeholder, input::placeholder {
    font-size: 13px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea  > div > div > textarea:focus {
    border-color: rgba(127, 119, 221, 0.5) !important;
    box-shadow:   none !important;
    outline:      none !important;
}
.stTextInput label, .stTextArea label,
.stNumberInput label, .stSelectbox label {
    font-size: 14px !important;
    color:     #7a6d5a !important;
}

/* ── Select ── */
[data-baseweb="select"] > div {
    background:   rgba(255, 255, 255, 0.88) !important;
    border-color: rgba(42, 31, 16, 0.26) !important;
    font-size:    16px !important;
    color:        #2a1f10 !important;
}

/* ── Buttons ── */
.stButton > button,
[data-testid="stBaseButton-secondary"],
[data-testid="stButton"] > button {
    background:      #EDEFF1 !important;
    border:          1.5px solid rgba(42, 31, 16, 0.30) !important;
    font-size:       16px !important;
    color:           #2a1f10 !important;
    border-radius:   4px !important;
    transition:      background 0.14s;
    height:          44px !important;
    min-height:      44px !important;
    padding:         0 14px !important;
    display:         flex !important;
    align-items:     center !important;
    justify-content: center !important;
    width:           100% !important;
    box-sizing:      border-box !important;
}
.stButton > button *,
[data-testid="stBaseButton-secondary"] *,
[data-testid="stButton"] > button * {
    white-space:     nowrap !important;
    margin:          0 !important;
}
.stButton > button:hover,
[data-testid="stBaseButton-secondary"]:hover   { background: #E2E6E9 !important; }
.stButton > button:active,
[data-testid="stBaseButton-secondary"]:active  { background: #D7DBDF !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background:    transparent !important;
    border-bottom: 1px solid rgba(42, 31, 16, 0.14) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-size:   15px !important;
    color:       #9a8d7c !important;
    background:  transparent !important;
    padding:     6px 14px !important;
}
.stTabs [aria-selected="true"] {
    color:         #2a1f10 !important;
    background:    transparent !important;
}
div[data-baseweb="tab-highlight"],
[data-testid="stTabsSelectionIndicator"] {
    background-color: #8a8a8a !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 12px !important; }

/* ── Expanders ── */
[data-testid="stExpander"] {
    border:        1px solid rgba(42, 31, 16, 0.13) !important;
    background:    rgba(255, 255, 255, 0.65) !important;
    border-radius: 4px !important;
    margin-bottom: 6px !important;
}
[data-testid="stExpander"] div[role="button"] p,
[data-testid="stExpander"] details summary p,
[data-testid="stExpanderToggleIcon"] { color: #2a1f10 !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #7F77DD !important; }

/* ── Alerts ── */
.stAlert { border-radius: 4px !important; }

/* ── Camera ── */
[data-testid="stCameraInput"] label { font-size: 15px !important; color: #7a6d5a !important; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, .stDeployButton,
[data-testid="stToolbar"] { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "consumed":         {"protein": 0.0, "carbs": 0.0, "fat": 0.0,
                             "calories": 0.0, "fiber": 0.0, "sugar": 0.0},
        "goals":            {"protein": 140.0, "carbs": 200.0,
                             "fat": 65.0, "calories": 1800.0},
        "weekly":           {},
        "journal_grouped":  {},
        "memory_content":   "",
        "pending_meal_id":  None,
        "last_refreshed":   0.0,
        "current_page":     "onboarding",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─────────────────────────────────────────────────────────────────────────────
# API HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def fetch_summary():
    try:
        r = requests.get(f"{API_URL}/summary", timeout=6)
        r.raise_for_status()
        d = r.json()
        st.session_state.consumed        = d["daily"]["consumed"]
        st.session_state.goals           = d["daily"]["goals"]
        st.session_state.weekly          = d.get("weekly", {})
        st.session_state.journal_grouped = d["daily"].get("grouped", {})
        st.session_state.last_refreshed  = time.time()
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the backend — make sure the API is running on localhost:8000.")
    except Exception as exc:
        st.warning(f"Data fetch failed: {exc}")


def api_start_log(text, meal_type, is_voice=False):
    r = requests.post(
        f"{API_URL}/log/start",
        json={"text": text, "meal_type": meal_type, "is_voice": is_voice},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["meal_id"]


def api_log_status(meal_id):
    r = requests.get(f"{API_URL}/log/status/{meal_id}", timeout=5)
    r.raise_for_status()
    return r.json().get("status", "processing")


def api_vision_log(b64, environment, hint):
    r = requests.post(
        f"{API_URL}/vision-log",
        json={"base64_image": b64, "environment": environment, "hint": hint},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def api_update_goals(p, c, f, cal):
    r = requests.post(
        f"{API_URL}/goals",
        json={"protein": p, "carbs": c, "fat": f, "calories": cal},
        timeout=5,
    )
    r.raise_for_status()


def api_onboard(bio):
    r = requests.post(f"{API_URL}/onboard", json={"bio_text": bio}, timeout=25)
    r.raise_for_status()
    return r.json()


def api_save_memory(text):
    r = requests.post(f"{API_URL}/memory", json={"text": text}, timeout=10)
    r.raise_for_status()
    return r.json().get("content", "")


def api_fetch_memory():
    r = requests.get(f"{API_URL}/memory", timeout=5)
    r.raise_for_status()
    return r.json().get("content", "")



# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _section_header(text, sub=None):
    """Renders a bold 17px section heading, with an optional 13px grey sub-label."""
    sub_html = (
        f'<span style="font-family:\'Courier Prime\',monospace;font-size:13px;'
        f'color:#9a8d7c;"> ({sub})</span>' if sub else ""
    )
    st.markdown(
        f'<p style="font-family:\'Courier Prime\',monospace;font-weight:bold;font-size:17px;'
        f'color:#2a1f10;margin:18px 0 6px;">{text}{sub_html}</p>',
        unsafe_allow_html=True,
    )


def _weekly_bar(label, consumed, goal, fill, track):
    """Renders a single horizontal weekly progress bar as an HTML string."""
    p     = min(consumed / max(goal, 1), 1.0)
    pct_w = round(p * 100, 1)
    color = "#EF9F27" if (p >= 0.88 and label == "carbs") else fill
    return (
        f'<div style="margin:5px 0;">'
        f'<div style="display:flex;justify-content:space-between;align-items:baseline;'
        f'font-family:\'Courier Prime\',monospace;font-size:12px;color:#7a6d5a;margin-bottom:3px;">'
        f'<span style="font-size:15px;color:#2a1f10;">{label}</span>'
        f'<span>{int(round(consumed))}g / {int(round(goal))}g</span></div>'
        f'<div style="background:{track};border-radius:3px;height:6px;overflow:hidden;">'
        f'<div style="background:{color};width:{pct_w}%;height:100%;border-radius:3px;"></div>'
        f'</div></div>'
    )


def macro_state(consumed, goal):
    """Returns (state, clamped_pct).  state: 'normal' | 'warning' | 'complete'"""
    if goal <= 0:
        return "normal", 0.0
    pct = consumed / goal
    if pct >= 1.0:
        return "complete", 1.0
    if pct >= 0.82:
        return "warning", pct
    return "normal", pct


def arc_dash(pct):
    fill = round(min(max(pct, 0.0), 1.0) * RING_CIRC, 2)
    gap  = round(RING_CIRC - fill + 8, 2)   # +8 gap prevents visual closure
    return fill, gap


# ─────────────────────────────────────────────────────────────────────────────
# RENDER: HUD
# ─────────────────────────────────────────────────────────────────────────────
def _ring(macro, consumed, goal, cx, pct, state):
    """Build SVG group for a single progress ring."""
    pal       = PALETTE[macro]
    fill, gap = arc_dash(pct)
    sw        = 9.5 if state == "warning" else 7
    v_weight  = "700" if state == "complete" else "400"
    v_color   = pal["dark"] if state in ("complete", "warning") else "#2a1f10"
    cy        = 62

    val_str  = f"{int(round(consumed))}g"
    goal_str = f"of {int(round(goal))}g"

    out = []
    # track ring
    out.append(
        f'<circle cx="{cx}" cy="{cy}" r="{RING_R}" fill="none" '
        f'stroke="{pal["track"]}" stroke-width="7"/>'
    )
    # progress arc
    out.append(
        f'<circle cx="{cx}" cy="{cy}" r="{RING_R}" fill="none" '
        f'stroke="{pal["fill"]}" stroke-width="{sw}" '
        f'stroke-dasharray="{fill} {gap}" stroke-linecap="round" '
        f'transform="rotate(-90 {cx} {cy})"/>'
    )
    # completion: thin outer halo
    if state == "complete":
        out.append(
            f'<circle cx="{cx}" cy="{cy}" r="47" fill="none" '
            f'stroke="{pal["fill"]}" stroke-width="1.5" opacity="0.36"/>'
        )
    # warning: small dot at ~1 o'clock
    if state == "warning":
        wx = cx + int(RING_R * 0.72)
        wy = cy - int(RING_R * 0.72)
        out.append(f'<circle cx="{wx}" cy="{wy}" r="5.5" fill="{pal["fill"]}"/>')
        out.append(
            f'<text x="{wx}" y="{wy + 4}" text-anchor="middle" '
            f'font-size="8" font-weight="700" '
            f'fill="{pal["dark"]}">!</text>'
        )
    # consumed value
    out.append(
        f'<text x="{cx}" y="{cy - 6}" text-anchor="middle" '
        f'font-size="13" font-weight="{v_weight}" '
        f'fill="{v_color}">{val_str}</text>'
    )
    # macro label
    out.append(
        f'<text x="{cx}" y="{cy + 9}" text-anchor="middle" '
        f'font-size="13" fill="{pal["mid"]}">{macro}</text>'
    )
    # goal label below ring
    out.append(
        f'<text x="{cx}" y="{cy + 53}" text-anchor="middle" '
        f'font-size="10" fill="#9a8d7c">{goal_str}</text>'
    )
    return "".join(out)


def render_hud():
    c, g = st.session_state.consumed, st.session_state.goals

    p_st,  p_pct  = macro_state(c["protein"],  g["protein"])
    ca_st, ca_pct = macro_state(c["carbs"],     g["carbs"])
    f_st,  f_pct  = macro_state(c["fat"],       g["fat"])

    cal_pct    = min(c["calories"] / max(g["calories"], 1), 1.4)
    cal_val    = f'{int(round(c["calories"])):,}'
    cal_goal   = f'{int(round(g["calories"])):,}'
    cal_color  = "#085041" if cal_pct >= 1.0 else ("#633806" if cal_pct >= 0.92 else "#2a1f10")
    cal_weight = "700" if cal_pct >= 1.0 else "400"

    rings = (
        _ring("protein", c["protein"], g["protein"], 50,  p_pct,  p_st)  +
        _ring("carbs",   c["carbs"],   g["carbs"],   150, ca_pct, ca_st) +
        _ring("fat",     c["fat"],     g["fat"],     250, f_pct,  f_st)
    )

    st.markdown(f"""
<div style="margin:4px 0 14px;">
  <div style="text-align:center;margin-bottom:10px;line-height:1.1;">
    <span style="font-family:'Courier Prime',monospace;font-size:28px;
                 font-weight:{cal_weight};color:{cal_color};">{cal_val}</span>
    <span style="font-family:'Courier Prime',monospace;font-size:14px;
                 color:#9a8d7c;">&thinsp;/ {cal_goal} kcal</span>
  </div>
  <svg viewBox="0 0 300 125" width="100%" xmlns="http://www.w3.org/2000/svg"
       style="font-family:'Courier Prime',monospace;">
    {rings}
  </svg>
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# RENDER: EMPATHETIC MESSAGES
# ─────────────────────────────────────────────────────────────────────────────
def render_message():
    c, g = st.session_state.consumed, st.session_state.goals

    def pct(k):
        return c[k] / max(g[k], 1)

    msgs = []

    if pct("protein") >= 1.0:
        msgs.append(("#1D9E75", "✓  Protein goal hit — muscles sorted for the day."))
    elif pct("protein") >= 0.70:
        rem = int(round(g["protein"] - c["protein"]))
        msgs.append(("#7F77DD", f"→  {rem}g of protein to go."))

    if pct("carbs") > 1.0:
        msgs.append(("#854F0B", "·  Carbs are over today — worth balancing tomorrow."))
    elif pct("carbs") >= 0.85:
        msgs.append(("#EF9F27", "·  Carbs are close to the daily limit."))

    if pct("calories") >= 1.0:
        msgs.append(("#633806", "·  Calorie goal reached for today."))

    if not msgs and c["calories"] < 50:
        msgs.append(("#9a8d7c", "→  Nothing logged yet — how's the day starting?"))

    for color, text in msgs[:2]:
        st.markdown(
            f'<p style="font-family:\'Courier Prime\',monospace;font-size:14px;'
            f'color:{color};margin:2px 0;line-height:1.4;">{text}</p>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# RENDER: WEEKLY BUFFER
# ─────────────────────────────────────────────────────────────────────────────
def render_weekly():
    w = st.session_state.weekly
    if not w:
        return

    st.markdown(_DIV, unsafe_allow_html=True)
    wg   = w.get("weekly_goals", {})
    days = w.get("days_logged", 0)

    def bar(label, consumed, goal, fill, track):
        p     = min(consumed / max(goal, 1), 1.0)
        pct_w = round(p * 100, 1)
        color = "#EF9F27" if (p >= 0.88 and label == "carbs") else fill
        return (
            f'<div style="margin:5px 0;">'
            f'<div style="display:flex;justify-content:space-between;align-items:baseline;'
            f'font-family:\'Courier Prime\',monospace;font-size:12px;color:#7a6d5a;margin-bottom:3px;">'
            f'<span style="font-size:15px;color:#2a1f10;">{label}</span>'
            f'<span>{int(round(consumed))}g / {int(round(goal))}g</span></div>'
            f'<div style="background:{track};border-radius:3px;height:6px;overflow:hidden;">'
            f'<div style="background:{color};width:{pct_w}%;height:100%;border-radius:3px;"></div>'
            f'</div></div>'
        )

    day_label = f"{days} day{'s' if days != 1 else ''} logged"
    inner = (
        _weekly_bar("protein", w.get("protein", 0), wg.get("protein", 1), "#7F77DD", "#E1DEFC") +
        _weekly_bar("carbs",   w.get("carbs", 0),   wg.get("carbs", 1),   "#EF9F27", "#FCE8BE") +
        _weekly_bar("fat",     w.get("fat", 0),     wg.get("fat", 1),     "#1D9E75", "#B5EDD8")
    )
    _section_header("this week", sub=day_label)
    st.markdown(f'<div style="margin:0 0 16px;">{inner}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# RENDER: FOOD LOG
# ─────────────────────────────────────────────────────────────────────────────
_MIC_HTML = """<!DOCTYPE html>
<html>
<head>
<style>
  body { margin:0; padding:0; background:transparent; overflow:hidden; 
         display:flex; justify-content:center; align-items:center; height:48px; }
  #btn {
    width: 44px; height: 44px; border-radius: 50%;
    background: #EDEFF1;
    border: 1.5px solid rgba(42, 31, 16, 0.30);
    cursor: pointer; display: flex; align-items: center; justify-content: center;
    font-size: 18px; color: #2a1f10;
    transition: all 0.15s ease;
    outline: none;
  }
  #btn:hover { background: #E2E6E9; }
  #btn:active { background: #D7DBDF; }
  #btn.recording {
    background: #FFEBEB;
    border-color: #C83232;
    color: #C83232;
    animation: pulse 1.2s infinite;
  }
  @keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(200, 50, 50, 0.4); }
    70% { box-shadow: 0 0 0 8px rgba(200, 50, 50, 0); }
    100% { box-shadow: 0 0 0 0 rgba(200, 50, 50, 0); }
  }
</style>
</head>
<body>
<button id="btn" onclick="toggle()" title="Tap to speak">🎤</button>
<script>
var rec = null, on = false;
function toggle() {
  if (on) { rec && rec.stop(); return; }
  if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
    alert('Speech recognition not supported in this browser.');
    return;
  }
  var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  rec = new SR();
  rec.lang = 'en-IN';
  rec.interimResults = false;
  rec.maxAlternatives = 1;
  rec.onstart = function() {
    on = true;
    var b = document.getElementById('btn');
    b.textContent = '⏹';
    b.classList.add('recording');
  };
  rec.onresult = function(e) {
    var t = Array.from(e.results).map(r => r[0].transcript).join('');
    if (t.trim()) {
      try {
        var ta = window.parent.document.querySelector('div[data-testid="stTextArea"] textarea');
        if (ta) {
          var setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
          setter.call(ta, t);
          ta.dispatchEvent(new Event('input', { bubbles: true }));
        }
      } catch(err) {
        navigator.clipboard.writeText(t);
      }
    }
  };
  rec.onend = function() {
    on = false;
    var b = document.getElementById('btn');
    b.textContent = '🎤';
    b.classList.remove('recording');
  };
  rec.onerror = function(e) {
    console.error(e);
    rec.stop();
  };
  rec.start();
}
</script>
</body>
</html>"""


def render_food_log():
    st.markdown(_DIV, unsafe_allow_html=True)
    _section_header("log a meal")

    tab_text, tab_cam = st.tabs(["✏️  text / voice", "📷  camera"])

    # ── Text / Voice ──────────────────────────────────────
    with tab_text:
        meal_type = st.selectbox(
            "meal type",
            ["breakfast", "lunch", "dinner", "snack"],
            key="mt_text",
            label_visibility="collapsed",
        )
        st.markdown(
            '<p style="font-size:15px;color:#9a8d7c;margin:8px 0 4px;">'
            'what did you eat? (tap mic to speak)</p>',
            unsafe_allow_html=True,
        )
        col_input, col_mic = st.columns([4.0, 0.5], vertical_alignment="center")
        with col_input:
            user_text = st.text_area(
                "what did you eat?",
                placeholder="e.g. 2 rotis with dal and a small bowl of rice…",
                height=56,
                key="log_text",
                label_visibility="collapsed",
            )
        with col_mic:
            components.html(_MIC_HTML, height=48, scrolling=False)

        log_clicked = st.button("log it →", key="btn_log", use_container_width=True)

        if log_clicked:
            if user_text.strip():
                try:
                    meal_id = api_start_log(user_text.strip(), meal_type)
                    st.session_state.pending_meal_id = meal_id
                    st.rerun()
                except Exception as exc:
                    st.error(f"Couldn't start log: {exc}")
            else:
                st.warning("Describe what you ate first.")

    # ── Camera ────────────────────────────────────────────
    with tab_cam:
        env = st.selectbox(
            "setting",
            ["home", "restaurant", "street food", "packaged"],
            key="cam_env",
            label_visibility="collapsed",
        )
        hint = st.text_input(
            "hint (optional)",
            placeholder="e.g. South Indian thali",
            key="cam_hint",
            label_visibility="collapsed",
        )
        img = st.camera_input("photo", label_visibility="collapsed")
        if img is not None:
            b64 = base64.b64encode(img.read()).decode()
            if st.button("analyse photo →", key="btn_vision"):
                with st.spinner("Analysing image…"):
                    try:
                        api_vision_log(b64, env, hint or "")
                        fetch_summary()
                        st.success("Photo logged.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Vision log failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# RENDER: JOURNAL
# ─────────────────────────────────────────────────────────────────────────────
def render_journal():
    st.markdown(_DIV, unsafe_allow_html=True)
    grouped = st.session_state.journal_grouped
    _section_header("today's journal")
    if not grouped:
        st.markdown(
            '<p style="font-size:15px;color:#9a8d7c;margin:0 0 8px;">'
            'No meals logged yet today.</p>',
            unsafe_allow_html=True,
        )
        return

    for meal_type, batches in grouped.items():
        st.markdown(
            f'<p style="font-family:\'Courier Prime\',monospace;font-weight:bold;font-size:14px;'
            f'color:#6b5e4a;margin:10px 0 4px;'
            f'border-bottom:1px solid rgba(42,31,16,0.12);padding-bottom:3px;">'
            f'{meal_type}</p>',
            unsafe_allow_html=True,
        )
        for batch in batches:
            for item in batch:
                name  = item.get("name", "Unknown")
                grams = item.get("grams", 0)
                cals  = item.get("cals", 0)
                m     = item.get("macros", {})
                p     = m.get("protein", 0)
                ca    = m.get("carbs", 0)
                f     = m.get("fat", 0)
                chk   = "&nbsp;✓" if item.get("verified") else ""
                st.markdown(
                    f'<div style="margin:6px 0; display:flex; flex-direction:column; gap:2px;">'
                    f'  <div style="font-size:15px; color:#2a1f10; font-weight:bold;">{name}{chk}</div>'
                    f'  <div style="display:flex; justify-content:space-between; align-items:center;">'
                    f'    <span style="font-size:13px; color:#9a8d7c;">{int(grams)}g · {int(cals)} kcal</span>'
                    f'    <span style="font-size:12px; color:#7a6d5a;">P {int(p)}g · C {int(ca)}g · F {int(f)}g</span>'
                    f'  </div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


# ─────────────────────────────────────────────────────────────────────────────
# DIALOG MODALS
# ─────────────────────────────────────────────────────────────────────────────
@st.dialog("remember this!")
def show_memory_dialog():
    st.markdown(
        '<p style="font-size:14px;color:#7a6d5a;margin:0 0 12px;">'
        'Things the AI should always know — utensils, portions, allergies, routines.</p>',
        unsafe_allow_html=True,
    )
    if not st.session_state.memory_content:
        try:
            st.session_state.memory_content = api_fetch_memory()
        except Exception:
            pass
    mem = st.text_area(
        "memory",
        value=st.session_state.memory_content,
        height=110,
        key="mem_input",
        label_visibility="collapsed",
        placeholder=(
            "e.g. I use a standard katori (150 ml). "
            "I'm lactose intolerant. I skip breakfast on weekdays."
        ),
    )
    if st.button("update memory →", key="btn_mem", use_container_width=True):
        with st.spinner("Saving…"):
            try:
                updated = api_save_memory(mem.strip())
                st.session_state.memory_content = updated
                st.success("Memory updated.")
                time.sleep(1)
                st.rerun()
            except Exception as exc:
                st.error(f"Couldn't save: {exc}")



# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ONBOARDING
# ─────────────────────────────────────────────────────────────────────────────
def render_onboarding_page():
    st.markdown('<div style="margin-top:12px;"></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="'
        f'background: linear-gradient(135deg, rgba(127, 119, 221, 0.16) 0%, rgba(239, 159, 39, 0.16) 50%, rgba(29, 158, 117, 0.16) 100%);'
        f'border: 1.5px solid rgba(42, 31, 16, 0.12);'
        f'border-radius: 12px;'
        f'padding: 22px 16px;'
        f'text-align: center;'
        f'margin-bottom: 24px;'
        f'box-shadow: 0 4px 24px rgba(42, 31, 16, 0.05);'
        f'backdrop-filter: blur(12px);'
        f'">'
        f'<p style="font-family:\'Courier Prime\',monospace;font-weight:bold;font-size:28px;'
        f'color:#2a1f10;margin:0;line-height:1.1;">📓 MacroManager</p>'
        f'<p style="font-size:14px;color:#7a6d5a;margin:6px 0 0 0;font-weight:500;letter-spacing:0.3px;">'
        f'PCOS goals & calibration</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p style="font-family:\'Courier Prime\',monospace;font-weight:bold;font-size:17px;'
        'color:#2a1f10;margin:0 0 6px;">PCOS baseline calibrator</p>'
        '<p style="font-size:13px;color:#9a8d7c;margin-bottom:12px;">'
        'Describe your profile for personalised PCOS macronutrient targets.</p>',
        unsafe_allow_html=True,
    )
    bio = st.text_area(
        "tell us about yourself",
        placeholder=(
            "e.g. 26F, 58 kg, 163 cm, lightly active, "
            "managing PCOS, want to reduce insulin resistance…"
        ),
        height=95,
        key="bio_text",
        label_visibility="collapsed"
    )
    if st.button("calculate my goals →", key="btn_onboard", use_container_width=True):
        if bio.strip():
            with st.spinner("Calculating PCOS-adjusted goals…"):
                try:
                    res = api_onboard(bio.strip())
                    mx  = res.get("macros", {})
                    st.success(
                        f"Goals set — Protein {int(mx.get('protein', 0))}g · "
                        f"Carbs {int(mx.get('carbs', 0))}g · "
                        f"Fat {int(mx.get('fat', 0))}g · "
                        f"{int(mx.get('calories', 0))} kcal"
                    )
                    fetch_summary()
                    time.sleep(1.5)
                    st.session_state.current_page = "dashboard"
                    st.rerun()
                except Exception as exc:
                    st.error(f"Onboarding failed: {exc}")
        else:
            st.warning("Fill in your details first.")

    st.markdown(
        '<hr style="border:none;border-top:1px solid rgba(42,31,16,0.12);margin:24px 0;"/>'
        '<p style="font-family:\'Courier Prime\',monospace;font-weight:bold;font-size:17px;'
        'color:#2a1f10;margin:0 0 14px;">manual override</p>',
        unsafe_allow_html=True,
    )
    g = st.session_state.goals
    c1, c2 = st.columns(2)
    with c1:
        new_p   = st.number_input("Protein (g)",     value=float(g["protein"]),   min_value=0.0, step=5.0,  key="g_p")
        new_c   = st.number_input("Carbs (g)",       value=float(g["carbs"]),     min_value=0.0, step=5.0,  key="g_c")
    with c2:
        new_f   = st.number_input("Fat (g)",         value=float(g["fat"]),       min_value=0.0, step=5.0,  key="g_f")
        new_cal = st.number_input("Calories (kcal)", value=float(g["calories"]),  min_value=0.0, step=50.0, key="g_cal")
    
    if st.button("save goals →", key="btn_goals", use_container_width=True):
        try:
            api_update_goals(new_p, new_c, new_f, new_cal)
            st.success("Goals saved.")
            fetch_summary()
            time.sleep(1)
            st.session_state.current_page = "dashboard"
            st.rerun()
        except Exception as exc:
            st.error(f"Couldn't save: {exc}")




# ─────────────────────────────────────────────────────────────────────────────
# ASYNC LOG POLLING
# ─────────────────────────────────────────────────────────────────────────────
def handle_pending_log():
    """Polls /log/status until the background meal resolution completes."""
    mid = st.session_state.pending_meal_id
    if not mid:
        return
    with st.spinner("Logging your meal — calculating macros…"):
        time.sleep(2.5)
        try:
            status = api_log_status(mid)
            if status == "completed":
                st.session_state.pending_meal_id = None
                fetch_summary()
                st.success("✓  Meal logged and macros updated.")
                st.rerun()
            else:
                st.rerun()    # keep polling
        except Exception:
            st.session_state.pending_meal_id = None   # bail out silently on error



# ─────────────────────────────────────────────────────────────────────────────
# PAGE: DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def render_dashboard_page():
    now = datetime.now()
    st.markdown(
        f'<p style="font-family:\'Courier Prime\',monospace;font-weight:bold;font-size:24px;'
        f'color:#2a1f10;margin:0;line-height:1.1;">{now.strftime("%A").lower()}</p>'
        f'<p style="font-size:15px;color:#9a8d7c;margin:0 0 14px;">'
        f'{now.strftime("%d %B %Y")}</p>',
        unsafe_allow_html=True,
    )

    render_hud()
    render_message()

    st.markdown('<div style="margin-top:12px;"></div>', unsafe_allow_html=True)
    if st.button("edit goals", key="btn_goto_onboarding", help="Edit your PCOS goals", use_container_width=True):
        st.session_state.current_page = "onboarding"
        st.rerun()

    render_food_log()
    render_journal()
    render_weekly()

    # Dashboard Action Modals at the Footer
    st.markdown(
        _DIV + '<div style="margin-top:12px;"></div>',
        unsafe_allow_html=True
    )
    if st.button("remember this!", key="btn_open_mem", use_container_width=True):
        show_memory_dialog()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ROUTER
# ─────────────────────────────────────────────────────────────────────────────
def main():
    inject_css()
    init_session()

    # Auto-refresh summary every 30 s (or on first load)
    if time.time() - st.session_state.last_refreshed > 30:
        fetch_summary()

    # Conditional Rendering based on Session Router
    if st.session_state.current_page == "onboarding":
        render_onboarding_page()
    else:
        render_dashboard_page()
        
        # Poll for any in-flight meal log (only relevant on dashboard)
        handle_pending_log()


if __name__ == "__main__":
    main()
