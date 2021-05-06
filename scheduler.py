'''Python 3.9.4'''
valid_locations = ['1', '2', '3', '6', '12', '38', '80', '10', '20', '345']
valid_operations = ['Pick', 'Place', 'Transfer']
valid_names = ['None', 'Source Location', 'Destination Location']

def check_valid_locs(locs_list):
    return all(i in valid_locations for i in locs_list if i != '')