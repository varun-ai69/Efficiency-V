# AI Healthcare Companion

## System Design & Implementation Roadmap

# Problem Statement

## Background

Access to timely primary healthcare and self-management support remains
a significant challenge, especially in semi-urban and rural India. Many
patients either:

-   Visit hospitals for conditions that can safely be managed at home.
-   Delay treatment for genuinely serious conditions.
-   Lack continuous support for chronic diseases such as:
    -   Type 2 Diabetes
    -   Hypertension
    -   Asthma

Current healthcare systems are reactive rather than proactive. Most
symptom checkers only suggest possible diseases, while chronic disease
apps simply store data without providing intelligent insights.

Our objective is to build an **AI-powered Healthcare Companion** that
assists users in both **acute symptom triage** and **long-term chronic
disease management** while remaining usable in low-bandwidth
environments with a privacy-first architecture.

------------------------------------------------------------------------

# Official Problem Requirements

The solution must:

1.  Accept patient-entered symptoms with optional vitals.
2.  Recommend one of three triage levels:
    -   Home Care
    -   Consult within 48 Hours
    -   Proceed Immediately to Healthcare Facility
3.  Explain the recommendation in plain language.
4.  Highlight emergency red flags.
5.  Show prediction confidence/uncertainty.
6.  Track one chronic disease through daily patient logs.
7.  Detect trends and generate personalized nudges.
8.  Generate a weekly clinician summary (PDF/HTML).
9.  Operate in low-bandwidth environments.
10. Follow a privacy-first architecture.
11. (Optional) Support multilingual and WhatsApp/voice interfaces.

------------------------------------------------------------------------

# Our Vision

We are **NOT building another chatbot**.

We are building a **production-style AI Healthcare Platform** consisting
of two independent but connected AI systems:

1.  Intelligent Symptom Triage Engine
2.  Chronic Disease Management Engine

Both share the same backend, authentication, storage, privacy, and
deployment infrastructure.

------------------------------------------------------------------------

# Phase 1 --- AI Symptom Triage System

## Objective

Given a patient's symptoms, determine the appropriate urgency level.

The model **does not diagnose diseases**.

Instead, it predicts:

-   Home Care
-   Consult within 48 Hours
-   Immediate Medical Attention

------------------------------------------------------------------------

# Overall Workflow

Patient Registration/Login

↓

Basic Profile Collection

↓

Symptom Conversation

↓

Sentence Embedding

↓

Semantic Template Retrieval

↓

Dynamic Question Flow

↓

Feature Engineering

↓

Machine Learning Prediction

↓

Explainability

↓

LLM Explanation

↓

Final Recommendation

------------------------------------------------------------------------

# Step 1 --- Patient Registration

The first interaction collects persistent patient information.

Example fields:

-   Name
-   Age
-   Gender
-   Height
-   Weight
-   Existing diseases
-   Current medications
-   Allergies
-   Emergency contact (optional)

These details are stored securely and reused for future sessions.

------------------------------------------------------------------------

# Step 2 --- Symptom Conversation

Instead of immediately predicting from the first user message, the
system first understands the user's complaint.

Example:

"I have chest pain and difficulty breathing."

------------------------------------------------------------------------

# Step 3 --- Sentence Transformer

Model:

-   BAAI/bge-small-en-v1.5 (preferred) OR
-   all-MiniLM-L6-v2

Purpose:

Convert the user's natural language into a semantic embedding.

This enables semantic understanding rather than keyword matching.

------------------------------------------------------------------------

# Step 4 --- Symptom Template Retrieval

We maintain approximately 20 Chief Complaint Templates.

Examples:

-   Chest Pain
-   Fever
-   Headache
-   Abdominal Pain
-   Cough
-   Breathing Difficulty
-   Vomiting
-   Urinary Problems
-   Skin Problems
-   Trauma
-   etc.

Using FAISS:

Embedding

↓

Nearest Template

↓

Selected Question Flow

------------------------------------------------------------------------

# Step 5 --- Dynamic Question Engine

Every template contains structured follow-up questions.

Example (Chest Pain):

-   Duration?
-   Severity?
-   Radiating pain?
-   Sweating?
-   Difficulty breathing?
-   Existing heart disease?
-   Blood pressure?
-   Oxygen saturation (optional)

The engine asks only missing questions.

------------------------------------------------------------------------

# Step 6 --- Feature Builder

Conversation

↓

Structured Feature Vector

Example:

-   Age
-   Gender
-   Symptom
-   Duration
-   Severity
-   Temperature
-   Heart Rate
-   Blood Pressure
-   SpO₂
-   Medical History
-   Medication History

This standardized vector becomes the ML model input.

------------------------------------------------------------------------

# Step 7 --- Machine Learning Model

Recommended:

-   XGBoost Classifier

Output:

-   Home Care
-   Consult within 48 Hours
-   Immediate Medical Attention

The model also provides:

-   Prediction confidence
-   Feature importance (SHAP)

------------------------------------------------------------------------

# Step 8 --- Explainability

SHAP identifies which patient features most influenced the prediction.

Example:

High importance:

-   Chest Pain
-   Severe Pain
-   Difficulty Breathing

------------------------------------------------------------------------

# Step 9 --- LLM Explanation

The LLM **never makes the medical decision**.

It only receives:

-   Prediction
-   Confidence
-   Important Features

The LLM generates:

-   Plain-language explanation
-   Red flag warning
-   Recommended next step
-   Safety disclaimer

------------------------------------------------------------------------

# Phase 1 Technology Stack

Frontend

-   React
-   PWA
-   IndexedDB

Backend

-   FastAPI

AI

-   Sentence Transformers
-   FAISS
-   XGBoost
-   SHAP
-   LLM (Explanation)

Storage

-   Redis
-   PostgreSQL

Security

-   JWT
-   HTTPS
-   Consent-based storage

------------------------------------------------------------------------

# Phase 2 --- Chronic Disease Management

## Objective

Monitor patients over time rather than diagnosing disease.

Target condition (initial):

-   Type 2 Diabetes

------------------------------------------------------------------------

# Daily Workflow

Patient

↓

Daily Health Log

↓

Trend Engine

↓

Risk Analysis

↓

Personalized Nudges

↓

Weekly Summary

------------------------------------------------------------------------

# Daily Metrics

Examples:

-   Morning glucose
-   Evening glucose
-   Medication adherence
-   Exercise
-   Diet
-   Water intake
-   Symptoms

------------------------------------------------------------------------

# Trend Engine

Detects:

-   Increasing glucose trend
-   Decreasing trend
-   High variability
-   Poor medication adherence
-   Poor exercise adherence

------------------------------------------------------------------------

# Risk Engine

Using historical logs, estimate:

-   Low Risk
-   Medium Risk
-   High Risk

Future versions may include forecasting.

------------------------------------------------------------------------

# Weekly Clinician Report

Automatically generate:

-   Average glucose
-   Highest / Lowest
-   Trend
-   Medication adherence
-   Exercise adherence
-   Symptoms
-   Risk level
-   AI-generated summary

Export:

-   PDF
-   HTML

------------------------------------------------------------------------

# Low-Bandwidth Design

-   Progressive Web App (PWA)
-   IndexedDB offline storage
-   Background synchronization
-   Small API payloads
-   Gzip compression
-   Cached assets

Users can continue using the application without continuous internet
connectivity.

------------------------------------------------------------------------

# Privacy-First Architecture

-   JWT Authentication
-   HTTPS
-   Consent-based storage
-   Minimal data collection
-   UUID-based patient identifiers
-   Redis for temporary conversation state
-   PostgreSQL for permanent records
-   LLM receives anonymized medical context only

------------------------------------------------------------------------

# Production Backend Architecture

React PWA

↓

FastAPI

↓

API Layer

↓

Service Layer

↓

AI Layer

-   Embedding Service
-   FAISS Retrieval
-   Question Engine
-   Feature Builder
-   Prediction Service
-   SHAP Service
-   Explanation Service

↓

Repository Layer

↓

Redis + PostgreSQL

------------------------------------------------------------------------

# Future Enhancements

-   Multilingual Support
-   Voice Assistant
-   WhatsApp Integration
-   Fine-tuned Medical Sentence Transformer
-   Better clinical datasets
-   Continuous model monitoring
-   Clinician Dashboard
-   Model versioning
-   MLOps pipeline

------------------------------------------------------------------------

# End Goal

Rather than building a chatbot, our objective is to build a modular,
production-style AI healthcare platform that combines:

-   Intelligent symptom triage
-   Longitudinal chronic disease monitoring
-   Explainable AI
-   Privacy-first architecture
-   Offline-first usability
-   Scalable backend design

This architecture is designed to be extensible, maintainable, and
suitable for future deployment beyond the hackathon prototype.
