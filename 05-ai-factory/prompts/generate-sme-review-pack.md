# Generate SME Review Pack Prompt

Generate a Markdown SME Review Pack from intake candidates.

For each item, include:

- Item ID
- Type
- Legacy object
- AI Recommended Answer
- Why AI recommends this
- Evidence
- Confidence
- Alternative Answers
- Question for SME
- Options A/B/C/D/E
- SME Selected Option
- SME Corrected Answer
- SME Comment
- Review Status

Use section-based Markdown. Do not use complex Markdown tables.

Use the standard options:

- A: Accept AI Recommended Answer
- B: Choose Alternative Answer
- C: Provide Corrected Answer
- D: Need Discussion
- E: Not Applicable / Not Correct

Keep questions focused on legacy understanding. Do not ask the SME to review target architecture, API design, Java service design, domain models, or service decomposition.
