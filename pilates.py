from playwright.sync_api import sync_playwright
import json

URL = 'https://www.pilates.org.au/find/studio-instructor'

def run(playwright, postcode):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto(URL, timeout=90000)
    print(f'Postcode = {postcode}')
    data = []
    page.fill('#addressInput', str(postcode))
    page.locator('#addressSubmit').click()
    try:
        try:
            page.wait_for_selector('.no_results_found')
            print(f'[INFO] No result found for {postcode}')
        except:
            page.wait_for_selector('.results_wrapper')
    except Exception as e:
        print(f'[ERROR] {e}')
    else:
        boxes = page.query_selector_all('.results_wrapper')
        for idx, box in enumerate(boxes):
            item = {}
            side_left = box.query_selector('.results_row_left_column')
            item['name'] = side_left.query_selector('.location_name').inner_text()
            item['profession'] = side_left.query_selector('.slp_result_address').inner_text()
            side_center = box.query_selector('.results_row_center_column')
            item['studio'] = side_center.query_selector('.slp_result_address').inner_text()
            address1 = side_center.query_selector_all('.slp_result_street')[-1].inner_text()
            address2 = side_center.query_selector('.slp_result_street2').inner_text()
            item['street'] = ' '.join([address1, address2])
            item['citystatezip'] = side_center.query_selector('.slp_result_citystatezip').inner_text()
            try:
                item['phone'] = side_center.query_selector('.slp_result_phone').inner_text()
            except Exception as e:
                pass
            item['email'] = box.query_selector('a#slp_marker_email').get_attribute('href').replace('mailto:', '')
            print(idx, ':', item['name'], f"{item['citystatezip']}")
            data.append(item)
        if len(data) > 0:
            with open(f'pilates/{postcode}.json', 'w') as fout:
                json.dump(data, fout)
    finally:
        browser.close()

with sync_playwright() as playwright:
    with open('postcode.txt') as f:
        postcodes = [line.rstrip() for line in f]
    for postcode in postcodes[0:1000]:
        run(playwright, postcode)
