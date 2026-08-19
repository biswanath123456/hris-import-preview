# HRIS Import Preview

A Django-based HRIS employee import preview tool that validates employee CSV files and analyzes reporting relationships before an import is accepted.

The application parses employee data, validates required fields and duplicates, resolves manager relationships, identifies root employees, and detects circular reporting structures.

---

## Features

- CSV employee import preview
- Required-field validation
- Duplicate employee ID detection
- Duplicate email detection
- Manager resolution by employee ID
- Manager resolution by email
- Validation of conflicting manager references
- Root employee detection
- Direct-report hierarchy construction
- Circular reporting detection
- Human-readable validation errors
- Import summary and reporting preview
- Responsive browser UI
- Automated unit and integration tests

---

## Architecture

The application separates CSV parsing, validation, hierarchy processing, cycle detection, and presentation.

```text
CSV Upload
    │
    ▼
CSV Parser
    │
    ▼
Employee Records
    │
    ▼
Validator
    │
    ├── Validation Errors
    │
    ▼
Valid Records
    │
    ▼
Hierarchy Builder
    │
    ├── Manager Resolution
    ├── Root Detection
    └── Direct Reports
    │
    ▼
Cycle Detector
    │
    ▼
Import Result
    │
    ▼
Preview UI
```

### Service responsibilities

| Service | Responsibility |
|---|---|
| `csv_parser.py` | Reads and converts CSV rows into employee records |
| `employee.py` | Defines employee data structures |
| `validator.py` | Validates employee-level data |
| `record_filter.py` | Removes records containing validation errors |
| `hierarchy.py` | Resolves managers and builds reporting relationships |
| `cycle_detector.py` | Detects circular reporting relationships |
| `import_result.py` | Provides the final import-preview result |
| `import_service.py` | Orchestrates the complete import pipeline |

---

## Validation Rules

The following employee fields are required:

- Employee ID
- Employee name
- Email
- Department

The application also detects:

- Duplicate employee IDs
- Duplicate email addresses
- Invalid manager IDs
- Invalid manager emails
- Conflicting manager ID and email references
- Self-management
- Circular reporting relationships

Validation errors are associated with the original CSV row where possible so they can be displayed directly in the preview.

---

## Manager Resolution

Managers can be specified using either:

```text
manager_id
```

or:

```text
manager_email
```

If both are supplied, they must resolve to the same employee.

An employee without a manager reference is considered a root employee.

An employee with an invalid manager reference is not treated as a root simply because the referenced manager cannot be resolved.

---

## Hierarchy and Cycle Detection

Employee relationships are represented as a directed graph:

```text
Employee → Manager
```

For example:

```text
E001 → E002 → E003
```

means E001 reports to E002 and E002 reports to E003.

The application builds lookup dictionaries for employee IDs and email addresses, allowing manager resolution in approximately constant time per lookup.

Circular reporting is detected using depth-first search with three traversal states:

```text
UNVISITED
VISITING
COMPLETED
```

When a node points to another node currently in the `VISITING` state, a cycle has been found.

The detected cycle is returned as an ordered reporting path, for example:

```text
E001 → E002 → E003 → E001
```

---

## CSV Format

The uploaded CSV must contain the following columns:

```csv
employee_id,employee_name,email,department,manager_id,manager_email
```

Example:

```csv
employee_id,employee_name,email,department,manager_id,manager_email
E001,Robert Smith,robert@example.com,Executive,,
E002,Alice Johnson,alice@example.com,Engineering,E001,
E003,Bob Williams,bob@example.com,Engineering,E001,
E004,Charlie Brown,charlie@example.com,Engineering,E002,
```

`manager_id` and `manager_email` may be empty for root employees.

---

## Project Structure

```text
hris-import-preview/
│
├── examples/
│   ├── 01_valid_company.csv
│   ├── 02_missing_required_data.csv
│   ├── 03_duplicate_employees.csv
│   ├── 04_invalid_managers.csv
│   └── 05_circular_reporting.csv
│
├── hris_preview/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── importer/
│   ├── services/
│   │   ├── csv_parser.py
│   │   ├── cycle_detector.py
│   │   ├── employee.py
│   │   ├── hierarchy.py
│   │   ├── import_result.py
│   │   ├── import_service.py
│   │   ├── record_filter.py
│   │   └── validator.py
│   │
│   ├── templates/
│   │   └── importer/
│   │       └── upload.html
│   │
│   └── tests/
│       ├── test_cycle_detector.py
│       ├── test_hierarchy.py
│       ├── test_import_integration.py
│       ├── test_import_result.py
│       ├── test_record_filter.py
│       └── test_validator.py
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Installation

Clone the repository and create a virtual environment:

```powershell
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

## Running the Application

Start the Django development server:

```powershell
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

Upload an employee CSV file and review the generated import preview.

---

## Running Tests

Run the complete test suite:

```powershell
python manage.py test
```

The current implementation contains 46 automated tests covering:

- Employee validation
- Duplicate detection
- Hierarchy construction
- Manager resolution
- Root detection
- Cycle detection
- Record filtering
- Import-result behavior
- End-to-end import integration

Expected result:

```text
Found 46 test(s).

----------------------------------------------------------------------
Ran 46 tests

OK
```

---

## Example Scenarios

The `examples/` directory contains CSV files covering common import situations.

### Valid organization

Demonstrates a valid multi-level reporting hierarchy.

### Missing required data

Demonstrates missing employee names, emails, or departments.

### Duplicate employees

Demonstrates duplicate employee IDs and email addresses.

### Invalid managers

Demonstrates employees referencing managers that do not exist.

### Circular reporting

Demonstrates a reporting cycle such as:

```text
E001 → E002 → E003 → E001
```

These files can be uploaded directly through the application.

---

## Complexity

The implementation uses dictionaries for employee ID and email lookups.

For `n` employee records:

```text
CSV parsing              O(n)
Validation               O(n)
Employee indexing        O(n)
Manager resolution       O(n)
Hierarchy construction   O(n)
Cycle detection          O(V + E)
```

For the employee reporting graph, `E` is bounded by the number of manager relationships.

Overall, the import pipeline is approximately linear in the number of employee records.

---

## Design Decisions

### In-memory processing

The exercise is implemented as an import-preview workflow, so employee records are processed in memory rather than persisted to a database.

This keeps the implementation focused on validation and hierarchy analysis.

### Dictionary-based lookups

Employee IDs and emails are indexed using dictionaries so manager references can be resolved efficiently without repeatedly scanning the employee list.

### Separate validation and hierarchy processing

Basic employee validation occurs before hierarchy construction.

Manager-reference validation happens while constructing the hierarchy because manager resolution requires access to the complete employee index.

### Cycle detection with DFS

Depth-first search provides a simple and efficient way to detect cycles in the directed reporting graph while also allowing the application to display the actual cycle.

---

## Testing Strategy

The project uses multiple levels of tests:

```text
Unit Tests
    │
    ├── Validator
    ├── Hierarchy
    ├── Cycle Detector
    ├── Record Filter
    └── Import Result
    │
    ▼
Integration Tests
    │
    └── Complete CSV → Import Result pipeline
```

This allows individual algorithms to be tested independently while also verifying that the complete import workflow works correctly.

---

## AI Assistance

This project was developed as an AI-assisted technical exercise.

AI assistance was used for:

- discussing implementation approaches
- generating initial implementation ideas
- identifying edge cases
- developing test cases
- debugging test failures
- reviewing implementation structure

The generated code and suggestions were reviewed, tested, and modified during development.

The final implementation was verified using the project's automated test suite and manual CSV acceptance testing.

---

## Current Verification

The implementation has been verified with:

```text
Automated tests:       46 / 46 passing
Acceptance scenarios:   5 / 5 passing
Django system checks:   No issues
```

The application successfully handles valid imports, validation errors, duplicate records, invalid manager references, root employees, manager relationships, and circular reporting structures.
