# CrossBrowse

Enterprise Cross-Browser Automation and Monitoring Framework

## Overview

CrossBrowse is a Python-based browser automation framework that enables parallel execution of Chrome, Microsoft Edge, and Firefox browser instances with isolated sessions.

The framework is designed for QA testing, website monitoring, deployment validation, performance analysis, and application health checks.

---

## Features

- Chrome Support
- Edge Support
- Firefox Support
- Parallel Browser Execution
- Multiple Browser Windows
- Isolated Browser Contexts
- Screenshot Capture
- Console Log Collection
- Network Error Monitoring
- HTML Reporting
- JSON Reporting
- AsyncIO-Based Execution
- YAML Configuration
- Structured Logging

---

## Architecture

Each execution creates:

- 2 Chrome Windows
- 2 Edge Windows
- 2 Firefox Windows

Every window runs in an isolated browser context.

---

## Installation

### Clone Repository

```bash
git clone https://github.com/<your-org>/crossbrowse.git

cd crossbrowse
```

### Create Virtual Environment

```bash
python -m venv venv
```

Linux:

```bash
source venv/bin/activate
```

Windows:

```cmd
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install Playwright Browsers

```bash
playwright install
```

---

## Configuration

Edit:

```yaml
input/urls.yaml
```

Example:

```yaml
urls:
  - https://example.com
```

---

## Execution

```bash
python src/main.py
```

Run Headless:

```bash
python src/main.py --headless true
```

Run with Custom Input File:

```bash
python src/main.py --input input/urls.yaml
```

---

## Reports

Generated Reports:

```text
reports/
├── html/
└── json/
```

Generated Screenshots:

```text
screenshots/
```

Logs:

```text
logs/
```

---

## Project Goals

- Simplify cross-browser validation.
- Improve deployment verification.
- Enable automated website health monitoring.
- Support enterprise testing requirements.

---

## Technology Stack

- Python 3.11+
- Playwright
- AsyncIO
- PyYAML
- Logging
- HTML Reporting

---

## Future Roadmap

- Teams Integration
- ServiceNow Integration
- Certificate Expiry Monitoring
- Synthetic Monitoring
- AI-Driven Failure Analysis
- Jenkins Integration
- Bamboo Integration
- Kubernetes Support
- Docker Support

---

## License

MIT License

---

## Author

Rajan Dubey

Platform Integrations Specialist
