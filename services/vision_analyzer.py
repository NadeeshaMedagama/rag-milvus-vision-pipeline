"""Google Vision API service implementation."""
import os
from typing import List
from google.cloud import vision
from google.oauth2 import service_account

from interfaces import IVisionAnalyzer


class GoogleVisionAnalyzer(IVisionAnalyzer):
    """Service for analyzing images and diagrams using Google Vision API."""

    def __init__(self, credentials_path: str, max_results: int = 10):
        """
        Initialize the Google Vision analyzer.

        Args:
            credentials_path: Path to Google Cloud credentials JSON file
            max_results: Maximum number of results to return from Vision API
        """
        self.credentials_path = credentials_path
        self.max_results = max_results

        # Set environment variable for Google credentials
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        # Initialize Vision API client
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        self.client = vision.ImageAnnotatorClient(credentials=credentials)

    def analyze_image(self, image_path: str) -> str:
        """
        Analyze an image and return a comprehensive description.

        Args:
            image_path: Path to the image file

        Returns:
            Comprehensive description of the image
        """
        try:
            with open(image_path, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)

            # Perform multiple types of detection
            response = self.client.annotate_image({
                'image': image,
                'features': [
                    {'type_': vision.Feature.Type.LABEL_DETECTION, 'max_results': self.max_results},
                    {'type_': vision.Feature.Type.TEXT_DETECTION},
                    {'type_': vision.Feature.Type.DOCUMENT_TEXT_DETECTION},
                    {'type_': vision.Feature.Type.OBJECT_LOCALIZATION, 'max_results': self.max_results},
                    {'type_': vision.Feature.Type.LOGO_DETECTION, 'max_results': self.max_results},
                ],
            })

            analysis_parts = []

            # Add labels
            if response.label_annotations:
                labels = [label.description for label in response.label_annotations]
                analysis_parts.append(f"Labels detected: {', '.join(labels)}")

            # Add detected objects
            if response.localized_object_annotations:
                objects = [obj.name for obj in response.localized_object_annotations]
                analysis_parts.append(f"Objects detected: {', '.join(objects)}")

            # Add detected logos
            if response.logo_annotations:
                logos = [logo.description for logo in response.logo_annotations]
                analysis_parts.append(f"Logos detected: {', '.join(logos)}")

            # Add text content
            if response.text_annotations:
                text_content = response.text_annotations[0].description
                analysis_parts.append(f"Text content:\n{text_content}")

            return "\n\n".join(analysis_parts) if analysis_parts else "No significant content detected."

        except Exception as e:
            return f"Error analyzing image: {str(e)}"

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from an image using OCR.

        Args:
            image_path: Path to the image file

        Returns:
            Extracted text
        """
        try:
            with open(image_path, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)
            response = self.client.document_text_detection(image=image)

            if response.text_annotations:
                return response.text_annotations[0].description

            return ""

        except Exception as e:
            return f"Error extracting text: {str(e)}"

    def generate_summary(self, image_path: str) -> str:
        """
        Generate a comprehensive summary of an image or diagram.

        Args:
            image_path: Path to the image file

        Returns:
            Comprehensive summary
        """
        file_name = os.path.basename(image_path)
        file_extension = os.path.splitext(file_name)[1].lower()

        summary_parts = [
            f"File: {file_name}",
            f"Type: {file_extension}",
            f"\n--- Image Analysis ---"
        ]

        # Get full analysis
        analysis = self.analyze_image(image_path)
        summary_parts.append(analysis)

        # Add extracted text separately for better context
        text = self.extract_text_from_image(image_path)
        if text and text not in analysis:
            summary_parts.append(f"\n--- Extracted Text ---\n{text}")

        return "\n".join(summary_parts)

