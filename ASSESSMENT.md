## Paid Technical Assessment - Full-Stack Developer (Full-Time Position)

### Project Summary

Thank you for applying to our **Full-Stack Developer** position. As part of our hiring process, we ask candidates to complete a **paid technical assessment**. This is a real, compensated task — not an unpaid take-home test. We value your time and effort regardless of the outcome.

This assessment allows us to evaluate your skills in a practical setting before making a hiring decision.

**You will be paid upon satisfactory completion**, regardless of whether we extend a full-time offer.

---

## About the Project

You will build a **Bulk Shipping Label Creation Platform** — a web application that allows users to:

1. Upload a spreadsheet containing shipping orders
2. Review, validate, and edit the imported data
3. Select shipping providers and services
4. Purchase and generate shipping labels in bulk

The application follows a **4-step wizard flow**:

**Step 1: Upload -> Step 2: Review & Edit -> Step 3: Select Shipping -> Step 4: Purchase**

### Provided Files

* **PRD Document (PRD.md)** — Detailed product requirements
* **Template.csv** — Sample CSV with 100 shipping records (includes intentionally incomplete data)

Please review both files carefully before starting.

---

## AI / LLM Tool Usage

You **ARE allowed** to use AI tools such as:

* ChatGPT
* Claude
* GitHub Copilot
* Cursor
* Any other productivity tools

We care about **results and code quality**, not whether you typed every line manually.
However, you **must understand and be able to explain your code** if asked during the follow-up review.

---

## What We're Evaluating

1. **Creative Design & UX**

   * Clean visual hierarchy
   * Intuitive workflow
   * Thoughtful loading, error, and empty states
   * Best possible user flow — we value design that feels natural and effortless

2. **Validation & Data Handling**

   * The CSV contains missing addresses, weights, and other data
   * Validation rules are **intentionally not defined**
   * You must decide:

     * What's required
     * How errors are handled
     * How issues are communicated to users

3. **Code Quality**

   * Clean architecture
   * Maintainable and well-organized code
   * Proper error handling

4. **Problem Solving**

   * Handling ambiguity
   * Edge cases
   * Third-party API failures

---





### Option : Django + React

* **Django** with **Django REST Framework (DRF)** for the backend
* **React + TypeScript** for the frontend
* REST API

### Database

* Any database:  **SQLite**

**Important:**
All core validation and business logic must be implemented on the **server side** (API routes Django).
Frontend-only or logic-heavy frontend solutions will **not** be accepted.

---

## Address Validation Requirement (Important)

You must integrate a **real address validation API**, such as:

* USPS Address Validation API (free)
* Google Address Validation API
* Smarty (SmartyStreets)
* Lob Address Verification
* Or another reliable service

### Validation Timing

Address validation must occur:
- During CSV upload (Step 1) — validate all addresses after parsing
- During any row edit in Step 2 or Step 3 — re-validate changed addresses
- Step 4 (Purchase) is for label size selection and final confirmation only — no editing allowed

### Handling Validation Failures

When an address fails validation:
- Mark the row with a warning indicator (e.g., yellow highlight, warning icon)
- Allow the user to proceed with the order (do not block)
- Display clear feedback about what failed validation
- If you can integrate an API that provides address auto-correction/suggestions, implementing this feature will be considered a plus.

### Fallback Requirement

If one API fails or hits its free-tier limit, the system must automatically try an alternative.

**Note:** Free-tier API rate limits are expected and acceptable. We want to see how you **handle rate limiting gracefully** — fallback logic, error handling, and user communication matter more than unlimited API access.

This is a key part of the evaluation — we want to see how you design **resilient third-party integrations**.

---

## Deliverables

1. **Live Demo URL** (Required)

   * Hosted by you
   * Must remain live for **at least 2 weeks**

2. **Source Code**

   * Public GitHub repository **or** downloadable zip file

3. **README File**

   * Setup instructions
   * Assumptions made
   * Design and architectural decisions

**No video walkthroughs**
**We need a working live application we can test ourselves**

---

## Compensation

* **Assessment Compensation:** **$70 USD (fixed)**
* This is a **paid assessment task**. We appreciate the time and effort you put into this.
* Payment will be processed **within 3 days after delivery**, provided the submission is complete and functional.
* You will be compensated **regardless of whether we extend a full-time offer**.

> The compensation is fixed for this assessment and is not negotiable.




## Important Assessment Notes (Please Read Carefully)

Before starting the task, please keep the following **critical evaluation criteria** in mind:

### Backend Requirement (Mandatory)

* You must use one of the approved stacks:  **Django with DRF**.
* All core logic must live on the server side. This is **non-negotiable**.


---

### Logging (Highly Important)

* Implement **robust, structured logging** across the entire application flow, including:

  * CSV upload and parsing
  * Data validation and error handling
  * Address verification and fallback logic
  * Bulk actions (edit, delete, shipping selection, purchase)
* Logging quality has a **significant impact on scoring**.
* Logs should be clear, meaningful, and helpful for debugging and production monitoring.

---

### UI / UX (Highest Priority)

* **UI/UX is the most heavily weighted part of this assessment.**
* We are looking for:

  * A modern, clean, and polished design
  * Strong visual hierarchy and spacing
  * Intuitive multi-step flow
  * The best possible user flow — design that feels natural and effortless
  * Thoughtful states:

    * Loading
    * Validation errors
    * Empty states
    * Confirmations and success feedback
* This should feel like a **real production-ready product**, not a rough internal tool.

---

### Product Mindset Matters

This assessment is evaluated as a **real product**, not just a functional demo.

We care deeply about:

* Attention to detail
* Product thinking
* Reasonable assumptions
* Clear UX decisions
* Well-documented trade-offs in the README

A solution that is **polished, thoughtful, and user-centric** will score significantly higher than one that is only technically correct.
