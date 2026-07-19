from bs4 import BeautifulSoup

def extract_title(soup: BeautifulSoup) -> str:
    """
    Extracts the page/company title from the HTML document.
    """
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        return og_title.get("content").strip()
        
    return ""

def extract_description(soup: BeautifulSoup) -> str:
    """
    Extracts the meta description or OG description.
    """
    desc = soup.find("meta", attrs={"name": "description"})
    if desc and desc.get("content"):
        return desc.get("content").strip()
        
    og_desc = soup.find("meta", property="og:description")
    if og_desc and og_desc.get("content"):
        return og_desc.get("content").strip()
        
    return ""

def extract_about_text(soup: BeautifulSoup) -> str:
    """
    Extracts a description about the company using semantic sections, headings, or fallbacks.
    """
    about_paragraphs = []
    
    # 1. Scan for standard identity element IDs or classes
    for keyword in ["about", "about-us", "who-we-are", "company", "mission", "overview"]:
        section = soup.find(id=keyword) or soup.find(class_=lambda c: c and keyword in c.lower())
        if section:
            paragraphs = section.find_all("p")
            if paragraphs:
                about_paragraphs.extend(paragraphs)
                break
                
    # 2. Look for headings containing identity keywords and fetch subsequent paragraphs
    if not about_paragraphs:
        for heading in soup.find_all(["h1", "h2", "h3"]):
            text = heading.get_text().lower()
            if "about" in text or "who we are" in text or "our mission" in text or "our story" in text:
                sibling = heading.next_sibling
                count = 0
                while sibling and count < 3:
                    if sibling.name == "p":
                        about_paragraphs.append(sibling)
                        count += 1
                    elif sibling.name in ["h1", "h2", "h3", "section", "div"] and sibling.get_text():
                        # If a div has paragraphs, search inside it
                        sub_p = sibling.find_all("p")
                        if sub_p:
                            about_paragraphs.extend(sub_p[:3])
                            break
                    sibling = sibling.next_sibling
                if about_paragraphs:
                    break

    # 3. Fallback: Grab the first three paragraphs in the document
    if not about_paragraphs:
        about_paragraphs = soup.find_all("p")[:3]
        
    about_text = " ".join([p.get_text().strip() for p in about_paragraphs if p.get_text()])
    about_text = " ".join(about_text.split()) # normalize spaces
    
    if len(about_text) > 1000:
        about_text = about_text[:997] + "..."
        
    return about_text
