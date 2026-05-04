"""
Format Parser Utility Module

This module provides automatic format detection and parsing for JSON, YAML, and XML files.
Supports .json, .yaml, .yml, and .xml file extensions with automatic detection based on
file extension or content analysis.
"""

import json
import yaml
import xmltodict
from pathlib import Path


def detect_format(filepath):
    """
    Detect file format based on extension or content.
    
    Args:
        filepath (str): Path to the file
        
    Returns:
        str: 'json', 'yaml', or 'xml'
        
    Raises:
        ValueError: If format cannot be detected
    """
    filepath = str(filepath)
    ext = Path(filepath).suffix.lower()
    
    # Detect by extension
    if ext == '.json':
        return 'json'
    elif ext in ['.yaml', '.yml']:
        return 'yaml'
    elif ext == '.xml':
        return 'xml'
    
    # If no extension match, try to detect by content
    try:
        with open(filepath, 'r') as f:
            content = f.read().strip()
        
        if content.startswith('{') or content.startswith('['):
            return 'json'
        elif content.startswith('<'):
            return 'xml'
        elif any(content.startswith(c) for c in ['---', '-', 'key:', 'name:']):
            return 'yaml'
    except Exception:
        pass
    
    raise ValueError(f"Unable to detect format for file: {filepath}")


def parse_file(filepath):
    """
    Parse a file in JSON, YAML, or XML format.
    
    Args:
        filepath (str): Path to the file
        
    Returns:
        dict or list: Parsed data structure
        
    Raises:
        Exception: If file parsing fails
    """
    format_type = detect_format(filepath)
    
    try:
        with open(filepath, 'r') as f:
            if format_type == 'json':
                return json.load(f)
            elif format_type == 'yaml':
                return yaml.safe_load(f) or []
            elif format_type == 'xml':
                content = f.read()
                parsed = xmltodict.parse(content)
                # If root has a single key, return its value (common pattern)
                if isinstance(parsed, dict) and len(parsed) == 1:
                    root_key = list(parsed.keys())[0]
                    data = parsed[root_key]
                    # If that key's value is a dict with a list, extract the list
                    if isinstance(data, dict) and len(data) == 1:
                        list_key = list(data.keys())[0]
                        item = data[list_key]
                        if isinstance(item, list):
                            items = item
                        else:
                            items = [item]
                        # Normalize all single-item dicts to lists
                        result = []
                        for record in items:
                            if isinstance(record, dict):
                                result.append(_normalize_xml_dict(record))
                            else:
                                result.append(record)
                        return result
                    elif isinstance(data, list):
                        return [_normalize_xml_dict(item) if isinstance(item, dict) else item for item in data]
                    else:
                        return [_normalize_xml_dict(data)] if isinstance(data, dict) else [data]
                return parsed
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML format: {e}")
    except Exception as e:
        raise ValueError(f"Error parsing {format_type.upper()} file: {e}")


def _normalize_xml_dict(obj):
    """
    Normalize XML-parsed dicts to convert single-item dicts to lists.
    This handles the xmltodict behavior where single items are dicts instead of lists.
    
    Args:
        obj (dict): Dictionary to normalize
        
    Returns:
        dict: Normalized dictionary
    """
    if not isinstance(obj, dict):
        return obj
    
    result = {}
    for key, value in obj.items():
        # List of keys that should definitely be lists
        list_keys = {'interface', 'interfaces', 'neighbor', 'neighbors', 
                     'network', 'networks', 'pool', 'pools', 
                     'rule', 'rules', 'acl', 'acls', 'item', 'items'}
        
        if isinstance(value, dict):
            # Check if this should be a list
            if key in list_keys or (len(value) == 1 and list(value.keys())[0] == 'item'):
                # Unwrap single 'item' wrapper
                if len(value) == 1 and list(value.keys())[0] == 'item':
                    inner_value = value['item']
                    if isinstance(inner_value, list):
                        result[key] = [_normalize_xml_dict(v) if isinstance(v, dict) else v for v in inner_value]
                    else:
                        result[key] = [_normalize_xml_dict(inner_value) if isinstance(inner_value, dict) else inner_value]
                else:
                    result[key] = [_normalize_xml_dict(value)]
            else:
                result[key] = _normalize_xml_dict(value)
        elif isinstance(value, list):
            result[key] = [_normalize_xml_dict(v) if isinstance(v, dict) else v for v in value]
        else:
            result[key] = value
    
    return result


def save_file(data, filepath, format_type=None):
    """
    Save data to a file in the specified format.
    
    Args:
        data (dict or list): Data to save
        filepath (str): Path to save the file
        format_type (str): 'json', 'yaml', or 'xml'. If None, detects from filepath extension.
        
    Raises:
        ValueError: If format is not recognized
    """
    if format_type is None:
        format_type = detect_format(filepath)
    
    format_type = format_type.lower()
    
    with open(filepath, 'w') as f:
        if format_type == 'json':
            json.dump(data, f, indent=4)
        elif format_type == 'yaml':
            yaml.dump(data, f, default_flow_style=False)
        elif format_type == 'xml':
            # For XML, wrap data if it's a list
            if isinstance(data, list):
                xml_data = {'items': {'item': data}}
            else:
                xml_data = {'data': data}
            xml_str = xmltodict.unparse(xml_data, pretty=True)
            f.write(xml_str)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
