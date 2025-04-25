import requests
import csv
import json
import time
from datetime import datetime
from tqdm import tqdm

# Base URL and headers
BASE_URL = "https://pultegroup.wd1.myworkdayjobs.com/wday/cxs/pultegroup/PGI/jobs"
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

def fetch_jobs(offset=0, limit=20):
    """Fetch jobs from the API with pagination"""
    payload = {
        "appliedFacets": {},
        "limit": limit,
        "offset": offset,
        "searchText": ""
    }
    
    try:
        response = requests.post(BASE_URL, json=payload, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching jobs: {e}")
        return None

def get_job_details(job_id):
    """Fetch detailed information for a specific job"""
    detail_url = f"{BASE_URL}/{job_id}"
    
    try:
        response = requests.get(detail_url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching job details for {job_id}: {e}")
        return None

def scrape_jobs():
    """Scrape all jobs with pagination and return as a list"""
    all_jobs = []
    offset = 0
    limit = 20
    total = None
    
    print("Starting job scraping process...")
    
    while True:
        data = fetch_jobs(offset, limit)
        
        if not data or "jobPostings" not in data:
            print("No data returned or invalid response format")
            break
        
        if total is None:
            total = data.get("total", 0)
            print(f"Found {total} job postings to scrape")
        
        jobs = data["jobPostings"]
        if not jobs:
            break
            
        for job in jobs:
            job_id = job.get("externalPath", "").split("/")[-1]
            
            job_info = {
                "title": job.get("title", ""),
                "location": ", ".join([loc.get("name", "") for loc in job.get("locations", [])]),
                "posted_date": job.get("postedOn", ""),
                "job_id": job_id,
                "url": f"https://pultegroup.wd1.myworkdayjobs.com/en-US/PGI/job/{job_id}"
            }
            
            all_jobs.append(job_info)
        
        print(f"Scraped {len(all_jobs)} jobs so far...")
        
        # Pagination: Check if we've processed all jobs
        if len(all_jobs) >= total or len(jobs) < limit:
            break
            
        offset += limit
        time.sleep(1)  # Polite delay between requests
    
    print(f"Successfully scraped {len(all_jobs)} jobs")
    return all_jobs

def save_to_csv(jobs, filename=None):
    """Save the scraped jobs to a CSV file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pultegroup_jobs_{timestamp}.csv"
    
    if not jobs:
        print("No jobs to save.")
        return
    
    fieldnames = jobs[0].keys()
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for job in jobs:
                writer.writerow(job)
        
        print(f"Successfully saved {len(jobs)} jobs to {filename}")
    except IOError as e:
        print(f"Error saving to CSV: {e}")

def main():
    """Main function to run the scraper"""
    print("Starting PulteGroup job scraper...")
    jobs = scrape_jobs()
    
    if jobs:
        save_to_csv(jobs)
    
    print("Job scraping completed.")

if __name__ == "__main__":
    main()
