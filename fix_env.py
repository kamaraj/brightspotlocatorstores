"""
Fix .env file with correct API keys
"""
import re

# Read the .env.example as template
with open('.env.example', 'r', encoding='utf-8') as f:
    content = f.read()

# Update with actual API keys
api_keys = {
    'GOOGLE_MAPS_API_KEY': 'AIzaSyDrkgPuGY7tUOJSGvEqQiVQKa9YrtVYnCo',
    'CENSUS_API_KEY': '37de8144df63b38cd5a7e7f866d6cef946d96a44',
    'GEMINI_API_KEY': 'AIzaSyD9CFgKXqJkG66mUuxWeHzZaw-VdXAC4Y',
}

for key, value in api_keys.items():
    # Replace the placeholder values
    content = re.sub(
        f'{key}="[^"]*"',
        f'{key}="{value}"',
        content
    )
    content = re.sub(
        f'{key}=[^\n]*',
        f'{key}="{value}"',
        content
    )

# Write to .env
with open('.env', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ .env file updated successfully")
print("\nAPI Keys configured:")
for key in api_keys:
    print(f"  - {key}")
