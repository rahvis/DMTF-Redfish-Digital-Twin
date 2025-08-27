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

5. Main App and Demos (`main.py`, `demo.py`)
   - `main.py`: interactive menu to run scenarios, generate custom devices, simulate operations, and produce recordings.
   - `demo.py`: automated end-to-end run including generation and automatic recording creation.

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
- `demo.py`                 Automated end-to-end demo
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
python demo.py
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
  ai-digital-twin-demo:latest python demo.py
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


Demo
----

```
rahulvishwakarma@MacBookAir digital-twin-demo % python demo.py 
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ AI-Driven Digital Twin - Comprehensive Demo                                                                                      │
│ SNIA SDC 2025 - Rahul Vishwakarma                                                                                                │
│ Leveraging DMTF Redfish 2025.2 Specifications                                                                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────────────────────────────────────── System Startup ─────────────────────────────────────────────────────────╮
│ AI-Driven Digital Twin System Initialization                                                                                     │
│ Loading DMTF Redfish 2025.2 specifications and Azure OpenAI components...                                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
✓ All components initialized successfully

Initializing system... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   0% -:--:--📋 Redfish Profile Analysis
  Analyzing available DMTF Redfish mockup profiles
Initializing system... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   0% -:--:--📋 Specification Loading
  Loading Redfish schemas and validation rules
Initializing system... ━━━━━╺━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  12% -:--:--📋 AI Model Preparation
  Configuring Azure OpenAI GPT for device generation
Initializing system... ━━━━━━━━━━╺━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  25% 0:00:04📋 Demo Scenario Setup
  Preparing comprehensive infrastructure scenarios
Initializing system... ━━━━━━━━━━━━━━━╺━━━━━━━━━━━━━━━━━━━━━━━━  38% 0:00:03📋 Live Generation
  Generating digital twin devices in real-time
Initializing system... ━━━━━━━━━━━━━━━━━━━━╺━━━━━━━━━━━━━━━━━━━  50% 0:00:03📋 Validation Pipeline
  Running compliance checks and validation
Initializing system... ━━━━━━━━━━━━━━━━━━━━━━━━━╺━━━━━━━━━━━━━━  62% 0:00:02📋 Recording Generation
  Creating Redfish-compliant output structures
Initializing system... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╺━━━━━━━━━  75% 0:00:02📋 Results Analysis
  Analyzing generation success rates and compliance
Initializing system... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:04

✓ System ready for demonstration!

╭──────────────────────────────────────────────────────── Profile Analysis ────────────────────────────────────────────────────────╮
│ Step 1: Redfish Profile Overview                                                                                                 │
│ Exploring available DMTF Redfish mockup profiles                                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Found 9 Redfish profiles from DSP2043_2025.2 bundle
                                        Available Redfish Profiles                                         
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Profile              ┃ Description                                                ┃ Resources           ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ public-localstorage  │ Local storage infrastructure with controllers and drives   │ Systems, Chassis... │
│ public-bladed        │ Blade server infrastructure with compute and storage       │ Systems, Chassis... │
│ public-rackmount1    │ Standard rackmount server infrastructure                   │ Systems, Chassis... │
│ public-tower         │ Tower server infrastructure for small deployments          │ Systems, Chassis... │
│ public-composability │ Composable infrastructure with dynamic resource allocation │ Systems, Chassis... │
└──────────────────────┴────────────────────────────────────────────────────────────┴─────────────────────┘
... and 4 more profiles available

╭────────────────────────────────────────────────────────── Storage Demo ──────────────────────────────────────────────────────────╮
│ Step 2: Storage Infrastructure Demo                                                                                              │
│ Generating storage controllers, drives, and volumes using AI                                                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Running enterprise storage infrastructure scenario...
╭───────────────────────────────────────────────────────── Demo Scenario ──────────────────────────────────────────────────────────╮
│ Enterprise Storage Infrastructure                                                                                                │
│ High-performance, scalable, enterprise-grade storage infrastructure with advanced features                                       │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Generating StorageController devices...
✓ Generated valid StorageController instance 1 using public-localstorage profile
✓ Generated valid StorageController instance 2 using public-localstorage profile
✓ Generated valid StorageController instance 3 using public-localstorage profile
  Generating 3 storagecontroller device(s) using public-localstorage profile...
✓ Generated 3 StorageController devices using public-localstorage profile
  Validation: 3/3 valid

Generating Drive devices...
✓ Generated valid Drive instance 1 using public-localstorage profile
✓ Generated valid Drive instance 2 using public-localstorage profile
✓ Generated valid Drive instance 3 using public-localstorage profile
  Generating 3 drive device(s) using public-localstorage profile...
✓ Generated 3 Drive devices using public-localstorage profile
  Validation: 3/3 valid

Generating Volume devices...
✓ Generated valid Volume instance 1 using public-localstorage profile
✓ Generated valid Volume instance 2 using public-localstorage profile
✓ Generated valid Volume instance 3 using public-localstorage profile
  Generating 3 volume device(s) using public-localstorage profile...
✓ Generated 3 Volume devices using public-localstorage profile
  Validation: 3/3 valid

Generating StoragePool devices...
✓ Generated valid StoragePool instance 1 using public-localstorage profile
✓ Generated valid StoragePool instance 2 using public-localstorage profile
✓ Generated valid StoragePool instance 3 using public-localstorage profile
  Generating 3 storagepool device(s) using public-localstorage profile...
✓ Generated 3 StoragePool devices using public-localstorage profile
  Validation: 3/3 valid

Scenario Results: enterprise_storage
                        Generation Summary                         
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Resource Type     ┃ Count ┃ Profile             ┃ Status        ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ StorageController │ 3     │ public-localstorage │ ✓ 3 generated │
│ Drive             │ 3     │ public-localstorage │ ✓ 3 generated │
│ Volume            │ 3     │ public-localstorage │ ✓ 3 generated │
│ StoragePool       │ 3     │ public-localstorage │ ✓ 3 generated │
└───────────────────┴───────┴─────────────────────┴───────────────┘

Overall Statistics:
  Total Devices Generated: 12
  Total Valid Devices: 12
  Success Rate: 100.0%
  Profiles Used: public-localstorage, public-nvmeof-jbof, public-sasfabric
✓ Recording generated: output/recordings/StorageController_StorageController_20250827_020605
StorageController_StorageController_20250827_020605
├── index.json
├── metadata.json
└── redfish/
    └── v1/
        └── Storage/
            └── 1/
                └── Controllers/
                    ├── 1/
                    ├── 2/
                    ├── 3/
                    └── index.json
Recording saved: output/recordings/StorageController_StorageController_20250827_020605
✓ Recording generated: output/recordings/Drive_Drive_20250827_020605
Drive_Drive_20250827_020605
├── index.json
├── metadata.json
└── redfish/
    └── v1/
        └── Storage/
            └── 1/
                └── Drives/
                    ├── 1/
                    ├── 2/
                    ├── 3/
                    └── index.json
Recording saved: output/recordings/Drive_Drive_20250827_020605
✓ Recording generated: output/recordings/Volume_Volume_20250827_020605
Volume_Volume_20250827_020605
├── index.json
├── metadata.json
└── redfish/
    └── v1/
        └── Storage/
            └── 1/
                └── Volumes/
                    ├── 1/
                    ├── 2/
                    ├── 3/
                    └── index.json
Recording saved: output/recordings/Volume_Volume_20250827_020605
✓ Recording generated: output/recordings/StoragePool_StoragePool_20250827_020605
StoragePool_StoragePool_20250827_020605
├── index.json
├── metadata.json
└── redfish/
    └── v1/
        └── Storage/
            └── 1/
                └── StoragePools/
                    ├── 1/
                    ├── 2/
                    ├── 3/
                    └── index.json
Recording saved: output/recordings/StoragePool_StoragePool_20250827_020605
╭────────────────────────────────────────────────────────── Compute Demo ──────────────────────────────────────────────────────────╮
│ Step 3: Compute Infrastructure Demo                                                                                              │
│ Generating compute systems and components                                                                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Running high-performance compute infrastructure scenario...
╭───────────────────────────────────────────────────────── Demo Scenario ──────────────────────────────────────────────────────────╮
│ High-Performance Computing Infrastructure                                                                                        │
│ Modern compute infrastructure optimized for performance, scalability, and enterprise workloads                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Generating ComputerSystem devices...
✓ Generated valid ComputerSystem instance 1 using public-rackmount1 profile
✓ Generated valid ComputerSystem instance 2 using public-rackmount1 profile
  Generating 2 computersystem device(s) using public-rackmount1 profile...
✓ Generated 2 ComputerSystem devices using public-rackmount1 profile
  Validation: 2/2 valid

Generating Processor devices...
✓ Generated valid Processor instance 1 using public-rackmount1 profile
✓ Generated valid Processor instance 2 using public-rackmount1 profile
  Generating 2 processor device(s) using public-rackmount1 profile...
✓ Generated 2 Processor devices using public-rackmount1 profile
  Validation: 2/2 valid

Generating Memory devices...
✓ Generated valid Memory instance 1 using public-rackmount1 profile
✓ Generated valid Memory instance 2 using public-rackmount1 profile
✓ Generated valid Memory instance 3 using public-rackmount1 profile
  Generating 3 memory device(s) using public-rackmount1 profile...
✓ Generated 3 Memory devices using public-rackmount1 profile
  Validation: 3/3 valid

Generating NetworkAdapter devices...
✓ Generated valid NetworkAdapter instance 1 using public-rackmount1 profile
✓ Generated valid NetworkAdapter instance 2 using public-rackmount1 profile
✓ Generated valid NetworkAdapter instance 3 using public-rackmount1 profile
  Generating 3 networkadapter device(s) using public-rackmount1 profile...
✓ Generated 3 NetworkAdapter devices using public-rackmount1 profile
  Validation: 3/3 valid

Scenario Results: high_performance_compute
                      Generation Summary                      
┏━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Resource Type  ┃ Count ┃ Profile           ┃ Status        ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ ComputerSystem │ 2     │ public-rackmount1 │ ✓ 2 generated │
│ Processor      │ 2     │ public-rackmount1 │ ✓ 2 generated │
│ Memory         │ 3     │ public-rackmount1 │ ✓ 3 generated │
│ NetworkAdapter │ 3     │ public-rackmount1 │ ✓ 3 generated │
└────────────────┴───────┴───────────────────┴───────────────┘

Overall Statistics:
  Total Devices Generated: 10
  Total Valid Devices: 10
  Success Rate: 100.0%
  Profiles Used: public-rackmount1, public-bladed, public-composability, public-cxl
╭────────────────────────────────────────────────────── Infrastructure Demo ───────────────────────────────────────────────────────╮
│ Step 4: Comprehensive Infrastructure Demo                                                                                        │
│ Generating complete data center infrastructure                                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Generating comprehensive infrastructure...
╭────────────────────────────────────────────────────── Infrastructure Demo ───────────────────────────────────────────────────────╮
│ Comprehensive Infrastructure Generation                                                                                          │
│ Generating complete data center infrastructure...                                                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Generating 2 Chassis devices...
✓ Generated valid Chassis instance 1 using default profile
✓ Generated valid Chassis instance 2 using default profile
  Generating 2 chassis device(s) using default profile...
✓ 2 Chassis devices generated

Generating 4 ComputerSystem devices...
✓ Generated valid ComputerSystem instance 1 using default profile
✓ Generated valid ComputerSystem instance 2 using default profile
✓ Generated valid ComputerSystem instance 3 using default profile
✓ Generated valid ComputerSystem instance 4 using default profile
  Generating 4 computersystem device(s) using default profile...
✓ 4 ComputerSystem devices generated

Generating 2 StorageController devices...
✓ Generated valid StorageController instance 1 using default profile
✓ Generated valid StorageController instance 2 using default profile
  Generating 2 storagecontroller device(s) using default profile...
✓ 2 StorageController devices generated

Generating 8 Drive devices...
✓ Generated valid Drive instance 1 using default profile
✓ Generated valid Drive instance 2 using default profile
✓ Generated valid Drive instance 3 using default profile
✓ Generated valid Drive instance 4 using default profile
✓ Generated valid Drive instance 5 using default profile
✓ Generated valid Drive instance 6 using default profile
✓ Generated valid Drive instance 7 using default profile
✓ Generated valid Drive instance 8 using default profile
  Generating 8 drive device(s) using default profile...
✓ 8 Drive devices generated

Generating 1 Manager devices...
✓ Generated valid Manager instance 1 using default profile
  Generating 1 manager device(s) using default profile...
✓ 1 Manager devices generated

Infrastructure Generation Results
                Infrastructure Components                
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Component ┃ Type              ┃ Count ┃ Status        ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━┩
│ Chassis   │ Chassis           │ 2     │ ✓ 2 generated │
│ Systems   │ ComputerSystem    │ 4     │ ✓ 4 generated │
│ Storage   │ StorageController │ 2     │ ✓ 2 generated │
│ Drives    │ Drive             │ 8     │ ✓ 8 generated │
│ Managers  │ Manager           │ 1     │ ✓ 1 generated │
└───────────┴───────────────────┴───────┴───────────────┘

Overall Statistics:
  Total Devices: 17
  Valid Devices: 17
  Success Rate: 100.0%
  Profile Used: Auto-selected
╭──────────────────────────────────────────────────────── Validation Demo ─────────────────────────────────────────────────────────╮
│ Step 5: Validation and Compliance                                                                                                │
│ Demonstrating Redfish compliance validation                                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Running compliance validation pipeline...
    Compliance Validation Results    
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┓
┃ Metric          ┃ Value  ┃ Status ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━┩
│ Total Devices   │ 25     │ ✓      │
│ Valid Devices   │ 24     │ ✓      │
│ Compliance Rate │ 96.0%  │ ✓      │
│ Redfish Version │ 1.19.0 │ ✓      │
│ Schema Version  │ 2025.2 │ ✓      │
└─────────────────┴────────┴────────┘

✓ All devices pass Redfish schema validation
✓ Required properties present and correctly typed
✓ Value constraints satisfied
✓ Naming conventions followed

╭──────────────────────────────────────────────────────── Impact Analysis ─────────────────────────────────────────────────────────╮
│ Step 6: Benefits and Impact Analysis                                                                                             │
│ Quantifying the value of AI-driven digital twins                                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
                                   AI-Driven Digital Twin Benefits                                   
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ Capability           ┃ Traditional Approach    ┃ AI-Driven Digital Twin       ┃ Improvement       ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ Hardware Required    │ Physical devices needed │ Zero hardware dependency     │ 100% reduction    │
│ Time to Deploy       │ Weeks to months         │ Minutes                      │ 99% faster        │
│ Cost per Prototype   │ $10,000+                │ API costs only (~$0.01)      │ 99.999% cheaper   │
│ Scalability          │ Limited by hardware     │ Unlimited virtual devices    │ Infinite scale    │
│ Edge Cases           │ Difficult to replicate  │ Easy to simulate             │ 100% coverage     │
│ Standards Compliance │ Manual verification     │ Automated validation         │ 100% accuracy     │
│ Profile Support      │ Limited examples        │ Full DMTF mockup integration │ Complete coverage │
└──────────────────────┴─────────────────────────┴──────────────────────────────┴───────────────────┘

╭────────────────────────────────────────────────────────── Architecture ──────────────────────────────────────────────────────────╮
│ Step 7: Technical Architecture Overview                                                                                          │
│ Understanding the system design and components                                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

    System Architecture:
    
    1. DMTF Redfish 2025.2 Integration
       • Direct access to official mockup profiles
       • Schema validation against latest specifications
       • Profile-based device generation
    
    2. AI-Powered Generation Engine
       • Azure OpenAI GPT-4 integration via LangChain
       • Context-aware prompt engineering
       • Multi-retry validation pipeline
    
    3. Comprehensive Validation System
       • JSON schema compliance checking
       • Redfish property validation
       • Data type and constraint verification
    
    4. Recording and Output Management
       • Redfish-compliant folder structures
       • Metadata generation and tracking
       • Export capabilities for integration
    
    Key Technologies:
    • Python 3.13 with modern async capabilities
    • LangChain for LLM orchestration
    • Rich for enhanced terminal experience
    • Pydantic for data validation
    • JSON Schema for compliance checking
    
╭─────────────────────────────────────────────────────────── Conclusion ───────────────────────────────────────────────────────────╮
│ Demo Complete!                                                                                                                   │
│ Thank you for experiencing the AI-Driven Digital Twin demonstration                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
           Demo Summary            
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Metric            ┃ Value       ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ Profiles Explored │ 9           │
│ Devices Generated │ 25          │
│ Compliance Rate   │ 96.0        │
│ Redfish Version   │ 1.19.0      │
│ Demo Duration     │ ~10 minutes │
└───────────────────┴─────────────┘

Next Steps:
• Explore the interactive menu with 'python main.py'
• Generate custom devices for your specific use cases
• Integrate with your existing Redfish infrastructure
• Extend the system with additional device types

Questions? Let's discuss how this can accelerate your development!
```

```
rahulvishwakarma@MacBookAir digital-twin-demo % python main.py 
╭──────────────────────────────────────────────────────────── Welcome ─────────────────────────────────────────────────────────────╮
│                                                                                                                                  │
│         AI-Driven Digital Twin for Storage Devices                                                                               │
│         SNIA SDC 2025 - Demonstration Application                                                                                │
│                                                                                                                                  │
│         Redfish Version: 1.19.0                                                                                                  │
│         Schema Version: 2025.2                                                                                                   │
│         Available Profiles: 9                                                                                                    │
│                                                                                                                                  │
│         This demo showcases how Azure OpenAI GPT can generate                                                                    │
│         Redfish/Swordfish compliant device simulations using official                                                            │
│         DMTF specifications from DSP2043_2025.2.                                                                                 │
│                                                                                                                                  │
│         Key Features:                                                                                                            │
│         • Official Redfish mockup integration                                                                                    │
│         • Multi-profile device generation                                                                                        │
│         • Comprehensive validation pipeline                                                                                      │
│         • Automated demo scenarios                                                                                               │
│         • Real-time infrastructure simulation                                                                                    │
│                                                                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

        Main Menu:
        1. Run Demo Scenarios - Predefined infrastructure demos
        2. Generate Custom Devices - Create specific device types
        3. Comprehensive Infrastructure - Full data center simulation
        4. Simulate Device Operations - Power, reset, maintenance
        5. Explore Redfish Profiles - View available mockup profiles
        6. Validate Existing Recordings - Check compliance
        7. Show Architecture - System design overview
        8. Automated Demo - Hands-free presentation mode
        9. Exit
        
Select an option [1/2/3/4/5/6/7/8/9]: 4

Device Operation Simulation
Sample device loaded for operation simulation
Current status: {'State': 'Enabled', 'Health': 'OK'}

Available operations: power_off, power_on, reset, maintenance, test
Simulate power_off operation? [y/n]: y
✓ Executed operation: power_off
Result: {'State': 'Disabled', 'Health': 'OK'}
Simulate power_on operation? [y/n]: y
✓ Executed operation: power_on
Result: {'State': 'Enabled', 'Health': 'OK'}
Simulate reset operation? [y/n]: y
✓ Executed operation: reset
Result: {'State': 'Enabled', 'Health': 'OK'}
Simulate maintenance operation? [y/n]: y
✓ Executed operation: maintenance
Result: {'State': 'StandbyOffline', 'Health': 'Warning'}
Simulate test operation? [y/n]: y
✓ Executed operation: test
Result: {'State': 'InTest', 'Health': 'OK'}

        Main Menu:
        1. Run Demo Scenarios - Predefined infrastructure demos
        2. Generate Custom Devices - Create specific device types
        3. Comprehensive Infrastructure - Full data center simulation
        4. Simulate Device Operations - Power, reset, maintenance
        5. Explore Redfish Profiles - View available mockup profiles
        6. Validate Existing Recordings - Check compliance
        7. Show Architecture - System design overview
        8. Automated Demo - Hands-free presentation mode
        9. Exit
        
Select an option [1/2/3/4/5/6/7/8/9]: 7
╭────────────────────────────────────────────────────── System Architecture ───────────────────────────────────────────────────────╮
│                                                                                                                                  │
│         ┌─────────────────────────────────────────────────────────────────────────┐                                              │
│         │                    DMTF REDFISH 2025.2 SPECIFICATIONS                  │                                               │
│         │              (Official Mockups from DSP2043_2025.2 Bundle)             │                                               │
│         └─────────────────────────────┬───────────────────────────────────────────┘                                              │
│                                       │                                                                                          │
│                                       ▼                                                                                          │
│         ┌─────────────────────────────────────────────────────────────────────────┐                                              │
│         │                   PROMPT PROCESSOR                                    │                                                │
│         │         (Context Setting + Template Engine + Mockup Integration)       │                                               │
│         └─────────────────────────────┬───────────────────────────────────────────┘                                              │
│                                       │                                                                                          │
│                                       ▼                                                                                          │
│         ┌─────────────────────────────────────────────────────────────────────────┐                                              │
│         │               SIMULATION ENGINE                                        │                                               │
│         │            (LangChain + Azure OpenAI GPT + Profile Selection)             │                                            │
│         └─────────────────────────────┬───────────────────────────────────────────┘                                              │
│                                       │                                                                                          │
│                                       ▼                                                                                          │
│         ┌─────────────────────────────────────────────────────────────────────────┐                                              │
│         │              RESPONSE VALIDATOR                                        │                                               │
│         │         (Schema Validation + Retry Logic + Compliance Checking)        │                                               │
│         └─────────────────────────────┬───────────────────────────────────────────┘                                              │
│                                       │                                                                                          │
│                                       ▼                                                                                          │
│         ┌─────────────────────────────────────────────────────────────────────────┐                                              │
│         │             RECORDING GENERATOR                                        │                                               │
│         │         (Redfish Structure + Metadata + Profile Information)           │                                               │
│         └─────────────────────────────┬───────────────────────────────────────────┘                                              │
│                                       │                                                                                          │
│                                       ▼                                                                                          │
│         ┌─────────────────────────────────────────────────────────────────────────┐                                              │
│         │                  DIGITAL TWIN                                          │                                               │
│         │            (Standards-Compliant Output + Official Mockup Structure)    │                                               │
│         └─────────────────────────────────────────────────────────────────────────┘                                              │
│                                                                                                                                  │
│         Key Innovations:                                                                                                         │
│         • Direct integration with DMTF Redfish 2025.2 specifications                                                             │
│         • Profile-based device generation using official mockups                                                                 │
│         • Multi-scenario demo system for comprehensive demonstrations                                                            │
│         • Real-time validation against official schemas                                                                          │
│         • Automated infrastructure generation                                                                                    │
│                                                                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

        Main Menu:
        1. Run Demo Scenarios - Predefined infrastructure demos
        2. Generate Custom Devices - Create specific device types
        3. Comprehensive Infrastructure - Full data center simulation
        4. Simulate Device Operations - Power, reset, maintenance
        5. Explore Redfish Profiles - View available mockup profiles
        6. Validate Existing Recordings - Check compliance
        7. Show Architecture - System design overview
        8. Automated Demo - Hands-free presentation mode
        9. Exit
        
Select an option [1/2/3/4/5/6/7/8/9]: 1

Demo Scenarios
                                             Available Demo Scenarios for SNIA SDC 2025                                             
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Key                      ┃ Name                        ┃ Focus Areas                 ┃ Target Score ┃ Devices                    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ enterprise_storage       │ Enterprise Storage          │ RAID technologies and data  │ 90           │ StorageController, Drive,  │
│                          │ Infrastructure              │ protection, NVMe and        │              │ Volume...                  │
│                          │                             │ high-speed protocols...     │              │                            │
│ high_performance_compute │ High-Performance Computing  │ Multi-core processor        │ 88           │ ComputerSystem, Processor, │
│                          │ Infrastructure              │ architectures, High-speed   │              │ Memory...                  │
│                          │                             │ memory technologies...      │              │                            │
│ modular_infrastructure   │ Modular and Composable      │ Modular chassis design,     │ 85           │ Chassis, Manager,          │
│                          │ Infrastructure              │ Fabric interconnect         │              │ Fabric...                  │
│                          │                             │ technologies...             │              │                            │
│ edge_computing           │ Edge Computing              │ Edge-optimized form         │ 82           │ ComputerSystem,            │
│                          │ Infrastructure              │ factors, Local storage and  │              │ StorageController,         │
│                          │                             │ processing...               │              │ Drive...                   │
│ cloud_native             │ Cloud-Native Infrastructure │ Automation and              │ 87           │ ComputerSystem,            │
│                          │                             │ orchestration, Scalable     │              │ StorageController, Manager │
│                          │                             │ architecture...             │              │                            │
│ ai_ml_ready              │ AI/ML Ready Infrastructure  │ GPU and accelerator         │ 89           │ ComputerSystem, Processor, │
│                          │                             │ support, High-speed         │              │ Memory...                  │
│                          │                             │ interconnects...            │              │                            │
└──────────────────────────┴─────────────────────────────┴─────────────────────────────┴──────────────┴────────────────────────────┘
Select scenario to run [enterprise_storage/high_performance_compute/modular_infrastructure/edge_computing/cloud_native/ai_ml_ready]:ai_ml_ready

Running AI/ML Ready Infrastructure...
╭───────────────────────────────────────────────────────── Demo Scenario ──────────────────────────────────────────────────────────╮
│ AI/ML Ready Infrastructure                                                                                                       │
│ High-performance infrastructure optimized for artificial intelligence and machine learning workloads                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Generating ComputerSystem devices...
✓ Generated valid ComputerSystem instance 1 using public-rackmount1 profile
✓ Generated valid ComputerSystem instance 2 using public-rackmount1 profile
  Generating 2 computersystem device(s) using public-rackmount1 profile...
✓ Generated 2 ComputerSystem devices using public-rackmount1 profile
  Validation: 2/2 valid

Generating Processor devices...
✓ Generated valid Processor instance 1 using public-rackmount1 profile
✓ Generated valid Processor instance 2 using public-rackmount1 profile
✓ Generated valid Processor instance 3 using public-rackmount1 profile
  Generating 3 processor device(s) using public-rackmount1 profile...
✓ Generated 3 Processor devices using public-rackmount1 profile
  Validation: 3/3 valid

Generating Memory devices...
✓ Generated valid Memory instance 1 using public-rackmount1 profile
✓ Generated valid Memory instance 2 using public-rackmount1 profile
  Generating 2 memory device(s) using public-rackmount1 profile...
✓ Generated 2 Memory devices using public-rackmount1 profile
  Validation: 2/2 valid

Generating StorageController devices...
✓ Generated valid StorageController instance 1 using public-rackmount1 profile
✓ Generated valid StorageController instance 2 using public-rackmount1 profile
✓ Generated valid StorageController instance 3 using public-rackmount1 profile
  Generating 3 storagecontroller device(s) using public-rackmount1 profile...
✓ Generated 3 StorageController devices using public-rackmount1 profile
  Validation: 3/3 valid

Scenario Results: ai_ml_ready
                       Generation Summary                        
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Resource Type     ┃ Count ┃ Profile           ┃ Status        ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ ComputerSystem    │ 2     │ public-rackmount1 │ ✓ 2 generated │
│ Processor         │ 3     │ public-rackmount1 │ ✓ 3 generated │
│ Memory            │ 2     │ public-rackmount1 │ ✓ 2 generated │
│ StorageController │ 3     │ public-rackmount1 │ ✓ 3 generated │
└───────────────────┴───────┴───────────────────┴───────────────┘

Overall Statistics:
  Total Devices Generated: 10
  Total Valid Devices: 10
  Success Rate: 100.0%
  Profiles Used: public-rackmount1, public-composability, public-cxl, public-smartnic
✓ Recording generated: output/recordings/scenario_ai_ml_ready_ComputerSystem_20250827_021721
scenario_ai_ml_ready_ComputerSystem_20250827_021721
├── index.json
├── metadata.json
└── redfish/
    └── v1/
        └── ComputerSystem/
            ├── 1/
            │   └── index.json
            ├── 10/
            │   └── index.json
            ├── 2/
            │   └── index.json
            ├── 3/
            │   └── index.json
            ├── 4/
            │   └── index.json
            ├── 5/
            │   └── index.json
            ├── 6/
            │   └── index.json
            ├── 7/
            │   └── index.json
            ├── 8/
            │   └── index.json
            ├── 9/
            │   └── index.json
            └── index.json
✓ Recording saved to: output/recordings/scenario_ai_ml_ready_ComputerSystem_20250827_021721

        Main Menu:
        1. Run Demo Scenarios - Predefined infrastructure demos
        2. Generate Custom Devices - Create specific device types
        3. Comprehensive Infrastructure - Full data center simulation
        4. Simulate Device Operations - Power, reset, maintenance
        5. Explore Redfish Profiles - View available mockup profiles
        6. Validate Existing Recordings - Check compliance
        7. Show Architecture - System design overview
        8. Automated Demo - Hands-free presentation mode
        9. Exit
        
Select an option [1/2/3/4/5/6/7/8/9]: 9
Exiting...
```
License
-------

This project is provided as-is for demonstration and development purposes. Review and adapt to your licensing needs.

