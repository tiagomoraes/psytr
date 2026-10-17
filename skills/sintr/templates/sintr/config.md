# sintr config

Owner preferences. Empty value = not configured. Never invent values.

- name:
- language: en
- timezone:
- checkin_reminders:              # e.g. 09:00, 21:00 (optional)

## Therapy
- therapist_name:
- therapist_contact:              # e.g. a WhatsApp number in international format (+55...)
- session_day:                    # e.g. Wednesday
- session_time:                   # e.g. 18:00
- report_day: Sunday              # day the weekly report is generated
- report_time: 20:00
- require_approval: true          # true = nothing is sent without explicit approval
- report_disclaimer: true         # include the "not a clinical assessment" line

## Privacy
- ledger_share: owner only
