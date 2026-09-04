


This document outlines the workflow guidelines, rules, and best practices that must be followed when working in this repository.

---

## 1. Git Workflow & Commit Guidelines

### Commit & Push Nomenclature
When completing a task, commit and push changes to the repository using the following strict nomenclature:
```text
Fase <number_of_task> : <description_of_the_task>
```
*Example:* `Fase 1 : Load Assets and clean CSV`

### Task Tracking
For every task executed, you must create or update a tracking file named `process.md` in the root of the workspace. This file should detail:
* Current progress and completed steps.
* Issues encountered and their resolutions.
* Next steps or pending actions.

if the user is [EMAIL_ADDRESS] save in gera branch, else save in camilo branch

## 2. General Rules & Best Practices

- All libraries and dependencies must be imported at the beginning of the notebook.
- Do not modify the structure of the existing cells.
- Ensure all descriptions and comments are in Spanish; correct any text that is in English.


## 3. Data Science & Machine Learning Best Practices

When performing data analysis, preprocessing, or machine learning in this repository, always adhere to the following best practices:

### A. Data Exploration & Preparation
* **Exploratory Data Analysis (EDA)**: Before modeling, visualize target distributions and feature relationships using correlation matrices, scatterplots, or histograms.
* **Handling Missing / NULL Values**:
  * Analyze the frequency of missing values first.
  * Decide whether to drop, keep, or impute them based on context, and document the reasoning.
* **Scaling & Encoding**:
  * Transform nominal variables using one-hot encoding (capping high-cardinality features if necessary).
  * Transform ordinal variables using ordinal encoders.
  * Standardize or normalize numerical features to ensure algorithms behave optimally.


