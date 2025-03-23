# DPI-681M The Science and Implications of Generative AI: Section Repo

Welcome to **The Science and Implications of Generative AI!** This repository contains resources and code for your breakout sessions.

## Getting Started

To ensure your environment is set up properly and securely, you'll (at minimum) need to configure a `.env` file. Creating a virtual environment is typically best practice, but not mandatory.

### 1. Configure Environment Variables with a .env File

A `.env` file is used to securely store sensitive information, such as API keys, without hardcoding them into your scripts. To use one, open your favorite code editor and follow these steps:

1. **Create a `.env` file:**  
   In the root directory of your project, create a file named `.env`.

2. **Add your OpenAI API key:**  
   Add the following line to the `.env` file:  
   ```dotenv
   OPENAI_API_KEY=your_api_key_here
   ```

3. **Loading the `.env` file:**  
   Python provides a package for handling `.env` files called `python-dotenv`. The provided Python scripts automatically load these variables into your environment at runtime. This is useful to know when writing your own code.

### 2. Create a Virtual Environment

A virtual environment (venv) isolates your project's dependencies from your system's Python installation. This helps prevent conflicts between package versions and keeps your project self-contained.

**On macOS and Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

Once your virtual environment is activated, install the necessary packages:
```bash
pip install openai python-dotenv
```

### Supplementary: Differences Between .env File and Virtual Environment

- **Virtual Environment (venv):**  
  A virtual environment is a self-contained directory that contains a Python installation for your project along with its dependencies. This ensures that your project uses the correct versions of libraries without affecting other projects or system-wide packages.

- **.env File:**  
  A `.env` file is used to store environment-specific configuration, such as API keys, database credentials, or other sensitive data. It keeps sensitive information out of your codebase and allows you to change configurations without modifying your source code.

**Both tools serve different purposes and are best used together:**

- Use a **venv** to manage your project's dependencies.
- Use a **.env file** to manage sensitive configuration data.

## Forking and Keeping Your Copy Up-to-Date

To work on your own copy of this repository without affecting the original, follow these steps:

### 1. Fork the Repository

- Navigate to the GitHub page for this repository.
- Click the **"Fork"** button in the top-right corner to create your own copy in your GitHub account.

### 2. Clone Your Fork Locally

Once you have forked the repository, clone your fork to your local machine:
```bash
git clone https://github.com/your-username/dpi-681.git
```
Replace `your-username` with your GitHub username.

### 3. Set Up the Upstream Remote

After cloning your fork, set the original repository as the upstream remote so you can pull in future updates:
```bash
cd your-repo
git remote add upstream https://github.com/calisley/dpi-681.git
```
Replace `original-username` with the GitHub username of the repository owner.

### 4. Re-Pulling Updates from Upstream

When new materials or updates are added to the original repository, you can update your fork by following these steps:

1. **Fetch the latest changes from upstream:**
   ```bash
   git fetch upstream
   ```

2. **Merge the changes into your local main branch:**
   ```bash
   git checkout main
   git merge upstream/main
   ```
   If you prefer to rebase:
   ```bash
   git checkout main
   git rebase upstream/main
   ```

3. **Push the updates to your fork (if desired):**
   ```bash
   git push origin main
   ```
