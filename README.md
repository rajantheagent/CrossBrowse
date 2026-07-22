# 🚀 CrossBrowse

> Enterprise Cross-Browser Automation & Monitoring Framework

CrossBrowse is a powerful Python-based automation framework designed to launch and manage multiple browser sessions across **Google Chrome**, **Microsoft Edge**, and **Mozilla Firefox** simultaneously.

Built using **Playwright** and **AsyncIO**, CrossBrowse helps QA Engineers, DevOps Engineers, Middleware Teams, SREs, and Application Support Teams perform browser validation, website monitoring, screenshot capture, performance analysis, and automated reporting.

---

## 🌟 Highlights

✅ Multi-Browser Automation

✅ Parallel Execution

✅ Isolated Browser Sessions

✅ Screenshot Capture

✅ Performance Monitoring

✅ Console Log Collection

✅ HTML Reporting

✅ JSON Reporting

✅ YAML Configuration Support

✅ AsyncIO Powered

✅ Enterprise Ready Architecture

---

# 🏗️ Architecture

```text
                              +-------------------+
                              |     urls.yaml     |
                              +---------+---------+
                                        |
                                        |
                                        ▼
                           +------------------------+
                           | Configuration Loader   |
                           +------------+-----------+
                                        |
                                        |
                                        ▼
                             +--------------------+
                             | Session Manager    |
                             +----------+---------+
                                        |
      ----------------------------------------------------------------
      |                              |                               |
      ▼                              ▼                               ▼

+-------------+             +-------------+              +-------------+
|   Chrome    |             |    Edge     |              |   Firefox   |
+------+------+             +------+------+              +------+------+
       |                           |                            |
  -----+-----                 -----+-----                  -----+-----
  |         |                 |         |                  |         |
  ▼         ▼                 ▼         ▼                  ▼         ▼

Chrome-1  Chrome-2      Edge-1    Edge-2          Firefox-1  Firefox-2

       \         \           |          /             /          /
        \         \          |         /             /          /
         -------------------------------------------------------
                              |
                              ▼

                  +----------------------------+
                  | Reporting & Log Engine     |
                  +-------------+--------------+
                                |
          ------------------------------------------------
          |                      |                      |
          ▼                      ▼                      ▼

    Screenshots            JSON Reports          HTML Reports
```

---

# 🎯 Key Features

## 🌐 Multi-Browser Support

Launch and automate:

- Google Chrome
- Microsoft Edge
- Mozilla Firefox

---

## ⚡ Parallel Execution

CrossBrowse executes multiple browser instances simultaneously using AsyncIO.

Example:

```text
Chrome Window 1
Chrome Window 2

Edge Window 1
Edge Window 2

Firefox Window 1
Firefox Window 2
```

All sessions run concurrently to reduce execution time.

---

## 🔐 Session Isolation

Every browser window runs in a dedicated Playwright Browser Context.

Each context contains:

- Independent Cookies
- Independent Cache
- Independent Local Storage
- Independent Session Data

This enables realistic browser testing scenarios.

---

## 📸 Screenshot Capture

Automatically capture screenshots during execution.

Example:

```text
screenshots/

chrome_1_home.png
chrome_2_home.png

edge_1_home.png
edge_2_home.png

firefox_1_home.png
firefox_2_home.png
```

---

## 📊 Performance Metrics

Capture:

- Page Load Time
- First Response Time
- HTTP Status Codes
- Network Errors
- Failed Requests
- Browser Rendering Metrics

---

## 📝 Advanced Logging

CrossBrowse stores detailed logs for troubleshooting and auditing.

```text
logs/

execution.log
performance.log
error.log
```

---

## 📈 Reporting Engine

Generate:

### HTML Reports

```text
reports/html/
```

### JSON Reports

```text
reports/json/
```

Reports include:

- Browser Name
- Execution Status
- Response Time
- Screenshot Location
- Error Information
- Execution Duration

---

# 📂 Project Structure

```text
crossbrowse/
│
├── config/
│   └── settings.yaml
│
├── input/
│   └── urls.yaml
│
├── logs/
│
├── reports/
│   ├── html/
│   └── json/
│
├── screenshots/
│
├── src/
│   ├── main.py
│   ├── browser_manager.py
│   ├── session_manager.py
│   ├── config_loader.py
│   ├── performance_monitor.py
│   ├── screenshot_manager.py
│   ├── logger.py
│   └── reporter.py
│
├── tests/
│
├── requirements.txt
│
└── README.md
```

---

# 📋 Configuration

## urls.yaml

Place all target URLs in:

```yaml
urls:
  - https://www.google.com
  - https://www.microsoft.com
  - https://www.github.com
```

---

# 🚀 Installation

## 1. Clone Repository

```bash
git clone https://github.com/your-username/crossbrowse.git

cd crossbrowse
```

---

## 2. Create Virtual Environment

### Linux

```bash
python3 -m venv venv

source venv/bin/activate
```

### Windows

```cmd
python -m venv venv

venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Install Playwright Browsers

```bash
playwright install
```

---

# ▶️ Running CrossBrowse

## Default Execution

```bash
python src/main.py
```

---

## Run Headless

```bash
python src/main.py --headless true
```

---

## Run With Custom Input File

```bash
python src/main.py --input input/urls.yaml
```

---

## Run Specific Browser

```bash
python src/main.py --browser chrome
```

or

```bash
python src/main.py --browser edge
```

or

```bash
python src/main.py --browser firefox
```

---

# 📊 Sample Execution Output

```text
[INFO] Loading URLs...

[INFO] Found 3 URLs.

[INFO] Launching Chrome Instance 1
[INFO] Launching Chrome Instance 2

[INFO] Launching Edge Instance 1
[INFO] Launching Edge Instance 2

[INFO] Launching Firefox Instance 1
[INFO] Launching Firefox Instance 2

[INFO] Opening URLs...

[INFO] Capturing Screenshots...

[INFO] Collecting Performance Metrics...

[INFO] Generating Reports...

[SUCCESS] Execution Completed Successfully.
```

---

# 📸 Generated Artifacts

## Screenshots

```text
screenshots/
```

Contains browser screenshots.

---

## Reports

```text
reports/html/
reports/json/
```

Contains detailed execution reports.

---

## Logs

```text
logs/
```

Contains execution and troubleshooting logs.

---

# 💼 Enterprise Use Cases

## ✅ Website Validation

Verify websites across multiple browser platforms.

---

## ✅ Release Verification

Perform post-deployment smoke testing.

---

## ✅ Application Health Checks

Monitor critical business URLs.

---

## ✅ Browser Compatibility Validation

Ensure consistent application behaviour.

---

## ✅ Regression Testing

Validate application functionality after releases.

---

## ✅ Performance Analysis

Compare load times between browsers.

---

## ✅ Incident Investigation

Capture evidence including screenshots and logs.

---

# 🛣️ Product Roadmap

## Version 1.0

- Multi-Browser Support
- Parallel Execution
- Reporting Engine
- Screenshot Capture
- Logging Framework

## Version 2.0

- Teams Notifications
- ServiceNow Integration
- Slack Integration
- Email Notifications
- Certificate Monitoring
- Health Dashboard

## Version 3.0

- AI-Powered Failure Analysis
- Root Cause Suggestions
- Trend Analysis
- Historical Reporting

---

# 🧪 Technology Stack

| Technology | Purpose |
|------------|----------|
| Python 3.11+ | Core Development |
| Playwright | Browser Automation |
| AsyncIO | Parallel Execution |
| YAML | Configuration |
| Logging | Audit & Monitoring |
| HTML | Reporting |
| JSON | Structured Reporting |

---

# 🤝 Contributing

Contributions are welcome!

### Steps

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push changes
5. Submit Pull Request

Example:

```bash
git checkout -b feature/new-feature

git commit -m "Added new feature"

git push origin feature/new-feature
```

---

# 👨‍💻 Author

## Rajan Dubey

**Platform Integrations Specialist**

Specializing in:

- DevOps
- Middleware
- Automation
- AI Agents
- Platform Engineering
- Enterprise Integrations

---

# ⭐ Support

If you find CrossBrowse useful:

⭐ Star the repository

🍴 Fork the project

🛠️ Contribute enhancements

📢 Share with your team

---

<div align="center">

# 🚀 CrossBrowse

### Automate Once. Validate Everywhere.

Built for DevOps, Middleware, QA and Enterprise Operations Teams.

</div>
