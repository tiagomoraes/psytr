# The weekly report framework — what the therapist gets, and why

> **Language note.** English is the pack's base language. Reports are written in the owner's language; the examples here are from the fictional Portuguese ledger in `scripts/fixtures/demo-ledger`.

This file records the research behind sintr's weekly report and the decision it led to for each part of it. How to *write* each section is in `weekly-report-guide.md`; how the PDF is produced is in `scripts/report_pdf.py`.

The report is a short document **about how the person's week felt**, prepared for their therapist from the person's own records, reviewed by the person, and sent as a PDF. Four bodies of practice shaped it:

1. the **DBT diary card** (Linehan) — a one-page, day-by-day record reviewed at the start of each session;
2. **CBT mood monitoring and thought records** (Beck; Greenberger & Padesky) — the mood check, the session agenda, and the situation → thoughts → emotions → behavior record that sintr entries already follow;
3. research on **pre-session summaries and patient-generated data** — what helps a clinician in the few minutes before a session, and what gets in the way;
4. how a reference app, **Cogni**, presents a recorded event.

Source labels: **[fetched]** the page or PDF was opened and supports the claim; **[book]** a standard book citation, not read for this note; **[unverified]** commonly claimed, not confirmed by an opened source.

## 1. What the evidence says

### DBT diary card

- **One week, one sheet, one row per day.** The University of Washington clinic card (Linehan's clinic) rates each day's *highest* urges and emotions on 0–5, logs actions yes/no, rates skills use on a 0–7 scale ("0 = Not thought about or used … 7 = Didn't try, used them, helped"), and gives each weekday a "Daily Events & Notes" box. [fetched: UW BRTC]
- **It is honest about its own gaps.** The card asks "How often did you fill out this side? Daily / 2-3x / 4-6x / Once". Missing days are normal: in one daily-diary pilot, missing data ranged from 7.7% to 77.3%. [fetched: UW BRTC; NCT07786883 protocol]
- **It opens the session and sets its agenda.** "Begin all individual sessions … with a mindfulness activity and review of the diary card." The card "guides individual therapy, provides weekly progress monitoring" and "facilitates agenda setting and suicide risk assessment". [fetched: Psychotherapy Academy; Wilks et al. 2021]
- **The therapist does the analysis.** A chain analysis "usually begins early in the session, after the therapist has reviewed the client's diary card"; its links are "thoughts, emotions, and behaviors as well as environmental factors", including physiological responses, with urges quoted in the client's words. [fetched: Rizvi & Ritschel 2014]
- **Skills use matters.** It "fully mediated the decrease in suicide attempts and depression" in DBT (measured with a checklist, not the card). [fetched: Neacsiu, Rizvi & Linehan 2010]
- **Adapted, not fixed.** Programs change the card's columns and scales (a college course drops therapeutic targets and keeps skills practice; an autism protocol moves from 5-point scales to 0–100). [fetched: Behavioral Tech; NCT07786883]

### CBT mood monitoring and thought records

- **A CBT session opens with a bridge from the last session, "significant events (positive and/or negative experiences)", the Action Plan review, a mood check, and the client's goals for the session.** [fetched: Beck Institute CTRS-R checklist]
- **Scores, then the person's own words.** Judith Beck reads the scores and asks the client to say "in your own words, how you've been feeling this week"; agenda setting starts with the client's goal. Because "clients who are depressed almost always report only negative situations", she also asks for "the best part of this past week". [fetched: Beck, *Basics and Beyond* 3rd ed., Session 2 transcript]
- **The mood check informs the agenda and is tracked over time** as an indicator of progress. [fetched: Creed, Beck Institute 2019]
- **The thought record** (*Mind Over Mood*, Worksheet 9.2) has seven columns: situation; moods named in one word and rated 0–100%; automatic thoughts, with the **hot thought circled by the person**; evidence for; evidence against; alternative thought with believability; moods re-rated. sintr's entry schema maps onto it field by field. [fetched: Guilford worksheet]
- **Daily records beat recall.** "Retrospective reports are subject to biases"; there are "significant discrepancies between real-time assessments and retrospective self-reports of mood". Recall leans on "the most extreme and recent instances" and on today's mood, and people overestimate past negative emotion, most strongly with a history of depression. Tracked data points work in session as "a memory aid … to recall situations … that otherwise might not have surfaced". [fetched: Trull & Ebner-Priemer 2009; Mareva et al. 2016; Urban et al. 2018; Larsen et al.]

### Pre-session summaries and patient-generated data

- **Measurement-based care helps when the data is reviewed and discussed**: benefit is greater "when both parties understand the data" and "when patterns of data are considered over time"; feedback should be "timely, easy to interpret, specific". Clinicians "typically overestimate how well patients are doing". [fetched: Lewis et al., *JAMA Psychiatry* 2018]
- **Therapists miss decline.** Of 550 clients, therapists flagged 3 as likely to fail; feedback "reduced deterioration rates and nearly doubled" good outcomes for clients predicted to do poorly. [fetched: Lambert & Shimokawa 2011; Lambert, Whipple & Kleinstäuber 2018]
- **Patient data helps "plan the agenda or manage conversations in a visit" — and overwhelms when raw.** Review time in a visit is short (about five minutes in primary care). Patients made their own reports and highlighted entries, and were "frustrated about not being able to focus on the questions in which they were interested". Design for "goal-oriented visualizations or summaries" and let patients "annotate and highlight data with questions or exceptional events". [fetched: Chung et al., CSCW 2016]
- **Barriers run from judging data quality to interpreting it**: aligning objectives, judging data quality, evaluating utility, rearranging data into a clinical format, interpreting, deciding. [fetched abstract: West et al., CHI 2018]
- **Numbers need context.** In mental health, "the relationships between [patient data] and therapeutic progress are often ambiguous", and "options to annotate data may be especially desirable". Clinicians asked for "a dashboard or PDF report demonstrating patterns", since building graphs by hand "would take 20 minutes of the patient session"; "patients like to see the visual, the graph". [fetched: Ng et al., CSCW 2019; Wu et al., JMIR Form Res 2020]
- **AI summaries: highlights, provenance, humility.** Therapists wanted "a 'highlights' version" and access to "clients' own insights", and worried "about the assumptions the AI is making or the connections it draws". Recommendations: "prioritize provenance by default", keep "transparent pathways back to raw entries", "explicitly mark AI-generated insights as suggestions", avoid "definitive judgments or unsolicited therapeutic next steps". (Small pilot.) [fetched: Wang et al., CHI 2026]
- **What hinders in session**: measurement that gets "cumbersome", that pulls "attention … away from the central agenda", or that makes clinicians "miss things that they don't measure"; self-report is "very clearly not just an objective measurement". [fetched: Jonášová et al. 2024; Låver et al. 2024]
- **Where a client's report sits in a clinical note**: in a DAP note, *Data* is what was heard and observed, including the client's quotes; *Assessment* "reflects clinician interpretation". A client-authored report is Data. [fetched: TheraPlatform, vendor guidance]

### Cogni

- **A saved record reads**: date and time → emotions → physiological reactions → situation → thoughts (one can be starred as a "strong thought") → behavior. Body reactions were added in October 2021; records can be shared with professionals, who follow them in a paid clinical dashboard that promises to "make better use of session time". [fetched: App Store listing and screenshots; cogniapp.com text]
- **Not verified**: the input order of the situation and thought screens, whether emotions carry intensities, and the format of the report sent to the therapist (no official source mentions a PDF). [unverified]
- The dashboard's marketing ("discover dysfunctional patterns") is the kind of framing sintr rejects.

## 2. Decisions, section by section

| Part of the report | Decision | Why |
|---|---|---|
| **When** | Prepared `report_lead` (default 1 hour) before each session, from `session_day`/`session_time`, covering the 7 days that end at that moment. Consecutive reports meet exactly, so the evening after a session is never lost and nothing is counted twice. Calendar weeks remain for people without a fixed session. | The owner's call: the report should be fresh for the session. Consistent with the evidence that daily records beat recall and that recall leans on the most recent and extreme moments (Trull & Ebner-Priemer; Mareva): a report made days before the session would itself go stale. |
| **Header** | Dates of the period as the title; the session it is for; check-in coverage ("6 of 7 days · none on Wed"), moments recorded, next session. Confidential, addressed to the therapist. | DBT card's "how often did you fill out this side?"; missing data is normal; judging data quality is a named barrier (West). |
| **1. How the week went** | 3–6 warm lines, page 1. Names the hard moments *and* the best one, with weekday references. No interpretation. | Beck's mood check "in your own words" and "the best part of this past week"; "significant events (positive and/or negative)". |
| **2. For the session** | Page 1, right after the summary. The person's own topics first, in their words; topics the agent proposed and the person kept are labeled *suggested by sintr*. Printed as an open checklist. | Beck starts the agenda with the client's goal; the card "facilitates agenda setting"; Chung: patients' questions get lost; Wang: mark AI suggestions. Moved up from last place, where it risks being read last or not at all. |
| **3. Mood, energy and sleep** | Page 2. Averages **with n** and the week before; a two-panel chart (mood and anxiety on their shared 1–5 scale; hours of sleep) over the last 4 weeks with this week lit; a day-by-day grid; then the day's check-in notes, verbatim. Lines are continuous and smoothed with monotone interpolation, which never overshoots a recorded value; a stretch that crosses days without a check-in is dotted and carries no dot, so the gap stays visible and no value is estimated. Scales say which way is up. Computed by the script, never typed by the agent. | DBT's 7-day grid and Daily Notes; mood tracked over time (Beck, Creed); "patterns … over time", "easy to interpret" (Lewis); therapists miss decline (Lambert); daily data beats recall (EMA); clinicians and patients want the graph (Wu); numbers need context (Ng). Two panels rather than a dual axis, so no correlation is implied. |
| **4. Moments that stood out** | 3–5 moments, opened by one line saying how they were chosen; at least one good moment when there was one. Each card leads with the emotions and their intensities (for scanning), then follows the thought record: what happened, context, thoughts **verbatim**, body, what they did, and — only if the person did that work — evidence, alternative thought with believability, and the re-rate as "70 → 45". The strongest thought is marked only when the person marked it. A core field the entry lacks reads "not recorded". | Thought record columns (*Mind Over Mood*); chain-analysis links (Rizvi & Ritschel); highlighted "exceptional events" (Chung) and memory anchors (Larsen); Cogni's emotion-first record; the person, not the agent, picks the hot thought. |
| **5. What repeated** | Dated co-occurrences only, two or more occurrences each, dates in their own column. No causal verbs, no labels, no computed correlations between measures (the grid lets the therapist read them). | DAP: the report is Data, Assessment is the clinician's; ambiguity of patient data (Ng); worries about AI-drawn connections (Wang). |
| **6. What helped** | What the person recorded as helping, verbatim and dated, with the re-rate numbers when the help was working a thought; homework from the last session noted when it applies. "Helped" only where the person said so or the numbers moved. | DBT skills section and its "tried / helped" scale; skills use as a mechanism of change (Neacsiu); Action Plan review (Beck). |
| **Foot (page 1)** | How it was prepared and reviewed; observations are not diagnoses; not a clinical assessment; highlighted quotes are exact words; suggestions are labeled; **not monitored in real time, not a crisis channel**. | Provenance (Wang); DAP split; self-report is not objective (Låver). |
| **Appendix (opt-in)** | `appendix: true` in the front matter adds every shareable entry of the week, in full, after the report. Off by default. | Therapists want detail for preparation and "pathways back to raw entries" (Wang), but raw volume on the front pages overwhelms (Chung). |

### Revision after the first demo

The owner found the first chart hard to read: straight segments that stopped at every missing day, earlier weeks drawn as faded fragments, oversized rings where two values met. The chart was redrawn as one continuous, smoothed line per measure. The research point stands — **no value is invented for a missing day** — and is kept by the drawing rather than by a hole: the curve is monotone (no peak or dip that is not in the data), the stretch over a missing day is dotted, and only recorded days get a dot. The numbers page was also thinned: each average keeps its number of days and the week before; sleep quality and the daily peak emotion left the grid (the moments carry intensities).

### What was deliberately left out

- DBT's risk-urge columns, target hierarchy, 0–7 skills code and its vocabulary ("target behavior", "chain analysis"): they need a treatment contract and clinical judgment the report does not have.
- Interpretive or diagnostic words ("catastrophizing", "avoidance", "dysfunctional"), causal claims, and advice to the therapist.
- Agent-chosen hot thoughts, rewording of thoughts, averages without their number of days, valence donuts, completion scores.
- Raw data on the front pages.

### Form

- **A PDF, not Markdown.** The therapist reads a document, not a file format; the owner previews exactly what will be sent. The Markdown stays in the ledger as the auditable source.
- **About four pages, five minutes.** Page 1 is a letter (summary, agenda, how to read it); page 2 the numbers; then the moments, what repeated, what helped. No study sets a page limit; the target follows from visit-time findings (Chung) and the request for highlights (Wang).
- **The same page in every viewer.** The PDF carries no transparency: the window light is a pre-rendered image, every color is opaque. (The first version drew the light with soft masks and a blend mode; macOS Preview cut it into a grey band.)
- **Set in the sintr design system** (`DESIGN.md`): serif for the person's words, sans for labels, hairlines instead of boxes, and the peach highlighter reserved for verbatim quotes — so the therapist can always tell the person's words from the assistant's.

## 3. Rules that do not change

- Observations are dated and labeled as observations — **never a diagnosis**.
- The person's words are quoted **verbatim**; the PDF generator checks every quote against the ledger and every moment's intensities against its entry.
- **Nothing invented**: `unknown` stays unknown; a missing day stays empty; a field the entry lacks is "not recorded".
- Entries marked `share: no` are never quoted, summarized, counted, or printed.
- Nothing is sent without the owner's explicit approval, and what is sent is the PDF they previewed.

### Open decision for the owner: safety content

DBT puts life-threatening behavior first. If the week's entries mention self-harm or suicide, the report must not filter or soften it: it is quoted verbatim, dated, and placed first among the moments. But a weekly PDF is not a crisis channel — the crisis protocol in `privacy-and-safety.md` applies at the moment of capture, not at report time. Whether such content should also trigger a direct message to the therapist outside the weekly report is a decision for the owner and their therapist, not for the pack.

## Sources

DBT diary card
- University of Washington BRTC, "How to Complete the Diary Card" and DBT Skills Diary Card (NIMH4 2004; NIDA 1993–98, mod. Dimeff 2008). https://depts.washington.edu/uwbrtc/wp-content/uploads/NIMH4-S-DBT-Diary-Cards-with-Instructions.pdf [fetched]
- Rizvi, S. L., & Ritschel, L. A. (2014). Mastering the Art of Chain Analysis in DBT. *Cognitive and Behavioral Practice*, 21, 335–349. https://www.cbc-psychology.com/uploads/Mastering-the-Art-of-Chain-Analysis-in-Dialectical-Behavior-Therapy.pdf [fetched]
- Wilks, C. R., et al. (2021). A systematic review of DBT mobile apps. *Borderline Personality Disorder and Emotion Dysregulation*, 8:29. https://pmc.ncbi.nlm.nih.gov/articles/PMC8639404/ [fetched]
- Vaughn, S. DBT Individual Session Overview. Psychotherapy Academy. https://psychotherapyacademy.org/courses/dbt-training-online/modules/dbt-individual-therapy-overview/section/individual-session-overview/ [fetched]
- Sonkiss, J. Dialectical Behavior Therapy: A Primer. *The Carlat Report*. https://www.thecarlatreport.com/articles/2034-dialectical-behavior-therapy-a-primer [fetched]
- Behavioral Tech. DBT with College Students (Part 2). https://behavioraltech.org/dbt-with-college-students-part-2/ [fetched]
- Neacsiu, A. D., Rizvi, S. L., & Linehan, M. M. (2010). DBT skills use as a mediator and outcome of treatment for BPD. *Behav Res Ther*, 48(9). https://pmc.ncbi.nlm.nih.gov/articles/PMC2914145 [fetched]
- Helweg-Joergensen, S., et al. (2019). Mobile diary app in the treatment of BPD. *JMIR Formative Research*, 3(3):e12852. https://pmc.ncbi.nlm.nih.gov/articles/PMC6792028 [fetched]
- Laursen, S. L., et al. (2021). Mobile diary app vs. paper diary cards for BPD. *JMIR*, 23(11):e28874. https://pmc.ncbi.nlm.nih.gov/articles/PMC8663638 [fetched]
- Study protocol NCT07786883, DBT for autistic adults. https://cdn.clinicaltrials.gov/large-docs/83/NCT07786883/Prot_000.pdf [fetched]
- Linehan, M. M. (1993). *Cognitive-Behavioral Treatment of Borderline Personality Disorder*. Guilford. [book]
- Linehan, M. M. (2015). *DBT Skills Training Manual* (2nd ed.) and *Handouts and Worksheets*. Guilford. [book] — the exact emotion columns of its diary card were not verified.

CBT
- Beck Institute (2022). CTRS-R Scoring Rubric and CBT Session Checklist. https://beckinstitute.org/wp-content/uploads/2022/09/Beck-Institute-CTRS-R-Scoring-Rubric-and-CBT-Checklist.pdf [fetched]
- Beck, J. Session 2 annotated transcript, from *Cognitive Behavior Therapy: Basics and Beyond* (3rd ed.). https://beckinstitute.org/wp-content/uploads/2021/06/BB3-Session-2-Annotated-Transcript.pdf [fetched]
- Creed, T. A. (2019). Clinical Measures in CBT – A Hassle or a Help? https://beckinstitute.org/blog/clinical-measures-in-cbt-a-hassle-or-a-help/ [fetched]
- Greenberger, D., & Padesky, C. A. *Mind Over Mood* (2nd ed.), Worksheet 9.2, Thought Record. https://www.guilford.com/add/greenberger/MOM2-worksheet-9-2.pdf?t=1 [fetched]
- Trull, T. J., & Ebner-Priemer, U. W. (2009). Using ESM/EMA in clinical assessment and research. *Psychological Assessment*, 21(4). https://pmc.ncbi.nlm.nih.gov/articles/PMC4255457 [fetched]
- Mareva, S., et al. (2016). EMA of HRQoL using a smartphone app (protocol). *Frontiers in Psychology*, 7:1086. https://pmc.ncbi.nlm.nih.gov/articles/PMC4947580 [fetched]
- Urban, E. J., et al. (2018). Depression history and memory bias for specific daily emotions. *PLoS One*, 13(9):e0203574. https://pmc.ncbi.nlm.nih.gov/articles/PMC6128594/ [fetched]
- Larsen, J. E., Christiansen, T. B., & Eskelund, K. Fostering bilateral patient-clinician engagement in active self-tracking of subjective experience. https://arxiv.org/pdf/1801.06352 [fetched]
- Beck, J. S. (2021). *Cognitive Behavior Therapy: Basics and Beyond* (3rd ed.). Guilford. [book]
- Shiffman, S., Stone, A. A., & Hufford, M. R. (2008). Ecological momentary assessment. *Annual Review of Clinical Psychology*, 4, 1–32. [book-style citation, not fetched]

Pre-session summaries and patient-generated data
- Lewis, C. C., et al. (2018). Implementing measurement-based care in behavioral health: a review. *JAMA Psychiatry*. https://pmc.ncbi.nlm.nih.gov/articles/PMC6584602/ [fetched]
- Lambert, M. J., Whipple, J. L., & Kleinstäuber, M. (2018). Collecting and delivering progress feedback: a meta-analysis of routine outcome monitoring. *Psychotherapy*, 55(4), 520–537. https://digitalcommons.usu.edu/psych_facpub/1871 [fetched]
- Lambert, M. J., & Shimokawa, K. Collecting client feedback. https://clinica.ispa.pt/sites/default/files/5lambert2011.pdf [fetched; journal details unverified]
- Chung, C.-F., et al. (2016). Boundary negotiating artifacts in personal informatics: patient-provider collaboration with patient-generated data. CSCW '16. https://pmc.ncbi.nlm.nih.gov/articles/PMC5432205 [fetched]
- West, P., et al. (2018). Common barriers to the use of patient-generated data across clinical settings. CHI '18. DOI 10.1145/3173574.3174058 [fetched abstract]
- Ng, A., et al. (2019). Provider perspectives on integrating sensor-captured patient-generated data in mental health care. *PACM HCI* 3 (CSCW). https://pmc.ncbi.nlm.nih.gov/articles/PMC7877802 [fetched]
- Wu, D. T. Y., et al. (2020). Clinician perspectives and design implications in using patient-generated health data to improve mental health practices. *JMIR Formative Research*, 4(8):e18123. https://pmc.ncbi.nlm.nih.gov/articles/PMC7442947/ [fetched]
- Wang, Y., et al. (2026). Exploring customizable interactive tools for therapeutic homework support in mental health counseling. CHI '26. https://arxiv.org/html/2601.18179 [fetched]
- Jonášová, K., et al. (2024). Psychotherapists' experience with in-session use of routine outcome monitoring: a qualitative meta-analysis. *Adm Policy Ment Health*. https://pmc.ncbi.nlm.nih.gov/articles/PMC11703987/ [fetched]
- Låver, J., et al. (2024). Therapists' and patients' experiences of using patients' self-reported data in ongoing psychotherapy processes. *Psychotherapy Research*, 34(3), 293–310. https://pure.psu.edu/en/publications/therapists-and-patients-experiences-of-using-patients-self-report/ [fetched abstract page]
- TheraPlatform. DAP notes. https://www.theraplatform.com/blog/343/dap-notes [fetched; vendor guidance]

Cogni
- Apple App Store, Cogni (US and BR listings, screenshots, version history). https://apps.apple.com/us/app/id902479424 · https://apps.apple.com/br/app/cogni/id902479424 [fetched]
- Cogni official site and its text (`/assets/i18n/en-US.json`, `/assets/i18n/pt-BR.json`). https://cogniapp.com/ [fetched]
