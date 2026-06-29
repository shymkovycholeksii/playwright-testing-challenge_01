from playwright.sync_api import sync_playwright
import datetime

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://testingchallenges.thetestingmap.org/challenge6.php")
        
        # Get default value
        default_val = page.locator('input[name="date_time"]').input_value()
        print(f"Default date_time: {default_val}")
        
        parts = default_val.split(" ")
        date_parts = parts[0].split("/")
        time_parts = parts[1].split(":")
        
        day = int(date_parts[0])
        month = int(date_parts[1])
        year = int(date_parts[2])
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        
        dt_default = datetime.datetime(year, month, day, hour, minute)
        dt_current = dt_default - datetime.timedelta(minutes=70)
        
        candidates = []
        
        # 1. Past dates in 2017
        dt_yesterday = dt_current - datetime.timedelta(days=1)
        candidates.append(dt_yesterday.strftime("%d/%m/%Y %H:%M")) # Yesterday
        candidates.append("01/01/2017 12:00") # Beginning of 2017
        candidates.append("15/05/2017 12:00") # Past month
        
        # 2. Format variations
        candidates.append("15-06-2017 22:45")
        candidates.append("15.06.2017 22:45")
        candidates.append("15/06/2017 22.45")
        candidates.append("15/06/2017")
        candidates.append("22:45")
        candidates.append("15/6/2017 22:45")
        candidates.append("15/06/17 22:45")
        candidates.append("5/06/2017 22:45")
        candidates.append("15/06/2017 2:45")
        candidates.append("15/06/2017 22:5")
        candidates.append("15 / 06 / 2017 22:45")
        
        # 3. Nonexistent Feb dates
        candidates.append("30/02/2017 22:45")
        candidates.append("31/02/2017 22:45")
        
        # 4. Other 30-day month limits
        candidates.append("31/04/2017 22:45")
        candidates.append("31/06/2017 22:45")
        candidates.append("31/09/2017 22:45")
        candidates.append("31/11/2017 22:45")
        
        # 5. Extremes
        candidates.append("99/99/9999 99:99")
        candidates.append("00/00/0000 00:00")
        
        found_descriptions = set()
        
        # First populate with already known descriptions
        known_inputs = [
            "00/06/2017 22:45",
            "32/01/2017 22:45",
            "31/04/2017 22:45",
            "29/02/2017 22:45",
            "15/00/2017 22:45",
            "15/13/2017 22:45",
            "31/12/2016 23:59",
            "01/01/2018 00:00",
            "15/06/2017 24:00",
            "15/06/2017 22:60",
            dt_current.strftime("%d/%m/%Y %H:%M")
        ]
        
        # Pre-fill session with known ones
        for inp in known_inputs:
            page.goto("http://testingchallenges.thetestingmap.org/challenge6.php")
            page.locator('input[name="date_time"]').fill(inp)
            page.locator('input[type="submit"]').click()
            
        items = page.locator("ul.values-description li").all_text_contents()
        for item in items:
            found_descriptions.add(item)
            
        print(f"Loaded {len(found_descriptions)} known checks.")
        
        # Now fuzz the new ones
        for inp in candidates:
            page.goto("http://testingchallenges.thetestingmap.org/challenge6.php")
            page.locator('input[name="date_time"]').fill(inp)
            page.locator('input[type="submit"]').click()
            
            checks = page.locator("span.values-tested").text_content()
            items = page.locator("ul.values-description li").all_text_contents()
            
            for item in items:
                if item not in found_descriptions:
                    found_descriptions.add(item)
                    print(f"[NEW CHECK] Count={len(found_descriptions)}: '{item}' (triggered by '{inp}')")
                    
            if len(found_descriptions) == 16:
                print("All 16 checks found!")
                break
                
        print(f"\nTotal checks found: {len(found_descriptions)}")
        print("Descriptions:", sorted(list(found_descriptions)))
        browser.close()

if __name__ == "__main__":
    run()
