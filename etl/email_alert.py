# etl/email_alert.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import csv
from tempfile import NamedTemporaryFile
import os





def send_email(products, sender_email, recipient_email, smtp_server, smtp_port, smtp_user, smtp_password):
    if not products:
        print("ℹ️ No discounted products to email.")
        return

    source_site = products[0].get('source_site', 'Unknown Site') 
    
    # Create the email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📢 Discount Alert – E-Commerce Deals"
    msg["From"] = sender_email
    msg["To"] = recipient_email

    # # Build the HTML body (an optional way to format the email)
    # html_body = """
    # <h2>🔥 Discounted Products</h2>
    # <table border='1' cellpadding='6' cellspacing='0'>
    #     <tr>
    #         <th>Name</th>
    #         <th>Brand</th>
    #         <th>Price</th>
    #         <th>Discount</th>
    #         <th>Link</th>
    #         <th>Source Site</th>
    #     </tr>
    # """

    # for p in products:
    #     name = p.get('name', 'Unknown')
    #     brand = p.get('brand', 'Unknown')
    #     price = f"{p.get('discounted_price', 0.0)} {p.get('currency', 'EUR')}"
    #     discount = f"{p.get('discount_percent', 0)}%"
    #     url = p.get('url', '#')
    #     source_site = p.get('source_site', 'Unknown Site')

    #     html_body += f"""
    #     <tr>
    #         <td>{name}</td>
    #         <td>{brand}</td>
    #         <td>{price}</td>
    #         <td>{discount}</td>
    #         <td><a href="{url}">View</a></td>
    #         <td>{source_site}</td>
    #     </tr>
    #     """

    # html_body += "</table>"
    
    with NamedTemporaryFile(mode='w', delete=False, suffix='.csv',encoding='utf-8', newline='') as temp_csv:
        fieldnames = ['Name', 'Brand', 'Price', 'Discount', 'Link', 'Source Site']
        writer = csv.DictWriter(temp_csv, fieldnames=fieldnames)
        writer.writeheader()
        for p in products:
            writer.writerow({
                'Name': p.get('name', 'Unknown'),
                'Brand': p.get('brand', 'Unknown'),
                'Price': f"{p.get('discounted_price', 0.0)} {p.get('currency', 'EUR')}",
                'Discount': f"{p.get('discount_percent', 0)}%",
                'Link': p.get('url', '#'),
                'Source Site': p.get('source_site', 'Unknown Site')
            })
        temp_csv_path = temp_csv.name
        
    with open(temp_csv_path, 'rb') as f:
        part = MIMEApplication(f.read(), _subtype="csv")
        part.add_header('Content-Disposition', 'attachment', filename="discounted_products.csv")
        msg.attach(part)
    
    
    

    # Send email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print("✅ Email sent.")
    except Exception as e:
        print(f"❌ Email failed: {e}")
        
    finally:
        os.remove(temp_csv_path)
        print(f"🗑️ Temporary file {temp_csv_path} deleted.")
