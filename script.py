from __future__ import absolute_import, unicode_literals

#mail
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
import os
#scraper
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from urllib.request import urlopen
import requests
import re
from datetime import datetime, timedelta
import http.client
from pathlib import Path
import pandas as pd
import numpy as np
import json
import time 
import lxml
import pytz
from pyvirtualdisplay import Display
display = Display(visible=0, size=(800, 800))  
display.start()

tmstmp = time.strftime("%d-%m-%Y %H%M%S")
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.headless = True
driver = webdriver.Chrome(chrome_options=chrome_options)
driver.create_options()
driver.get("https://greek-movies.com/series.php?s=1081") 
time.sleep(3)
cookies = driver.find_element_by_xpath ('//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]') #button [1][2] etc.
cookies.click()
latest = driver.find_element_by_xpath ('/html/body/div[2]/div[2]/div[2]/div[4]/div[1]/button[1]') #button [1][2] etc.
latest.click()
time.sleep(3)
urls = driver.find_elements_by_partial_link_text("προβολή")
time.sleep(2)


ep_lst = []
for url in urls:  
    ep_dic = {} 
    ep_dic ['url'] = url.get_attribute('href')
    ep_lst.append(ep_dic)



df_sd = pd.DataFrame(ep_lst)


for item in df_sd:
    def get_url(row):
        driver.get(row['url'])       
        act_url = driver.find_element_by_xpath("/html/body/div/div[2]/div[2]/div[1]/div[3]/a")
            
        return pd.Series({
            'actual_url': act_url.get_attribute('href')
        })

f_df_sd = df_sd.apply(get_url, axis=1).join(df_sd)
f_df_sd=f_df_sd[f_df_sd.actual_url.str.contains('megatv')==False]
f_df_sd_mixdrop=f_df_sd[f_df_sd.actual_url.str.contains('mixdrop')==True]
f_df_sd=f_df_sd[f_df_sd.actual_url.str.contains('mixdrop')==False]

for item in f_df_sd:
     def check_url(row):
        try:
            driver.get(row['actual_url']) 
            title = driver.title
            active = driver.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[1]/div/div[2]/div/div/div/div/div[4]').text
        except:
            title = '/n'
            active = 'yes'
        return pd.Series({
            'title': title,
            'active': active
        })
    

for item in f_df_sd_mixdrop:
     def check_url(row):
        try:
            driver.get(row['actual_url']) 
            title = driver.title
            mxdropactive=driver.find_element_by_class_name('container').find_element_by_class_name('error').find_element_by_class_name('wrapper').find_element_by_tag_name('h2').text
        except:
            title = '/n'
            mxdropactive = 'yes'
        return pd.Series({
            'title': title,
            'mxdropactive':mxdropactive
        })  



final_sd = f_df_sd.apply(check_url, axis=1).join(f_df_sd)

final_sd_mxdrop = f_df_sd_mixdrop.apply(check_url, axis=1).join(f_df_sd_mixdrop)


final_sd=final_sd[final_sd.title.str.contains('not found')==False]
final_sd=final_sd[final_sd.title.str.contains('Unable')==False]
final_sd=final_sd[final_sd.title.str.contains('violates')==False]
final_sd=final_sd[final_sd.title.str.contains('Private')==False]

final_sd.replace('', np.nan, inplace=True)
#final_sd.active.replace('', np.nan, inplace=True)
final_sd.dropna(inplace=True)

#final_sd.dropna(subset=['title'], inplace=True)
#final_sd.dropna(subset=['active'], inplace=True)

final_sd_mxdrop=final_sd_mxdrop[final_sd_mxdrop.mxdropactive.str.contains('SORRY')==False]



dm_list_sd = []
oload_list_sd = []
mule_list_sd = []
tune_list_sd = []
vcloud_list_sd = []
cw_list_sd=[]
mixdrop_list_sd=[]
streamtape_list_sd=[]


for item in final_sd.actual_url:
    if 'dailymotion' in item:
        dm_list_sd.append(item)
    if 'openload' in item:
        oload_list_sd.append(item)
    if 'datemule' in item:
        mule_list_sd.append(item)
    if 'tune.pk' in item:
        tune_list_sd.append(item)
    if 'vidcloud' in item:
        vcloud_list_sd.append(item)
    if 'clipwatching' in item:
        cw_list_sd.append(item)
    if 'streamtape' in item:
        streamtape_list_sd.append(item)
        
for item in final_sd_mxdrop:
    if 'mixdrop' in item:
            mixdrop_list_sd.append(item)

smtp = smtplib.SMTP()
smtp.connect('localhost')

msgRoot = MIMEMultipart("alternative")
msgRoot['Subject'] = Header("DMCA Notice_request for immediate removal of content", "utf-8")
msgRoot['From'] = "npitsiladis@megatv.com"

if any ('dailymotion' in s for s in dm_list_sd):
    msgRoot['To'] = "feedback@dailymotion.com"
    html ='Dear Sir/Madam, some new links have been found on your website. MEGA TV, a national TV broadcaster and producer from Greece, is the sole owner of the copyrighted material found on your website and has never granted any license to the uploader. The whole uploaded video (100%) is infringing as it is a whole episode.Thus, we demand immediate removal of this content:\n'+"\n".join(dm_list_sd)+'\nI state that upon a good faith belief the disputed use of the material or activity is not authorized by the copyright or intellectual property owner, its agent or the law and under penalty of perjury, MEGA TV is the copyright or intellectual property owner or is authorized to act on behalf of the copyright or intellectual property owner and that the information provided in the notice is accurate.Also (i) I have good faith belief that use of the material in the manner complained of is not authorized by the copyright owner, its agent, or the law.(ii) I swear under penalty of perjury, that the information in this notification is accurate and I am the copyright owner or am authorized to act on behalf of the owner of an exclusive right that is allegedly infringed.(iii) I accept that my private data will only be used by Dailymotion in the context of its copyright notification process which include sharing a copy of this claim with the user(s) who uploaded the allegedly infringing material.(iv) I recognize that I may be liable for damages if I knowingly materially misrepresent that the material or activity infringes on my copyright.'+'\n Nikos Pitsiladis Digital Manager \nSyggrou Ave 35, 17565, Athens-GREECE\nThank you'
    part1 = MIMEText(html, 'html')
    msgRoot.attach(part1)
    smtp.sendmail("npitsiladis@megatv.com", "feedback@dailymotion.com", msgRoot.as_string())

elif any ('mixdrop' in s for s in mixdrop_list_sd):
    msgRoot['To'] = "abuse@mixdrop.co"
    html ='Dear Sir/Madam, some new ACTIVE links have been found on your website. MEGA TV, a national TV broadcaster and producer from Greece, is the sole owner of the copyrighted material found on your website and has never granted any license to the uploader. Thus, we demand immediate removal of this content:\n'+"\n".join(mixdrop_list_sd)+'\nI state that upon a good faith belief the disputed use of the material or activity is not authorized by the copyright or intellectual property owner, its agent or the law and under penalty of perjury, MEGA TV is the copyright or intellectual property owner or is authorized to act on behalf of the copyright or intellectual property owner and that the information provided in the notice is accurate.'+'\n Nikos Pitsiladis Digital Manager \nSyggrou Ave 35, 17565, Athens-GREECE\nThank you'
    part1 = MIMEText(html, 'html')
    msgRoot.attach(part1)
    smtp.sendmail("npitsiladis@megatv.com", "abuse@mixdrop.co", msgRoot.as_string())

elif any ('streamtape' in s for s in streamtape_list_sd):
    msgRoot['To'] = "dmca@streamtape.com"
    html ='Dear Sir/Madam, some new ACTIVE links have been found on your website. MEGA TV, a national TV broadcaster and producer from Greece, is the sole owner of the copyrighted material found on your website and has never granted any license to the uploader. Thus, we demand immediate removal of this content:\n'+"\n".join(streamtape_list_sd)+'\nI state that upon a good faith belief the disputed use of the material or activity is not authorized by the copyright or intellectual property owner, its agent or the law and under penalty of perjury, MEGA TV is the copyright or intellectual property owner or is authorized to act on behalf of the copyright or intellectual property owner and that the information provided in the notice is accurate.'+'\n Nikos Pitsiladis Digital Manager \nSyggrou Ave 35, 17565, Athens-GREECE\nThank you'
    part1 = MIMEText(html, 'html')
    msgRoot.attach(part1)
    smtp.sendmail("npitsiladis@megatv.com", "dmca@streamtape.com", msgRoot.as_string())
elif any ('datemule' in s for s in mule_list_sd):
    driver.get("https://www.datemule.com/compliance/MegaTVGreece") 
    mail=driver.find_element_by_xpath('//*[@id="form"]/input[1]')
    mail.send_keys("npitsiladis@megatv.com")
    links=driver.find_element_by_xpath('//*[@id="links"]')
    links.send_keys('\n'.join(mule_list_sd)+"\n")
    terms=driver.find_element_by_xpath('//*[@id="form"]/input[2]')
    terms.click()
    submit=driver.find_element_by_xpath('//*[@id="form"]/input[3]')
    submit.click()

driver.close()

smtp = smtplib.SMTP()
smtp.connect('localhost')
msgRoot = MIMEMultipart("alternative")
msgRoot['Subject'] = Header("DMCA Notice_request for immediate removal of content", "utf-8")
msgRoot['From'] = "npitsiladis@megatv.com"
msgRoot['To'] = "nickospi@gmail.com"
html ='These are the reported links: ' +'\n'.join(mule_list_sd)+'\n'+'\n'.join(streamtape_list_sd)+'\n'+'\n'.join(mixdrop_list_sd)+'\n'+'\n'.join(dm_list_sd)
part1 = MIMEText(html, 'html')
msgRoot.attach(part1)
smtp.sendmail("npitsiladis@megatv.com", "nickospi@gmail.com", msgRoot.as_string())


#######

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.headless = True
driver = webdriver.Chrome(chrome_options=chrome_options)
driver.create_options()
driver.get("https://greek-movies.com/series.php?s=1081") 
time.sleep(3)
cookies = driver.find_element_by_xpath ('//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]') #button [1][2] etc.
cookies.click()
latest = driver.find_element_by_xpath ('/html/body/div[2]/div[2]/div[2]/div[4]/div[1]/button[2]') #button [1][2] etc.
latest.click()
time.sleep(3)
urls = driver.find_elements_by_partial_link_text("προβολή")
time.sleep(2)


ep_lst = []
for url in urls:  
    ep_dic = {} 
    ep_dic ['url'] = url.get_attribute('href')
    ep_lst.append(ep_dic)



df_sd = pd.DataFrame(ep_lst)


for item in df_sd:
    def get_url(row):
        driver.get(row['url'])       
        act_url = driver.find_element_by_xpath("/html/body/div/div[2]/div[2]/div[1]/div[3]/a")
            
        return pd.Series({
            'actual_url': act_url.get_attribute('href')
        })


f_df_sd = df_sd.apply(get_url, axis=1).join(df_sd)

f_df_sd=f_df_sd[f_df_sd.actual_url.str.contains('megatv')==False]

for item in f_df_sd:
     def check_url(row):
        try:
            driver.get(row['actual_url']) 
            title = driver.title
            active=driver.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[1]/div/div[2]/div/div/div/div/div[4]').text
        except:
            title = '/n'
            active = 'yes'
        return pd.Series({
            'title': title,
            'active': active
        })  

final_sd = f_df_sd.apply(check_url, axis=1).join(f_df_sd)
final_sd=final_sd[final_sd.title.str.contains('not found')==False]
final_sd=final_sd[final_sd.title.str.contains('Unable')==False]
final_sd=final_sd[final_sd.title.str.contains('violates')==False]
final_sd=final_sd[final_sd.title.str.contains('Private')==False]

final_sd.replace('', np.nan, inplace=True)
#final_sd.active.replace('', np.nan, inplace=True)
final_sd.dropna(inplace=True)

#final_sd.dropna(subset=['title'], inplace=True)
#final_sd.dropna(subset=['active'], inplace=True)


dm_list_sd = []
oload_list_sd = []
mule_list_sd = []
tune_list_sd = []
vcloud_list_sd = []
cw_list_sd=[]
mixdrop_list_sd=[]
streamtape_list_sd=[]


for item in final_sd.actual_url:
    if 'dailymotion' in item:
        dm_list_sd.append(item)
    if 'openload' in item:
        oload_list_sd.append(item)
    if 'datemule' in item:
        mule_list_sd.append(item)
    if 'tune.pk' in item:
        tune_list_sd.append(item)
    if 'vidcloud' in item:
        vcloud_list_sd.append(item)
    if 'clipwatching' in item:
        cw_list_sd.append(item)
    if 'mixdrop' in item:
        mixdrop_list_sd.append(item)
    if 'streamtape' in item:
        streamtape_list_sd.append(item)





smtp = smtplib.SMTP()
smtp.connect('localhost')

msgRoot = MIMEMultipart("alternative")
msgRoot['Subject'] = Header("DMCA Notice_request for immediate removal of content", "utf-8")
msgRoot['From'] = "npitsiladis@megatv.com"

if any ('dailymotion' in s for s in dm_list_sd):
    msgRoot['To'] = "feedback@dailymotion.com"
    html ='Dear Sir/Madam, some new links have been found on your website. MEGA TV, a national TV broadcaster and producer from Greece, is the sole owner of the copyrighted material found on your website and has never granted any license to the uploader. The whole uploaded video (100%) is infringing as it is a whole episode.Thus, we demand immediate removal of this content:\n'+"\n".join(dm_list_sd)+'\nI state that upon a good faith belief the disputed use of the material or activity is not authorized by the copyright or intellectual property owner, its agent or the law and under penalty of perjury, MEGA TV is the copyright or intellectual property owner or is authorized to act on behalf of the copyright or intellectual property owner and that the information provided in the notice is accurate.Also (i) I have good faith belief that use of the material in the manner complained of is not authorized by the copyright owner, its agent, or the law.(ii) I swear under penalty of perjury, that the information in this notification is accurate and I am the copyright owner or am authorized to act on behalf of the owner of an exclusive right that is allegedly infringed.(iii) I accept that my private data will only be used by Dailymotion in the context of its copyright notification process which include sharing a copy of this claim with the user(s) who uploaded the allegedly infringing material.(iv) I recognize that I may be liable for damages if I knowingly materially misrepresent that the material or activity infringes on my copyright.'+'\n Nikos Pitsiladis Digital Manager \nSyggrou Ave 35, 17565, Athens-GREECE\nThank you'
    part1 = MIMEText(html, 'html')
    msgRoot.attach(part1)
    smtp.sendmail("npitsiladis@megatv.com", "feedback@dailymotion.com", msgRoot.as_string())

elif any ('mixdrop' in s for s in mixdrop_list_sd):
    msgRoot['To'] = "abuse@mixdrop.co"
    html ='Dear Sir/Madam, some new ACTIVE links have been found on your website. MEGA TV, a national TV broadcaster and producer from Greece, is the sole owner of the copyrighted material found on your website and has never granted any license to the uploader. Thus, we demand immediate removal of this content:\n'+"\n".join(mixdrop_list_sd)+'\nI state that upon a good faith belief the disputed use of the material or activity is not authorized by the copyright or intellectual property owner, its agent or the law and under penalty of perjury, MEGA TV is the copyright or intellectual property owner or is authorized to act on behalf of the copyright or intellectual property owner and that the information provided in the notice is accurate.'+'\n Nikos Pitsiladis Digital Manager \nSyggrou Ave 35, 17565, Athens-GREECE\nThank you'
    part1 = MIMEText(html, 'html')
    msgRoot.attach(part1)
    smtp.sendmail("npitsiladis@megatv.com", "abuse@mixdrop.co", msgRoot.as_string())

elif any ('streamtape' in s for s in streamtape_list_sd):
    msgRoot['To'] = "dmca@streamtape.com"
    html ='Dear Sir/Madam, some new ACTIVE links have been found on your website. MEGA TV, a national TV broadcaster and producer from Greece, is the sole owner of the copyrighted material found on your website and has never granted any license to the uploader. Thus, we demand immediate removal of this content:\n'+"\n".join(streamtape_list_sd)+'\nI state that upon a good faith belief the disputed use of the material or activity is not authorized by the copyright or intellectual property owner, its agent or the law and under penalty of perjury, MEGA TV is the copyright or intellectual property owner or is authorized to act on behalf of the copyright or intellectual property owner and that the information provided in the notice is accurate.'+'\n Nikos Pitsiladis Digital Manager \nSyggrou Ave 35, 17565, Athens-GREECE\nThank you'
    part1 = MIMEText(html, 'html')
    msgRoot.attach(part1)
    smtp.sendmail("npitsiladis@megatv.com", "dmca@streamtape.com", msgRoot.as_string())

elif any ('datemule' in s for s in mule_list_sd):
    driver.get("https://www.datemule.com/compliance/MegaTVGreece") 
    mail=driver.find_element_by_xpath('//*[@id="form"]/input[1]')
    mail.send_keys('npitsiladis@megatv.com')
    links=driver.find_element_by_xpath('//*[@id="links"]')
    links.send_keys('\n'.join(mule_list_sd)+'\n')
    terms=driver.find_element_by_xpath('//*[@id="form"]/input[2]')
    terms.click()
    submit=driver.find_element_by_xpath('//*[@id="form"]/input[3]')
    submit.click()

driver.quit()

    
smtp = smtplib.SMTP()
smtp.connect('localhost')

msgRoot = MIMEMultipart("alternative")
msgRoot['Subject'] = Header("DMCA Notice_request for immediate removal of content", "utf-8")
msgRoot['From'] = "npitsiladis@megatv.com"
msgRoot['To'] = "nickospi@gmail.com"
html ='These are the reported links: ' +'\n'.join(mule_list_sd)+'\n'+'\n'.join(streamtape_list_sd)+'\n'+'\n'.join(mixdrop_list_sd)+'\n'+'\n'.join(dm_list_sd)
part1 = MIMEText(html, 'html')
msgRoot.attach(part1)
smtp.sendmail("npitsiladis@megatv.com", "nickospi@gmail.com", msgRoot.as_string())



