# Focus Hub 🎯

> **Stop Doomscrolling. Start Studying.** > A distraction-free environment to curate your own study materials without the algorithmic noise.

## 📖 About The Project

**Focus Hub** solves the problem of getting distracted while studying online. Instead of watching educational videos on YouTube—where the sidebar and homepage are designed to distract you—you can embed them here. 

This app acts as a **centralized study dashboard** where you can organize videos into playlists, upload PDF notes, and save important web links, all in a calm, "earthy" aesthetic designed for focus.

### ✨ Key Features
* **🚫 Distraction-Free Video Player:** Watch YouTube videos without ads, sidebars, or "Up Next" recommendations.
* **📂 Playlist Folders:** Organize your videos into specific subjects (e.g., Math, Physics, Coding).
* **📄 Resource Manager:** Upload PDF notes and textbooks to keep them right next to your videos.
* **🔗 Link Saver:** Save important articles or discussion threads (Quora/Reddit) so you don't lose them.
* **🔐 User Accounts:** Secure login/registration system. Each user's data is private and isolated.
* **🎨 Calming UI:** A custom "Sage & Cream" color palette designed to reduce eye strain and anxiety.

---

## 🛠️ Tech Stack

* **Backend:** Python (Flask)
* **Database:** SQLite (SQLAlchemy)
* **Frontend:** HTML5, CSS3, Bootstrap 5
* **Authentication:** Flask-Login
* **Fonts:** Playfair Display (Headers), Segoe UI (Body)

---

## 🎨 Color Palette

| Color | Hex | Usage |
| :--- | :--- | :--- |
| **Cream** | `#F6F0D7` | Main Background |
| **Sage Green** | `#9CAB84` | Primary Buttons |
| **Olive Dark** | `#89986D` | Navbar & Headings |
| **Light Green** | `#C5D89D` | Card Accents |

---

## 🚀 Getting Started

Follow these instructions to run the project on your local machine.

### Prerequisites
* Python 3.x installed
* Git installed

### Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/YOUR-USERNAME/focus-hub.git](https://github.com/YOUR-USERNAME/focus-hub.git)
    cd focus-hub
    ```

2.  **Create a Virtual Environment**
    * Windows:
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```
    * Mac/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install Dependencies**
    ```bash
    pip install flask flask-sqlalchemy flask-login flask-wtf wtforms
    ```

4.  **Initialize the Uploads Folder**
    (This ensures the folder exists for PDF uploads)
    ```bash
    # Windows (PowerShell)
    New-Item -Path static/uploads -ItemType Directory -Force
    
    # Mac/Linux
    mkdir -p static/uploads
    ```

5.  **Run the Application**
    ```bash
    python app.py
    ```

6.  **Open in Browser**
    Visit `http://127.0.0.1:5000` to see the app.

---

## 📂 Project Structure

```text
focus_hub/
├── static/
│   ├── style.css        # Custom styling
│   └── uploads/         # User PDF storage
├── templates/
│   ├── layout.html      # Base template with Navbar
│   ├── index.html       # Landing Page
│   ├── dashboard.html   # Main Hub (Playlist Folders)
│   ├── playlist.html    # Video Player View
│   ├── login.html
│   └── register.html
├── app.py               # Main Flask Application
└── database.db          # SQLite Database (Auto-created)
