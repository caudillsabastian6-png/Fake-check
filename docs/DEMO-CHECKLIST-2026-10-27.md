# Demo checklist — fully functional, good good good
Owner order Oct 27, 2026: demo must be fully functional, just as good as the real app.
Playground only until owner reviews preview and approves a shareable deploy per item.
"Fully functional" means: every button/nav item does something real or honestly says
what it cannot do yet — no dead screens, no canned verdict presented as real,
no claim SAM authenticates, no grade guess.

## A. Checker — must pass, canned + real phone
- [ ] Home loads, site styles (Cinzel, gold #ffc53d, dark #0b0908), mobile nav not covered by banner
- [ ] Picker: choose front photo, back photo, or live camera — all three work
- [ ] Live camera: Start camera, Capture front, Capture back, Stop camera, in a real browser
- [ ] Front check: identity shown (Name | Set | Number), front tells measured, 5-bubble meter = tells matching only
- [ ] Back check: back tells scored separately, aspect-gated 0.15, combined rule (Counterfeit if either side Counterfeit, Genuine only if both Genuine)
- [ ] Front-only check works and says honestly front-only when no back is given
- [ ] Verification gate: no verdict files unless checklist proven and findings cite recorded tells
- [ ] Needs_input: missing identity, missing back when claimed, missing slab cert/card — stops, names exact item, never guesses
- [ ] Slab: cert + card-inside both required, cert alone never Genuine, status labelled presence/format only offline
- [ ] Timeline panel: what was seen, decided, and returned, 6+ rows, per step
- [ ] Plan panel: steps shown before check, updated as steps complete
- [ ] Recorded facts panel: every tell with match, difference, threshold, source, reference
- [ ] Canned tests pass: Alakazam vs itself = Likely Genuine 5/5, Alakazam vs Charizard = Inconclusive, front Genuine + fake back = Counterfeit, slab without cert = needs_input

## B. Whole app screens — no dead nav
- [ ] Home, Picker, Light Test, Condition Grader, Verdict, Receipt, Binders, Plan, Games, Tells — each opens, each does its stated job or honestly says "not in this demo yet"
- [ ] Verdict uses verdict-pill + 5-bubble meter, never a percentage, never a grade
- [ ] Receipt uses Lens/Gauge tell format with REAL V2 front tells + REAL back tells, not sample text
- [ ] Tells screen: Tells Explainer, user marks tells themselves, labelled "NOT A REAL CARD CHECK" where it is not
- [ ] 10-idea elements present, minimal: Fake-of-the-Week (labelled FAKE, no card photo), Limits-first, photo guide, slab cert field, Look-twice, What-would-have-helped + Re-run on Inconclusive only, community report held locally (nothing sent)

## C. Look, motion, phone — must pass on a real phone
- [ ] Background crossfade ~700ms ease, preload next, contrast check, reduced-motion = instant
- [ ] Top-bar overlap fixed on all screens, button shadows do not dim text
- [ ] Pop-ups/modals: short fade + gentle slide/scale, no hard jump/layout shift, reduced-motion respected
- [ ] Quick-snap works, Little Office works, camera does not break on file preview
- [ ] No Raian Suzuki art/wording, no official Pokémon art verbatim, no real card photos as backgrounds

## D. Before sharing / filming
- [ ] Owner reviews preview on his phone and approves per item
- [ ] Separate shareable deploy decided — public demo link still serves OLD version until approved
- [ ] Tester message ready with specific focus: UX + evidence clarity, plus caveat "not done, playground version later with real verdicts"
- [ ] Demo video: film only after quick-snap + Little Office + top-bar + Grade live on phone, verified, owner-approved; video opens separating pre-existing Real or Replica from Oct 26–Nov 4 new work
- [ ] Hackathon compliance: claim only Oct 26–Nov 4, demo only event-built features, no sensitive material through free-credit calls
