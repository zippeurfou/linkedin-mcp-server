# src/linkedin_mcp_server/tools/person.py
"""
LinkedIn person profile scraping tools with structured data extraction.

Provides MCP tools for extracting comprehensive LinkedIn profile information including
experience, education, skills, and contact details with proper error handling.
"""

import logging
from typing import Any, Dict, List

from fastmcp import FastMCP
from linkedin_scraper import Person, PersonSearch

from linkedin_mcp_server.error_handler import handle_tool_error, safe_get_driver

logger = logging.getLogger(__name__)


def register_person_tools(mcp: FastMCP) -> None:
    """
    Register all person-related tools with the MCP server.

    Args:
        mcp (FastMCP): The MCP server instance
    """

    @mcp.tool()
    async def get_person_profile(linkedin_username: str) -> Dict[str, Any]:
        """
        Get a specific person's LinkedIn profile.

        Args:
            linkedin_username (str): LinkedIn username (e.g., "stickerdaniel", "anistji")

        Returns:
            Dict[str, Any]: Structured data from the person's profile
        """
        try:
            # Construct clean LinkedIn URL from username
            linkedin_url = f"https://www.linkedin.com/in/{linkedin_username}/"

            driver = safe_get_driver()

            logger.info(f"Scraping profile: {linkedin_url}")
            person = Person(linkedin_url, driver=driver, close_on_complete=False)

            # Convert experiences to structured dictionaries
            experiences: List[Dict[str, Any]] = [
                {
                    "position_title": exp.position_title,
                    "company": exp.institution_name,
                    "from_date": exp.from_date,
                    "to_date": exp.to_date,
                    "duration": exp.duration,
                    "location": exp.location,
                    "description": exp.description,
                }
                for exp in person.experiences
            ]

            # Convert educations to structured dictionaries
            educations: List[Dict[str, Any]] = [
                {
                    "institution": edu.institution_name,
                    "degree": edu.degree,
                    "from_date": edu.from_date,
                    "to_date": edu.to_date,
                    "description": edu.description,
                }
                for edu in person.educations
            ]

            # Convert interests to list of titles
            interests: List[str] = [interest.title for interest in person.interests]

            # Convert accomplishments to structured dictionaries
            accomplishments: List[Dict[str, str]] = [
                {"category": acc.category, "title": acc.title}
                for acc in person.accomplishments
            ]

            # Convert contacts to structured dictionaries
            contacts: List[Dict[str, str]] = [
                {
                    "name": contact.name,
                    "occupation": contact.occupation,
                    "url": contact.url,
                }
                for contact in person.contacts
            ]

            # Return the complete profile data
            return {
                "name": person.name,
                "about": person.about,
                "experiences": experiences,
                "educations": educations,
                "interests": interests,
                "accomplishments": accomplishments,
                "contacts": contacts,
                "company": person.company,
                "job_title": person.job_title,
                "open_to_work": getattr(person, "open_to_work", False),
            }
        except Exception as e:
            return handle_tool_error(e, "get_person_profile")

    @mcp.tool()
    async def search_people(search_term: str) -> List[Dict[str, Any]]:
        """
        Search for people on LinkedIn using a search term.

        Args:
            search_term (str): Search term to use for the people search.

        Returns:
            List[Dict[str, Any]]: List of people search results
        """
        try:
            driver = safe_get_driver()

            logger.info(f"Searching for people: {search_term}")
            person_search = PersonSearch(
                search_term=search_term,
                max_results=10,
                driver=driver,
                get=True,
                scrape=True,
                close_on_complete=False,
            )

            # Get the results from the search
            results = person_search.results

            # Convert results to structured dictionaries
            search_results: List[Dict[str, Any]] = [
                {
                    "name": person.name,
                    "linkedin_url": person.linkedin_url,
                    "linkedin_username": person.linkedin_username,
                    "title": person.title,
                    "location": person.location,
                    "connection_degree": person.connection_degree,
                    "profile_image_url": person.profile_image_url,
                }
                for person in results
            ]

            return search_results

        except Exception as e:
            error = handle_tool_error(e, "search_people")
            return [error]  # Return as list for consistency
