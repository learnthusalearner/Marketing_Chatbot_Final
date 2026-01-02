# Agentic Marketing Intelligence System

This document describes a goal-driven, multi-agent marketing chatbot designed to convert natural language prompts into structured, data-backed outputs using an agent orchestration pipeline.

The system is built to handle vague or high-level marketing queries by breaking them down into executable tasks, querying real data from MongoDB, and iteratively refining results until all required information is collected.

---

## Overview

Traditional chatbots rely primarily on text generation. This system focuses on **intent understanding, task planning, and tool-grounded execution**.

It is designed for marketing and growth workflows where accuracy, traceability, and real data matter more than conversational responses.

---

## Architecture

User Prompt
↓
Intent Router
├── Greeting Agent
└── Sequential Agent Pipeline
  ↓
 Intent Elaborator
  ↓
 Task Decomposer
  ↓
 Query Generator Agent
  ↓
 MongoDB Tool (Iterative Execution)
  ↓
 Structured Data Output

---

---

### Flow Summary

- **User Prompt**: Free-form natural language input.
- **Intent Router**: Classifies the input and routes it to the appropriate agent.
- **Greeting Agent**: Handles casual greetings with minimal computation.
- **Sequential Agent Pipeline**: Executes goal-oriented reasoning and data retrieval.
- **Intent Elaborator**: Clarifies objectives and required information.
- **Task Decomposer**: Breaks objectives into executable data tasks.
- **Query Generator Agent**: Converts tasks into MongoDB queries.
- **MongoDB Tool**: Executes queries iteratively until all prerequisites are satisfied.
- **Structured Data Output**: Grounded data ready for insights or reports.

## End-to-End Workflow

1. A user submits a free-text prompt.
2. The Intent Router classifies the input.

   * Greeting intents are routed to the Greeting Agent.
   * Actionable intents are routed to the Sequential Agent Pipeline.
3. The Intent Elaborator extracts the core objective and identifies required information.
4. The Task Decomposer breaks the objective into atomic data-retrieval tasks.
5. The Query Generator Agent converts each task into MongoDB queries.
6. The MongoDB Tool executes queries in a loop, resolving prerequisites such as date, time range, and filters.
7. Structured data is collected for downstream processing or insight generation.

---

## Agents

### Intent Router

Acts as the first decision layer. It classifies user input and routes it to the appropriate agent pipeline to optimize latency and cost.

### Greeting Agent

Handles casual greetings such as hi or hello without invoking the full reasoning and data pipeline.

### Intent Elaborator

Interprets the user’s request, clarifies scope, and determines what information is required to satisfy the intent.

### Task Decomposer

Breaks clarified intent into a sequence of small, executable tasks that define what data needs to be fetched.

### Query Generator Agent

Generates MongoDB queries for each task, taking schema constraints and prerequisites into account.

### MongoDB Tool

Executes queries against the database and returns grounded results. Runs iteratively until all task requirements are satisfied.

---

## Key Characteristics

* Multi-agent orchestration
* Sequential execution with dependency awareness
* Tool-grounded reasoning (no hallucinated data)
* Iterative query refinement
* Optimized routing for performance and cost
* Designed for marketing intelligence and analytics use cases

---

## Example Use Cases

* Campaign performance analysis
* Marketing insight generation
* Launch and engagement data exploration
* Growth trend analysis
* Enterprise-focused marketing intelligence

---

## Tech Stack (High Level)

* Large Language Model (LLM)
* Agent orchestration with sequential execution
* MongoDB for persistent data storage
* Tool-based database querying
* Backend API layer (framework agnostic)

---

## Future Enhancements

* Structured insight and report generation
* Credibility and readiness scoring
* Visual dashboards and summaries
* Multi-tenant support
* Role-specific agent specialization

---

## Project Status

This project currently focuses on the **agentic reasoning and data retrieval layer**. Presentation and UI layers can be built on top of the structured outputs produced by the system.

---
