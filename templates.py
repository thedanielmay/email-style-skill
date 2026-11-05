"""The six approved templates (1 Oct 2026), one per email type. Copy the shape, replace the content.
Run directly: checks every template and writes snippets.html (the visual reference)."""
from house_email import *

DOC = "https://docs.google.com/document/d/1JS0frDk2UvfXEqTywUjdKRspMvmqYezcUG3E56-jXt8/edit#heading=h.fk89drexowbm"

# Each returns (tier, subject, html). Subjects for new threads carry a tag; replies keep the thread subject.

def test_report():
    """Full tier. Results first, numbered detail after. From the Cade email of Thu 1 Oct."""
    body = (p("Following up on your Wed 30 Sep reply.")
            + ask_box(ask_rows("On a staging application, should styles saved with " + code("set_interface_styles") + " show on the page before a publish?",
                               "no fixed date.", "the brand styling on the Snapshot sign-in page.", '"yes", "no, publish first", or what I am doing wrong.'),
                      "One question for you")
            + table(["What you suggested testing", "Result"],
                    [["1. Does sign-in carry to a fresh tab, in a plain window?", pill("YES", "PASS")],
                     ["2. Does SDK 1.0.13 re-subscribe a channel by itself after sign-in?", pill("YES", "PASS")],
                     ['3. Does the "your access changed" signal reach an open page?', pill("YES", "PASS")]], ["75%", "25%"])
            + h3("1. Fresh tab, plain window")
            + ul(["In an ordinary Chrome window, with no automation, a new window opened at the sandbox address was already signed in.",
                  "A second tab saw the sign-out and sign-in arrive from the other window, live, with no reload."])
            + h3("2. SDK 1.0.13 re-subscribes by itself")
            + ul([f"The page subscribed once to {code('spikeTestTrainee:edit')} while signed out, and never again.",
                  "After sign-in, an admin edit arrived on that channel without a reload."])
            + p("Everything I restored or created for this is deleted again, and the org is back to its baseline.", 0))
    return "Full", "Re: How we tested Qik through the MCP (and where we probably got it wrong)", wrap(body, "Hi Cade,")

def decision_request():
    """Full tier, the heaviest shape. Drop any block that has nothing real to say (e.g. no 'since' box if nothing changed)."""
    body = (p("Following up on your Wed 30 Sep answers.")
            + ask_box(ask_steps(["<strong>Run Prompts 1 to 3 at the bottom of this email, in order, and tell me when they are done.</strong> " + tag("Unblocks your publish"),
                                 "<strong>Reply with A or B for each of the three decisions in section 2.</strong> Decision 2 " + tag("Releases Prompt 4")]))
            + attached_note("The prompts are also attached as a file.")
            + since(["The Thu 1 Oct date check passed.", "Questions 16 and 17 were added to the Google Doc."])
            + h3("1. The Thu 1 Oct date check passed")
            + table(["What I checked", "Result"],
                    [["Month and quarter defaults", pill("PASS")], ["Follow-up prompt dates", pill("NOT TESTED")]], ["70%", "30%"])
            + h3("2. Three decisions for you")
            + table(["Decision", "Holds up", "Needed by"],
                    [["1. Which months the projections use", "Nothing", "Mon 5 Oct"],
                     ["2. Volunteering in the dollar figures", "Prompt 4", "Tomorrow, Fri 2 Oct"],
                     ["3. Follow-up choices for graduates", "Nothing", "After the Sue-Lee and Bron session"]], ["50%", "20%", "30%"],
                    {(0, 2): NEAR, (1, 2): NEAR})
            + choice_card("Decision 2: does volunteering count in the dollar figures?",
                          table(["", "A. Include", "B. Keep out"],
                                [["<b>Positive outcome</b>", "Yes", "Yes"],
                                 ["<b>Fiscal savings</b>", "Adds $412,000 per trainee", "Adds nothing"],
                                 ["<b>Cost per outcome</b>", "Counts", "Does not count"]], ["28%", "36%", "36%"])
                          + p(link("Question 16 in the Doc", DOC, "Google Doc") + " sets out both options.", 0))
            + copy_line("Decision 1: __ &nbsp;&nbsp; Decision 2: __ &nbsp;&nbsp; Decision 3: __ or later")
            + h3("3. The three prompts, in full")
            + copy_block("Prompt 3 of 3: reports use 86 Mollison Street",
                         '**Change:** in the three footers in `proof.tsx`, "58 Mollison Street" becomes "86 Mollison Street".\n\n**Commit** "Reports use 86 Mollison Street". Don\'t publish.')
            + attached_list([f"{code('snapshot-prompts-1-3.txt')}: the three prompts, the same as in this email."]))
    return "Full", "Re: SOFO Snapshot: your test logins worked, one question about saving and deleting", wrap(body, "Hi Simon,")

def client_update():
    """Client tier. No code or file names. Example content."""
    body = (p("It has been two weeks since our last update, so here is where the dashboard is up to.")
            + ask_box(ask_rows("Choose a time for a 30-minute walkthrough of the dashboard.",
                               "<b>Tomorrow, Fri 2 Oct</b>, so I can send the invite.", "the walkthrough, and your sign-off on the October figures.",
                               'a day, for example "Tuesday".'))
            + h3("1. Where the dashboard is up to")
            + table(["Item", "Status"],
                    [["Monthly figures use Melbourne dates", pill("DONE", "PASS")],
                     ["Report footers show 86 Mollison Street", pill("DONE", "PASS")],
                     ["Volunteering in the dollar figures", pill("WAITING ON A DECISION", "NOT TESTED")]], ["65%", "35%"])
            + h3("2. Times that work for me")
            + ul(["Tue 6 Oct, 10:00 to 10:30", "Thu 8 Oct, 14:00 to 14:30"], mb=0))
    return "Client", "[Action needed] SOFO Snapshot: pick a walkthrough time", wrap(body, "Hi Sue-Lee,")

def question_list():
    """Client tier. Numbered questions: yes or no inline, lettered choices stacked with options(). Example content."""
    body = (p("Following up on the brochure draft you commented on.")
            + ask_box(ask_rows("Answer the three questions below, in any order.", "no date", "the final version.",
                               'the numbers, for example "1 yes, 2A, 3B".'))
            + h3("The three questions")
            + ul(["<b>Page 6.</b> Is the last line under the first line what you meant? Yes or no. <i>If I don't hear, it stays.</i>",
                  options("<b>Page 11.</b> Is the print run on:", ["recycled board", "new stock"], needs_answer=True),
                  options("<b>Page 13.</b> Capacity:", ["add a figure (largest order: ___)", "keep your text without one"], default="If I don't hear, B.")],
                 ordered=True, mb=0))
    return "Client", "Re: Brochure draft", wrap(body, "Hi Sue-Lee,")

def short_reply():
    """Light tier. Bold first line is the ask. No boxes, headings or tables."""
    body = (p("<strong>Can you publish now? All three prompts passed my re-test on the dev preview.</strong>")
            + ul(['The projections card reads "3-Month Projections".', "Both PDF footers say 86 Mollison Street."], mb=0))
    return "Light", "Re: SOFO Snapshot: prompts 1 to 3", wrap(body, "Hi Simon,")

def personal():
    """Plain tier. Paragraphs only. Contact shortcuts (e.g. Leemo) override greeting and sign-off."""
    return "Plain", "Sunday lunch", wrap(lines(["Sunday lunch works for us.", "We will be there at 12:30.", "Leemo is bringing the cake."], 0), "Hi Mum,")

ALL = [test_report, decision_request, client_update, question_list, short_reply, personal]

if __name__ == "__main__":
    from pathlib import Path
    parts = [f'<div style="max-width:800px;margin:0 auto;padding:24px 16px;background:#fff">{p("<b>House email style: reference.</b> Every block and template from house_email.py, as Gmail renders them. Generated; do not edit by hand.")}']
    for f in ALL:
        tier, subj, html = f()
        errs, warns = check(html)
        assert not errs, f"{f.__name__}: {errs}"
        assert to_text(html).strip(), f"{f.__name__}: empty plain text"
        parts.append(f'<h2 style="font-family:{FONT};font-size:18px;margin:32px 0 6px 0">{f.__name__} ({tier} tier)</h2>'
                     f'<div style="font-family:{FONT};font-size:13px;color:#555;margin:0 0 8px 0"><b>Subject:</b> {subj}</div>'
                     f'<div style="border:1px solid #ddd;padding:16px">{html}</div>')
        print(f"{f.__name__:18} {tier:6} {len(html.encode())/1024:5.1f}KB  warnings: {warns or 'none'}")
    # the checker must catch what it claims to catch
    bad = wrap(ask_box(p("a")) + ask_box(p("b")) + table(list("abcd"), [list("1234")]) + p("x \u2014 y"), "Hi,")
    e, _ = check(bad)
    assert len(e) == 3, e
    _, w = check(wrap(ul(["Is custom print on: A) board or B) new stock?"]), "Hi,"))
    assert any("run-on A/B" in x for x in w), w          # inline lettered options must warn
    _, w = check(question_list()[2])
    assert not any("run-on A/B" in x for x in w), w      # stacked options must not
    # telegraphic guard: a good telegraphic copy loses nothing, a bad one is caught
    full = wrap(p("We will not submit before Fri 13 Nov. The grant is $20,000, only if Adam agrees."), "Hi,")
    assert facts_kept(full, wrap(p("We won't submit before Fri 13 Nov. Grant $20,000, only if Adam agrees."), "Hi,")) == []
    assert any("negation" in x for x in facts_kept(full, wrap(p("We'll submit before Fri 13 Nov. Grant $20,000, only if Adam agrees."), "Hi,")))
    assert any("$20,000" in x for x in facts_kept(full, wrap(p("We won't submit before Fri 13 Nov. Grant, only if Adam agrees."), "Hi,")))
    assert any("qualifier" in x for x in facts_kept(full, wrap(p("We won't submit before Fri 13 Nov. Grant $20,000, if Adam agrees."), "Hi,")))
    Path(__file__).with_name("snippets.html").write_text("<title>House email snippets</title>" + "".join(parts) + "</div>")
    print("all checks passed; snippets.html written")
