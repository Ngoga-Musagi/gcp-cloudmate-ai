# gcp_advisor_agent/tools.py

from typing import Dict, List, Optional
import requests
from os import getenv
from dotenv import load_dotenv

# Load environment variables (ensure .env file exists)
load_dotenv()

def search_gcp_services(use_case: str, budget_range: Optional[str] = None, requirements: Optional[str] = None) -> Dict:
    """
    Searches and recommends GCP services based on use case, budget, and requirements.
    """
    try:
        search_query = f"Google Cloud Platform services for {use_case}"
        if budget_range:
            search_query += f" with {budget_range} budget"
        if requirements:
            search_query += f" with {requirements}"

        search_results = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                'key': getenv('GOOGLE_SEARCH_API_KEY'),
                'cx': getenv('GOOGLE_SEARCH_ENGINE_ID'),
                'q': search_query
            }
        ).json()

        recommendations = {
            "primary_services": [],
            "alternative_services": [],
            "estimated_costs": "",
            "architecture_tips": [],
            "best_practices": []
        }

        for item in search_results.get('items', []):
            link = item.get('link', '')
            if 'cloud.google.com' in link:
                if 'solutions' in link:
                    recommendations['architecture_tips'].append({
                        'title': item['title'],
                        'link': link,
                        'description': item['snippet']
                    })
                elif 'products' in link:
                    recommendations['primary_services'].append({
                        'name': item['title'],
                        'description': item['snippet'],
                        'link': link
                    })

        return {"status": "success", "recommendations": recommendations}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}

def estimate_costs(services: List[str]) -> Dict:
    """
    Provides rough cost estimates for recommended GCP services.
    """
    try:
        cost_estimates = {
            "monthly_estimate": {},
            "pricing_breakdown": {},
            "cost_optimization_tips": []
        }

        for service in services:
            pricing_query = f"Google Cloud {service} pricing calculator"
            search_results = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    'key': getenv('GOOGLE_SEARCH_API_KEY'),
                    'cx': getenv('GOOGLE_SEARCH_ENGINE_ID'),
                    'q': pricing_query
                }
            ).json()

            for item in search_results.get('items', []):
                if 'cloud.google.com/pricing' in item.get('link', ''):
                    cost_estimates['pricing_breakdown'][service] = {
                        'pricing_page': item['link'],
                        'summary': item['snippet']
                    }

            cost_estimates['cost_optimization_tips'].extend([
                f"Consider committed use discounts for {service}.",
                f"Enable budget alerts and monitoring for {service}.",
                f"Use autoscaling to avoid over-provisioning for {service}."
            ])

        return {"status": "success", "cost_estimates": cost_estimates}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}

def get_compliance_info(industry: str) -> Dict:
    """
    Retrieves compliance and security information for specific industries.
    """
    try:
        search_query = f"Google Cloud Platform compliance {industry} industry requirements"
        search_results = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                'key': getenv('GOOGLE_SEARCH_API_KEY'),
                'cx': getenv('GOOGLE_SEARCH_ENGINE_ID'),
                'q': search_query
            }
        ).json()

        compliance_info = {
            "requirements": [],
            "certifications": [],
            "best_practices": []
        }

        for item in search_results.get('items', []):
            link = item.get('link', '')
            if 'cloud.google.com/security' in link or 'cloud.google.com/compliance' in link:
                compliance_info['requirements'].append({
                    'title': item['title'],
                    'link': link,
                    'description': item['snippet']
                })

        return {"status": "success", "compliance_info": compliance_info}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
