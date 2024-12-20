import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
import os

def extract_wikipedia_table(url):
    """
    Extracts a Wikipedia table from a given URL and converts it to CSV.

    Args:
        url: The URL of the Wikipedia page.

    Returns:
        A tuple containing:
            - CSV data as a string, or None if an error occurs.
            - Table title (string), or None if not found or multiple tables.
            - Error message (string), or None if no error.
        If multiple tables are found returns a list of titles, and the list of tables.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        tables = soup.find_all('table', class_='wikitable')
        if not tables:
            return None, None, "No wikitable found on this page."

        if len(tables) > 1:
            table_titles = []
            for i, table in enumerate(tables):
                caption = table.find('caption')
                if caption:
                    table_titles.append(f"{i+1}. {caption.text.strip()}")
                else:
                    table_titles.append(f"{i+1}. Table {i+1}")
            return table_titles, tables, None
        else:
            table = tables[0]
            caption = table.find('caption')
            table_title = caption.text.strip() if caption else "Wikipedia_Table"
            df = pd.read_html(str(table), header=0)[0]
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            return csv_buffer.getvalue(), table_title, None

    except requests.exceptions.RequestException as e:
        return None, None, f"Error fetching URL: {e}"
    except pd.errors.ParserError as e:
        return None, None, f"Error parsing table: {e}. The table may be too complex or malformed."
    except Exception as e:
        return None, None, f"An unexpected error occurred: {e}"

if __name__ == "__main__":
    wiki_url = input("Enter the Wikipedia URL: ")
    table_data, table_title, error_message = extract_wikipedia_table(wiki_url)

    if error_message:
        print(error_message)
    elif isinstance(table_data, list):
        print("Multiple tables found:")
        for title in table_data:
            print(title)
        while True:
            try:
                table_index = int(input("Enter the number of the table you want: ")) - 1
                if 0 <= table_index < len(table_data):
                    table = table_data[table_index]
                    caption = table.find('caption')
                    table_title = caption.text.strip() if caption else f"Wikipedia_Table_{table_index+1}"
                    df = pd.read_html(str(table), header=0)[0]
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)
                    table_data = csv_buffer.getvalue()
                    break
                else:
                    print("Invalid table number. Please choose a number from the list.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    if table_data and table_title:
        # Create the "databases" directory if it doesn't exist
        os.makedirs("databases", exist_ok=True)

        # Sanitize the filename to remove invalid characters
        filename = "".join(x for x in table_title if (x.isalnum() or x in "._- ")).strip() + ".csv"
        filepath = os.path.join("databases", filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f: #added encoding
                f.write(table_data)
            print(f"Table saved to: {filepath}")
        except Exception as e:
            print(f"Error saving file: {e}")