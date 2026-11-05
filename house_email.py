"""Daniel's house email blocks, checks and sender. Decided 1 Oct 2026 over four review rounds.

Every block returns inline-styled HTML: Gmail drops <style> tags and class-based CSS.
Use from Python:  sys.path.insert(0, os.path.expanduser("~/.claude/skills/email-style")); from house_email import *
Do not name a local variable or function `email`: it shadows the stdlib module (this bit us once).
"""
import re, base64, mimetypes, subprocess, json
from html.parser import HTMLParser
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders

# ---------- tokens (round 1) ----------
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
MONO = "Menlo,Consolas,monospace"
INK, NAVY, RULE, GREY = "#1b1b1b", "#1f3a5f", "#d8e1ee", "#667085"
ASK_BG, ASK_BD = "#fff4cc", "#e0a800"          # yellow = the reader must act. Once per email.
CHOICE_BG = "#f5f8fc"                          # pale blue = choices and context
PASS, FAIL, PARTIAL = "#1e7b34", "#b42318", "#b54708"
TXT = f"font-family:{FONT};font-size:13px;line-height:1.5;color:{INK}"
TH = f"font-family:{FONT};font-size:12px;text-align:left;background:#eef2f7;border:1px solid #cfd8e3;padding:8px;color:{INK}"
TD = f"font-family:{FONT};font-size:12px;line-height:1.45;border:1px solid #cfd8e3;padding:8px;vertical-align:top;color:{INK}"

# ---------- text ----------
def p(html, mb=10):
    return f'<p style="{TXT};margin:0 0 {mb}px 0">{html}</p>'

def lines(items, mb=10):
    """One fact per line, no blank line between (Plain tier, and short runs elsewhere). Keep a claim and its reason on one line."""
    return p("<br>".join(items), mb)

def ul(items, ordered=False, mb=10):
    tag_ = "ol" if ordered else "ul"
    lis = "".join(f'<li style="{TXT};margin-bottom:8px">{i}</li>' for i in items)
    return f'<{tag_} style="margin:0 0 {mb}px 0;padding-left:22px">{lis}</{tag_}>'

def h3(text):
    """Numbered navy heading with a rule. Full and Client tiers. Pass the number in the text: '2. Three decisions'."""
    return (f'<h3 style="font-family:{FONT};font-size:15px;color:{NAVY};margin:24px 0 8px 0;'
            f'border-bottom:2px solid {RULE};padding-bottom:4px">{text}</h3>')

def label(text, color=INK, mb=6):
    return (f'<div style="font-family:{FONT};font-size:12px;font-weight:bold;letter-spacing:.5px;'
            f'text-transform:uppercase;color:{color};margin-bottom:{mb}px">{text}</div>')

def code(t):
    """Grey chip. Full tier only."""
    return f'<code style="font-family:{MONO};font-size:12px;background:#f2f4f7;padding:1px 4px;border-radius:3px">{t}</code>'

def tag(text, bg="#eef2f7", fg=NAVY):
    """Small pill after a step or title: 'Releases Prompt 4', 'Can wait'."""
    return (f'<span style="font-family:{FONT};font-size:12px;font-weight:bold;background:{bg};color:{fg};'
            f'padding:2px 7px;border-radius:10px;white-space:nowrap">{text}</span>')

def link(text, href, where):
    """Link plus where it goes, e.g. link('Question 16 in the Doc', url, 'Google Doc'). href must come from a real record."""
    return f'<a href="{href}" style="color:{NAVY}">{text}</a> <span style="color:{GREY};font-size:12px">({where})</span>'

def issue(repo, n, owner="thedanielmay"):
    """Issue reference per the repo#N rule. URL is generated, never typed."""
    return link(f"{repo}#{n}", f"https://github.com/{owner}/{repo}/issues/{n}", "GitHub")

# ---------- the ask (round 2) ----------
def ask_box(inner, title="What I need from you"):
    """The one call to action. Yellow, left bar. Exactly one per email."""
    return f'<div style="background:{ASK_BG};border-left:6px solid {ASK_BD};padding:12px 16px;margin:0 0 16px 0">{label(title)}{inner}</div>'

def ask_rows(ask, by, unblocks, reply):
    """Single ask: the ask in bold, then By / This unblocks / Reply with."""
    return (p(f"<strong>{ask}</strong>", 8) + p(f"<b>By:</b> {by}", 4)
            + p(f"<b>This unblocks:</b> {unblocks}", 4) + p(f"<b>Reply with:</b> {reply}", 0))

def ask_steps(steps):
    """Several things to do: one numbered list, each step may end with a tag(). Several recipients: start each step with '<b>Name:</b>'."""
    return ul(steps, ordered=True, mb=0)

def options(stem, choices, default=None, needs_answer=False):
    """A question with two or more lettered choices (set Thu 1 Oct 2026). Stack the choices under the question,
    one per line, lettered A, B, C, so a reply like "3A" points at one. Never run them inline ("A) ... B) ...").
    Use as an item inside ul(..., ordered=True) or ask_steps(). Yes or no questions stay inline: end them "Yes or no."
    default: "If I don't hear, A." on its own line under the choices.
    needs_answer=True: the red tag instead of a default (money, people, anything that can't be undone)."""
    assert 2 <= len(choices) <= 8, "options() is for two or more choices"
    lis = "".join(f'<li style="{TXT};margin:0 0 2px 0">{"ABCDEFGH"[i]}. {c}</li>' for i, c in enumerate(choices))
    tail = ""
    if default: tail = f'<div style="{TXT};margin:2px 0 0 0"><i>{default}</i></div>'
    elif needs_answer: tail = f'<div style="margin:3px 0 0 0">{tag("Needs your answer", "#fde8e6", FAIL)}</div>'
    return f'{stem}<ul style="margin:3px 0 2px 0;padding:0 0 0 20px;list-style:none">{lis}</ul>{tail}'

def cc_line(text):
    """e.g. 'Cade is copied for information; nothing needed from him.' Only when true."""
    return f'<div style="font-family:{FONT};font-size:12px;color:#555;margin:-8px 0 16px 0">{text}</div>'

attached_note = cc_line   # 'The prompts are also attached as a file.' sits in the same place, same look

# ---------- choices (round 2) ----------
def choice_card(title, body):
    """Decision card. body = ul([A, B]) normally; a table() when options change the same things or it is complex."""
    return (f'<div style="border-left:4px solid {NAVY};background:{CHOICE_BG};padding:10px 14px;margin:0 0 14px 0">'
            f'<div style="font-family:{FONT};font-size:12px;font-weight:bold;color:{INK};margin-bottom:6px">{title}</div>{body}</div>')

def suggestion(text):
    return p(f'<span style="color:{GREY}"><b>If you have no preference:</b> {text}</span>', 0)

def copy_line(text):
    """Reply line for two or more decisions, Full tier. text like 'Decision 1: __ &nbsp; Decision 2: __'."""
    return (p("Copy this line into your reply and fill it in:", 6)
            + f'<div style="font-family:{MONO};font-size:12px;background:#f2f4f7;border:1px solid #cfd8e3;padding:8px 12px;border-radius:4px;color:{INK}">{text}</div>')

def since(items):
    """'Since my last email' box, straight after the ask, for follow-ups."""
    return f'<div style="background:{CHOICE_BG};padding:10px 14px;margin:0 0 16px 0">{label("Since my last email", NAVY)}{ul(items, mb=0)}</div>'

# ---------- evidence (round 3) ----------
_PILL = {"PASS": (PASS, "#e3f4e8", "✓"), "FAIL": (FAIL, "#fde8e6", "✗"),
         "NOT TESTED": (GREY, "#eef0f3", "○"), "PARTIAL": (PARTIAL, "#fdf0e1", "◐")}

def pill(word, status=None):
    """Status pill. Match the row: pill('YES','PASS') for a question, pill('PASS') for a test. Statuses: PASS FAIL NOT TESTED PARTIAL."""
    fg, bg, sym = _PILL[status or word]
    return (f'<span style="font-family:{FONT};font-size:12px;font-weight:bold;letter-spacing:.3px;background:{bg};'
            f'color:{fg};padding:2px 8px;border-radius:10px;white-space:nowrap">{sym} {word}</span>')

def table(head, rows, widths=None, cell_styles=None):
    """Max 3 columns (checked). cell_styles={(row, col): css}; use NEAR for a date within 5 working days."""
    w = widths or [""] * len(head)
    cs = cell_styles or {}
    h = "".join(f'<th style="{TH};{"width:"+x if x else ""}">{c}</th>' for c, x in zip(head, w))
    r = "".join("<tr>" + "".join(f'<td style="{TD};{cs.get((i, j), "")}">{c}</td>' for j, c in enumerate(row)) + "</tr>"
                for i, row in enumerate(rows))
    return f'<table style="border-collapse:collapse;width:100%;margin:0 0 12px 0"><tr>{h}</tr>{r}</table>'

NEAR = f"background:{ASK_BG};font-weight:bold"   # near date cell: write the day in words, e.g. 'Tomorrow, Fri 2 Oct'

def copy_block(title, text):
    """Prompt or command the reader copies. Attach as a file too when there are two or more."""
    return (f'{label(title, NAVY)}<div style="font-family:{MONO};font-size:12px;line-height:1.5;white-space:pre-wrap;color:{INK};'
            f'background:#f7f7f9;border-left:4px solid {NAVY};padding:12px;margin:0 0 16px 0">{text}</div>')

def attached_list(items):
    return f'<div style="margin:22px 0 0 0">{label("Attached", NAVY)}{ul(items, mb=0)}</div>'

def figure(cid, alt, caption):
    """Inline screenshot. Pass the file in send(images={cid: path}). Never a data: URI (Gmail blocks them)."""
    return (f'<div style="margin:0 0 14px 0"><img src="cid:{cid}" alt="{alt}" style="display:block;max-width:100%;width:auto;border:1px solid #cfd8e3">'
            f'<div style="font-family:{FONT};font-size:12px;color:#555;margin-top:4px">{caption}</div></div>')

# ---------- wrapper ----------
def wrap(body, greeting, signoff="Thanks,<br>Daniel"):
    """Whole email. Full/Client: greeting, one context line, ask_box, rest. 760px max."""
    return (f'<div style="max-width:760px">{p(greeting)}{body}'
            f'<p style="{TXT};margin:20px 0 0 0">{signoff}</p></div>')

# ---------- checks ----------
CLIP_LIMIT = 80 * 1024   # Gmail clips at about 102KB of HTML; leave room

def check(html):
    """Returns (errors, warnings). Errors block sending."""
    errors, warnings = [], []
    if re.search("[\u2013\u2014]", html): errors.append("en or em dash present")
    if "<style" in html or re.search(r'\sclass="', html): errors.append("<style> or class= present; Gmail drops them")
    if 'src="data:' in html: errors.append("data: image; Gmail blocks it, use figure() with a CID image")
    if len(html.encode()) > CLIP_LIMIT: errors.append(f"{len(html.encode())//1024}KB HTML; Gmail clips near 102KB. Move prompts to the attachment only")
    for t in re.findall(r"<table.*?</table>", html, re.S):
        cols = len(re.findall(r"<th[ >]", t.split("</tr>", 1)[0]))
        if cols > 3: errors.append(f"table with {cols} columns; max 3, use a list instead")
    asks = html.count(f"border-left:6px solid {ASK_BD}")
    if asks > 1: errors.append(f"{asks} ask boxes; exactly one per email")
    for para in re.findall(r"<(?:p|li)\b[^>]*>(.*?)</(?:p|li)>", html, re.S):
        if para.count("<strong>") > 1: warnings.append("more than one bold phrase in: " + re.sub("<[^>]+>", "", para)[:60])
    for para in re.findall(r"<(?:p|li)\b[^>]*>(.*?)</(?:p|li)>", html, re.S):
        if re.search(r"\bA[.)]\s.{3,}?\bB[.)]\s", re.sub("<[^>]+>", " ", para)): warnings.append("run-on A/B options; stack them with options(): " + re.sub("<[^>]+>", "", para)[:50])
    if re.search(r"(?<![\w/\[&])#\d+\b", re.sub(r"<[^>]+>", " ", html)): warnings.append("bare #N issue reference; use issue(repo, n)")
    text = re.sub(r"<[^>]+>", " ", html)
    for pat, say in ((r"\bjust (checking|connecting|wanted|a heads up|summarising|confirming|following up|a quick)\b", '"Just" as a softener'), (r"\bAs per\b", '"As per"'),
                     (r"\b(reach out|circle back|touch base)\b", "business filler"), (r"\bASAP\b", '"ASAP": give a date'),
                     (r"\b(Kind|Best) regards\b", "use a house sign-off"), (r"(^|[.!?]\s+)Unfortunately\b", '"Unfortunately" opening bad news'),
                     (r"\b(seems to|appears to|should be)\b", "soft hedge: use a certainty label"),
                     (r"\b(utilise|leverage|facilitate)\b", "use a plain word"), (r"hope (this|you're|you are) (email finds you )?well", "generic opener")):
        if re.search(pat, text, re.I): warnings.append(f"voice.md word list: {say}")
    return errors, warnings

_NEG = r"n't\b|\b(?:not|no|never|none|nothing|without|cannot)\b"
_QUAL = r"\b(?:only|may|might|probably|if|unless|except|about|roughly|at least|at most|up to|until|before)\b"

def facts_kept(full_html, telegraphic_html):
    """Telegraphic guard (set Fri 6 Nov 2026). Returns what the full version has and the telegraphic one lost: numbers, dates, amounts,
    names and acronyms, plus negation and qualifier words (by count). Empty list = nothing detectable was lost.
    It cannot see a changed meaning or a lost actor, so still read both versions side by side."""
    strip = lambda h: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h))
    f, c = strip(full_html), strip(telegraphic_html)
    nums = lambda t: set(re.findall(r"\$?\d[\d,.:]*\d|\$?\d", t))
    names = lambda t: set(re.findall(r"(?<=[a-z,;:] )[A-Z][a-z]+|\b[A-Z]{2,}\b", t))
    lost = []
    for label, fn_ in (("number or date", nums), ("name or acronym", names)):
        lost += [f"{label} dropped: {x}" for x in sorted(fn_(f) - fn_(c))]
    for label, pat in (("negation", _NEG), ("qualifier", _QUAL)):
        a, b = re.findall(pat, f, re.I), re.findall(pat, c, re.I)
        if len(b) < len(a): lost.append(f"{label} words: full has {len(a)}, telegraphic has {len(b)} ({', '.join(sorted(set(x.lower() for x in a)))})")
    return lost

class _Text(HTMLParser):
    BLOCK = {"p", "div", "h3", "tr", "table", "ul", "ol", "br"}
    def __init__(self): super().__init__(); self.out = []
    def handle_starttag(self, t, a):
        if t == "li": self.out.append("\n- ")
        elif t in self.BLOCK: self.out.append("\n")
        elif t in ("td", "th"): self.out.append(" | ")
        elif t == "img": self.out.append(f"[image: {dict(a).get('alt','')}]")
    def handle_endtag(self, t):
        if t in ("p", "h3", "div", "table"): self.out.append("\n")
    def handle_data(self, d): self.out.append(d)

def to_text(html):
    t = _Text(); t.feed(html)
    return re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+\n", "\n", "".join(t.out))).strip() + "\n"

# ---------- send ----------
def _payload(html, to, subject, cc, thread_id, in_reply_to, attachments, images):
    errors, warnings = check(html)
    if errors: raise ValueError("Blocked: " + "; ".join(errors))
    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(to_text(html), "plain", "utf-8"))
    alt.attach(MIMEText(html, "html", "utf-8"))
    body = alt
    if images:
        body = MIMEMultipart("related"); body.attach(alt)
        for cid, path in images.items():
            img = MIMEImage(Path(path).read_bytes()); img.add_header("Content-ID", f"<{cid}>")
            img.add_header("Content-Disposition", "inline", filename=Path(path).name); body.attach(img)
    msg = body
    if attachments:
        msg = MIMEMultipart("mixed"); msg.attach(body)
        for path in attachments:
            ctype = (mimetypes.guess_type(path)[0] or "application/octet-stream").split("/")
            part = MIMEBase(*ctype); part.set_payload(Path(path).read_bytes()); encoders.encode_base64(part)
            part.add_header("Content-Disposition", "attachment", filename=Path(path).name); msg.attach(part)
    msg["To"] = to; msg["Subject"] = subject
    if cc: msg["Cc"] = cc
    if in_reply_to: msg["In-Reply-To"] = in_reply_to; msg["References"] = in_reply_to
    payload = {"raw": base64.urlsafe_b64encode(msg.as_bytes()).decode()}
    if thread_id: payload["threadId"] = thread_id
    return payload, warnings

def send(html, to, subject, cc=None, thread_id=None, in_reply_to=None, attachments=(), images=None, dry_run=False):
    """Send via gws as daniel@thedanielmay.com. ONLY after Daniel has approved the rendered preview.
    Reply in-thread: pass thread_id and in_reply_to (the Message-ID header of the email being answered), keep the subject.
    images={cid: path} for figure(); attachments=[path, ...]."""
    payload, warnings = _payload(html, to, subject, cc, thread_id, in_reply_to, attachments, images)
    if dry_run: return {"warnings": warnings, "bytes": len(html.encode())}
    r = subprocess.run(["gws", "gmail", "users", "messages", "send", "--params", '{"userId":"me"}', "--json", json.dumps(payload)],
                       capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr[-500:])
    return {"warnings": warnings, "result": r.stdout[-300:]}

def draft(html, to, subject, cc=None, thread_id=None, in_reply_to=None, attachments=(), images=None, dry_run=False):
    """Save as a Gmail DRAFT only (set 2026-10-15). Never sends: Daniel reads it in Gmail and sends it himself.
    userId must be in --params or gws silently does nothing. Verify with `gws gmail users drafts get`."""
    payload, warnings = _payload(html, to, subject, cc, thread_id, in_reply_to, attachments, images)
    if dry_run: return {"warnings": warnings, "bytes": len(html.encode())}
    r = subprocess.run(["gws", "gmail", "users", "drafts", "create", "--params", '{"userId":"me"}', "--json", json.dumps({"message": payload})],
                       capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr[-500:])
    out = "\n".join(l for l in r.stdout.splitlines() if not l.startswith("Using keyring"))
    d = json.loads(out)
    if not d.get("id"): raise RuntimeError("draft not created (no id): " + out[-300:])
    return {"warnings": warnings, "draft_id": d["id"], "message_id": d.get("message", {}).get("id")}
