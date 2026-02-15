from botasaurus.browser import browser, Driver
import pandas as pd
import time



def Get_Story_Url():
    """_summary_
        Calls the website and in each loop
        fetches the links of stories and clicks the next page button.
    Returns:
        _1D list_: _of Url's of the stories_
    """
    
    # visit to the website
    driver = Driver(headless=True)
    driver.get("https://www.urdupoint.com/kids/category/moral-stories-page1.html")
    story_url = []
    for i in range(40):
        # find the url of the top 10 stories
        # go to the next page
        # repeat until the next button page is stopped working
        
        
        stories_anchor_tags = driver.select_all("a.sharp_box") # will fetch the urls of the stories
        urls = [i.get_attribute('href') for i in stories_anchor_tags ]
        story_url.extend(urls)
        next_page_button = driver.get_element_with_exact_text(" Next Page ")
        next_page_button.click()
    
    df = pd.DataFrame({'Urls': story_url})
    df.to_csv("Scraping/Stories_Urls.csv", index=False)
    
    #  store the links in the csv files
    return story_url


# @browser (
#     headless=True
# )
def Scrape_Data(folderPath = "Scraping"):
    """
        This function extracts the text of the stories,
        Saves the text of each of the story to the doc#.txt
    

    Args:
        Folder Path is the Scrapping Folder.
    """
    
    print("Reading the Csv File...")
    try:
        story_urls = pd.read_csv(f"{folderPath}/Stories_Urls.csv")
        
        
        if (len(story_urls) == 0):
            print("File not found. Fetching Urls...")
            story_urls = Get_Story_Url()
    except Exception as e:
        print("Error: " ,e)
        return    
    print("Getting Texts from each of the story...")
    docNumber = 1
    for i in range(0, 200):
        driver = Driver(headless=True)
        driver.get(story_urls["Urls"][i])
        text = driver.select('div.txt_detail').text
        
        with open(f"{folderPath}/Documents/doc{docNumber}.txt", 'w', encoding='utf-8') as f:
            f.write(text)
        docNumber += 1  
        
Scrape_Data()