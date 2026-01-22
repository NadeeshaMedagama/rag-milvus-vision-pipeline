# URL Processing Guide

This guide explains how to use the URL-based content processing feature in the RAG system.

## Overview

The RAG system can now fetch and analyze content from URLs, including:
- **Image URLs**: Analyzed using Google Vision API (OCR, labels, objects, logos)
- **Web Page URLs**: Text content extracted and indexed
- **JSON/Text URLs**: Raw content indexed directly

## Configuration

### Enable URL Processing

In your `.env` file:

```bash
# Enable URL processing
PROCESS_URLS=true
```

### Option 1: Comma-Separated URL List

Provide URLs directly in the `.env` file:

```bash
URL_LIST=https://example.com/diagram1.png,https://example.com/diagram2.jpg,https://example.com/docs.html
```

### Option 2: URL File

Create a text file with URLs (one per line):

```text
# Architecture diagrams
https://example.com/architecture/diagram1.png
https://example.com/architecture/diagram2.png

# Documentation pages
https://docs.example.com/api-reference
https://docs.example.com/getting-started

# Images from GitHub
https://raw.githubusercontent.com/org/repo/main/docs/images/flow.png
```

Then reference the file in `.env`:

```bash
URL_FILE_PATH=./urls.txt
```

### Timeout Configuration

Set the timeout for URL requests (default: 30 seconds):

```bash
URL_TIMEOUT=30
```

## Supported URL Types

### Image URLs

Image URLs are automatically detected and analyzed using Google Vision API:

**Supported formats:**
- `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp`, `.svg`

**Detected image hosting services:**
- GitHub raw content (`raw.githubusercontent.com`)
- Cloudinary
- Imgur
- AWS S3

**What's extracted:**
- Labels (objects, scenes, concepts)
- Text content (OCR)
- Logos
- Object localization

### Web Page URLs

HTML pages are processed by:
1. Fetching the page content
2. Extracting readable text (removing scripts, styles, nav, footer)
3. Preserving title and main content

### Text/JSON URLs

Raw text and JSON content is indexed directly.

## Example Workflow

1. **Configure URLs** in `.env`:

```bash
PROCESS_URLS=true
URL_LIST=https://raw.githubusercontent.com/myorg/myrepo/main/docs/architecture.png
```

2. **Run the pipeline**:

```bash
python main.py
```

3. **Check output**:

```
=== Step 3b: Processing URLs (Images, Web Content) ===
Processing 1 URLs from configuration...
Processed URL: https://raw.githubusercontent.com/myorg/myrepo/main/docs/architecture.png
Total documents after URL processing: 1
```

4. **Query the index**:

```bash
python query.py "What does the architecture diagram show?"
```

## Error Handling

- Invalid URLs are skipped with a warning
- Network errors don't stop the pipeline
- Images without detectable content return a placeholder message

## Best Practices

1. **Use direct image URLs**: Avoid URLs that redirect
2. **Test URLs first**: Ensure they're publicly accessible
3. **Set appropriate timeout**: Increase for slow servers
4. **Use URL file for many URLs**: Easier to manage than comma-separated list
5. **Comment your URL files**: Use `#` for organization

## Troubleshooting

### "Error analyzing image from URL"

- Check if the URL is publicly accessible
- Verify Google Vision API credentials are configured
- Ensure the URL points to a valid image format

### "Connection timeout"

- Increase `URL_TIMEOUT` in `.env`
- Check your network connectivity
- Verify the server is responding

### "No significant content detected"

- The image may be too simple or abstract
- Try a higher resolution image
- Ensure the image contains recognizable content
