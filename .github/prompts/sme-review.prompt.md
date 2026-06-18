# SME Review Prompt

Use this prompt in GitHub Copilot Chat when reviewing a Markdown SME Review Pack.

Review one item at a time.

For each item:

1. Read the AI Recommended Answer, evidence, and confidence.
2. Ask the SME to choose one option: `A`, `B`, `C`, `D`, or `E`.
3. Accept a natural language correction if the choices are not sufficient.
4. Update the reviewed result in the standard Markdown format.

Use the standard options:

- A: Accept AI Recommended Answer
- B: Choose Alternative Answer
- C: Provide Corrected Answer
- D: Need Discussion
- E: Not Applicable / Not Correct

Apply these rules:

- A, B, or C may become `SME Confirmed`.
- D must remain `Need Discussion` and must not be written to final dictionaries or mappings.
- E must be `Rejected / Not Applicable` and must not be written to final dictionaries or mappings.
- Never mark AI-generated content as `SME Confirmed` unless the SME explicitly chooses A, B, or C, or provides a correction.

Do not ask the SME to validate target architecture, Java service design, API design, domain models, or service decomposition.
