@echo off
set GOOGLE_MAPS_API_KEY=AIzaSyDrkgPuGY7tUOJSGvEqQiVQKa9YrtVYnCo
set GOOGLE_PLACES_API_KEY=AIzaSyDrkgPuGY7tUOJSGvEqQiVQKa9YrtVYnCo
set CENSUS_API_KEY=37de8144df63b38cd5a7e7f866d6cef946d96a44
set GEMINI_API_KEY=AIzaSyD9CFgKXqJkG66mUuxWeHzZaw-VdXAC4Y

echo Starting Brightspot Locator AI with API keys configured...
echo.
echo IMPORTANT: Make sure these APIs are enabled in Google Cloud Console:
echo   1. Geocoding API - https://console.cloud.google.com/apis/library/geocoding-backend.googleapis.com
echo   2. Places API - https://console.cloud.google.com/apis/library/places-backend.googleapis.com
echo   3. Distance Matrix API - https://console.cloud.google.com/apis/library/distance-matrix-backend.googleapis.com
echo.
python run.py
