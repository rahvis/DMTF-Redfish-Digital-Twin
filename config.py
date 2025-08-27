import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-04-01-preview')
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4.1')
    AZURE_OPENAI_EMBED_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_EMBED_DEPLOYMENT_NAME', 'text-embedding-3-large')
    
    # Legacy Google Gemini (kept for backward compatibility)
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    TEMPERATURE = float(os.getenv('TEMPERATURE', 0.7))

    # Paths
    SPECS_DIR = 'specifications'
    TEMPLATES_DIR = 'templates'
    EXAMPLES_DIR = 'examples'
    OUTPUT_DIR = 'output/recordings'
    REDFISH_MOCKUPS_DIR = 'DSP2043_2025.2'
    
    # Redfish Configuration
    STRICT_VALIDATION = True
    SCHEMA_VERSION = '2025.2'
    REDFISH_VERSION = '1.19.0'
    
    # Demo Configuration
    DEMO_MODE = os.getenv('DEMO_MODE', 'interactive')  # interactive, automated, presentation
    DEMO_SPEED = float(os.getenv('DEMO_SPEED', '1.0'))  # Speed multiplier for demo
    
    # Available Redfish Mockup Profiles
    REDFISH_PROFILES = [
        'public-localstorage',
        'public-bladed',
        'public-rackmount1',
        'public-tower',
        'public-composability',
        'public-cxl',
        'public-nvmeof-jbof',
        'public-smartnic',
        'public-telemetry'
    ]
    
    # Enhanced Demo Scenarios for SNIA SDC 2025
    DEMO_SCENARIOS = {
        'enterprise_storage': {
            'name': 'Enterprise Storage Infrastructure',
            'description': 'High-performance, scalable, enterprise-grade storage infrastructure with advanced features',
            'profiles': ['public-localstorage', 'public-nvmeof-jbof', 'public-sasfabric'],
            'devices': ['StorageController', 'Drive', 'Volume', 'StoragePool'],
            'focus_areas': [
                'RAID technologies and data protection',
                'NVMe and high-speed protocols',
                'Storage virtualization and pooling',
                'Enterprise management and monitoring',
                'SNIA Swordfish extensions'
            ],
            'target_score': 90
        },
        'high_performance_compute': {
            'name': 'High-Performance Computing Infrastructure',
            'description': 'Modern compute infrastructure optimized for performance, scalability, and enterprise workloads',
            'profiles': ['public-rackmount1', 'public-bladed', 'public-composability', 'public-cxl'],
            'devices': ['ComputerSystem', 'Processor', 'Memory', 'NetworkAdapter'],
            'focus_areas': [
                'Multi-core processor architectures',
                'High-speed memory technologies',
                'Network performance optimization',
                'Virtualization and composability',
                'Power and thermal management'
            ],
            'target_score': 88
        },
        'modular_infrastructure': {
            'name': 'Modular and Composable Infrastructure',
            'description': 'Flexible, scalable infrastructure with modular design and composable capabilities',
            'profiles': ['public-composability', 'public-cxl', 'public-rackmount1'],
            'devices': ['Chassis', 'Manager', 'Fabric', 'Switch', 'Port'],
            'focus_areas': [
                'Modular chassis design',
                'Fabric interconnect technologies',
                'Management and orchestration',
                'Physical security and monitoring',
                'Scalability and growth'
            ],
            'target_score': 85
        },
        'edge_computing': {
            'name': 'Edge Computing Infrastructure',
            'description': 'Distributed, resilient infrastructure optimized for edge workloads and IoT integration',
            'profiles': ['public-tower', 'public-localstorage', 'public-smartnic'],
            'devices': ['ComputerSystem', 'StorageController', 'Drive', 'Chassis'],
            'focus_areas': [
                'Edge-optimized form factors',
                'Local storage and processing',
                'Network connectivity options',
                'Environmental resilience',
                'Remote management'
            ],
            'target_score': 82
        },
        'cloud_native': {
            'name': 'Cloud-Native Infrastructure',
            'description': 'Scalable, automated infrastructure designed for cloud-native workloads and orchestration',
            'profiles': ['public-composability', 'public-rackmount1', 'public-localstorage'],
            'devices': ['ComputerSystem', 'StorageController', 'Manager'],
            'focus_areas': [
                'Automation and orchestration',
                'Scalable architecture',
                'API-driven management',
                'Multi-tenant support',
                'Cloud integration'
            ],
            'target_score': 87
        },
        'ai_ml_ready': {
            'name': 'AI/ML Ready Infrastructure',
            'description': 'High-performance infrastructure optimized for artificial intelligence and machine learning workloads',
            'profiles': ['public-rackmount1', 'public-composability', 'public-cxl', 'public-smartnic'],
            'devices': ['ComputerSystem', 'Processor', 'Memory', 'StorageController'],
            'focus_areas': [
                'GPU and accelerator support',
                'High-speed interconnects',
                'Large memory configurations',
                'Storage performance',
                'Network optimization'
            ],
            'target_score': 89
        }
    }
    
    # Enhanced Template Configuration
    TEMPLATE_FILES = {
        'validation_rules': 'templates/validation_rules.json',
        'device_prompts': 'templates/device_prompts.json',
        'demo_scenarios': 'templates/demo_scenarios.json',
        'presentation_templates': 'templates/presentation_templates.json',
        'quality_metrics': 'templates/quality_metrics.json',
        'enterprise_features': 'templates/enterprise_features.json'
    }
    
    # Quality Assurance Configuration
    QUALITY_THRESHOLDS = {
        'presentation_ready': 75,
        'excellent_quality': 90,
        'enterprise_grade': 85,
        'minimum_compliance': 70
    }
    
    # Presentation Configuration
    PRESENTATION_MODE = {
        'snia_sdc_2025': True,
        'professional_demo': True,
        'audience_engagement': True,
        'live_generation': True,
        'quality_validation': True
    }
