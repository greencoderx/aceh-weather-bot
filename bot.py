name: Aceh Weather Bot v2

on:
  schedule:
    # Changed from "*/5 * * * *" to "*/15 * * * *" to further reduce API load
    - cron: "*/15 * * * *"
  workflow_dispatch:

jobs:
  run-bot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      # Step 1: Download the cached IDs from the previous run
      - name: Download User IDs Cache
        uses: actions/download-artifact@v4 # FIX: Updated from v3 to v4
        with:
          name: source-user-ids-cache
          path: .
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.x'
          
      - run: pip install tweepy
      
      # Step 2: Run the bot. The bot will load IDs from the downloaded file.
      - name: Run Bot Script
        run: python bot.py
        env:
          BEARER_TOKEN: ${{ secrets.BEARER_TOKEN }}
          API_KEY: ${{ secrets.API_KEY }}
          API_SECRET: ${{ secrets.API_SECRET }}
          ACCESS_TOKEN: ${{ secrets.ACCESS_TOKEN }}
          ACCESS_SECRET: ${{ secrets.ACCESS_SECRET }}
          
      # Step 3: Upload the IDs file (in case they were newly fetched or updated)
      - name: Upload User IDs Cache
        uses: actions/upload-artifact@v4 # FIX: Updated from v3 to v4
        with:
          name: source-user-ids-cache
          path: source_ids.json
          # Note: 'if-no-files-found' is not a v4 input, but the action handles missing files gracefully.
