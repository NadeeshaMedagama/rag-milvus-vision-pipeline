# Skip Existing Documents - Feature Guide

## Overview

The **Skip Existing Documents** feature prevents re-processing of files that are already indexed in your Milvus vector database. This saves time, reduces API costs, and makes the system efficient for incremental updates.

## How It Works

### Incremental Mode (Recommended) ✅

```env
SKIP_EXISTING_DOCUMENTS=true
FORCE_REPROCESS=false
```

**What happens:**
1. System checks Milvus for existing file paths
2. Compares found files with already indexed files
3. Only processes NEW or CHANGED files
4. Appends new embeddings to existing collection

**Benefits:**
- ⚡ **Fast**: Only processes new files (seconds vs minutes)
- 💰 **Cost-effective**: Saves Azure OpenAI API credits
- 📈 **Scalable**: Add 1 new diagram = process only 1 file
- 🔄 **Preserves data**: Keeps existing embeddings intact

**Use when:**
- ✅ Adding new diagrams to your data directory
- ✅ Daily/regular updates
- ✅ Running the system multiple times
- ✅ Normal operation

### Full Reindex Mode

```env
SKIP_EXISTING_DOCUMENTS=false
FORCE_REPROCESS=false
```

**What happens:**
1. Processes ALL documents every time
2. Appends to existing collection (may create duplicates)

**Use when:**
- First time setup
- Testing changes

### Force Reprocess Mode ⚠️

```env
FORCE_REPROCESS=true
# (SKIP_EXISTING_DOCUMENTS is ignored)
```

**What happens:**
1. **DELETES** existing Milvus collection
2. Creates new collection
3. Processes ALL documents from scratch
4. Rebuilds entire index

**⚠️ Warning**: This is expensive and slow!

**Use ONLY when:**
- Changed embedding model
- Changed CHUNK_SIZE or CHUNK_OVERLAP
- Corrupted index (troubleshooting)
- Want fresh start

## Real-World Examples

### Example 1: Adding New Architecture Diagrams (Common Use Case)

**Scenario:** You have 50 diagrams indexed. You add 3 new ones.

**Configuration:**
```env
SKIP_EXISTING_DOCUMENTS=true
FORCE_REPROCESS=false
```

**Output:**
```
📊 Document Status:
  - Total found: 53
  - Already indexed: 50
  - New to process: 3

✅ Processing 3 new documents
⚡ Completed in 15 seconds
```

**Result:** Only 3 new diagrams processed, 50 existing ones skipped!

### Example 2: Changed Chunk Size

**Scenario:** You changed `CHUNK_SIZE` from 1000 to 500. Need to re-chunk everything.

**Configuration:**
```env
FORCE_REPROCESS=true
```

**Output:**
```
Mode: FORCE REPROCESS (will process all documents)
🔄 Deleting existing collection...
✅ Processing all 53 documents from scratch
⏱️  Completed in 5 minutes
```

**Result:** Entire index rebuilt with new chunk size.

### Example 3: First Time Setup

**Scenario:** Running for the first time, no existing data.

**Configuration:**
```env
SKIP_EXISTING_DOCUMENTS=true
FORCE_REPROCESS=false
```

**Output:**
```
No existing documents found in vector store
✅ Processing all 50 documents
⏱️  Completed in 4 minutes
```

**Result:** All documents processed and indexed.

### Example 4: All Files Already Processed

**Scenario:** Running again with no new files.

**Configuration:**
```env
SKIP_EXISTING_DOCUMENTS=true
FORCE_REPROCESS=false
```

**Output:**
```
📊 Document Status:
  - Total found: 50
  - Already indexed: 50
  - New to process: 0

✅ All documents already indexed - no changes needed!

💡 Tip: Use FORCE_REPROCESS=true in .env to reprocess all documents
```

**Result:** Completes in seconds, no processing needed!

## Configuration Options Explained

### `GOOGLE_VISION_MAX_RESULTS`

**What it means:** How many results Google Vision API returns for each detection type.

**Example with `GOOGLE_VISION_MAX_RESULTS=10`:**

For this architecture diagram:
```
Labels detected: Cloud, Architecture, Diagram, Container, Kubernetes, 
                 Microservices, Docker, API, Database, Networking
Objects detected: Rectangle, Arrow, Circle, Text Box, Line, Icon, 
                  Logo, Shape, Connection, Node
```

**Settings comparison:**

| Value | Labels Detected | Processing Speed | API Cost |
|-------|----------------|------------------|----------|
| 5 | Top 5 most relevant | ⚡ Fastest | 💰 Lowest |
| 10 | Top 10 most relevant | ⚡ Fast | 💰 Low |
| 20 | Top 20 most relevant | 🐌 Slower | 💰💰 Higher |
| 50 | Up to 50 | 🐌 Slow | 💰💰💰 Expensive |

**Recommended:** `10` (balanced)

### `SKIP_EXISTING_DOCUMENTS`

| Value | Behavior | Speed | Use Case |
|-------|----------|-------|----------|
| `true` | Incremental updates | ⚡⚡⚡ | Daily use ✅ |
| `false` | Process all files | 🐌 | Testing, first setup |

### `FORCE_REPROCESS`

| Value | Behavior | When to Use |
|-------|----------|-------------|
| `true` | Delete & rebuild index | Changed settings, troubleshooting |
| `false` | Respect SKIP_EXISTING | Normal operation ✅ |

## Cost Savings Example

**Scenario:** 100 architecture diagrams in your data directory

### Without Skip (Process All Every Time)
```
Run 1: Process 100 files → 10 minutes, $0.50 in API costs
Run 2: Process 100 files → 10 minutes, $0.50 in API costs
Run 3: Process 100 files → 10 minutes, $0.50 in API costs
Total: 30 minutes, $1.50
```

### With Skip (Incremental Updates)
```
Run 1: Process 100 files → 10 minutes, $0.50 in API costs
Run 2: 0 new files       → 5 seconds,  $0.00 in API costs ✅
Run 3: 5 new files       → 30 seconds, $0.02 in API costs ✅
Total: 10.6 minutes, $0.52 (65% savings!)
```

## Best Practices

### ✅ Recommended Settings for Most Users

```env
# Normal daily use - FAST and COST-EFFECTIVE
SKIP_EXISTING_DOCUMENTS=true
FORCE_REPROCESS=false
GOOGLE_VISION_MAX_RESULTS=10
```

### 🔧 When to Change Settings

**Adding new diagrams regularly:**
```env
SKIP_EXISTING_DOCUMENTS=true  # ✅ Only process new files
FORCE_REPROCESS=false
```

**Changed chunk size or embedding model:**
```env
FORCE_REPROCESS=true  # ⚠️ Rebuild entire index
```

**Testing/Development:**
```env
SKIP_EXISTING_DOCUMENTS=false  # Process all for testing
FORCE_REPROCESS=true           # Fresh start each time
```

**Production (stable):**
```env
SKIP_EXISTING_DOCUMENTS=true   # ✅ Incremental updates
FORCE_REPROCESS=false          # ✅ Preserve existing data
```

## Workflow Updates

### New Workflow Steps

```
1. Clone Repository & Check Existing Data ← NEW: Checks Milvus
2. Extract Markdown Files
3. Process Local Files
4. Filter Existing Documents ← NEW: Removes already-indexed files
5. Chunk Documents (only new ones)
6. Create Embeddings (only new ones)
7. Store Embeddings (append to existing)
8. Cleanup
```

### Output Improvements

**Before:**
```
Processing documents...
Created 500 chunks
Stored 500 embeddings
```

**After:**
```
📊 Document Status:
  - Total found: 100
  - Already indexed: 95
  - New to process: 5

✅ Processing 5 new documents
✅ Created 25 chunks
✅ Stored 25 embeddings
⚡ Completed in 20 seconds
```

## FAQ

**Q: Will this delete my existing embeddings?**  
A: No (unless `FORCE_REPROCESS=true`). Incremental mode appends new documents.

**Q: What if I modify an existing diagram?**  
A: The system checks file paths, not content. To reprocess modified files, set `FORCE_REPROCESS=true`.

**Q: How does it know which files are already processed?**  
A: Queries Milvus for unique file paths, compares with files found in your directories.

**Q: What if I delete a file from my directory?**  
A: Existing embeddings remain in Milvus. Use `FORCE_REPROCESS=true` to rebuild if needed.

**Q: Can I process files from multiple directories?**  
A: Currently processes one `DATA_DIRECTORY`. For multiple directories, run multiple times or extend the code.

**Q: Does this work with GitHub repo changes too?**  
A: Yes! Skips already-processed `.md` files from GitHub repositories.

## Troubleshooting

### "All documents already indexed - no changes needed!"

**Cause:** No new files found, all files already in Milvus.

**Solution:** 
- If you added new files, check `DATA_DIRECTORY` path
- If you want to reprocess, set `FORCE_REPROCESS=true`

### "Could not filter existing documents: ..."

**Cause:** Error querying Milvus for existing file paths.

**Solution:** 
- Check Milvus connection settings
- System will process all files as a safety measure
- Check logs for specific error

### "Processing takes too long"

**Cause:** Processing too many files or `SKIP_EXISTING_DOCUMENTS=false`

**Solution:**
- Set `SKIP_EXISTING_DOCUMENTS=true`
- Lower `GOOGLE_VISION_MAX_RESULTS` (try 5)
- Process in batches

## Summary

| Setting | Value | What It Does | When to Use |
|---------|-------|--------------|-------------|
| `SKIP_EXISTING_DOCUMENTS` | `true` | Skip already-indexed files | ✅ Daily use |
| `SKIP_EXISTING_DOCUMENTS` | `false` | Process all files | First setup, testing |
| `FORCE_REPROCESS` | `true` | Delete & rebuild index | Changed settings |
| `FORCE_REPROCESS` | `false` | Preserve existing data | ✅ Normal operation |
| `GOOGLE_VISION_MAX_RESULTS` | `10` | Balanced analysis | ✅ Recommended |

**Default Recommended Configuration:**
```env
SKIP_EXISTING_DOCUMENTS=true
FORCE_REPROCESS=false
GOOGLE_VISION_MAX_RESULTS=10
```

This gives you:
- ⚡ Fast incremental updates
- 💰 Cost-effective processing
- 🔄 Preserved existing data
- 📈 Scalable for large collections

---

**Questions?** See `docs/USAGE.md` or `QUICKSTART.md`

