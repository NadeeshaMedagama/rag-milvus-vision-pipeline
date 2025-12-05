# Google Vision API Setup Guide

This guide will help you set up Google Vision API for analyzing diagrams, images, and visual content in your RAG system.

## Prerequisites

- A Google Cloud account
- Billing enabled on your Google Cloud project
- Python 3.8 or higher

## Step-by-Step Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "RAG-Vision-API")
5. Click "Create"

### 2. Enable the Vision API

1. In the Google Cloud Console, go to the [API Library](https://console.cloud.google.com/apis/library)
2. Search for "Cloud Vision API"
3. Click on "Cloud Vision API"
4. Click "Enable"
5. Wait for the API to be enabled (this may take a minute)

### 3. Create Service Account Credentials

1. Go to [IAM & Admin > Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Click "Create Service Account"
3. Enter a name (e.g., "rag-vision-service")
4. Click "Create and Continue"
5. Grant the role "Cloud Vision API User"
6. Click "Continue" and then "Done"

### 4. Generate JSON Key

1. Find your service account in the list
2. Click on the three dots (⋮) in the Actions column
3. Select "Manage keys"
4. Click "Add Key" > "Create new key"
5. Select "JSON" as the key type
6. Click "Create"
7. The JSON key file will be downloaded to your computer

### 5. Add Credentials to Your Project

1. Move the downloaded JSON file to your project's `credentials/` directory:
   ```bash
   mv ~/Downloads/your-project-xxxxx-xxxxx.json ./credentials/
   ```

2. Update your `.env` file with the path:
   ```env
   GOOGLE_APPLICATION_CREDENTIALS=./credentials/your-project-xxxxx-xxxxx.json
   ```

### 6. Verify Setup

Test your setup with this simple Python script:

```python
from google.cloud import vision
import os

# Set credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./credentials/your-credentials.json"

# Create client
client = vision.ImageAnnotatorClient()

print("✅ Google Vision API is configured correctly!")
```

## Configuration Options

### Environment Variables

Add these to your `.env` file:

```env
# Required: Path to your Google Cloud credentials JSON file
GOOGLE_APPLICATION_CREDENTIALS=./credentials/your-credentials.json

# Optional: Maximum number of results from Vision API (default: 10)
GOOGLE_VISION_MAX_RESULTS=10

# Optional: Enable/disable local file processing (default: true)
PROCESS_LOCAL_FILES=true

# Optional: Directory containing diagrams and images (default: ./data/diagrams)
DATA_DIRECTORY=./data/diagrams
```

## What the Vision API Does

The Google Vision API integration provides:

### 1. **Image Analysis**
- **Label Detection**: Identifies objects, concepts, and themes
- **Text Detection (OCR)**: Extracts all visible text
- **Object Localization**: Detects and locates specific objects
- **Logo Detection**: Identifies company logos and brands

### 2. **Diagram Processing**
For architecture diagrams and technical drawings:
- Extracts component labels and text
- Identifies shapes and objects
- Detects connections and relationships
- Provides comprehensive summaries

### 3. **Document Understanding**
For scanned documents or images with text:
- Full OCR text extraction
- Document structure detection
- Handwriting recognition (if present)

## File Type Support

The system automatically processes these file types with Vision API:

| File Type | Extensions | Processing Method |
|-----------|-----------|-------------------|
| Images | `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.svg`, `.webp` | Full Vision API analysis |
| Diagrams | `.drawio` | XML + PNG export analysis |
| Word Docs | `.docx` | Text extraction via python-docx |
| Spreadsheets | `.xlsx`, `.xls` | Data extraction via openpyxl |

## Cost Considerations

Google Vision API pricing (as of 2024):

- **First 1,000 images/month**: Free
- **1,001 - 5,000,000 images**: $1.50 per 1,000 images
- **5,000,001+ images**: Contact for pricing

### Cost Optimization Tips

1. **Batch Processing**: Process images in batches to reduce API calls
2. **Cache Results**: Store analysis results to avoid re-processing
3. **Selective Processing**: Only analyze images that need it
4. **Use Appropriate Features**: Only request the features you need

## Troubleshooting

### Authentication Errors

**Error**: `google.auth.exceptions.DefaultCredentialsError`

**Solution**:
- Verify the credentials file path in `.env`
- Check that the file exists and is readable
- Ensure the environment variable is set correctly

### API Not Enabled

**Error**: `google.api_core.exceptions.PermissionDenied: Cloud Vision API has not been used`

**Solution**:
- Go to Google Cloud Console
- Enable the Cloud Vision API for your project
- Wait a few minutes for propagation

### Quota Exceeded

**Error**: `google.api_core.exceptions.ResourceExhausted: Quota exceeded`

**Solution**:
- Check your quota in Google Cloud Console
- Request a quota increase if needed
- Implement rate limiting in your code

### Invalid Image Format

**Error**: `google.api_core.exceptions.InvalidArgument: Invalid image`

**Solution**:
- Verify the image file is not corrupted
- Check that the file format is supported
- Ensure the image size is within limits (max 20MB)

## Advanced Features

### Custom Vision Models

You can train custom Vision models for specific diagram types:

```python
from google.cloud import automl_v1

# Train a custom model for your specific diagram types
# This is useful for domain-specific diagrams
```

### Batch Processing

For large numbers of images:

```python
from google.cloud import vision

# Process multiple images in a single request
client = vision.ImageAnnotatorClient()
requests = [
    {"image": {"source": {"image_uri": uri}}, "features": [...]}
    for uri in image_uris
]
client.batch_annotate_images(requests=requests)
```

## Security Best Practices

1. **Never commit credentials**: Add `credentials/` to `.gitignore`
2. **Use service accounts**: Don't use personal credentials
3. **Rotate keys regularly**: Generate new keys periodically
4. **Limit permissions**: Grant only necessary roles
5. **Monitor usage**: Set up alerts for unusual activity

## Additional Resources

- [Google Vision API Documentation](https://cloud.google.com/vision/docs)
- [Vision API Python Client](https://googleapis.dev/python/vision/latest/)
- [Pricing Calculator](https://cloud.google.com/vision/pricing)
- [Best Practices](https://cloud.google.com/vision/docs/best-practices)

## Support

For issues specific to Google Vision API:
- [Stack Overflow - google-cloud-vision tag](https://stackoverflow.com/questions/tagged/google-cloud-vision)
- [Google Cloud Support](https://cloud.google.com/support)
- [GitHub Issues - google-cloud-python](https://github.com/googleapis/google-cloud-python/issues)

