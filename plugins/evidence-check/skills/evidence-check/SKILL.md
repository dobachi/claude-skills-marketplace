---
name: evidence-check
description: Verifies the validity of references and citations in reports and papers, conducting evidence-based fact-checking
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Evidence Check

Verifies the validity of references and citations in reports and papers, and fixes issues.

## Check Targets

Detects and verifies the following patterns:

- **URL Links**: `http://...`, `https://...`
- **Literature Citations**: `[1]`, `(Smith, 2020)`, `*Reference: ...`
- **Footnote References**: `^[...]`, footnote format
- **Image/Figure Sources**: `Source: ...`

## Verification Process

### 1. Reference Existence Check

- Verify that linked content exists
- Attempt access via multiple methods (direct access, alternatives)
- Request user confirmation if inaccessible

### 2. Citation Content Consistency Check

- Verify content matches the citation
- Confirm numerical and objective data accuracy
- Present correct information when discrepancies are found

### 3. Contextual Appropriateness Check

- Evaluate whether the citation fits the context
- Verify alignment with the source's intent
- Check for misleading citations

### 4. Correction and Reporting

- Automatically suggest fixes for correctable issues
- Request user confirmation for AI-inaccessible content
- Re-check after corrections

## Multi-Stage Verification Approach

**Step 1: Access Attempt**
1. Attempt content retrieval
2. Fallback approaches on failure:
   - URL variations (http/https, with/without www)
   - Check Archive.org snapshots
   - Check DOI redirects
3. Request manual user verification if all fail

**Step 2: Content Verification**
1. Confirm cited numbers/information exist in the original text
2. Identify correct information and suggest fixes on mismatch

**Step 3: Context Verification**
1. Evaluate whether citation usage is appropriate
2. Check for over-generalization that omits conditions or qualifications

## Check Item Priority

**High Priority (Required):**
- Link existence verification
- Numerical data consistency

**Medium Priority (Recommended):**
- Contextual appropriateness
- Alignment with source intent

**Low Priority (Optional):**
- Citation format consistency
- Reference list completeness

## Report Format

Check results are reported in the following categories:

| Status | Description |
|--------|-------------|
| No Issues | Link valid, content matches, context appropriate |
| Auto-Fixable | Minor numerical discrepancy, broken link (new URL found), protocol fix |
| Human Review Needed | Paid content, questionable contextual appropriateness |
| Critical Issue | Page gone, major discrepancy between citation and original |

## Error Handling

- **Network Error**: Suggest temporary issue, retry
- **404 Error**: Report as broken link, search for alternative URL
- **Access Denied**: Suggest authentication may be needed, request user confirmation
- **Timeout**: Suggest site response delay

## Best Practices

1. **Staged Checking**: Full check first > Fix issues > Re-check
2. **Human Collaboration**: Delegate AI-inaccessible sections to the user
3. **Regular Execution**: Run after major document updates and before final submission
