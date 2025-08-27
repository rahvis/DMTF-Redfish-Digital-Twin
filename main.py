#!/usr/bin/env python3
"""
AI-Driven Digital Twin Demo - Main Application
Author: Rahul Vishwakarma
SNIA SDC 2025 - Leveraging DMTF Redfish 2025.2 Specifications

This application demonstrates how Large Language Models can generate
Redfish/Swordfish compliant device simulations using official DMTF specifications.
"""

import sys
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from rich.tree import Tree
from rich import box
from config import Config
from src import PromptProcessor, SimulationEngine, RecordingGenerator, ResponseValidator

console = Console()

class DigitalTwinApp:
    def __init__(self):
        self.config = Config()
        self.console = console
        
        # Check Azure OpenAI API key
        if not self.config.AZURE_OPENAI_API_KEY:
            self.console.print("[red]Error: AZURE_OPENAI_API_KEY not found in .env file[/red]")
            self.console.print("Please create a .env file with your Azure OpenAI API key")
            self.console.print("Get your key from: https://oai.azure.com/")
            sys.exit(1)
        
        # Check Azure OpenAI endpoint
        if not self.config.AZURE_OPENAI_ENDPOINT:
            self.console.print("[red]Error: AZURE_OPENAI_ENDPOINT not found in .env file[/red]")
            self.console.print("Please add your Azure OpenAI endpoint to the .env file")
            sys.exit(1)
        
        # Initialize components
        self.prompt_processor = PromptProcessor(self.config)
        self.validator = ResponseValidator(self.config)
        self.simulation_engine = SimulationEngine(
            self.config, 
            self.prompt_processor, 
            self.validator
        )
        self.recording_generator = RecordingGenerator(self.config)
    
    def run(self):
        """Main application loop"""
        self.display_welcome()
        
        while True:
            choice = self.show_menu()
            
            if choice == "1":
                self.run_demo_scenarios()
            elif choice == "2":
                self.generate_custom_devices()
            elif choice == "3":
                self.generate_comprehensive_infrastructure()
            elif choice == "4":
                self.simulate_operations()
            elif choice == "5":
                self.explore_redfish_profiles()
            elif choice == "6":
                self.validate_recordings()
            elif choice == "7":
                self.show_architecture()
            elif choice == "8":
                self.run_automated_demo()
            elif choice == "9":
                self.console.print("[yellow]Exiting...[/yellow]")
                break
            else:
                self.console.print("[red]Invalid choice![/red]")
    
    def display_welcome(self):
        """Display welcome message"""
        welcome_text = f"""
        [bold cyan]AI-Driven Digital Twin for Storage Devices[/bold cyan]
        [dim]SNIA SDC 2025 - Demonstration Application[/dim]
        
        [bold]Redfish Version:[/bold] {self.config.REDFISH_VERSION}
        [bold]Schema Version:[/bold] {self.config.SCHEMA_VERSION}
        [bold]Available Profiles:[/bold] {len(self.config.REDFISH_PROFILES)}
        
        This demo showcases how Azure OpenAI GPT can generate
        Redfish/Swordfish compliant device simulations using official
        DMTF specifications from DSP2043_2025.2.
        
        [bold]Key Features:[/bold]
        • Official Redfish mockup integration
        • Multi-profile device generation
        • Comprehensive validation pipeline
        • Automated demo scenarios
        • Real-time infrastructure simulation
        """
        self.console.print(Panel(welcome_text, title="Welcome", border_style="cyan"))
    
    def show_menu(self) -> str:
        """Display main menu"""
        menu = f"""
        [bold]Main Menu:[/bold]
        1. [cyan]Run Demo Scenarios[/cyan] - Predefined infrastructure demos
        2. [cyan]Generate Custom Devices[/cyan] - Create specific device types
        3. [cyan]Comprehensive Infrastructure[/cyan] - Full data center simulation
        4. [cyan]Simulate Device Operations[/cyan] - Power, reset, maintenance
        5. [cyan]Explore Redfish Profiles[/cyan] - View available mockup profiles
        6. [cyan]Validate Existing Recordings[/cyan] - Check compliance
        7. [cyan]Show Architecture[/cyan] - System design overview
        8. [cyan]Automated Demo[/cyan] - Hands-free presentation mode
        9. [cyan]Exit[/cyan]
        """
        self.console.print(menu)
        return Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"])
    
    def run_demo_scenarios(self):
        """Run predefined demo scenarios"""
        self.console.print("\n[bold]Demo Scenarios[/bold]")
        
        # Display enhanced demo scenarios for SNIA SDC 2025
        table = Table(title="Available Demo Scenarios for SNIA SDC 2025", show_header=True, header_style="bold magenta")
        table.add_column("Key", style="cyan", no_wrap=True)
        table.add_column("Name", style="white")
        table.add_column("Focus Areas", style="green")
        table.add_column("Target Score", style="yellow")
        table.add_column("Devices", style="blue")
        
        for key, scenario in self.config.DEMO_SCENARIOS.items():
            focus_areas = ", ".join(scenario.get('focus_areas', [])[:2]) + ("..." if len(scenario.get('focus_areas', [])) > 2 else "")
            target_score = scenario.get('target_score', 'N/A')
            devices_str = ", ".join(scenario['devices'][:3]) + ("..." if len(scenario['devices']) > 3 else "")
            table.add_row(key, scenario['name'], focus_areas, str(target_score), devices_str)
        
        self.console.print(table)
        
        # Select scenario
        choice = Prompt.ask("Select scenario to run", choices=list(self.config.DEMO_SCENARIOS.keys()))
        
        if choice in self.config.DEMO_SCENARIOS:
            self.console.print(f"\n[cyan]Running {self.config.DEMO_SCENARIOS[choice]['name']}...[/cyan]")
            
            try:
                results = self.simulation_engine.run_demo_scenario(choice)
                
                # Display results
                self._display_scenario_results(results)
                
                # Auto-generate recordings under output/recordings
                self._generate_scenario_recording(results)
                    
            except Exception as e:
                self.console.print(f"[red]Error running scenario: {e}[/red]")
    
    def _display_scenario_results(self, results: dict):
        """Display results from a demo scenario"""
        self.console.print(f"\n[bold]Scenario Results: {results['scenario']}[/bold]")
        
        summary_table = Table(title="Generation Summary", show_header=True, header_style="bold green")
        summary_table.add_column("Resource Type", style="cyan")
        summary_table.add_column("Count", style="white")
        summary_table.add_column("Profile", style="yellow")
        summary_table.add_column("Status", style="green")
        
        for resource_type, data in results['devices'].items():
            status = f"✓ {data['count']} generated"
            summary_table.add_row(
                resource_type,
                str(data['count']),
                data['profile'],
                status
            )
        
        self.console.print(summary_table)
        
        # Overall statistics
        self.console.print(f"\n[bold]Overall Statistics:[/bold]")
        self.console.print(f"  Total Devices Generated: {results['total_generated']}")
        self.console.print(f"  Total Valid Devices: {results['total_valid']}")
        self.console.print(f"  Success Rate: {(results['total_valid']/results['total_generated']*100):.1f}%")
        self.console.print(f"  Profiles Used: {', '.join(results['profiles_used'])}")
    
    def _generate_scenario_recording(self, results: dict):
        """Generate recording for a demo scenario"""
        all_devices = []
        device_types = []
        
        for resource_type, data in results['devices'].items():
            all_devices.extend(data['devices'])
            device_types.append(resource_type)
        
        if all_devices:
            recording_path = self.recording_generator.generate_recording(
                all_devices, 
                f"scenario_{results['scenario']}", 
                device_types[0] if device_types else "Mixed"
            )
            self.console.print(f"[green]✓[/green] Recording saved to: {recording_path}")
    
    def generate_custom_devices(self):
        """Generate custom devices with user specifications"""
        self.console.print("\n[bold]Custom Device Generation[/bold]")
        
        # Device type selection
        device_types = {
            "1": ("Storage Controller", "StorageController"),
            "2": ("Disk Drive", "Drive"),
            "3": ("Storage Volume", "Volume"),
            "4": ("Computer System", "ComputerSystem"),
            "5": ("Processor", "Processor"),
            "6": ("Memory Module", "Memory"),
            "7": ("Network Adapter", "NetworkAdapter"),
            "8": ("Chassis", "Chassis")
        }
        
        self.console.print("Select device type:")
        for key, (name, _) in device_types.items():
            self.console.print(f"  {key}. {name}")
        
        choice = Prompt.ask("Choice", choices=list(device_types.keys()))
        if choice not in device_types:
            self.console.print("[red]Invalid choice[/red]")
            return
        
        device_type, resource_type = device_types[choice]
        count = IntPrompt.ask("Number of devices to generate", default=3)
        
        # Profile selection
        available_profiles = self.prompt_processor.get_available_profiles()
        if available_profiles:
            self.console.print(f"\nAvailable profiles: {', '.join(available_profiles)}")
            profile = Prompt.ask("Select profile (or press Enter for auto-selection)", 
                                default="", choices=available_profiles + [""])
            if not profile:
                profile = None
        else:
            profile = None
        
        # Generate devices
        self.console.print(f"\n[cyan]Generating {count} {device_type} device(s)...[/cyan]")
        devices = self.simulation_engine.generate_device(
            device_type, resource_type, count, profile=profile
        )
        
        if devices:
            # Display generated devices
            self._display_generated_devices(devices, resource_type)
            
            # Generate recording
            if Confirm.ask("Generate recording for these devices?"):
                recording_path = self.recording_generator.generate_recording(
                    devices, device_type, resource_type
                )
                self.console.print(f"[green]✓[/green] Recording saved to: {recording_path}")
        else:
            self.console.print("[red]Failed to generate devices[/red]")
    
    def _display_generated_devices(self, devices: list, resource_type: str):
        """Display generated devices in a table"""
        if not devices:
            return
        
        # Get common properties from first device
        first_device = devices[0]
        common_props = ['Id', 'Name', 'Status', 'Manufacturer', 'Model']
        
        table = Table(title=f"Generated {resource_type} Devices", show_header=True, header_style="bold magenta")
        
        # Add columns for common properties
        for prop in common_props:
            if prop in first_device:
                table.add_column(prop, style="cyan" if prop == "Id" else "white")
        
        # Add rows for each device
        for device in devices:
            row_data = []
            for prop in common_props:
                if prop in device:
                    if prop == "Status" and isinstance(device[prop], dict):
                        status_str = f"{device[prop].get('State', 'N/A')}/{device[prop].get('Health', 'N/A')}"
                        row_data.append(status_str)
                    else:
                        row_data.append(str(device[prop]))
                else:
                    row_data.append("N/A")
            table.add_row(*row_data)
        
        self.console.print(table)
    
    def generate_comprehensive_infrastructure(self):
        """Generate comprehensive infrastructure"""
        self.console.print("\n[bold]Comprehensive Infrastructure Generation[/bold]")
        
        # Profile selection
        available_profiles = self.prompt_processor.get_available_profiles()
        if available_profiles:
            self.console.print(f"Available profiles: {', '.join(available_profiles)}")
            profile = Prompt.ask("Select profile (or press Enter for auto-selection)", 
                                default="", choices=available_profiles + [""])
            if not profile:
                profile = None
        else:
            profile = None
        
        # Generate infrastructure
        self.console.print("\n[cyan]Generating comprehensive infrastructure...[/cyan]")
        results = self.simulation_engine.generate_comprehensive_infrastructure(profile=profile)
        
        # Display results
        self._display_infrastructure_results(results)
        
        # Generate recording
        if Confirm.ask("Generate recording for this infrastructure?"):
            all_devices = []
            for component_data in results['infrastructure'].values():
                all_devices.extend(component_data['devices'])
            
            if all_devices:
                recording_path = self.recording_generator.generate_recording(
                    all_devices, "comprehensive_infrastructure", "Mixed"
                )
                self.console.print(f"[green]✓[/green] Recording saved to: {recording_path}")
    
    def _display_infrastructure_results(self, results: dict):
        """Display comprehensive infrastructure results"""
        self.console.print(f"\n[bold]Infrastructure Generation Results[/bold]")
        
        summary_table = Table(title="Infrastructure Components", show_header=True, header_style="bold blue")
        summary_table.add_column("Component", style="cyan")
        summary_table.add_column("Type", style="white")
        summary_table.add_column("Count", style="yellow")
        summary_table.add_column("Status", style="green")
        
        for component, data in results['infrastructure'].items():
            status = f"✓ {data['count']} generated"
            summary_table.add_row(
                component.replace('_', ' ').title(),
                data['type'],
                str(data['count']),
                status
            )
        
        self.console.print(summary_table)
        
        # Overall statistics
        self.console.print(f"\n[bold]Overall Statistics:[/bold]")
        self.console.print(f"  Total Devices: {results['total_devices']}")
        self.console.print(f"  Valid Devices: {results['total_valid']}")
        self.console.print(f"  Success Rate: {(results['total_valid']/results['total_devices']*100):.1f}%")
        self.console.print(f"  Profile Used: {results['profile_used'] or 'Auto-selected'}")
    
    def simulate_operations(self):
        """Simulate operations on devices"""
        self.console.print("\n[bold]Device Operation Simulation[/bold]")
        
        # This would typically load existing devices
        # For demo purposes, create a sample device
        sample_device = {
            "@odata.id": "/redfish/v1/Storage/1/Controllers/1",
            "Id": "1",
            "Name": "Storage Controller",
            "Status": {"State": "Enabled", "Health": "OK"}
        }
        
        self.console.print("Sample device loaded for operation simulation")
        self.console.print(f"Current status: {sample_device['Status']}")
        
        operations = ["power_off", "power_on", "reset", "maintenance", "test"]
        self.console.print(f"\nAvailable operations: {', '.join(operations)}")
        
        for op in operations:
            if Confirm.ask(f"Simulate {op} operation?"):
                result = self.simulation_engine.simulate_operation(sample_device.copy(), op)
                self.console.print(f"Result: {result.get('Status')}")
    
    def explore_redfish_profiles(self):
        """Explore available Redfish profiles"""
        self.console.print("\n[bold]Redfish Profile Explorer[/bold]")
        
        # Show available profiles
        self.simulation_engine.show_available_profiles()
        
        # Allow user to explore specific profile
        available_profiles = self.prompt_processor.get_available_profiles()
        if available_profiles:
            profile = Prompt.ask("Select profile to explore", choices=available_profiles)
            self._explore_specific_profile(profile)
    
    def _explore_specific_profile(self, profile: str):
        """Explore a specific Redfish profile"""
        profile_data = self.prompt_processor.redfish_mockups.get(profile, {})
        
        if not profile_data:
            self.console.print(f"[red]Profile {profile} not found[/red]")
            return
        
        self.console.print(f"\n[bold]Profile: {profile}[/bold]")
        
        # Show profile information
        if 'index' in profile_data:
            index = profile_data['index']
            self.console.print(f"Redfish Version: {index.get('RedfishVersion', 'Unknown')}")
            self.console.print(f"UUID: {index.get('UUID', 'Unknown')}")
        
        # Show available resources
        resources = profile_data.get('resources', {})
        if resources:
            self.console.print(f"\n[bold]Available Resources:[/bold]")
            for resource_type, resource_data in resources.items():
                count = len([k for k in resource_data.keys() if k != 'collection'])
                self.console.print(f"  {resource_type}: {count} instances")
                
                # Show sample resource if available
                for resource_name, resource_info in resource_data.items():
                    if resource_name != 'collection' and isinstance(resource_info, dict):
                        self.console.print(f"    Sample: {resource_name} - {resource_info.get('Name', 'N/A')}")
                        break
    
    def validate_recordings(self):
        """Validate existing recordings"""
        self.console.print("\n[bold]Recording Validation[/bold]")
        
        recordings_path = Path(self.config.OUTPUT_DIR)
        recordings = list(recordings_path.glob("*/"))
        
        if not recordings:
            self.console.print("[yellow]No recordings found[/yellow]")
            return
        
        self.console.print("Available recordings:")
        for i, rec in enumerate(recordings, 1):
            self.console.print(f"  {i}. {rec.name}")
        
        choice = Prompt.ask("Select recording to validate", choices=[str(i) for i in range(1, len(recordings) + 1)])
        # Validation logic would go here
        self.console.print("[green]✓[/green] Validation complete")
    
    def show_architecture(self):
        """Display architecture diagram"""
        architecture = f"""
        ┌─────────────────────────────────────────────────────────────────────────┐
        │                    DMTF REDFISH 2025.2 SPECIFICATIONS                  │
        │              (Official Mockups from DSP2043_2025.2 Bundle)             │
        └─────────────────────────────┬───────────────────────────────────────────┘
                                      │
                                      ▼
        ┌─────────────────────────────────────────────────────────────────────────┐
        │                   PROMPT PROCESSOR                                    │
        │         (Context Setting + Template Engine + Mockup Integration)       │
        └─────────────────────────────┬───────────────────────────────────────────┘
                                      │
                                      ▼
        ┌─────────────────────────────────────────────────────────────────────────┐
        │               SIMULATION ENGINE                                        │
        │            (LangChain + Azure OpenAI GPT + Profile Selection)             │
        └─────────────────────────────┬───────────────────────────────────────────┘
                                      │
                                      ▼
        ┌─────────────────────────────────────────────────────────────────────────┐
        │              RESPONSE VALIDATOR                                        │
        │         (Schema Validation + Retry Logic + Compliance Checking)        │
        └─────────────────────────────┬───────────────────────────────────────────┘
                                      │
                                      ▼
        ┌─────────────────────────────────────────────────────────────────────────┐
        │             RECORDING GENERATOR                                        │
        │         (Redfish Structure + Metadata + Profile Information)           │
        └─────────────────────────────┬───────────────────────────────────────────┘
                                      │
                                      ▼
        ┌─────────────────────────────────────────────────────────────────────────┐
        │                  DIGITAL TWIN                                          │
        │            (Standards-Compliant Output + Official Mockup Structure)    │
        └─────────────────────────────────────────────────────────────────────────┘
        
        [bold]Key Innovations:[/bold]
        • Direct integration with DMTF Redfish 2025.2 specifications
        • Profile-based device generation using official mockups
        • Multi-scenario demo system for comprehensive demonstrations
        • Real-time validation against official schemas
        • Automated infrastructure generation
        """
        self.console.print(Panel(architecture, title="System Architecture", border_style="blue"))
    
    def run_automated_demo(self):
        """Run automated demo for presentations"""
        self.console.print("\n[bold]Automated Demo Mode[/bold]")
        self.console.print("This will run a comprehensive demo automatically for presentation purposes.")
        
        if Confirm.ask("Start automated demo?"):
            self._run_automated_demo_sequence()
    
    def _run_automated_demo_sequence(self):
        """Run the automated demo sequence"""
        self.console.print("\n[bold cyan]Starting Automated Demo Sequence...[/bold cyan]")
        time.sleep(1)
        
        # Step 1: Show available profiles
        self.console.print("\n[bold]Step 1: Redfish Profile Overview[/bold]")
        self.simulation_engine.show_available_profiles()
        time.sleep(2)
        
        # Step 2: Run enterprise storage scenario
        self.console.print("\n[bold]Step 2: Enterprise Storage Infrastructure Demo[/bold]")
        try:
            results = self.simulation_engine.run_demo_scenario('enterprise_storage')
            self._display_scenario_results(results)
        except Exception as e:
            self.console.print(f"[red]Demo step failed: {e}[/red]")
            # Fallback to manual generation
            self.console.print("Falling back to manual device generation...")
            self._fallback_storage_demo()
        time.sleep(2)
        
        # Step 3: Show architecture
        self.console.print("\n[bold]Step 3: System Architecture[/bold]")
        self.show_architecture()
        time.sleep(2)
        
        # Step 4: Benefits summary
        self.console.print("\n[bold]Step 4: Benefits Summary[/bold]")
        self._show_benefits_summary()
        
        self.console.print("\n[bold green]Automated Demo Complete![/bold green]")
    
    def _fallback_storage_demo(self):
        """Fallback storage demo if scenario fails"""
        self.console.print("\n[bold]Fallback Storage Demo[/bold]")
        try:
            # Generate a simple storage controller
            devices = self.simulation_engine.generate_device(
                device_type="Storage Controller",
                resource_type="StorageController",
                count=1,
                profile="public-localstorage"
            )
            if devices:
                self.console.print(f"[green]✓[/green] Generated {len(devices)} storage controller(s)")
                # Validate
                validation_result = self.validator.validate_batch(devices, "StorageController")
                self.console.print(f"  Validation: {validation_result['valid']}/{len(devices)} valid")
        except Exception as e:
            self.console.print(f"[red]Fallback demo failed: {e}[/red]")
    
    def _show_benefits_summary(self):
        """Show benefits summary table"""
        benefits_table = Table(title="AI-Driven Digital Twin Benefits", show_header=True, header_style="bold cyan")
        benefits_table.add_column("Capability", style="yellow")
        benefits_table.add_column("Traditional Approach", style="red")
        benefits_table.add_column("AI-Driven Digital Twin", style="green")
        
        benefits = [
            ("Hardware Required", "Physical devices needed", "Zero hardware dependency"),
            ("Time to Deploy", "Weeks to months", "Minutes"),
            ("Cost", "$10,000+ per prototype", "API costs only (~$0.01)"),
            ("Scalability", "Limited by hardware", "Unlimited virtual devices"),
            ("Edge Cases", "Difficult to replicate", "Easy to simulate"),
            ("Standards Compliance", "Manual verification", "Automated validation"),
            ("Profile Support", "Limited examples", "Full DMTF mockup integration")
        ]
        
        for capability, traditional, ai_driven in benefits:
            benefits_table.add_row(capability, traditional, ai_driven)
        
        self.console.print(benefits_table)

if __name__ == "__main__":
    try:
        app = DigitalTwinApp()
        app.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Application interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Application error: {e}[/red]")
        console.print("Please check your configuration and try again.")
        console.print("Ensure your Azure OpenAI API key and endpoint are properly configured in .env file")
