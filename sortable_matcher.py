__author__ = 'Aamir'

import json
import re

def load_products(file_name):
    """Loads a list of products from a file.

    Args:
        file_name: the file to load data from, should be a single json encoded
            product per line.

    Returns:
        A list of dicts corresponding to the file lines.

    Raises:
        Exception: An exception if there is an error on reading the file.
    """

    products = []
    with open(file_name, 'r') as product_file:
        for product in product_file:
            product = json.loads(product)
            product['lower_manufacturer'] = product['manufacturer'].lower()
            model_variants = get_model_variants(product['model'])
            lower_regex = get_lower_regex(model_variants)
            regex_allow_trail = get_regex_allow_trail(model_variants)
            regex_allow_lead_and_trail = get_regex_allow_lead_and_trail(model_variants)
            product['lower_regex'] = lower_regex
            product['regex_allow_trail'] = regex_allow_trail
            product['regex_allow_lead_and_trail'] = regex_allow_lead_and_trail
            products.append(product)
    return products

def load_listings(file_name):
    """Loads a list of listings from a file.

    Args:
        file_name: the file to load data from, should be a single json-encoded
            listing per line.

    Returns:
        A list of dict corresponding to the file lines.

    Raises:
        Exception: An exception if there is an error on reading the file.
    """

    listings = []
    listings_mfr_dict = {}
    with open(file_name, 'r') as listing_file:
        for listing in listing_file:
            listing = json.loads(listing)
            listing['lower_title'] = listing['title'].lower()
            listing['lower_title_nodash'] = listing['lower_title'].replace('-', '')
            manufacturer = listing['manufacturer'].lower()
            listing['lower_manufacturer'] = manufacturer
            listings.append(listing)
            if manufacturer in listings_mfr_dict:
                listings_mfr_dict[manufacturer].append(listing)
            else:
                listings_mfr_dict[manufacturer] = [listing]
    return listings, listings_mfr_dict

def get_model_variants(product_model):
    l_model = product_model.lower()
    e_model = re.escape(l_model)
    nospace = re.escape(l_model.replace(' ', ''))
    nodash = re.escape(l_model.replace('-', ''))
    dashtospace = re.escape(l_model.replace('-', ' '))
    spacetodash = re.escape(l_model.replace(' ', '-'))
    return e_model, nospace, nodash, dashtospace, spacetodash

def get_lower_regex(model_variants):

    regex = '\W(?:%s|%s|%s|%s|%s)\W' % (
        model_variants[0],
        model_variants[1],
        model_variants[2],
        model_variants[3],
        model_variants[4])

    return re.compile(regex)

def get_regex_allow_trail(model_variants):
    regex = '\W(?:%s|%s|%s|%s|%s)\D' % (
        model_variants[0],
        model_variants[1],
        model_variants[2],
        model_variants[3],
        model_variants[4])

    return re.compile(regex)

def get_regex_allow_lead_and_trail(model_variants):
    regex = '\D(?:%s|%s|%s|%s|%s)\D' % (
        model_variants[0],
        model_variants[1],
        model_variants[2],
        model_variants[3],
        model_variants[4])

    return re.compile(regex)

def search_for_regex(regex, listing):
    return regex.search(listing['lower_title']) or regex.search(listing['lower_title_nodash'])

def is_listing_matched(product, listing):
    all_regex = [product['lower_regex'], product['regex_allow_trail'], product['regex_allow_lead_and_trail']]
    for regex in all_regex:
        if search_for_regex(regex, listing):
            return True

def find_matching_listings(product, listings):
    matched_listings = []
    for listing in listings:
        if is_listing_matched(product, listing):
            matched_listings.append(listing)
    return matched_listings

def match_products():
    product_file = 'products.txt'
    listing_file = 'listings.txt'
    output_file = 'matches.txt'

    print("Loading products from '%s'..." % product_file)
    products = load_products(product_file)
    print("Loaded %d products." % len(products))

    print("Loading listings from '%s'..." % listing_file)
    listings, listings_mfr_dict = load_listings(listing_file)
    print("Loaded %d listings." % len(listings))

    print("Matching...")

    results = []

    for product in products:
        possible_listings = listings_mfr_dict.get(product['manufacturer'].lower(), [])
        matched_listings = find_matching_listings(product, possible_listings)
        result_row = {"product_name": product['product_name'], 'listings': matched_listings}
        results.append(json.dumps(result_row))
    with open(output_file, 'w') as _file:
        _file.write('\n'.join(results))

    print("Matching Done and results written to matches.txt.")

if __name__ == "__main__":
    match_products()
