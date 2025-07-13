import os
import sqlite3
import json
import asyncio
import re
from telethon import TelegramClient
from telethon.tl.types import PeerChannel, PeerUser
from telethon.errors import FloodWaitError, RPCError
import sys
import csv

# Configuration
STATE_FILE = 'state.json'
BATCH_SIZE = 100  # Fetch 100 messages per request
REQUEST_DELAY = 3  # 3 seconds between requests to respect rate limits
GROUP_LINK_REGEX = r'(t\.me/\+[a-zA-Z0-9_-]+|t\.me/joinchat/[a-zA-Z0-9_-]+)'  # Regex for group invite links

# ASCII art (unchanged)
def display_ascii_art():
    WHITE = "\033[97m"
    RESET = "\033[0m"
    art = r"""
___________________  _________
\__    ___/  _____/ /   _____/
  |    | /   \  ___ \_____  \ 
  |    | \    \_\  \/        \
  |____|  \______  /_______  /
                 \/        \/
    """
    print(WHITE + art + RESET)

display_ascii_art()

# State management (unchanged)
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {'api_id': None, 'api_hash': None, 'phone': None, 'dialogs': {}}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

state = load_state()

if not state['api_id'] or not state['api_hash'] or not state['phone']:
    state['api_id'] = int(input("Enter your API ID: "))
    state['api_hash'] = input("Enter your API Hash: ")
    state['phone'] = input("Enter your phone number: ")
    save_state(state)

client = TelegramClient('session', state['api_id'], state['api_hash'])

# Database setup
def init_db():
    conn = sqlite3.connect('user_ids.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_ids
                 (sender_id INTEGER PRIMARY KEY)''')
    # New table for group links
    c.execute('''CREATE TABLE IF NOT EXISTS group_links
                 (link TEXT PRIMARY KEY, dialog_id TEXT, message_id INTEGER)''')
    conn.commit()
    conn.close()

def save_user_id(sender_id):
    if not sender_id:  # Skip if no sender_id
        return
    conn = sqlite3.connect('user_ids.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO user_ids (sender_id) VALUES (?)', (sender_id,))
    conn.commit()
    conn.close()

def save_group_link(link, dialog_id, message_id):
    if not link:  # Skip if no link
        return
    conn = sqlite3.connect('user_ids.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO group_links (link, dialog_id, message_id) VALUES (?, ?, ?)',
              (link, str(dialog_id), message_id))
    conn.commit()
    conn.close()

# Scrape user IDs and group links from a dialog
async def scrape_dialog(dialog_id, offset_id=0):
    try:
        entity = await client.get_entity(PeerChannel(int(dialog_id)) if dialog_id.startswith('-') else PeerUser(int(dialog_id)) if dialog_id.isdigit() else dialog_id)
        total_messages = 0
        async for message in client.iter_messages(entity, limit=0):
            total_messages += 1  # Count total messages for progress

        if total_messages == 0:
            print(f"No messages in dialog {dialog_id}.")
            return

        processed_messages = 0
        while processed_messages < total_messages:
            try:
                messages = await client.get_messages(entity, limit=BATCH_SIZE, offset_id=offset_id)
                if not messages:
                    break
                for message in messages:
                    if message.sender_id:
                        save_user_id(message.sender_id)
                    # Extract group invite links from message text
                    if message.text:
                        links = re.findall(GROUP_LINK_REGEX, message.text)
                        for link in links:
                            save_group_link(link, dialog_id, message.id)
                            print(f"\nFound group invite link in {dialog_id}: {link}")
                    processed_messages += 1
                    offset_id = message.id
                progress = (processed_messages / total_messages) * 100
                sys.stdout.write(f"\rScraping dialog {dialog_id}: {progress:.2f}% complete")
                sys.stdout.flush()
                await asyncio.sleep(REQUEST_DELAY)  # Respect rate limits
            except FloodWaitError as e:
                print(f"\nFlood wait: {e.seconds} seconds")
                await asyncio.sleep(e.seconds)
            except RPCError as e:
                print(f"\nError scraping dialog {dialog_id}: {e}")
                break

        state['dialogs'][dialog_id] = offset_id
        save_state(state)
        print(f"\nFinished scraping dialog {dialog_id}. Processed {processed_messages} messages.")
    except Exception as e:
        print(f"Error with dialog {dialog_id}: {e}")

# Continuous scraping (unchanged)
async def continuous_scraping():
    global continuous_scraping_active
    continuous_scraping_active = True
    try:
        while continuous_scraping_active:
            for dialog_id in state['dialogs']:
                print(f"\nChecking for new messages in dialog: {dialog_id}")
                await scrape_dialog(dialog_id, state['dialogs'][dialog_id])
            await asyncio.sleep(60)  # Check every minute
    except asyncio.CancelledError:
        print("Continuous scraping stopped.")
        continuous_scraping_active = False

# Export user IDs and group links to files
def export_user_ids():
    conn = sqlite3.connect('user_ids.db')
    c = conn.cursor()
    # Export user IDs
    c.execute('SELECT sender_id FROM user_ids')
    user_ids = [row[0] for row in c.fetchall()]
    with open('user_ids.txt', 'w') as f:
        for user_id in user_ids:
            f.write(f"{user_id}\n")
    print(f"Exported {len(user_ids)} unique user IDs to user_ids.txt")
    # Export group links
    c.execute('SELECT link, dialog_id, message_id FROM group_links')
    group_links = c.fetchall()
    with open('group_links.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Link', 'Dialog ID', 'Message ID'])
        for link in group_links:
            writer.writerow(link)
    print(f"Exported {len(group_links)} group links to group_links.csv")
    conn.close()

# List all dialogs (unchanged)
async def list_dialogs():
    try:
        print("\nList of dialogs (DMs, groups, channels):")
        async for dialog in client.iter_dialogs():
            if dialog.id != 777000:  # Skip Telegram system account
                print(f"* {dialog.title} (#ID{dialog.id})")
    except Exception as e:
        print(f"Error listing dialogs: {e}")

# Menu (updated to mention group links in export)
async def manage_dialogs():
    init_db()
    while True:
        print("\nMenu:")
        print("[A] Add dialog (group, channel, or DM)")
        print("[R] Remove dialog")
        print("[S] Scrape all dialogs")
        print("[C] Continuous scraping")
        print("[E] Export user IDs and group links")
        print("[V] View saved dialogs")
        print("[L] List account dialogs")
        print("[Q] Quit")

        choice = input("Enter your choice: ").lower()
        match choice:
            case 'a':
                dialog_id = input("Enter dialog ID (e.g., -123456 for groups, 123456 for users): ")
                state['dialogs'][dialog_id] = 0
                save_state(state)
                print(f"Added dialog {dialog_id}.")
            case 'r':
                dialog_id = input("Enter dialog ID to remove: ")
                if dialog_id in state['dialogs']:
                    del state['dialogs'][dialog_id]
                    save_state(state)
                    print(f"Removed dialog {dialog_id}.")
                else:
                    print(f"Dialog {dialog_id} not found.")
            case 's':
                for dialog_id in state['dialogs']:
                    await scrape_dialog(dialog_id, state['dialogs'][dialog_id])
            case 'c':
                global continuous_scraping_active
                continuous_scraping_active = True
                task = asyncio.create_task(continuous_scraping())
                print("Continuous scraping started. Press Ctrl+C to stop.")
                try:
                    await asyncio.sleep(float('inf'))
                except KeyboardInterrupt:
                    continuous_scraping_active = False
                    task.cancel()
                    print("\nStopping continuous scraping...")
                    await task
            case 'e':
                export_user_ids()
            case 'v':
                if not state['dialogs']:
                    print("No dialogs to view.")
                else:
                    print("\nSaved dialogs:")
                    for dialog_id, last_id in state['dialogs'].items():
                        print(f"Dialog ID: {dialog_id}, Last Message ID: {last_id}")
            case 'l':
                await list_dialogs()
            case 'q':
                print("Quitting...")
                sys.exit()
            case _:
                print("Invalid option.")

async def main():
    await client.start()
    await manage_dialogs()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting...")
        sys.exit()
