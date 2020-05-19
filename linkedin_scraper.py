
# Importing Libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from datetime import datetime
from time import sleep
import pandas as pd
import numpy as np
import os

# Defining function

def scraper(keyword, start_page = 1, end_page = 100):
    
    #Timer - Start
    start_time_outer = datetime.now()
    
    # Login 
    driver = webdriver.Chrome('/Users/sharm/webdrivers/chromedriver') #Path to Chrome driver exe
    driver.get('https://www.linkedin.com/login')
    username = driver.find_element_by_id('username')
    username.send_keys('email@gmail.com') #Enter Email gere

    password = driver.find_element_by_id('password')
    password.send_keys('P@ssw0rd')  #enter password here

    login_button =  driver.find_element_by_class_name('btn__primary--large')
    login_button.click()
    search = keyword.replace(' ','%20') #Search keyword
    sleep(2)
    
    # Keyword search
    driver.get('https://www.linkedin.com/search/results/people/?keywords='+ search +'&origin=GLOBAL_SEARCH_HEADER&')
    driver.execute_script("window.scrollTo(0,1000);")
    sleep(2)
    pages = driver.find_elements_by_class_name('artdeco-pagination__indicator')
    
        
    # Pagination
    last_page = int(pages[-1].text)
    
    if end_page >= last_page:
        end_page = last_page

    page_range = range(start_page, end_page+1)
    sleep(1)

    urls = []

    for page_count in page_range:
        page_link = 'https://www.linkedin.com/search/results/people/?keywords='+ search +'&origin=GLOBAL_SEARCH_HEADER&page='+str(page_count)
        driver.get(page_link)
        sleep(1)

        # Collecting profile links
        driver.execute_script("window.scrollTo(0,1000);")
        sleep(2)

        # List of results
        result= driver.find_elements_by_class_name('search-result__result-link')

        for i in range(0,len(result),2):
            urls.append(result[i].get_attribute('href'))
        sleep(0.5)

    # Accessing csv file

    filename = 'candidates.csv'  
    
    if os.path.exists(filename):
        append_write = 'a'
    
    else:
        append_write = 'w'
        
        
    f = open(filename, append_write)
    
    if append_write == 'w':
        headers = 'Name,Title,Designation,Company,Duration,College,Degree,Subject,Skills,URL,Searched_By\n'
        f.write(headers)


    counter = 1 # To keep track of profiles
    

    # Scrapping

    for profile_link in urls:

        driver.get(profile_link)
        
        try:
            start_time_inner = datetime.now()   # Start time for profile extraction
            ## Profile extraction

            # Heading
            try:
                name = driver.find_element_by_class_name('inline').text.replace(',','-')
                title = driver.find_elements_by_class_name('mt1')[1].text.replace(',','-')
                driver.execute_script("window.scrollTo(0,500);")
                # sleep(1)
            except NoSuchElementException:
                name = 'N/A'
                title = 'N/A'

            # Experience
            try:

                WebDriverWait(driver, 10).until(lambda x: x.find_element_by_class_name('pv-entity__position-group-pager'))
                sleep(1)
                exp = driver.find_elements_by_class_name('pv-entity__position-group-pager')

                designation = []
                company = []
                duration = []

                for idx in range(len(exp)):
                    exp_details = exp[idx].text.split('\n')[::2]
                    designation.append(exp_details[0].replace(',','-'))
                    company.append(exp_details[1].replace(',','-'))

                    if len(exp_details)>=4:
                        duration.append(exp_details[3])
                    #sleep(0.5)

            except NoSuchElementException:
                designation = 'N/A'
                company = 'N/A'
                duration = 'N/A'

            except TimeoutException:
                pass


            # Education
            try:
                WebDriverWait(driver, 10).until(lambda x: x.find_elements_by_id('education-section'))
                sleep(1)
                edu = driver.find_elements_by_id('education-section')
                college = []
                degree = []
                subject = []

                for idx in range(len(edu)):
                    edu_details = edu[0].text.split('\n')
                    college.append(edu_details[1].replace(',','-'))

                    if len(edu_details)>=4:
                        degree.append(edu_details[3].replace(',','-'))

                    if len(edu_details)>=6:
                        subject.append(edu_details[5].replace(',','-'))
                sleep(0.5)

            except NoSuchElementException:            
                college = 'N/A'
                degree = 'N/A'
                subject = 'N/A'

            except TimeoutException:
                pass


            # Skills
            ## Srolling down to extract skills

            driver.execute_script("window.scrollTo(0,2000);")
            sleep(3)

            try:
                skill_more_button = driver.find_elements_by_class_name('pv-profile-section__card-action-bar')[0]
                #skill_more_button.click()
                driver.execute_script("arguments[0].click();", skill_more_button)

                sleep(1)


                skill_class = driver.find_elements_by_class_name('pv-skill-category-entity__name')
                skills = ' | '.join([skill.text.replace(',','-') for skill in skill_class])

            except NoSuchElementException:
                skills = 'N/A'

            except IndexError:
                pass

            # Formatting
            designation_info = ' | '.join(designation)
            company_info = ' | '.join(company)
            duration_info = ' | '.join(duration) 
            college_info = ' | '.join(college)
            degree_info = ' | '.join(degree)
            subject_info = ' | '.join(subject)
            profile_url = profile_link

            try:
                f.write(name + ',' +title+ ',' + designation_info + ',' + company_info + ',' + duration_info + ',' + 
                        college_info + ',' + degree_info + ',' + subject_info + ',' + skills + ',' + 
                        profile_url + ',' + keyword + '\n')
                
                end_time_inner = datetime.now() 
                time_diff_inner = end_time_inner - start_time_inner
                
                print('Profiles extracted:' + str(counter) + '  - time taken: '
                      +str(time_diff_inner.seconds)+'.'+str(time_diff_inner.microseconds)[:3]+' seconds')
                counter += 1

            except UnicodeEncodeError:
                pass
            
            
        except:
            pass

    # Saving the file
    driver.close()
    f.close()
    
    #Timer - Outer
    end_time_outer = datetime.now()
    time_diff_outer = end_time_outer - start_time_outer
    
    print('Program Execution Time: '+ str(time_diff_outer)[:-4])
###### DO NOT EDIT ###### WORKING CODE ######



# Calling function
# Here I will be scraping details of profiles with Python tag from 1st to 10th page

scraper('python', 1, 10) 

# Viewing the data first 10 and last 10 entries
df = pd.read_csv('test.csv', engine= 'python')

pd.concat([df.head(10),df.tail(10)])

##### END