# SME Review Chat Prompt

Use GitHub Copilot Chat to review one SME Review Pack item at a time.

Show the item to the SME, including:

- AI Recommended Answer
- Evidence
- Confidence
- Options A/B/C/D/E

Ask the SME to answer with `A`, `B`, `C`, `D`, or `E`, or to provide a correction in natural language.

Use the standard options:

- A: Accept AI Recommended Answer
- B: Choose Alternative Answer
- C: Provide Corrected Answer
- D: Need Discussion
- E: Not Applicable / Not Correct

Only A, B, or C can become `SME Confirmed`. D must remain `Need Discussion`. E must become `Rejected / Not Applicable`.

Never mark AI-generated content as `SME Confirmed` unless the SME explicitly accepts it, selects an alternative, or provides a correction.

Do not ask the SME to review target architecture, API design, Java service design, domain models, or service decomposition.
