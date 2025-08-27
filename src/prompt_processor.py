import json
import os
from typing import Dict, List, Any, Optional
from langchain.prompts import PromptTemplate
from langchain.prompts.few_shot import FewShotPromptTemplate
from pathlib import Path
import random

class PromptProcessor:
    def __init__(self, config):
        self.config = config
        self.templates = self._load_templates()
        self.specifications = self._load_specifications()
        self.redfish_mockups = self._load_redfish_mockups()
        self.validation_rules = self._load_validation_rules()
        
    def _load_templates(self) -> Dict:
        """Load enhanced prompt templates from JSON files"""
        templates = {}
        
        # Load device prompts
        device_prompts_path = Path(self.config.TEMPLATE_FILES.get('device_prompts', 'templates/device_prompts.json'))
        if device_prompts_path.exists():
            try:
                with open(device_prompts_path, 'r') as f:
                    device_prompts = json.load(f)
                    templates.update(device_prompts)
                    templates['device_prompts'] = device_prompts  # Keep reference to device prompts
            except Exception as e:
                print(f"Warning: Could not load device prompts: {e}")
        
        # Load demo scenarios
        demo_scenarios_path = Path(self.config.TEMPLATE_FILES.get('demo_scenarios', 'templates/demo_scenarios.json'))
        if demo_scenarios_path.exists():
            try:
                with open(demo_scenarios_path, 'r') as f:
                    templates['demo_scenarios'] = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load demo scenarios: {e}")
        
        # Load presentation templates
        presentation_path = Path(self.config.TEMPLATE_FILES.get('presentation_templates', 'templates/presentation_templates.json'))
        if presentation_path.exists():
            try:
                with open(presentation_path, 'r') as f:
                    templates['presentation_templates'] = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load presentation templates: {e}")
        
        # Load quality metrics
        quality_path = Path(self.config.TEMPLATE_FILES.get('quality_metrics', 'templates/quality_metrics.json'))
        if quality_path.exists():
            try:
                with open(quality_path, 'r') as f:
                    templates['quality_metrics'] = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load quality metrics: {e}")
        
        # Load enterprise features
        enterprise_path = Path(self.config.TEMPLATE_FILES.get('enterprise_features', 'templates/enterprise_features.json'))
        if enterprise_path.exists():
            try:
                with open(enterprise_path, 'r') as f:
                    templates['enterprise_features'] = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load enterprise features: {e}")
        
        if not templates:
            return self._get_default_templates()
        
        return templates
    
    def _load_specifications(self) -> Dict:
        """Load Redfish/Swordfish specifications"""
        specs = {}
        specs_dir = Path(self.config.SPECS_DIR)
        for spec_file in specs_dir.glob('*.json'):
            with open(spec_file, 'r') as f:
                specs[spec_file.stem] = json.load(f)
        return specs
    
    def _load_redfish_mockups(self) -> Dict:
        """Load official Redfish mockups from DSP2043_2025.2"""
        mockups = {}
        mockups_dir = Path(self.config.REDFISH_MOCKUPS_DIR)
        
        if not mockups_dir.exists():
            return mockups
            
        for profile in self.config.REDFISH_PROFILES:
            profile_path = mockups_dir / profile
            if profile_path.exists():
                mockups[profile] = self._extract_profile_info(profile_path)
        
        return mockups

    def _load_validation_rules(self) -> Dict:
        """Load validation rules to expose required fields into prompt context"""
        try:
            rules_path = Path(self.config.TEMPLATE_FILES.get('validation_rules', 'templates/validation_rules.json'))
            if rules_path.exists():
                with open(rules_path, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _extract_profile_info(self, profile_path: Path) -> Dict:
        """Extract key information from a Redfish profile"""
        profile_info = {
            'name': profile_path.name,
            'resources': {},
            'examples': {}
        }
        
        # Load main index
        index_file = profile_path / 'index.json'
        if index_file.exists():
            with open(index_file, 'r') as f:
                profile_info['index'] = json.load(f)
        
        # Extract resource examples
        for resource_dir in ['Systems', 'Chassis', 'Managers', 'Storage']:
            resource_path = profile_path / resource_dir
            if resource_path.exists():
                profile_info['resources'][resource_dir] = self._extract_resource_examples(resource_path)
        
        return profile_info
    
    def _extract_resource_examples(self, resource_path: Path) -> Dict:
        """Extract examples from a resource directory"""
        examples = {}
        
        # Look for index.json files
        index_file = resource_path / 'index.json'
        if index_file.exists():
            with open(index_file, 'r') as f:
                examples['collection'] = json.load(f)
        
        # Look for individual resource examples
        for item_dir in resource_path.iterdir():
            if item_dir.is_dir() and not item_dir.name.startswith('$'):
                item_index = item_dir / 'index.json'
                if item_index.exists():
                    with open(item_index, 'r') as f:
                        examples[item_dir.name] = json.load(f)
        
        return examples
    
    def _get_default_templates(self) -> Dict:
        """Default prompt templates for device generation"""
        return {
            "base_prompt": """You are an expert in DMTF Redfish standards and SNIA Swordfish extensions.
Generate a JSON response for a {device_type} that strictly adheres to Redfish specification v{schema_version}.

Context:
{context}

Requirements:
1. Must be valid JSON
2. Must include all required Redfish properties
3. Must use correct data types as per schema
4. Must include realistic values
5. Must follow Redfish naming conventions
6. Must include proper @odata.type and @odata.id values

Example structure from official Redfish mockup:
{example_structure}

Generate a complete JSON response for the {resource_type} resource that follows the exact format above:""",

            "validation_prompt": """Validate the following JSON against Redfish schema requirements:
{json_data}

Check for:
1. Required properties presence
2. Data type correctness
3. Value range validity
4. Schema compliance
5. Redfish naming conventions

Return validation result as JSON with 'valid' boolean and 'errors' array.""",

            "collection_prompt": """Generate a Redfish collection response for {resource_type} containing {count} members.

The collection must follow the standard Redfish collection format with:
- @odata.type for collection
- Members array with @odata.id references
- Members@odata.count property
- Proper Redfish versioning

Example collection structure:
{example_collection}

Generate the collection JSON:""",

            "enhanced_prompt": """As a Redfish/Swordfish expert, create a detailed {device_type} with the following specifications:

Manufacturer: {manufacturer}
Capacity: {capacity}
Protocol: {protocol}
Health Status: {health}
Location: {location}

Ensure all properties follow Redfish v{schema_version} standards.
Include both required and commonly used optional properties.
Use realistic values based on enterprise hardware specifications.

Reference Redfish mockup example:
{example_structure}

Generate complete JSON response:"""
        }
    
    def create_device_prompt(self, device_type: str, resource_type: str, 
                           context: Dict = None, profile: str = None) -> str:
        """Create a prompt for generating a specific device type"""
        template = PromptTemplate(
            input_variables=["device_type", "resource_type", "schema_version", 
                           "context", "example_structure"],
            template=self.templates.get("base_prompt")
        )
        
        # Get example structure from official mockups if available
        example_structure = self._get_example_structure(resource_type, profile)
        
        # Build enhanced context from specifications and mockups
        spec_context = self._build_enhanced_context(device_type, resource_type, profile)
        if context:
            spec_context.update(context)
        
        return template.format(
            device_type=device_type,
            resource_type=resource_type,
            schema_version=self.config.SCHEMA_VERSION,
            context=json.dumps(spec_context, indent=2),
            example_structure=json.dumps(example_structure, indent=2)
        )
    
    def _get_example_structure(self, resource_type: str, profile: str = None) -> Dict:
        """Get example structure from official Redfish mockups"""
        # Try to find in specified profile first
        if profile and profile in self.redfish_mockups:
            profile_data = self.redfish_mockups[profile]
            for resource_category, resources in profile_data.get('resources', {}).items():
                for resource_name, resource_data in resources.items():
                    if resource_name != 'collection' and isinstance(resource_data, dict):
                        if resource_type.lower() in resource_data.get('@odata.type', '').lower():
                            return resource_data
        
        # Fallback to examples directory
        examples = {
            "StorageController": {
                "@odata.type": "#StorageController.v1_0_0.StorageController",
                "@odata.id": "/redfish/v1/Storage/1/Controllers/1",
                "Id": "1",
                "Name": "Storage Controller",
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                },
                "Manufacturer": "Example Corp",
                "Model": "SC-3000",
                "SerialNumber": "2M220100SL"
            },
            "Drive": {
                "@odata.type": "#Drive.v1_0_0.Drive",
                "@odata.id": "/redfish/v1/Storage/1/Drives/1",
                "Id": "1",
                "Name": "Drive 1",
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                },
                "CapacityBytes": 1000000000000,
                "Protocol": "SAS"
            },
            "ComputerSystem": {
                "@odata.type": "#ComputerSystem.v1_19_0.ComputerSystem",
                "@odata.id": "/redfish/v1/Systems/1",
                "Id": "1",
                "Name": "Compute Node 1",
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                },
                "Manufacturer": "Example Corp",
                "Model": "CS-5000",
                "SerialNumber": "2M220100SL"
            }
        }
        return examples.get(resource_type, {})
    
    def _build_enhanced_context(self, device_type: str, resource_type: str, profile: str = None) -> Dict:
        """Build enhanced context from specifications and mockups"""
        context = {
            "device_type": device_type,
            "resource_type": resource_type,
            "redfish_version": self.config.REDFISH_VERSION,
            "schema_version": self.config.SCHEMA_VERSION,
            "required_properties": self.validation_rules.get('required_fields', {}).get(resource_type, []),
            "optional_properties": [],
            "property_types": {},
            "mockup_profile": profile,
            "available_profiles": list(self.redfish_mockups.keys())
        }
        
        # Extract from specifications if available
        if "redfish_schemas" in self.specifications:
            schema = self.specifications["redfish_schemas"].get(resource_type, {})
            if "properties" in schema:
                for prop, details in schema["properties"].items():
                    if details.get("required", False):
                        context["required_properties"].append(prop)
                    else:
                        context["optional_properties"].append(prop)
                    context["property_types"][prop] = details.get("type", "string")
        
        # Add mockup context if profile specified
        if profile and profile in self.redfish_mockups:
            profile_data = self.redfish_mockups[profile]
            context["profile_info"] = {
                "name": profile_data.get('name', profile),
                "available_resources": list(profile_data.get('resources', {}).keys()),
                "redfish_version": profile_data.get('index', {}).get('RedfishVersion', 'Unknown')
            }
        
        return context
    
    def create_validation_prompt(self, json_data: Dict) -> str:
        """Create a prompt for validating generated JSON"""
        template = PromptTemplate(
            input_variables=["json_data"],
            template=self.templates.get("validation_prompt")
        )
        return template.format(json_data=json.dumps(json_data, indent=2))
    
    def create_collection_prompt(self, resource_type: str, count: int, profile: str = None) -> str:
        """Create a prompt for generating Redfish collections"""
        template = PromptTemplate(
            input_variables=["resource_type", "count", "example_collection"],
            template=self.templates.get("collection_prompt")
        )
        
        example_collection = self._get_collection_example(resource_type, profile)
        
        return template.format(
            resource_type=resource_type,
            count=count,
            example_collection=json.dumps(example_collection, indent=2)
        )
    
    def _get_collection_example(self, resource_type: str, profile: str = None) -> Dict:
        """Get collection example from mockups"""
        if profile and profile in self.redfish_mockups:
            profile_data = self.redfish_mockups[profile]
            for resource_category, resources in profile_data.get('resources', {}).items():
                if resource_category.lower() in resource_type.lower():
                    collection_data = resources.get('collection', {})
                    if collection_data:
                        return collection_data
        
        # Fallback example
        return {
            "@odata.type": f"#{resource_type}Collection.{resource_type}Collection",
            "@odata.id": f"/redfish/v1/{resource_type}",
            "Name": f"{resource_type} Collection",
            "Members@odata.count": 1,
            "Members": [
                {
                    "@odata.id": f"/redfish/v1/{resource_type}/1"
                }
            ]
        }
    
    def get_available_profiles(self) -> List[str]:
        """Get list of available Redfish profiles"""
        return list(self.redfish_mockups.keys())
    
    def get_profile_resources(self, profile: str) -> Dict:
        """Get available resources for a specific profile"""
        if profile in self.redfish_mockups:
            return self.redfish_mockups[profile].get('resources', {})
        return {}
    
    def create_enhanced_prompt(self, device_type: str, resource_type: str, 
                             specifications: Dict, profile: str = None) -> str:
        """Create an enhanced prompt with specific device specifications"""
        template = PromptTemplate(
            input_variables=["device_type", "resource_type", "schema_version", 
                           "manufacturer", "capacity", "protocol", "health", "location",
                           "example_structure"],
            template=self.templates.get("enhanced_prompt")
        )
        
        example_structure = self._get_example_structure(resource_type, profile)
        
        return template.format(
            device_type=device_type,
            resource_type=resource_type,
            schema_version=self.config.SCHEMA_VERSION,
            manufacturer=specifications.get('manufacturer', 'Enterprise Corp'),
            capacity=specifications.get('capacity', '1TB'),
            protocol=specifications.get('protocol', 'NVMe'),
            health=specifications.get('health', 'OK'),
            location=specifications.get('location', 'Rack 1, Slot 1'),
            example_structure=json.dumps(example_structure, indent=2)
        )
