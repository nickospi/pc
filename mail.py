import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
import os


smtp = smtplib.SMTP()
smtp.connect('localhost')

msgRoot = MIMEMultipart("alternative")
msgRoot['Subject'] = Header("Subject subject", "utf-8")
msgRoot['From'] = "npitsiladis@megatv.com"
msgRoot['To'] = "nickospi@gmail.com"
text ='Dear Sir/Madam, some new ACTIVE links have been found on your website. ANT1 TV is the sole owner of the copyrighted material found on your website and has never granted any license to the uploader. Thus, we demand immediate removal of this content:\n'+"\n".join(oload_list_gyn)+"\n"+"\n".join(oload_list_ep)+"\n"+"\n".join(oload_list_frtz)+"\n"+"\n".join(oload_list_pathos)+"\n"+"\n".join(oload_list_goneis)+'\nI state that upon a good faith belief the disputed use of the material or activity is not authorized by the copyright or intellectual property owner, its agent or the law and under penalty of perjury, ANT1 TV is the copyright or intellectual property owner or is authorized to act on behalf of the copyright or intellectual property owner and that the information provided in the notice is accurate.'+'\nNikos Pitsiladis Digital Manager \nKifissias 10-12 Maroussi \nThank you'
#html = MIMEText(open('template.html', 'r').read(), "html", "utf-8")
msgRoot.attach(html)
smtp.sendmail("admin@example.com", "foo@bar.com", msgRoot.as_string())
