# sintr config

Owner preferences. Empty value = not configured. Never invent values.

- name:
- language: en
- timezone:
- checkin_reminders:              # e.g. 09:00, 21:00 (optional)

## Therapy
- therapist_name:
- therapist_contact:              # e.g. a WhatsApp number in international format (+55...)
- session_day:                    # e.g. Wednesday — the weekly report is prepared before each session
- session_time:                   # e.g. 18:00, in the timezone above
- report_lead: 1h                 # how long before the session the report is prepared
- report_day:                     # only without a fixed session: the day of a calendar-week report
- report_time:                    # and its time
- require_approval: true          # true = nothing is sent without explicit approval
- report_disclaimer: true         # include the "not a clinical assessment" line

## Privacy
- ledger_share: owner only
