# Generative AI and Public Policy Course

Welcome to the **Generative AI and Public Policy** course! This repository contains resources and code for your breakout sessions, including a CLI tool to make your first generative AI query using the OpenAI API.

## Getting Started

To ensure your environment is set up properly and securely, you'll (at minumum) need to configure a `.env` file. Create a virtual environment is typically best practivce, but not mandatory. 


### Configure Environment Variables with a .env File

A .env file is used to securely store sensitive information, such as API keys, without hardcoding them into your scripts. To use one, open you favorite code editor, and:

<ol><li>Create a .env file:
In the root directory of your project, create a file named .env.
</li><li>
Add your OpenAI API key:
Add the following line to the .env file:
```dotenv
OPENAI_API_KEY=your_api_key_here
```
</li>
<li>Loading the .env file:
Python provides a package for handling .env files "python-dotenv." The provided Python scripts use python-dotenv package to automatically load these variables into your environment at runtime, but this is good to know when writing your own code.
</li>
</ol>

### 2. Create a Virtual Environment

A virtual environment (venv) isolates your project's dependencies from your system's Python installation. This helps prevent conflicts between package versions and keeps your project self-contained.

**On macOS and Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```
**On Windows**:

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

Once your virtual environment is activated, install the necessary packages:
```python
pip install openai python-dotenv
```

### Supplementary: 

Differences: .env File vs. Virtual Environment

Virtual Environment (venv):
A virtual environment is a self-contained directory that contains a Python installation for your project along with its dependencies. This ensures that your project uses the correct versions of libraries without affecting other projects or system-wide packages.

.env File:
A .env file is used to store environment-specific configuration, such as API keys, database credentials, or other sensitive data. It keeps sensitive information out of your codebase and allows you to change configurations without modifying your source code.

Both tools serve different purposes and are best used together:

Use a venv to manage your project's dependencies.

Use a .env file to manage sensitive configuration data.

