Telegram Scraper
A Python-based Telegram scraper that collects user IDs and group invitation links from Telegram dialogs (groups, channels, or direct messages). Built with Telethon, this tool stores data in an SQLite database and exports results to text and CSV files.
Features

User ID Collection: Scrapes unique user IDs from messages in specified Telegram dialogs.
Group Invite Link Extraction: Detects and saves Telegram group invitation links (e.g., t.me/+... or t.me/joinchat/...) from message text.
SQLite Storage: Stores user IDs and group links in a local SQLite database (user_ids.db) to ensure uniqueness and track metadata.
Export Functionality: Exports user IDs to user_ids.txt and group links to group_links.csv for easy access.
Continuous Scraping: Supports continuous monitoring of dialogs for new messages and links.
Rate Limit Handling: Implements delays and flood wait handling to comply with Telegram's API limits.
Interactive Menu: User-friendly CLI menu to manage dialogs, scrape data, and export results.
State Persistence: Saves API credentials and dialog progress in a JSON file (state.json) for seamless resumption.
Dialog Management: Add, remove, view, and list dialogs (groups, channels, DMs) for targeted scraping.

Prerequisites

Python 3.7+: Ensure Python is installed.
Telethon: Python library for interacting with Telegram's API.
SQLite: Included with Python, no separate installation needed.
Telegram API Credentials:
API ID and API Hash from my.telegram.org.
Phone Number associated with a Telegram account.



Installation

Clone the Repository:
git clone https://github.com/yourusername/telegram-scraper.git
cd telegram-scraper


Install Dependencies:
pip install telethon


Set Up API Credentials:

Run the script for the first time, and it will prompt you to enter:
API ID: Your Telegram API ID.
API Hash: Your Telegram API Hash.
Phone Number: Your Telegram account phone number (e.g., +1234567890).


These are saved in state.json for future runs.



Usage

Run the Script:
python scraper.py


Initial Setup:

On first run, enter your Telegram API credentials and phone number.
Authenticate with Telegram if prompted (you may receive a code via Telegram).


Menu Options:Upon running, the script displays an interactive menu:
Menu:
[A] Add dialog (group, channel, or DM)
[R] Remove dialog
[S] Scrape all dialogs
[C] Continuous scraping
[E] Export user IDs and group links
[V] View saved dialogs
[L] List account dialogs
[Q] Quit


Add Dialog (A): Enter a dialog ID (e.g., -123456 for groups, 123456 for users) to scrape.
Remove Dialog (R): Remove a dialog ID from the scraping list.
Scrape All Dialogs (S): Scrape user IDs and group links from all saved dialogs.
Continuous Scraping (C): Continuously monitor dialogs for new messages/links (stop with Ctrl+C).
Export User IDs and Group Links (E): Export user IDs to user_ids.txt and group links to group_links.csv.
View Saved Dialogs (V): Display all dialogs being scraped.
List Account Dialogs (L): List all dialogs in your Telegram account.
Quit (Q): Exit the script.


Output Files:

user_ids.txt: Contains unique user IDs (one per line).
group_links.csv: Contains group invite links, dialog IDs, and message IDs (CSV format).



Tutorial
Step 1: Set Up and Authenticate

Run python scraper.py.
Enter your API ID, API Hash, and phone number when prompted.
Authenticate with the code sent to your Telegram account.

Step 2: Add Dialogs

Select [L] to list all dialogs in your Telegram account to find IDs.
Example output: * My Group (#ID-123456) or * John Doe (#ID123456).


Select [A] and enter a dialog ID (e.g., -123456 for a group).
Repeat for all dialogs you want to scrape.

Step 3: Scrape Data

Select [S] to scrape all saved dialogs.
The script will fetch messages in batches, extract user IDs, and detect group invite links (e.g., t.me/+abc123).
Progress is displayed (e.g., Scraping dialog -123456: 75.50% complete).


Alternatively, select [C] for continuous scraping (checks every 60 seconds).

Step 4: Export Results

Select [E] to export:
User IDs to user_ids.txt (e.g., 123456, 789012).
Group links to group_links.csv (e.g., t.me/+abc123,-123456,1001).


Check the output files in the project directory.

Step 5: Manage Dialogs

Use [V] to view saved dialogs and their last scraped message IDs.
Use [R] to remove dialogs you no longer want to scrape.

Configuration

STATE_FILE: state.json stores API credentials and dialog progress.
BATCH_SIZE: 100 messages per request (adjustable in code).
REQUEST_DELAY: 3 seconds between requests to avoid rate limits.
GROUP_LINK_REGEX: Matches t.me/+... and t.me/joinchat/... links.

Notes

Rate Limits: The script includes delays and flood wait handling to comply with Telegram's API limits. Avoid adding too many dialogs at once to prevent temporary bans.
Group Links: Only links matching the regex are saved. To support other formats, modify GROUP_LINK_REGEX in the code.
Database: Data is stored in user_ids.db (SQLite) with tables user_ids and group_links.
Safety: Be cautious when joining groups from scraped links to avoid bans. Automated joining is not included but can be added with safeguards.

Contributing
Contributions are welcome! Please submit a pull request or open an issue for bugs, features, or improvements.
License
This project is licensed under the MIT License.
