# MedlinePlus Structured Clinical Dataset

This repository contains a structured JSON dataset of clinical conditions, medical procedures, and health topics extracted from MedlinePlus. The data has been segmented and enriched with clinical metadata to support natural language processing (NLP), Retrieval-Augmented Generation (RAG) pipelines, and healthcare AI applications.

Dataset Version: MedlinePlus Compressed Health Topic XML (4664 K) <br>
[Medline Dataset Download](https://medlineplus.gov/xml/mplus_topics_compressed_2026-10-10.zip)

## Dataset Overview

The dataset transforms standard medical prose into a highly structured format. Each record represents a specific medical topic and isolates key information such as definitions, symptoms, treatments, and emergency red flags, making it optimized for programmatic parsing and machine learning workflows.

## Data Schema

Each entry in the dataset is a JSON object containing the following key-value pairs:

* **`title`** (String): The primary name of the condition, procedure, or health topic (e.g., "A1C", "Acute Bronchitis").
* **`url`** (String): The original MedlinePlus source URL.
* **`also_called`** (Array of Strings): A list of synonyms, acronyms, or common alternative names (e.g., `["Glycohemoglobin", "HbA1C"]`).
* **`clinical_metadata`** (Object): A nested object containing standardized taxonomies:
* **`specialty`** (String): The relevant medical specialty (e.g., "Endocrinology", "Gastroenterology").
* **`icd10_chapter`** (String): The broad ICD-10 categorization for the condition.
* **`body_system`** (String): The primary anatomical system affected.


* **`segmented_fields`** (Object): The core medical text parsed into distinct categories for targeted retrieval:
* **`definition`** (String): A concise explanation of the topic.
* **`symptoms`** (String | Null): Associated signs and clinical symptoms.
* **`treatments_and_prevention`** (String | Null): Medical interventions, therapies, and preventative measures.
* **`general_info`** (String): Additional context, background, or physiological explanations.


* **`red_flags`** (Array of Strings | Null): Critical escalation warnings or emergency symptoms requiring immediate medical attention (e.g., sudden sharp abdominal pain).
* **`structured_thresholds`** (Array of Strings | Null): Explicit medical metrics, diagnostic criteria, or quantitative guidelines (e.g., "A normal A1C level is below 5.7%").
* **`raw_text`** (String): The unparsed, continuous text block from the original source material.

## Primary Use Cases

* **Retrieval-Augmented Generation (RAG)**: The `segmented_fields` allow an LLM to retrieve only the specific section needed (e.g., fetching only "treatments" instead of the whole article) to improve answer precision and reduce prompt noise.
* **Emergency Triage Routing**: The `red_flags` array can be utilized as an application guardrail to instantly detect critical symptoms in user input and route them to emergency care.
* **Entity Resolution**: The `also_called` array provides a robust synonym dictionary for normalizing user queries in search applications.
* **Domain Filtering**: The `clinical_metadata` enables faceted search, allowing applications to filter results dynamically by `specialty` or `body_system`.

## Format

The file is formatted as JSON Lines (JSONL), where each individual line represents a valid, standalone JSON object. This structure allows for efficient streaming, parsing, and processing of large datasets without requiring the entire file to be loaded into memory at once.
