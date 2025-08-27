AI-Driven Digital Twin for Storage and Datacenter Devices
=========================================================

Overview
--------

This repository provides a standards-compliant, AI-driven Digital Twin system that simulates storage and datacenter devices using DMTF Redfish and SNIA Swordfish specifications. The system leverages Azure OpenAI (via LangChain) to generate realistic resource models, validates them against schemas and policy rules, and writes outputs to a Redfish-compliant folder hierarchy. The generated recordings can be consumed by Redfish-aware tooling as if they were real devices.


Motivation
----------

Modern hardware development faces increasing constraints:

- Limited prototype hardware availability
- Tight schedules and cost pressure
- Expensive test environments and complex edge-case reproduction

These constraints slow validation and integration timelines. The intent of this project is to provide a software-first approach for device modeling that is:

- Standards-compliant (DMTF Redfish 2025.2, SNIA Swordfish)
- Repeatable and configurable
- Capable of simulating realistic and edge-case scenarios without physical hardware


Problem Statement
-----------------

Teams need to design, build, and validate software stacks against hardware that is often not yet available, too limited in quantity, or expensive to deploy at scale. Traditional mocking is brittle, expensive to maintain, and typically diverges from standards over time.


Solution Summary
----------------

This project implements an AI-driven Digital Twin that:

1. Uses official Redfish specifications (schemas, examples, profiles) to ground device generation.
2. Generates resource JSON via Azure OpenAI with prompt templates and example structures.
3. Validates generated outputs using multilayer checks (required fields, data types, value constraints, JSON Schema).
4. Writes results into a Redfish-compliant directory tree so the output resembles real device endpoints.
5. Supports multiple demo scenarios and comprehensive infrastructure generation.


Key Features
------------

- Specification-driven generation
  - Prompts are grounded with Redfish/Swordfish versions and official mockups.
  - Example structures extracted from DSP2043_2025.2 reduce hallucination risk.

- AI-powered device creation via Azure OpenAI
  - Integrates with Azure OpenAI GPT using LangChain.
  - Profile-aware generation for realistic context.

- Multilayer validation and compliance
  - Policy rules: required fields, field types, value constraints (`templates/validation_rules.json`).
  - JSON Schema checks (`specifications/redfish_schemas.json`).
  - Graceful handling of minor type mismatches with scoring and warnings.

- Standards-compliant outputs
  - Redfish folder layout under `output/recordings/.../redfish/v1/...`.
  - Per-resource `index.json` files and collections with `Members`.
  - Metadata and index summaries for each recording.

- Scenario-based generation
  - Predefined scenarios such as `enterprise_storage`, `high_performance_compute`, `modular_infrastructure`, `edge_computing`, `cloud_native`, and `ai_ml_ready` (see `config.py`).
  - Comprehensive infrastructure generation across multiple resource types.

- Template and rules extensibility
  - Prompt templates: `templates/device_prompts.json`
  - Validation rules: `templates/validation_rules.json`
  - Demo scenarios: `templates/demo_scenarios.json` (optional) or `config.py`


Architecture
------------

High-level components:

1. Prompt Processor (`src/prompt_processor.py`)
   - Loads templates and Redfish mockups.
   - Builds context-aware prompts with example structures extracted from DSP2043_2025.2.
   - Minimizes hallucination by including schema version, constraints, and example resource shapes.

2. Simulation Engine (`src/simulation_engine.py`)
   - Orchestrates Azure OpenAI calls via LangChain.
   - Generates single or multiple device instances, profile-aware.
   - Performs validation-retry cycles until conformance is met or retry budget is exhausted.

3. Response Validator (`src/response_validator.py`)
   - Enforces required fields, types, value constraints from `templates/validation_rules.json`.
   - Applies JSON Schema validation (`specifications/redfish_schemas.json`).
   - Produces a compliance score and presentation-readiness flags; treats minor type mismatches as warnings.

4. Recording Generator (`src/recording_generator.py`)
   - Writes generated devices to Redfish-compliant directory trees under `output/recordings`.
   - Creates collection and per-member `index.json` files, plus `metadata.json` and a summary `index.json`.

5. Main App and Demos (`main.py`, `demo_fixed.py`)
   - `main.py`: interactive menu to run scenarios, generate custom devices, simulate operations, and produce recordings.
   - `demo_fixed.py`: automated end-to-end run including generation and automatic recording creation.

Text Diagram:

    DSP2043_2025.2 Profiles + Schemas
                │
                ▼
        Prompt Processor  ──► Example Structures + Context
                │
                ▼
        Simulation Engine ──► Azure OpenAI (LangChain)
                │
                ▼
        Response Validator ──► Policy + JSON Schema Validation
                │
                ▼
        Recording Generator ──► Redfish-Compliant Output Tree


Directory Structure (key paths)
-------------------------------

- `config.py`                      Project configuration (models, paths, scenarios)
- `specifications/`               JSON Schemas and extensions
  - `redfish_schemas.json`
  - `swordfish_extensions.json`
- `DSP2043_2025.2/`               Official Redfish mockups bundle
- `templates/`                    Templates and rules
  - `device_prompts.json`         Prompt templates for device generation
  - `validation_rules.json`       Required fields, types, value constraints, scoring hints
  - `demo_scenarios.json`         Optional scenario definitions
- `src/`
  - `prompt_processor.py`         Context builder and template loader
  - `simulation_engine.py`        Orchestrates generation and validation
  - `response_validator.py`       Validation and scoring
  - `recording_generator.py`      Writes Redfish-compliant outputs
- `output/recordings/`            Generated recordings (timestamped)
- `main.py`                       Interactive application
- `demo_fixed.py`                 Automated end-to-end demo
- `Dockerfile`, `docker-compose.yml`  Containerization and multi-mode runs


Requirements
------------

- Python 3.13
- Azure OpenAI resource with a GPT deployment (e.g., gpt-4.1)


Configuration
-------------

Create a `.env` file in the repository root with the following variables:

```
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-04-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1

# Optional tuning
MAX_RETRIES=3
TEMPERATURE=0.7

# Redfish configuration
REDFISH_VERSION=1.19.0
SCHEMA_VERSION=2025.2
STRICT_VALIDATION=true
```

Ensure the Redfish mockups bundle is available at `DSP2043_2025.2/`.


Local Setup and Run
-------------------

1. Create and activate a virtual environment

```
python -m venv venv
source venv/bin/activate  # macOS/Linux
# .\venv\Scripts\activate  # Windows PowerShell
```

2. Install dependencies

```
pip install --upgrade pip
pip install -r requirements.txt
```

3. Verify configuration

```
python -c "from config import Config; c=Config(); print(c.AZURE_OPENAI_ENDPOINT, c.AZURE_OPENAI_DEPLOYMENT_NAME)"
```

4. Run the interactive app

```
python main.py
```

5. Run the automated end-to-end demo

```
python demo_fixed.py
```

Outputs are written under:

```
output/recordings/<DeviceType_ResourceType_YYYYMMDD_HHMMSS>/redfish/v1/...
```

Each recording contains:

- `redfish/v1/...` resource tree with per-resource `index.json`
- Collection `index.json` with `Members`
- `metadata.json` and a summary `index.json`


Docker Setup and Run
--------------------

1. Build the image

```
docker build -t ai-digital-twin-demo:latest .
```

2. Run automated demo

```
docker run --rm \
  -e AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY \
  -e AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT \
  -e AZURE_OPENAI_API_VERSION=2024-04-01-preview \
  -e AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1 \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/DSP2043_2025.2:/app/DSP2043_2025.2:ro \
  ai-digital-twin-demo:latest python demo_fixed.py
```

3. Run interactive mode

```
docker run -it --rm \
  -e AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY \
  -e AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT \
  -e AZURE_OPENAI_API_VERSION=2024-04-01-preview \
  -e AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1 \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/DSP2043_2025.2:/app/DSP2043_2025.2:ro \
  ai-digital-twin-demo:latest python main.py
```

4. Docker Compose (optional)

```
docker compose up --build
```

Compose profiles include services for automated and interactive runs. Ensure `.env` is present so Compose can forward variables to the container.


How Generation and Validation Work
----------------------------------

1. Prompt building
   - `PromptProcessor` merges device prompts with example structures extracted from the mockups directory.
   - Context includes schema version, required properties, and profile information.

2. LLM invocation
   - `SimulationEngine` sends system and human prompts to Azure OpenAI via LangChain.
   - Responses are parsed and JSON is extracted.

3. Validation pipeline
   - `ResponseValidator` performs rules-based checks and JSON Schema validation.
   - Minor type issues become warnings and reduce the score instead of hard failing.
   - Retries occur up to `MAX_RETRIES` if conformance is not achieved.

4. Recording
   - `RecordingGenerator` writes Redfish-compliant output trees with collections and members.


Extending the System
--------------------

- Add or refine device prompts: edit `templates/device_prompts.json`.
- Tighten or relax validation: edit `templates/validation_rules.json`.
- Add new demo scenarios: update `config.py` or `templates/demo_scenarios.json`.
- Add additional schemas: place new JSON Schemas in `specifications/` and reference them.


Troubleshooting
---------------

- Azure OpenAI authentication errors
  - Verify `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT` in `.env`.
  - Ensure the deployment name exists and model is available.

- No outputs written
  - Confirm `output/recordings` is writable.
  - Ensure `RecordingGenerator` is invoked. The automated demo and interactive scenarios call it automatically.

- Validation failures
  - Review console warnings and errors.
  - Adjust `templates/validation_rules.json` to relax or enforce rules as needed.
  - Check schemas under `specifications/` for property constraints.


License
-------

This project is provided as-is for demonstration and development purposes. Review and adapt to your licensing needs.

