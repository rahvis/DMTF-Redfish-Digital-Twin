import json
from typing import Dict, List, Tuple
from jsonschema import validate, ValidationError
from pathlib import Path

class ResponseValidator:
    def __init__(self, config):
        self.config = config
        self.schemas = self._load_schemas()
        self.schemas.update(self._load_swordfish())
        self.rules = self._load_rules()

    def _load_schemas(self) -> Dict:
        p = Path(self.config.SPECS_DIR) / 'redfish_schemas.json'
        return json.loads(p.read_text()) if p.exists() else {}

    def _load_rules(self) -> Dict:
        """Load enhanced validation rules from templates"""
        rules_path = Path(self.config.TEMPLATE_FILES.get('validation_rules', 'templates/validation_rules.json'))
        if rules_path.exists():
            try:
                return json.loads(rules_path.read_text())
            except Exception as e:
                print(f"Warning: Could not load validation rules: {e}")
                return self._get_default_rules()
        return self._get_default_rules()
    
    def _get_default_rules(self) -> Dict:
        """Default validation rules if template loading fails"""
        return {
            "required_fields": {"all": ["@odata.type", "@odata.id", "Id", "Name"]},
            "field_types": {"@odata.type": "string", "@odata.id": "string"},
            "value_constraints": {}
        }

    def validate(self, data: Dict, resource_type: str) -> Tuple[bool, List[str], Dict]:
        """Enhanced validation with comprehensive scoring and analysis"""
        errs: List[str] = []
        warnings: List[str] = []
        compliance_score = 0
        validation_details = {
            'required_fields_score': 0,
            'data_types_score': 0,
            'value_constraints_score': 0,
            'business_logic_score': 0,
            'presentation_quality_score': 0
        }
        
        # Required fields validation
        req = self.rules.get('required_fields', {})
        all_fields = req.get('all', [])
        type_fields = req.get(resource_type, [])
        total_required = len(all_fields) + len(type_fields)
        missing_fields = 0
        
        for f in all_fields:
            if f not in data:
                errs.append(f'Missing required field: {f}')
                missing_fields += 1
        
        for f in type_fields:
            if f not in data:
                errs.append(f'Missing required field for {resource_type}: {f}')
                missing_fields += 1
        
        if total_required > 0:
            validation_details['required_fields_score'] = max(0, 100 - (missing_fields / total_required) * 100)
        
        # Data type validation - more lenient approach
        types = self.rules.get('field_types', {})
        typemap = {'string': str, 'integer': int, 'object': dict, 'boolean': bool, 'array': list}
        type_errors = 0
        total_typed_fields = 0
        
        for field, expected_type in types.items():
            if field in data:
                total_typed_fields += 1
                actual_type = type(data[field])
                expected_python_type = typemap.get(expected_type, object)
                
                # More flexible type checking
                if not isinstance(data[field], expected_python_type):
                    # Check for common type mismatches that are acceptable
                    if expected_type == 'integer' and isinstance(data[field], (int, float)):
                        # Allow float for integer fields (common LLM behavior)
                        continue
                    elif expected_type == 'array' and isinstance(data[field], (list, tuple)):
                        # Allow tuple for array fields
                        continue
                    elif expected_type == 'object' and isinstance(data[field], dict):
                        # Allow dict for object fields
                        continue
                    else:
                        # Add as warning instead of error for type mismatches
                        warnings.append(f'Field {field} should be {expected_type}, got {actual_type.__name__}')
                        type_errors += 1
        
        if total_typed_fields > 0:
            validation_details['data_types_score'] = max(0, 100 - (type_errors / total_typed_fields) * 100)
        
        # Value constraints validation
        vc = self.rules.get('value_constraints', {})
        constraint_errors = 0
        total_constraints = 0
        
        # Status validation
        if 'Status' in data and isinstance(data['Status'], dict):
            for sub in ('State', 'Health'):
                if sub in vc and sub in data['Status']:
                    total_constraints += 1
                    if data['Status'][sub] not in vc[sub]:
                        errs.append(f'Invalid Status.{sub}: {data["Status"][sub]}')
                        constraint_errors += 1
        
        # Protocol validation
        if 'Protocol' in data and 'Protocol' in vc:
            total_constraints += 1
            if data['Protocol'] not in vc['Protocol']:
                errs.append(f'Invalid Protocol: {data["Protocol"]}')
                constraint_errors += 1
        
        # Media type validation
        if 'MediaType' in data and 'MediaType' in vc:
            total_constraints += 1
            if data['MediaType'] not in vc['MediaType']:
                errs.append(f'Invalid MediaType: {data["MediaType"]}')
                constraint_errors += 1
        
        if total_constraints > 0:
            validation_details['value_constraints_score'] = max(0, 100 - (constraint_errors / total_constraints) * 100)
        
        # Business logic validation
        business_logic_score = 100
        advanced_validation = self.rules.get('advanced_validation', {})
        
        # Cross-field validation
        cross_validation = advanced_validation.get('cross_field_validation', {})
        if resource_type in cross_validation:
            for condition, requirements in cross_validation[resource_type].items():
                if self._evaluate_cross_field_condition(data, condition):
                    for field, requirement in requirements.items():
                        if not self._validate_business_requirement(data, field, requirement):
                            warnings.append(f'Business logic warning: {field} {requirement}')
                            business_logic_score -= 10
        
        validation_details['business_logic_score'] = max(0, business_logic_score)
        
        # Presentation quality assessment
        presentation_score = 100
        highlight_fields = self.rules.get('presentation_enhancements', {}).get('highlight_fields', [])
        
        for field in highlight_fields:
            if field not in data:
                presentation_score -= 5
                warnings.append(f'Presentation enhancement: Consider adding {field}')
        
        validation_details['presentation_quality_score'] = max(0, presentation_score)
        
        # Calculate overall compliance score
        weights = {
            'required_fields_score': 0.4,
            'data_types_score': 0.25,
            'value_constraints_score': 0.2,
            'business_logic_score': 0.1,
            'presentation_quality_score': 0.05
        }
        
        for metric, weight in weights.items():
            compliance_score += validation_details[metric] * weight
        
        # Schema validation - more lenient approach
        if resource_type in self.schemas:
            try:
                validate(instance=data, schema=self.schemas[resource_type])
            except ValidationError as e:
                # Handle schema validation errors more gracefully
                error_message = str(e.message)
                
                # Check if it's a type mismatch that we can handle
                if "is not of type" in error_message:
                    # This is a type mismatch - add as warning instead of error
                    warnings.append(f'Schema type warning: {error_message}')
                    compliance_score = max(0, compliance_score - 5)  # Smaller penalty for type issues
                else:
                    # More serious schema validation error
                    errs.append(f'Schema validation error: {error_message}')
                    compliance_score = max(0, compliance_score - 15)
        
        validation_result = {
            'valid': len(errs) == 0,
            'compliance_score': round(compliance_score, 2),
            'errors': errs,
            'warnings': warnings,
            'validation_details': validation_details,
            'resource_type': resource_type,
            'presentation_ready': compliance_score >= self.config.QUALITY_THRESHOLDS.get('presentation_ready', 75)
        }
        
        return (len(errs) == 0, errs, validation_result)
    
    def _evaluate_cross_field_condition(self, data: Dict, condition: str) -> bool:
        """Evaluate cross-field validation conditions"""
        if 'if_MediaType_is_HDD' in condition:
            return data.get('MediaType') == 'HDD'
        elif 'if_MediaType_is_SSD' in condition:
            return data.get('MediaType') == 'SSD'
        elif 'if_RAIDType_is_RAID0' in condition:
            return data.get('RAIDType') == 'RAID0'
        elif 'if_RAIDType_is_RAID1' in condition:
            return data.get('RAIDType') == 'RAID1'
        return False
    
    def _validate_business_requirement(self, data: Dict, field: str, requirement: str) -> bool:
        """Validate business logic requirements"""
        if requirement == 'required':
            return field in data
        elif requirement == 'must_be_512_or_4096':
            return data.get(field) in [512, 4096]
        elif requirement == 'must_be_4096_or_higher':
            return data.get(field, 0) >= 4096
        elif requirement == 'must_be_0':
            return data.get(field) == 0
        elif requirement == 'must_be_NonRedundant':
            return data.get(field) == 'NonRedundant'
        elif requirement == 'must_be_Mirrored':
            return data.get(field) == 'Mirrored'
        return True

    def validate_batch(self, devices: List[Dict], resource_type: str) -> Dict:
        """Enhanced batch validation with comprehensive analysis"""
        out = {
            'total': len(devices), 
            'valid': 0, 
            'invalid': 0, 
            'errors': [],
            'warnings': [],
            'compliance_scores': [],
            'average_score': 0,
            'presentation_ready_count': 0,
            'quality_distribution': {
                'excellent': 0,
                'very_good': 0,
                'good': 0,
                'acceptable': 0,
                'needs_improvement': 0,
                'poor': 0
            }
        }
        
        total_score = 0
        
        for i, d in enumerate(devices):
            ok, e, validation_result = self.validate(d, resource_type)
            out['valid' if ok else 'invalid'] += 1
            
            if not ok:
                out['errors'].append({'device_index': i, 'errors': e, 'validation_result': validation_result})
            
            if validation_result.get('warnings'):
                out['warnings'].extend([{'device_index': i, 'warning': w} for w in validation_result.get('warnings', [])])
            
            compliance_score = validation_result.get('compliance_score', 0)
            out['compliance_scores'].append(compliance_score)
            total_score += compliance_score
            
            if validation_result.get('presentation_ready', False):
                out['presentation_ready_count'] += 1
            
            # Quality distribution
            score = compliance_score
            if score >= 90:
                out['quality_distribution']['excellent'] += 1
            elif score >= 80:
                out['quality_distribution']['very_good'] += 1
            elif score >= 70:
                out['quality_distribution']['good'] += 1
            elif score >= 60:
                out['quality_distribution']['acceptable'] += 1
            elif score >= 50:
                out['quality_distribution']['needs_improvement'] += 1
            else:
                out['quality_distribution']['poor'] += 1
        
        if out['total'] > 0:
            out['average_score'] = round(total_score / out['total'], 2)
        
        return out


    def _load_swordfish(self) -> Dict:
        from pathlib import Path
        import json
        p = Path(self.config.SPECS_DIR) / 'swordfish_extensions.json'
        if p.exists():
            try:
                return json.loads(p.read_text())
            except Exception:
                return {}
        return {}
