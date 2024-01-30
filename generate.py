"""
MIT License

Copyright (c) 2024 Digital Descent

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from datetime import datetime
import requests
import json
import sys
import os

def generate_api_collection() -> None:
    """
    Generates the Postman API collection
    """

    # Define the URL
    steam_api_key = os.environ.get('STEAM_API_KEY', None)
    if steam_api_key is None:
        print("Please set the STEAM_API_KEY environment variable to your Steam Web API key")
        return
    
    url = f'https://api.steampowered.com/ISteamWebAPIUtil/GetSupportedAPIList/v1/?key={steam_api_key}'

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        input_data = response.json()

        # Create a dictionary to store methods grouped by interface
        methods_by_interface = {}

        # Iterate through interfaces and methods
        for interface in input_data["apilist"]["interfaces"]:
            interface_name = interface["name"]
            methods = interface["methods"]

            # Create a folder for the interface if it doesn't exist
            if interface_name not in methods_by_interface:
                methods_by_interface[interface_name] = []

            # Add methods to the corresponding folder
            methods_by_interface[interface_name].extend(methods)

        # Get the current date in "MM.DD.YYYY" format
        current_date = datetime.now().strftime("%m.%d.%Y")

        # Create a new Postman collection with the date in the name
        postman_collection = {
            "info": {
                "name": f"Steam Web API {current_date}",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": []
        }

        # Iterate through interfaces and their methods
        for interface_name, methods in methods_by_interface.items():
            # Create a folder for the interface
            interface_folder = {
                "name": interface_name,
                "item": []
            }

            # Iterate through methods and add them to the folder
            for method in methods:
                # Create a Postman request item
                request_item = {
                    "name": method["name"],
                    "request": {
                        "method": method["httpmethod"],
                        "url": {
                            "raw": "https://api.steampowered.com",
                            "host": ["api", "steampowered", "com"]
                        },
                        "header": [],
                        "body": {
                            "mode": "formdata",
                            "formdata": []
                        },
                        "description": method.get("description", "")
                    }
                }

                # Add parameters as request parameters
                for param in method["parameters"]:
                    param_item = {
                        "key": param["name"],
                        "value": "",
                        "description": param.get("description", "")
                    }

                    if param["type"] == "uint64":
                        param_item["type"] = "number"
                    elif param["type"] == "string":
                        param_item["type"] = "text"

                    request_item["request"]["body"]["formdata"].append(param_item)

                # Add the request item to the folder
                interface_folder["item"].append(request_item)

            # Add the interface folder to the collection
            postman_collection["item"].append(interface_folder)

        # Save the Postman collection as a JSON file
        with open("steam_api_collection.json", "w") as outfile:
            json.dump(postman_collection, outfile, indent=4)

        print("Postman collection JSON file generated successfully!")

    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")

def main() -> int:
    """
    Main entry point into the steam api generation tool
    """

    generate_api_collection()

    return 0

if __name__ == "__main__":
    sys.exit(main())