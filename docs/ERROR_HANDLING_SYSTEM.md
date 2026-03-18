# AgentForgeOS — Error Handling System

Purpose:

Define a consistent error system across the entire platform.

---

# Error Response Format

All errors must follow:

```json
{
  "success": false,
  "error": {
    "code": "error_code",
    "message": "Human readable message",
    "module": "module_name"
  }
}
```

---

# Error Codes

provider_unavailable
module_not_found
pipeline_failure
permission_denied
invalid_request

---

# Example

```json
{
  "success": false,
  "error": {
    "code": "provider_unavailable",
    "message": "Image generation provider not configured",
    "module": "assets"
  }
}
```

---

# Logging

All errors must be logged.

Logs must include:

timestamp
module
error_code
stack_trace

---

# End of Error Handling Specification
