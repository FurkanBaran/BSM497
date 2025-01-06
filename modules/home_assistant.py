# modules/home_assistant.py
import requests
from config.config import *
from modules.logger import ha_logger

HA_URL = HA_CONFIG.get('url')

def get_ha_states():
    """Retrieve current states from Home Assistant."""
    headers = {
        'Authorization': f'Bearer {HA_TOKEN}',
        'Content-Type': 'application/json',
    }
    
    try:
        ha_logger.info(f"Fetching Home Assistant data from: {HA_URL}")
        states_response = requests.get(f"{HA_URL}/states", headers=headers)
        states_response.raise_for_status()
        states = states_response.json()

        ha_logger.debug(f"Retrieved HA States: {states}")

        services_response = requests.get(f"{HA_URL}/services", headers=headers)
        services_response.raise_for_status()
        services = services_response.json()

        services_by_domain = {}
        for service_domain in services:
            domain = service_domain.get('domain')
            if domain and domain not in HA_CONFIG.get('excluded_domains'):
                if domain not in services_by_domain:
                    services_by_domain[domain] = []
                domain_services = service_domain.get('services', {})
                services_by_domain[domain].extend(domain_services.keys())

        filtered_data = {
            "services": services_by_domain,
            "entities": []
        }

        for state in states:
            entity_id = state['entity_id']
            domain = entity_id.split('.')[0]
            
            if domain in HA_CONFIG.get('excluded_domains'):
                continue
                
            if any(entity_id.startswith(prefix) for prefix in HA_CONFIG.get('excluded_sensor_prefixes')):
                continue
                
            important_attrs = HA_CONFIG.get('important_attributes').get(domain, HA_CONFIG.get('important_attributes').get('default'))
            
            filtered_state = {
                'entity_id': entity_id,
                'state': state['state'],
                'domain': domain,
                'attributes': {
                    k: v for k, v in state['attributes'].items()
                    if k in important_attrs
                }
            }
            filtered_data["entities"].append(filtered_state)
        
        ha_logger.info("Successfully processed Home Assistant states and services")
        return filtered_data

    except requests.exceptions.RequestException as e:
        ha_logger.error(f"Network error while fetching HA data: {str(e)}")
        return None
    except Exception as e:
        ha_logger.error(f"Unexpected error while fetching HA data: {str(e)}")
        return None

def process_api_call(api_call):
    """Process Home Assistant API calls."""
    service = api_call.get('action')
    entity_id = api_call.get('entity_id')
    parameters = api_call.get('parameters', {})

    headers = {
        'Authorization': f'Bearer {HA_TOKEN}',
        'Content-Type': 'application/json',
    }

    if not service or not entity_id:
        ha_logger.error(f"Invalid API call data - Missing service or entity_id: {api_call}")
        return

    service_url = f"{HA_URL}/services/{service.replace('.', '/')}"
    payload = {'entity_id': entity_id}
    payload.update(parameters)

    try:
        ha_logger.info(f"Making API call to HA - Service: {service}, Entity: {entity_id}, Parameters: {parameters}")
        response = requests.post(service_url, headers=headers, json=payload)
        
        if response.status_code in (200, 201):
            ha_logger.info(f"Successfully executed HA command - Status: {response.status_code}")
            ha_logger.debug(f"HA API Response: {response.text}")
        else:
            ha_logger.error(f"Failed to execute HA command - Status: {response.status_code}, Response: {response.text}")

    except requests.exceptions.RequestException as e:
        ha_logger.error(f"Network error during HA API call: {str(e)}")
    except Exception as e:
        ha_logger.error(f"Unexpected error during HA API call: {str(e)}")