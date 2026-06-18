# Sample Reviewed SME Pack

## Review Pack Metadata

- Pack ID: `SME-PACK-SAMPLE-001`
- Source Document References: `MAT-SAMPLE-001`, `MAT-SAMPLE-002`
- Created Date: 2026-06-18
- Review Status: SME Reviewed

## Reviewed Item 1

- Item ID: `SME-ITEM-001`
- Type: Program Review
- Legacy object: `ORDENTR`
- AI Recommended Answer: `ORDENTR` appears to be an order entry program used to create or maintain customer orders.
- Why AI recommends this: The program name resembles "order entry", and the sample evidence references order header and order detail file usage.
- Evidence:
  - Source material: `MAT-SAMPLE-002`
  - Observed terms: `ORDER HEADER`, `ORDER DETAIL`, `ENTRY SCREEN`
- Confidence: Medium
- Alternative Answers:
  1. Order inquiry screen program.
  2. Batch order validation program.
  3. Order maintenance program.
- Question for SME: What is the best description of legacy program `ORDENTR`?
- Options:
  - A: Accept AI Recommended Answer
  - B: Choose Alternative Answer
  - C: Provide Corrected Answer
  - D: Need Discussion
  - E: Not Applicable / Not Correct
- SME Selected Option: A
- SME Corrected Answer:
- SME Comment: Accepted. This is the main order entry program.
- Review Status: SME Confirmed

## Reviewed Item 2

- Item ID: `SME-ITEM-002`
- Type: Field Review
- Legacy object: `CUSTNO`
- AI Recommended Answer: `CUSTNO` is the customer number field used to identify the customer associated with an order or account record.
- Why AI recommends this: The field name resembles "customer number", and the sample evidence shows it near order and customer file references.
- Evidence:
  - Source material: `MAT-SAMPLE-001`
  - Observed terms: `CUSTOMER FILE`, `ORDER HEADER`, `CUSTNO`
- Confidence: High
- Alternative Answers:
  1. Billing customer number.
  2. Ship-to customer number.
  3. Customer account number used only for reporting.
- Question for SME: What is the correct meaning of field `CUSTNO`?
- Options:
  - A: Accept AI Recommended Answer
  - B: Choose Alternative Answer
  - C: Provide Corrected Answer
  - D: Need Discussion
  - E: Not Applicable / Not Correct
- SME Selected Option: C
- SME Corrected Answer: `CUSTNO` is the billing customer number. Ship-to customer is stored separately.
- SME Comment: Use billing customer meaning unless the source file specifically says ship-to.
- Review Status: SME Confirmed
