# Part 2 - Measuring Wikipedia on IPFS

## Preparation Phase:
- [URL_crawler.py](URL_crawler.py): recursively crawls a webpage for unique links. The URL of the webpage and the recursion depth can be passed as arguments.
- [convert_URL_to_CID.py](convert_URL_to_CID.py): Uses IPNS to convert the collected URLs to IPFS CIDs.

## Main loop:
- [process_CID.py](process_CID.py): Takes a single language from Wikipedia, samples a percentage of articles, and performs various IPFS commands with the CIDs of these articles. 
- [repeated_measurements_all.py](repeated_measurements_all.py): Calls `process_CID.py` continuously for all eight Wikipedia languages until stopped.

## Post-processing / Data Analysis
- [clean_unreachable_providers.py](clean_unreachable_providers.py): Removes providers that were unreachable from the output. Creates new files with the `_cleaned` suffix. The scripts below only work with `_cleaned` files. 
- [analyze_article_availability_IPFS.py](analyze_article_availability_IPFS.py): Creates a plot showing the article availabilty on IPFS.
- [analyze_article_availability_website.py](analyze_article_availability_website.py): Creates a plot showing the article availabilty on the wikipedia-on-ipfs.org website.
- [analyze_number_of_providers.py](analyze_number_of_providers.py): Creates a plot showing the number of unique providers contributing to Wikipedia.