import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)

def parse_bky(bky_content: str):
    """Parse a .bky Blockly XML file. Return root element or None."""
    if not bky_content.strip():
        return None
    try:
        return ET.fromstring(bky_content)
    except ET.ParseError as parse_error:
        logger.warning(f"XML parsing error in .bky file: {parse_error}")
        return None