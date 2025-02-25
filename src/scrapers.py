# scrapers.py
from utils import safe_get_text

class BaseScraper:
    def __init__(self, soup):
        self.soup = soup

    def extract_id(self, link):
        """Extract the ID from a URL (the portion after the final '/')"""
        return link.rstrip('/').split('/')[-1] if link else ''


class CommissionScraper(BaseScraper):
    """Generic scraper for commission meetings"""
    def scrape(self):
        data = []
        cards = self.soup.select('article.card.meeting-card')
        for card in cards:
            header = card.find('header', class_='card__header')
            date_text = safe_get_text(header.find('span', class_='card__date')) if header else ''
            h4 = header.find('h4', class_='card__title') if header else None
            h5 = header.find('h5', class_='card__title') if header else None
            title1 = safe_get_text(h4)
            title2 = safe_get_text(h5)
            full_title = title1 + ((" - " + title2) if title2 else "")
            description = safe_get_text(card.select_one('div.card__description p'))
            view_link_tag = card.select_one('li.card__link.card__link-view a')
            view_link = view_link_tag.get('href', '') if view_link_tag else ''
            watch_link_tag = card.select_one('li.card__link.card__link-watch a')
            watch_link = watch_link_tag.get('href', '') if watch_link_tag else ''
            extracted_id = self.extract_id(view_link)
            data.append({
                'date': date_text,
                'title': full_title,
                'description': description,
                'view_link': view_link,
                'watch_link': watch_link,
                'ID': extracted_id
            })
        fieldnames = ['date', 'title', 'description', 'view_link', 'watch_link', 'ID']
        return data, fieldnames


# Keep these for backward compatibility or if you want to process other types
class VragenOmgevingScraper(BaseScraper):
    def scrape(self):
        data = []
        cards = self.soup.select('article.card.card--document')
        for card in cards:
            title = safe_get_text(card.find(class_='card__title'))
            author = safe_get_text(card.find(class_='card__author'))
            status = safe_get_text(card.find(class_='card__status'))
            view_link_tag = card.select_one('.card__link.card__link-view a')
            view_link = view_link_tag.get('href', '') if view_link_tag else ''
            download_tag = card.select_one('.card__link.card__link-download a')
            download_link = download_tag.get('href', '') if download_tag else ''
            extracted_id = self.extract_id(view_link)
            data.append({
                'card__title': title,
                'card__author': author,
                'card__status': status,
                'view_link': view_link,
                'card__link card__link-download': download_link,
                'ID': extracted_id
            })
        fieldnames = ['card__title', 'card__author', 'card__status', 'view_link', 'card__link card__link-download', 'ID']
        return data, fieldnames


class CommOmgevingScraper(CommissionScraper):
    """Kept for backward compatibility"""
    pass