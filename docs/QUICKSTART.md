# Quick Start Guide - Google Vision API Integration

## TL;DR

This project now supports processing diagrams, images, Word documents, and spreadsheets using Google Vision API!

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or use the install script
chmod +x install.sh
./install.sh
```

## Setup (5 minutes)

### 1. Get Google Vision API Credentials

1. Go to https://console.cloud.google.com/
2. Create a project or select existing
3. Enable "Cloud Vision API"
4. Create Service Account → Download JSON key
5. Move to: `./credentials/your-credentials.json`

### 2. Configure .env

```bash
# Copy example
cp .env.example .env

# Edit .env and add:
GOOGLE_APPLICATION_CREDENTIALS=./credentials/your-credentials.json
DATA_DIRECTORY=./data/diagrams
PROCESS_LOCAL_FILES=true

# Also add your existing credentials:
# - Azure OpenAI
# - Milvus Cloud
# - GitHub repo
```

## Usage

### Process Everything

```bash
python main.py
```

This will:
- Clone your GitHub repo
- Extract markdown files
- **Scan `./data/diagrams` for all files**
- **Analyze images with Google Vision API**
- **Extract text from Word docs**
- **Process spreadsheets**
- Chunk everything
- Create embeddings
- Store in Milvus

### Query

```bash
python query.py
```

Now you can ask about:
- Markdown documentation
- Architecture diagrams
- Images with text
- Word documents
- Spreadsheet data

## What Files Are Supported?

| Type | Extensions | Example |
|------|-----------|---------|
| Images | `.png`, `.jpg`, `.svg` | Architecture diagrams |
| Diagrams | `.drawio` | Draw.io files |
| Documents | `.docx` | Requirements docs |
| Spreadsheets | `.xlsx` | API lists, data tables |
| Markdown | `.md` | README, docs |

## Example Queries

After processing, try asking:

- "What components are in the architecture diagram?"
- "Show me the API endpoints from the spreadsheet"
- "What are the requirements in the Word document?"
- "Explain the system architecture"

## Cost

Google Vision API:
- **First 1,000 images/month: FREE** 
- After that: $1.50 per 1,000 images

For most projects with <1000 diagrams, it's **completely free**!

## Disable Vision API (Optional)

Don't want to use it? Just set:

```env
PROCESS_LOCAL_FILES=false
```

The system will still work with markdown files from GitHub.

## Troubleshooting

### "Cannot find credentials"
→ Check `GOOGLE_APPLICATION_CREDENTIALS` path in `.env`

### "API not enabled"
→ Enable Cloud Vision API in Google Cloud Console

### "No files processed"
→ Check `DATA_DIRECTORY` path exists and has files

## Architecture

Following SOLID principles:

- **IVisionAnalyzer** - Interface for image analysis
- **ILocalFileReader** - Interface for file reading
- **GoogleVisionAnalyzer** - Vision API implementation
- **LocalFileReader** - File system scanner

All components are:
- ✅ Testable
- ✅ Replaceable
- ✅ Extensible
- ✅ Well-documented

## Full Documentation

- **Setup Guide**: `docs/GOOGLE_VISION_SETUP.md`
- **Usage Guide**: `docs/USAGE.md`
- **Implementation**: `docs/IMPLEMENTATION_SUMMARY.md`
- **Architecture**: `docs/ARCHITECTURE.md`

## Support

Questions? Check:
1. `docs/GOOGLE_VISION_SETUP.md` - Detailed setup
2. `docs/USAGE.md` - Usage examples
3. README.md - Project overview

---

**Built with SOLID principles** | **Production-ready** | **Fully documented**

