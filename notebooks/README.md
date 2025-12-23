# Google Colab Notebooks

Interactive notebooks for working with dorc-engine to create and validate Candidate Canon Entries (CCE).

## Notebooks

### 00_quickstart.ipynb

**Purpose:** Health check and basic setup

- Install the SDK
- Configure environment variables
- Test connection to dorc-engine
- Verify the service is healthy

**Use this first** to ensure your environment is set up correctly.

### 01_create_and_validate_cce.ipynb

**Purpose:** Submit and display validation results

- Submit candidate content for validation
- Display summary counts (PASS/FAIL/WARN/ERROR)
- Show detailed chunk results in a pandas DataFrame
- Visualize validation status

**Use this** to validate a single CCE and see the results.

### 02_review_and_rectify_loop.ipynb

**Purpose:** Human-in-the-loop validation workflow

- Submit initial validation
- Check for FAIL status
- If failures exist, edit content and re-validate
- Track multiple validation attempts
- Continue until validation passes or user is satisfied

**Use this** when you need to iteratively fix content based on validation feedback.

### 03_export_jsonl_for_rag.ipynb

**Purpose:** Export validated CCE to JSONL format

- After validation passes (or user override)
- Export candidate to JSONL format
- Save to `/content/dorc_exports/` with timestamp
- Format suitable for RAG systems

**Use this** to export validated content for use in other systems.

## Setup

All notebooks require:

1. **Environment variables:**
   - `DORC_BASE_URL` - Your dorc-engine Cloud Run service URL
   - `DORC_TENANT_SLUG` - Your tenant identifier
   - `DORC_API_KEY` (optional) - API key if authentication is required

   Note: `DORC_ENGINE_URL` is accepted for backwards compatibility but deprecated.

2. **SDK installation:**
   - Notebooks install the SDK from the repository path
   - First cell in each notebook handles installation

## Security Note

**Important:** Do not commit API keys or sensitive credentials to version control.

- Use Colab's "Secrets" feature for sensitive values
- Or set environment variables in Colab's environment settings
- Never hardcode credentials in notebook cells

## How Notebooks Work

- Notebooks call dorc-engine over HTTPS
- All validation happens on the server (dorc-engine)
- Results are returned synchronously
- No canon content is stored in GitHub or this repository
- BigQuery ledger is managed by dorc-engine (not accessed directly)

## Usage Tips

1. **Start with 00_quickstart.ipynb** to verify your setup
2. **Use 01_create_and_validate_cce.ipynb** for single validations
3. **Use 02_review_and_rectify_loop.ipynb** for iterative refinement
4. **Use 03_export_jsonl_for_rag.ipynb** to export final results

Each notebook is self-contained and can be run independently.

