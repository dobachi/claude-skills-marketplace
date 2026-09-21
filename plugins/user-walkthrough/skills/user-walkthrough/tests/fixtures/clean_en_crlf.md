Walkthrough of the billing API

## Findings

### [Blocker] POST /invoices returns 500 on a non-ASCII customer name · bug
* **Where**: POST /v1/invoices
* **Steps**:
    1) create a customer named "山田"
    2) POST /v1/invoices with that customer id
* **Expected**: 201 with the invoice, as for ASCII names
* **Actual**: 500, body `{"error": "internal"}`. The client could not recover and retried forever.
* **Evidence**: walkthrough-evidence/F1-curl.txt
* **Reproduced**: 3/3 from a fresh database

### [Minor] Error body shape differs between endpoints · contradiction
* **Where**: GET /v1/customers/xyz vs POST /v1/invoices
* **Steps**:
    1) GET an unknown customer
    2) POST an invoice with a missing field
* **Expected**: the same error shape on both
* **Actual**: one returns `{"error": ...}`, the other `{"message": ..., "code": ...}`
* **Evidence**: walkthrough-evidence/F2.txt
* **Reproduced**: observed by user (pasted output)

## Not checked
- auth expiry
